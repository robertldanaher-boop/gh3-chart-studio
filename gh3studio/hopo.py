"""Conservative TheGHOST .chart HOPO assistance; runtime acceptance is required."""
import copy
from itertools import groupby
from .model import ChartError


def is_flip(marker):return marker in ('N 5','N 5 0','E *')


def events(song,difficulty):return [(tick,list(items)) for tick,items in groupby(sorted(song.tracks.get(difficulty,[])),key=lambda n:n.tick)]


def natural_states(song,difficulty,measure=2.95):
    if measure<=0:raise ChartError('HOPO measure must be positive')
    previous=None;result={}
    for tick,notes in events(song,difficulty):
        beat=tick//song.resolution
        now=int(song.seconds(tick)*1000)
        period=int(song.seconds((beat+1)*song.resolution)*1000)-int(song.seconds(beat*song.resolution)*1000)
        numerator=4
        for t,n,_ in song.signatures:
            if int(song.seconds(t)*1000)<now:numerator=n
        lanes={n.lane for n in notes}
        result[tick]=bool(previous and len(notes)==1 and lanes.isdisjoint(previous[1]) and
                          int(now-period*(4/numerator)/measure)<=previous[0])
        previous=(now,lanes)
    return result


def effective_states(song,difficulty,measure=2.95):
    result=natural_states(song,difficulty,measure)
    for tick,marker in song.modifiers.get(difficulty,[]):
        if is_flip(marker) and tick in result:result[tick]=not result[tick]
    return result


def prefer_hopos(song,max_gap_beats=.5,measure=2.95):
    if measure!=2.95:raise ChartError('This reviewed HOPO export profile requires TheGHOST measure 2.95')
    if max_gap_beats not in (.5,1.):raise ChartError('Choose a half-beat or one-beat HOPO run gap')
    if not song.tracks.get('Medium'):raise ChartError('Create Medium from Hard or Expert first')
    if any(not is_flip(m) for _,m in song.modifiers.get('Medium',[])):
        raise ChartError('Review/remove unsupported Medium markers before applying HOPO assistance')
    result=copy.deepcopy(song);before=list(result.modifiers.get('Medium',[]));result.modifiers['Medium']=[]
    natural=natural_states(song,'Medium',measure);previous=None;added=[]
    for tick,notes in events(song,'Medium'):
        eligible=bool(previous and len(notes)==len(previous[1])==1 and
                      notes[0].lane!=previous[1][0].lane and
                      0<tick-previous[0]<=song.resolution*max_gap_beats)
        if eligible and not natural[tick]:
            result.modifiers['Medium'].append((tick,'N 5 0'));added.append(tick)
        previous=(tick,notes)
    states=effective_states(result,'Medium',measure);count=sum(states.values())
    return result,dict(profile='TheGHOST chart HOPO flips; experimental until in-game acceptance',
                       importer_hopo_measure=measure,max_gap_beats=max_gap_beats,
                       removed_existing_flip_markers=before,added_flip_ticks=added,
                       note_events=len(states),estimated_hopo_events=count,
                       estimated_hopo_percent=round(100*count/len(states),1),
                       remaining_note_triples_unchanged=result.tracks==song.tracks,
                       warning='Set TheGHOST HOPO measure to 2.95. N 5 toggles natural state; other importer settings can change results. First notes, repeated-fret runs and chords are not newly forced. HOPOs require starting/restarting the combo with a strum; these are not tap notes.')
