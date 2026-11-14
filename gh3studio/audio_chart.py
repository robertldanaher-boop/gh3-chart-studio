"""Audio-onset drafts and alignment diagnostics with explicit offset convention."""
import copy
from fractions import Fraction
from pathlib import Path
import numpy as np
from .model import Song,Note,ChartError
from .validation import ensure_valid
from .converter import Settings
from .variations import generate_variations

class TempoClock:
    def __init__(self,song):
        self.resolution=song.resolution;self.tempos=song.tempos;self.starts=[];seconds=Fraction(0)
        for i,(tick,tempo) in enumerate(song.tempos):
            if i:seconds+=(tick-song.tempos[i-1][0])*song.tempos[i-1][1]/song.resolution/1000000
            self.starts.append(seconds)
    def tick(self,seconds):
        value=Fraction(str(seconds))
        if value<0:raise ChartError('Chart shift would place an attack before tick zero; reduce the negative shift')
        index=int(np.searchsorted(self.starts,value,side='right'))-1;index=max(0,index)
        tick,tempo=self.tempos[index]
        return tick+round((value-self.starts[index])*self.resolution*1000000/tempo)

def make_draft(analysis,shift_ms=0,template=None,store=None,seed=0,cancelled=lambda:False):
    if not np.isfinite(shift_ms) or abs(shift_ms)>10000:raise ChartError('Chart shift must be within ±10,000 ms')
    if not analysis.onsets:raise ChartError('No detected attacks to chart')
    if template is None and analysis.bpm is None:raise ChartError('Set a manual BPM and reanalyze, or use an authored tempo map')
    if template:
        ensure_valid(template)
        if float(template.metadata.get('Offset','0'))!=0:raise ChartError('Template Offset must be zero; apply an explicit chart shift instead')
        song=copy.deepcopy(template)
    else:
        song=Song(resolution=960,metadata={'Name':Path(analysis.source_path).stem+' - Audio Draft','Artist':'Unknown','Offset':'0'},
                  tempos=[(0,Fraction(60000000)/Fraction(str(analysis.bpm)))])
    clock=TempoClock(song)
    values=np.array([o['centroid_hz'] for o in analysis.onsets]);bounds=np.quantile(values,[.25,.5,.75])
    notes=[];seen=set()
    for onset in analysis.onsets:
        if cancelled():raise ChartError('Cancelled; no audio draft published')
        tick=clock.tick(onset['time']+shift_ms/1000)
        if tick in seen:raise ChartError('Two detected attacks collide at this PPQ; use a higher-resolution template')
        seen.add(tick)
        # Timbre rank is only a deterministic lane-shape heuristic, not pitch transcription.
        lane=int(np.searchsorted(bounds,onset['centroid_hz'],side='left'))
        notes.append(Note(tick,lane,0))
    matches=None
    if store:
        temporary=copy.deepcopy(song);temporary.tracks={'Expert':notes};temporary.phrases={};temporary.modifiers={}
        variations=generate_variations(temporary,Settings(chords=1),store,seed,cancelled)
        candidate,learned_report=variations['Adaptive Expert Medium'];notes=candidate.tracks['Medium'];matches=learned_report
    song.tracks['Medium']=notes;song.phrases['Medium']=[];song.modifiers.pop('Medium',None)
    if template is None:song.tracks['Expert']=copy.deepcopy(notes)
    # Do not fabricate Star Power or infer note sustain lengths from a mixed recording.
    existing_end=max((t for t,e in song.events if e=='end'),default=0)
    note_end=max((n.tick+n.length for ns in song.tracks.values() for n in ns),default=0)
    end_tick=max(existing_end,note_end,clock.tick(analysis.duration+max(0,shift_ms/1000)))
    song.events=[(t,e) for t,e in song.events if e!='end']
    song.events.append((end_tick,'end'));song.events.sort()
    validation=ensure_valid(song,True)
    report=dict(validation,source_events=len(analysis.onsets),source_gems=len(analysis.onsets),medium_events=len(notes),medium_gems=len(notes),
                removed_events=0,removed_gems=0,status='Audio onset draft — listening and gameplay review required',
                settings={'audio_analysis':analysis.settings,'shift_ms':shift_ms,'use_authored_tempo_map':template is not None,'use_learned_patterns':store is not None,'seed':seed},
                audio={'path':analysis.source_path,'sha256':analysis.source_hash,'duration':analysis.duration,'algorithm':analysis.algorithm,
                       'estimated_bpm':analysis.bpm,'beat_fit':analysis.beat_fit},
                pattern_transfer=matches,
                max_tick_rounding_error_ms=max(abs(song.seconds(n.tick)-(o['time']+shift_ms/1000))*1000 for n,o in zip(notes,analysis.onsets)))
    report['warnings']+=analysis.warnings+[
        'This is an onset-derived draft, not verified guitar transcription. No sustain or Star Power inference is performed.',
        'Positive shift moves chart notes later relative to audio; the original audio is never moved or re-encoded.',
        'Without learned patterns, lane shape follows timbre ranks, not detected guitar pitches.',
        'TheGHOST/Windows/Dolphin/Wii runtime acceptance remains pending.']
    return song,report

def alignment_report(song,difficulty,analysis,shift_ms=0):
    ensure_valid(song)
    if not np.isfinite(shift_ms) or abs(shift_ms)>10000:raise ChartError('Chart shift must be within ±10,000 ms')
    ticks=sorted({n.tick for n in song.tracks.get(difficulty,[])})
    if not ticks or not analysis.onsets:raise ChartError('Alignment requires both chart notes and detected audio attacks')
    note_times=np.array([song.seconds(t)+shift_ms/1000 for t in ticks]);attacks=np.array([o['time'] for o in analysis.onsets])
    indexes=np.searchsorted(attacks,note_times)
    right=np.minimum(indexes,len(attacks)-1);left=np.maximum(0,indexes-1)
    nearest=np.where(np.abs(attacks[left]-note_times)<=np.abs(attacks[right]-note_times),left,right)
    residual=attacks[nearest]-note_times
    within=np.abs(residual)<=.25
    warnings=['Nearest-attack matching can associate a note with the wrong instrument/beat; suggested corrections require listening.',
              'Positive residual means the chart note is early; positive chart shift moves it later.']
    if float(song.metadata.get('Offset','0'))!=0:warnings.append('Authored chart Offset is not automatically applied; include the intended shift explicitly.')
    count=int(within.sum());unique_matches=len(set(nearest[within].tolist()));result={'difficulty':difficulty,'chart_events':len(ticks),'audio_attacks':len(attacks),'matched_within_250ms':count,
        'unmatched_events':len(ticks)-count,'unique_matched_attacks':unique_matches,'shift_ms':shift_ms,'warnings':warnings,'samples':[]}
    result['samples']=[{'chart_seconds':round(float(t),6),'nearest_attack':float(attacks[i]),'residual_ms':round(float(r)*1000,3),'within_250ms':bool(ok)}
        for t,i,r,ok in zip(note_times,nearest,residual,within)]
    if count<3 or unique_matches<3:
        result.update(suggested_additional_shift_ms=None,median_abs_error_ms=None,drift_ms_per_minute=None,interpretation='Insufficient matched events')
        return result
    accepted=residual[within];positions=note_times[within];median=float(np.median(accepted))
    # Median residuals by time third reduce outlier sensitivity; not an automatic warp.
    order=np.argsort(positions);chunks=np.array_split(order,3)
    xs=np.array([np.median(positions[c]) for c in chunks]);ys=np.array([np.median(accepted[c]) for c in chunks])
    slope=float(np.polyfit(xs,ys,1)[0]) if xs[-1]-xs[0]>1 else 0.0
    scatter=float(np.median(np.abs(accepted-median)))
    interpretation='Possible tempo drift; inspect the tempo map' if abs(slope)*60000>20 else 'Possible global offset' if abs(median)>.02 and scatter<.03 else 'Mixed/local timing differences; review individual attacks'
    result.update(suggested_additional_shift_ms=round(median*1000,3),median_abs_error_ms=round(float(np.median(np.abs(accepted)))*1000,3),
        residual_mad_ms=round(scatter*1000,3),drift_ms_per_minute=round(slope*60000,3),interpretation=interpretation)
    return result
