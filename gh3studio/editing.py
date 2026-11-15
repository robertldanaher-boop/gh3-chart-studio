"""Explicit, reviewable working-copy repairs and timing edits."""
import copy
import math
import random
from itertools import groupby
from .model import Note, Phrase, ChartError
from .validation import ensure_valid
from .audio_chart import TempoClock


def prepare_cleanup(song, strip_markers=True, trim_sustains=False):
    ensure_valid(song, learning_only=True)
    result=copy.deepcopy(song);changes=[]
    if strip_markers:
        for difficulty,markers in result.modifiers.items():
            for tick,marker in markers:
                changes.append(dict(difficulty=difficulty,tick=tick,action='remove marker/open-note event',marker=marker))
        result.modifiers={}
    if trim_sustains:
        for difficulty,notes in result.tracks.items():
            groups=[(tick,list(items)) for tick,items in groupby(sorted(notes),key=lambda n:n.tick)]
            output=[]
            for i,(tick,items) in enumerate(groups):
                length=min(n.length for n in items)
                if i+1<len(groups):length=min(length,groups[i+1][0]-tick)
                for note in items:
                    if length!=note.length:
                        changes.append(dict(difficulty=difficulty,tick=tick,lane=note.lane,action='shorten sustain',old_length=note.length,new_length=length))
                    output.append(Note(tick,note.lane,length))
            result.tracks[difficulty]=output
    # Preview can remain invalid when the user hasn't selected sustain repair.
    from .validation import validate
    checks=validate(result)
    report=dict(changes=changes,remaining_errors=checks['errors'],
                warning='Removing forced/tap markers changes gameplay. Natural HOPOs depend on the importer/game. Open-note events are removed, never guessed as a fret.')
    result.warnings += [f'User-reviewed cleanup: {len(changes)} changes; see cleanup report.'] if changes else []
    return result,report


def shift_timing(song, milliseconds):
    """Move all playable notes/phrases/events; retain tempo and meter maps."""
    ensure_valid(song,True)
    if not math.isfinite(milliseconds) or abs(milliseconds)>10000:raise ChartError('Shift must be within ±10,000 ms')
    if float(song.metadata.get('Offset','0'))!=0:raise ChartError('Use a zero-Offset chart before applying a timing shift')
    if any(song.modifiers.values()):raise ChartError('Review marker cleanup before shifting the complete chart')
    result=copy.deepcopy(song);clock=TempoClock(song);delta=milliseconds/1000
    def move(tick):return clock.tick(song.seconds(tick)+delta)
    for difficulty,notes in song.tracks.items():
        result.tracks[difficulty]=[Note(move(n.tick),n.lane,move(n.tick+n.length)-move(n.tick)) for n in notes]
    for difficulty,phrases in song.phrases.items():
        result.phrases[difficulty]=[Phrase(move(p.tick),p.kind,move(p.tick+p.length)-move(p.tick)) for p in phrases]
    result.events=[(move(t),event) for t,event in song.events]
    ensure_valid(result,True)
    result.warnings.append(f'Applied {milliseconds:+g} ms to notes, phrases and events; tempo/meter unchanged. Positions rounded to nearest tick.')
    return result


def timeline(song,difficulty,threshold_beats=1/3):
    """Conservative natural-HOPO candidates, not a GH3 engine simulation."""
    from .hopo import effective_states
    states=effective_states(song,difficulty,1/threshold_beats)
    return [(song.seconds(n.tick),song.seconds(n.tick+n.length),n.lane,states.get(n.tick,False))
            for n in sorted(song.tracks.get(difficulty,[]))]



def remove_orange_to_medium(song,source,*,strict=True,orange_sustains_to_blue=False,randomize_orange_sustains=False,sustain_seed=0):
    """Copy a source to Medium; optionally preserve Orange sustains on four frets."""
    if source not in ('Expert','Hard','Medium','Easy'):raise ChartError('Choose an available source difficulty')
    ensure_valid(song,learning_only=not strict)
    original=song.tracks.get(source,[])
    if not original:raise ChartError(f'No {source} notes to copy')
    if strict and song.modifiers.get(source):
        raise ChartError('This source contains unsupported gameplay markers. Orange-only mode does not strip those markers or change Expert/Hard. Use a supported source or review a separate cleanup copy first.')
    remaining=[n for n in original if n.lane!=4]
    mapped=[n for n in original if n.lane==4 and n.length>0] if (orange_sustains_to_blue or randomize_orange_sustains) else []
    transfers=[]
    rng=random.Random(sustain_seed)
    for note in sorted(mapped):
        simultaneous={n.lane:n for n in remaining if n.tick==note.tick}
        def conflicts(lane):
            existing=simultaneous.get(lane)
            end=note.tick+max(note.length,existing.length if existing else 0)
            return any(n.lane==lane and n.tick!=note.tick and
                       ((n.tick<note.tick and n.tick+n.length>note.tick) or
                        note.tick<n.tick<end) for n in remaining)
        clear=[lane for lane in range(4) if not conflicts(lane)]
        if randomize_orange_sustains:
            candidates=[lane for lane in clear if lane in simultaneous] or clear
            if not candidates:candidates=sorted(simultaneous) or list(range(4))
            lane=rng.choice(candidates)
        else:lane=3
        conflict=conflicts(lane)
        existing=simultaneous.get(lane)
        length=max(note.length,existing.length if existing else 0)
        if existing:remaining.remove(existing)
        remaining.append(Note(note.tick,lane,length))
        transfers.append(dict(tick=note.tick,lane=lane,orange_length=note.length,
                              previous_length=existing.length if existing else None,
                              result_length=length,conflict=conflict))
    if mapped:remaining.sort()
    if not remaining:raise ChartError('Removing Orange would leave Medium empty; no output created')
    previous_end=0
    for tick,items in groupby(sorted(remaining),key=lambda n:n.tick):
        group=list(items)
        if strict and (len({n.length for n in group})>1 or tick<previous_end):
            raise ChartError(f'Medium would contain unsupported chord/extended sustains at tick {tick}. Orange-only mode will not shorten other notes.')
        previous_end=max(n.tick+n.length for n in group)
    result=copy.deepcopy(song)
    result.tracks['Medium']=copy.deepcopy(remaining)
    result.phrases['Medium']=copy.deepcopy(song.phrases.get(source,[]))
    result.modifiers['Medium']=copy.deepcopy(song.modifiers.get(source,[]))
    if strict and any(result.modifiers.values()):
        raise ChartError('A retained difficulty contains unsupported markers that paired MIDI export cannot preserve. Orange-only mode leaves those difficulties untouched; no output was created.')
    if strict:report=ensure_valid(result,True)
    else:
        from .validation import validate
        report=validate(result,True)
        report['compatibility_errors']=report.pop('errors')
    removed=[n for n in original if n.lane==4]
    report.update(operation='remove-orange-only',source_difficulty=source,source_gems=len(original),
                  medium_gems=len(remaining),removed_orange_gems=len(removed),
                  source_events=len({n.tick for n in original}),medium_events=len({n.tick for n in remaining}),
                  settings={'operation':'remove-orange-only','source':source},
                  timing='All remaining G/R/Y/B lanes, onset ticks and sustain lengths are unchanged',
                  preserved_difficulties=[d for d in song.tracks if d!='Medium'],
                  status='Structural checks passed; TheGHOST/Dolphin acceptance required')
    if not mapped:assert result.tracks['Medium']==[n for n in original if n.lane!=4]
    report['retained_notes_exact']=not any(t['previous_length'] is not None and t['previous_length']!=t['result_length'] for t in transfers)
    report['orange_sustains_to_blue']=orange_sustains_to_blue
    report['transferred_orange_sustains']=len(mapped)
    report['sustain_transfers']=transfers
    report['settings'].update(orange_sustains_to_blue=orange_sustains_to_blue,
                              randomize_orange_sustains=randomize_orange_sustains,sustain_seed=sustain_seed)
    report['sustain_seed']=sustain_seed
    report['sustain_lane_conflicts']=sum(t['conflict'] for t in transfers)
    if mapped:
        report['timing']='Orange sustains transferred at original ticks without shortening; simultaneous notes use the longer duration. Overlaps require export review.'
        report['warnings'].append('Orange sustain placement is recorded in sustain_transfers. Existing simultaneous notes may be extended. Lane conflicts and cross-lane/chord sustain compatibility require export review; no sustain was silently shortened.')
    if not strict:report['status']=('Orange sustain transfer created; export compatibility review required' if mapped else 'Exact Orange-only copy created; export compatibility review required')
    report['warnings'] += [('Unsustained Orange onsets disappear; sustained Orange is transferred to a playable fret.' if mapped else 'Orange-only onsets disappear; chords containing Orange lose only that gem.'),
                           'Existing Medium is replaced in the output copy; Expert and Hard are unchanged.',
                           'Natural HOPO behavior may change when Orange notes are removed. No forced/tap actions are added.',
                           'TheGHOST may alter sustain timing; prefer .chart for short sustains. Runtime acceptance is pending.']
    return result,report
