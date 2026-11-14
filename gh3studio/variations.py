"""Seeded pattern retrieval and constrained lane transfer. No neural training."""
import copy
import hashlib
import json
import random
from dataclasses import replace
from itertools import combinations
from .converter import convert
from .model import Note,ChartError
from .patterns import extract,groups,WINDOW_BEATS
from .validation import ensure_valid

VARIANTS=('Rhythm Technical','Melodic Technical','Adaptive Expert Medium')
ALGORITHM='pattern-transfer-v1'

def generate_variations(song,settings,store,seed=0,cancelled=lambda:False):
    if not isinstance(seed,int) or not 0<=seed<=2147483647: raise ChartError('Seed must be 0–2147483647')
    if store.summary()['patterns']==0: raise ChartError('Scan a chart folder before generating learned variations')
    fingerprint=store.fingerprint(cancelled)
    baseline,base_report=convert(song,settings,cancelled)
    windows=extract(baseline,'Medium',cancelled)
    baseline_groups=groups(baseline.tracks['Medium'])
    by_window={}
    for tick,ns in baseline_groups: by_window.setdefault(tick//(song.resolution*WINDOW_BEATS),[]).append((tick,ns))
    outputs={}
    for variant_index,name in enumerate(VARIANTS):
        rng=random.Random(seed+variant_index*104729);result=copy.deepcopy(baseline);notes=[];matches=[];memo={}
        for query in windows:
            if cancelled(): raise ChartError('Cancelled; no variants published')
            features=dict(query['features'])
            if variant_index==0: features['chord_ratio']=max(.5,features['chord_ratio'])
            elif variant_index==1: features.update(chord_ratio=0,movement=max(1.5,features['movement']))
            motif=json.dumps(query['tokens'],sort_keys=True)
            if motif not in memo:
                candidates=store.similar(features,limit=6)
                if not candidates: raise ChartError('No eligible stored patterns')
                weights=[1/(1+max(0,c['distance']-candidates[0]['distance'])) for c in candidates]
                memo[motif]=rng.choices(candidates,weights=weights,k=1)[0]
            chosen=memo[motif];donor=chosen['data']['tokens']
            events=by_window[query['start_tick']//(song.resolution*WINDOW_BEATS)]
            previous=None
            for index,(tick,ns) in enumerate(events):
                if cancelled(): raise ChartError('Cancelled; no variants published')
                token=donor[min(len(donor)-1,index*len(donor)//len(events))]
                desired=[lane*.75 for lane in token['lanes']]
                # Rhythm retains baseline chords. Melody selects one voice. Adaptive
                # follows donor chord size but never adds gems beyond the source cap.
                size=len(ns) if variant_index==0 else 1 if variant_index==1 else min(len(ns),len(desired))
                options=list(combinations(range(4),size))
                targets=[desired[min(len(desired)-1,i*len(desired)//size)] for i in range(size)]
                def score(candidate):
                    shape=sum((a-b)**2 for a,b in zip(candidate,targets))
                    movement=0 if previous is None else abs(sum(candidate)/len(candidate)-sum(previous)/len(previous))
                    return shape+(6-settings.movement)*.2*movement
                best=min(score(c) for c in options)
                tied=[c for c in options if abs(score(c)-best)<1e-9]
                target=rng.choice(tied)
                # Selected source has already passed the common-length sustain gate.
                notes.extend(Note(tick,lane,ns[0].length) for lane in target)
                previous=target
            matches.append({'window_start_tick':query['start_tick'],'pattern_id':chosen['id'],
                            'source_hash':chosen['source_id'],'source_difficulty':chosen['difficulty'],
                            'source_window_start':chosen['start_tick'],'distance':chosen['distance'],
                            'rating':chosen['rating']})
        result.tracks['Medium']=sorted(notes)
        ensure_valid(result,True)
        report=copy.deepcopy(base_report)
        report.update(variant=name,seed=seed,algorithm=ALGORITHM,corpus_fingerprint=fingerprint,pattern_matches=matches,
                      medium_events=len({n.tick for n in notes}),medium_gems=len(notes),
                      removed_gems=base_report['source_gems']-len(notes))
        report['settings']=dict(report['settings'],variation=name,seed=seed,algorithm=ALGORITHM,corpus_fingerprint=fingerprint)
        # Baseline warning about removed gems may no longer describe melodic output.
        report['warnings']=[w for w in report['warnings'] if 'gems removed by density/chord settings' not in w]
        report['warnings'] += [f"{report['removed_gems']} source gems removed by settings and variation policy.",
            'Variations transfer stored lane shapes onto existing authored events. No audio analysis or neural model training occurred.',
            'Similarity and pattern ratings are selection heuristics, not objective musical-quality scores.']
        outputs[name]=(result,report)
    unique=len({tuple(pair[0].tracks['Medium']) for pair in outputs.values()})
    for _,report in outputs.values():
        report['distinct_variation_count']=unique
        if unique<3: report['warnings'].append(f'Only {unique} distinct note arrangement(s) resulted; the corpus/input does not guarantee three unique patterns.')
    if store.fingerprint(cancelled)!=fingerprint: raise ChartError('Pattern database changed during generation; retry with a stable corpus')
    return outputs
