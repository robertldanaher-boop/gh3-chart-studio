"""Challenging lower-lane tracks plus complete guitar difficulty slots."""
from copy import deepcopy
import random
from .model import Note, ChartError
from .editing import remove_orange_to_medium, prepare_cleanup


def limited_track(song,source,target,lanes,preserve_sustains,seed):
    """Keep allowed gems; place excluded sustains on a repeatable playable lane."""
    original=song.tracks[source];notes=[n for n in original if n.lane<lanes]
    rng=random.Random(seed);transfers=[]
    for note in sorted(n for n in original if n.lane>=lanes and n.length and preserve_sustains):
        simultaneous={n.lane:n for n in notes if n.tick==note.tick}
        def clear(lane):
            end=note.tick+max(note.length,simultaneous.get(lane,Note(0,0)).length)
            return not any(n.lane==lane and n.tick!=note.tick and
                           (n.tick<note.tick<n.tick+n.length or note.tick<n.tick<end) for n in notes)
        free=[l for l in range(lanes) if clear(l)]
        candidates=[l for l in free if l in simultaneous] or free or list(range(lanes))
        lane=rng.choice(candidates);previous=simultaneous.get(lane)
        length=max(note.length,previous.length if previous else 0)
        if previous:notes.remove(previous)
        notes.append(Note(note.tick,lane,length))
        transfers.append(dict(tick=note.tick,source_lane=note.lane,lane=lane,length=length))
    fallback=False
    if not notes:
        # Never insert a token placeholder. Retain the authored event rhythm.
        fallback=True;by_tick={}
        for n in original:by_tick[n.tick]=max(by_tick.get(n.tick,0),n.length)
        notes=[Note(t,rng.randrange(lanes),length) for t,length in sorted(by_tick.items())]
    isolated=deepcopy(song);isolated.tracks={target:sorted(notes)}
    isolated.phrases={target:deepcopy(song.phrases.get(source,[]))}
    isolated.modifiers={target:deepcopy(song.modifiers.get(source,[]))}
    clean,review=prepare_cleanup(isolated,strip_markers=True,trim_sustains=True)
    if review['remaining_errors']:raise ChartError('\n'.join(review['remaining_errors']))
    return clean,dict(source=source,target=target,lanes=lanes,transfers=transfers,
                     remapped_all_events_to_avoid_empty=fallback,repairs=review['changes'])


def complete_conversion(song,source,*,strict=False,randomize_orange_sustains=True,sustain_seed=0):
    """Medium four lanes, Easy three lanes; retain or fill Hard and Expert."""
    if source not in ('Expert','Hard','Medium','Easy') or not song.tracks.get(source):raise ChartError('Select a nonempty source track')
    try:
        result,report=remove_orange_to_medium(song,source,strict=strict,
            randomize_orange_sustains=randomize_orange_sustains,sustain_seed=sustain_seed)
    except ChartError as exc:
        if str(exc)!='Removing Orange would leave Medium empty; no output created':raise
        medium,details=limited_track(song,source,'Medium',4,randomize_orange_sustains,sustain_seed)
        result=deepcopy(song)
        for field in ('tracks','phrases','modifiers'):getattr(result,field)['Medium']=getattr(medium,field).get('Medium',[])
        report=dict(source_difficulty=source,source_gems=len(song.tracks[source]),medium_gems=len(result.tracks['Medium']),removed_orange_gems=len(song.tracks[source]),warnings=[],medium_empty_fallback=details)
    easy,details=limited_track(song,source,'Easy',3,randomize_orange_sustains,sustain_seed)
    for field in ('tracks','phrases','modifiers'):getattr(result,field)['Easy']=getattr(easy,field).get('Easy',[])
    filled=[]
    for difficulty in ('Hard','Expert'):
        if not result.tracks.get(difficulty):
            for field in ('tracks','phrases','modifiers'):getattr(result,field)[difficulty]=deepcopy(getattr(song,field).get(source,[]))
            filled.append(difficulty)
    report['difficulty_completion']=dict(source=source,easy=details,filled_from_source=filled,
        note_counts={d:len(result.tracks[d]) for d in ('Easy','Medium','Hard','Expert')})
    report['preserved_difficulties']=[d for d in ('Hard','Expert') if song.tracks.get(d)]
    report['warnings']+=['Easy replaced with a three-fret copy of the selected source; all four guitar difficulties populated. Missing Hard/Expert copied from source without density reduction. See difficulty_completion for Easy sustain repairs and any empty-track fallback.']
    return result,report


def check_complete_conversion(song):
    for d in ('Easy','Medium','Hard','Expert'):
        if not song.tracks.get(d):raise ChartError('Converted song has no '+d+' notes')
    if any(n.lane>=3 for n in song.tracks['Easy']):raise ChartError('Easy must use Green, Red and Yellow only')
    if any(n.lane>=4 for n in song.tracks['Medium']):raise ChartError('Medium must use four frets only')
