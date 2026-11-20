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


# ---- Keep the charter's forced HOPO / strum intent (0.18.5) -----------------
# Cleanup removes every source marker. Forced notes (N 5 / E *) only FLIP the
# importer's natural guess, and Clone Hero (where charts are authored) guesses
# differently from TheGHOST (GH3). So: work out what each authored note was
# meant to be in Clone Hero (natural XOR flip; taps play as HOPOs because GH3 has
# no tap notes), then write TheGHOST N 5 flips wherever its natural guess at
# measure 2.95 would differ. Open notes stay removed.

def _marker_kind(marker):
    parts = str(marker).split()
    if parts[:2] == ['N', '5'] or marker == 'E *':
        return 'flip'
    if parts[:2] == ['N', '6']:
        return 'tap'
    return None


def clone_hero_threshold(song):
    """Clone Hero natural-HOPO distance in ticks (song.ini overrides honoured)."""
    ini = {k.lower(): v for k, v in (song.ini_metadata or {}).items()}
    try:
        value = int(float(ini.get('hopo_frequency', '')))
        if value > 0:
            return value
    except ValueError:
        pass
    if str(ini.get('eighthnote_hopo', '')).strip().lower() in ('1', 'true', 'yes'):
        return song.resolution / 2
    return song.resolution * 65 / 192


def authored_states(song, difficulty):
    """{tick: True if the charter meant a HOPO}, from Clone Hero rules plus markers."""
    threshold = clone_hero_threshold(song)
    flips, taps = set(), set()
    for tick, marker in song.modifiers.get(difficulty, []):
        kind = _marker_kind(marker)
        if kind == 'flip':
            flips.add(tick)
        elif kind == 'tap':
            taps.add(tick)
    result, previous = {}, None
    for tick, notes in events(song, difficulty):
        lanes = {n.lane for n in notes}
        natural = bool(previous and len(notes) == 1 and lanes.isdisjoint(previous[1])
                       and tick - previous[0] <= threshold)
        result[tick] = True if tick in taps else (natural != (tick in flips))
        previous = (tick, lanes)
    return result


def authored_marker_counts(song, difficulty):
    kinds = [_marker_kind(m) for _, m in song.modifiers.get(difficulty, [])]
    return {'forced': kinds.count('flip'), 'tap': kinds.count('tap')}


def restore_hopo_intent(cleaned, original, sources, measure=2.95):
    """Write TheGHOST N 5 flips into cleaned (markers already removed).

    sources: {output difficulty: original difficulty whose authored intent applies}.
    Only difficulties whose source had forced or tap markers get flips, so charts
    without them export exactly as before. Returns a per-difficulty report.
    """
    report = {}
    for difficulty, source in sources.items():
        counts = authored_marker_counts(original, source)
        if not cleaned.tracks.get(difficulty) or not (counts['forced'] or counts['tap']):
            continue
        intended = authored_states(original, source)
        natural = natural_states(cleaned, difficulty, measure)
        flips = [tick for tick in sorted(natural) if tick in intended and intended[tick] != natural[tick]]
        kept = [(t, m) for t, m in cleaned.modifiers.get(difficulty, []) if not is_flip(m)]
        cleaned.modifiers[difficulty] = sorted(kept + [(t, 'N 5 0') for t in flips])
        report[difficulty] = dict(source=source, authored_forced=counts['forced'], authored_taps=counts['tap'],
                                  theghost_flips=len(flips),
                                  intended_hopos=sum(1 for t in natural if intended.get(t)))
    return report
