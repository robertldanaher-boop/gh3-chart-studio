"""Deterministic authored-rhythm conversion, not ML or audio transcription."""
import copy
from dataclasses import dataclass, asdict
from itertools import combinations, groupby
from .model import Note, ChartError
from .validation import ensure_valid

@dataclass(frozen=True)
class Settings:
    source: str = 'Expert'
    density: int = 6
    chords: int = 4
    movement: int = 5
    max_chord: int = 3

    def check(self):
        if self.source not in ('Expert','Hard'): raise ChartError('Choose Expert or Hard')
        if any(not 1<=v<=6 for v in (self.density,self.chords,self.movement)): raise ChartError('Controls must be 1..6')
        if not 1<=self.max_chord<=3: raise ChartError('Maximum chord size must be 1..3')

def convert(song, settings=Settings(), cancelled=lambda:False):
    settings.check(); ensure_valid(song)
    notes=sorted(song.tracks.get(settings.source,[]))
    if not notes: raise ChartError(f'No {settings.source} guitar notes')
    if song.modifiers.get(settings.source):
        raise ChartError('Source has forced HOPO/tap/open/unsupported events. This profile cannot safely translate these; use Review GH3 cleanup to inspect and remove them from a working copy.')
    result=copy.deepcopy(song)
    output=[]; previous_source=None; previous_target=None; cache={}; last_tick=-10**12
    dropped_events=0; dropped_gems=0; previous_end=0
    # Retain authored onsets only. Lower density suppresses close events;
    # quarter-beat anchors and section/phrase starts always survive.
    spacing = {6:0,5:1/8,4:1/6,3:1/4,2:1/3,1:1/2}[settings.density]*song.resolution
    anchors={t for t,_ in song.events}
    anchors.update(p.tick for p in song.phrases.get(settings.source,[]))
    for tick, group in groupby(notes,key=lambda n:n.tick):
        if cancelled(): raise ChartError('Cancelled; no export created')
        group=list(group)
        if len({n.length for n in group})>1:
            raise ChartError(f'Disjoint chord sustains at tick {tick}: TheGHOST uses one duration per chord. Use Review GH3 cleanup with sustain shortening.')
        if tick < previous_end:
            raise ChartError(f'Extended sustain at tick {tick}: use Review GH3 cleanup with sustain shortening')
        previous_end=max(n.tick+n.length for n in group)
        if tick-last_tick<spacing and tick%song.resolution and tick not in anchors:
            dropped_events+=1; dropped_gems+=len(group); continue
        lanes=tuple(n.lane for n in group)
        cap=min(settings.max_chord, 1 if settings.chords<=2 else 2 if settings.chords<=4 else 3)
        selected=group
        if len(group)>cap:
            # Keep the outer voices, then an inner voice, rather than random gems.
            indices=[0] if cap==1 else [0,len(group)-1] if cap==2 else [0,len(group)//2,len(group)-1]
            selected=[group[i] for i in indices]
            dropped_gems+=len(group)-len(selected)
        source=tuple(n.lane for n in selected)
        motif=(previous_source,source,previous_target)
        candidates=list(combinations(range(4),len(selected)))
        def cost(target):
            anchor=sum((b-a*0.75)**2 for a,b in zip(source,target))
            if previous_source is None: return anchor
            delta=sum(source)/len(source)-sum(previous_source)/len(previous_source)
            move=sum(target)/len(target)-sum(previous_target)/len(previous_target)
            contour=0 if delta==0 or delta*move>0 else 3
            repetition=4 if source!=previous_source and target==previous_target else 0
            # Low movement penalizes travel; high movement follows source contour.
            return anchor+contour+repetition+(6-settings.movement)*0.45*abs(move)
        target=cache.setdefault(motif,min(candidates,key=lambda c:(cost(c),c)))
        output.extend(Note(n.tick,lane,n.length) for n,lane in zip(selected,target))
        previous_source,previous_target=source,target; last_tick=tick
    result.tracks['Medium']=sorted(output)
    result.phrases['Medium']=copy.deepcopy(song.phrases.get(settings.source,[]))
    result.modifiers.pop('Medium',None)
    report=ensure_valid(result,True)
    report.update(settings=asdict(settings), source_events=len({n.tick for n in notes}),
                  source_gems=len(notes), medium_events=len({n.tick for n in output}),
                  medium_gems=len(output), removed_events=dropped_events, removed_gems=dropped_gems,
                  timing='Retained onsets and sustain lengths are exact integer ticks',
                  status='Structural checks passed; TheGHOST/Dolphin testing required')
    report['warnings'] += ['Natural HOPO behavior may change after fret remapping. No forced HOPO or modern tap mechanics are generated.',
                           'This conversion does not analyze audio. Use Audio Analysis and Listen & Sync to review synchronization.',
                           'TheGHOST MIDI discards sustains below 160 ticks; prefer .chart. Both importers may alter sustain lengths across tempo changes.',
                           'Legacy MIDI phrase export: Medium Star Power pitch 79. Modern shared pitch 116 is input-only.',
                           'Nonzero Offset blocks paired export. Apply timing offsets explicitly in TheGHOST.']
    if dropped_gems: report['warnings'].append(f'{dropped_gems} gems removed by density/chord settings; see counts above.')
    return result,report
