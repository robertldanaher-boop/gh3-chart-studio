from collections import defaultdict
from .model import ChartError

def validate(song, require_medium=False, *, learning_only=False):
    if require_medium and learning_only:
        raise ValueError("Learning validation cannot validate an export")
    errors=[]; warnings=list(song.warnings)
    if song.anchors and not learning_only:errors.append("Unreviewed tempo anchors; use Clean songs")
    if not 1 <= song.resolution <= 32767: errors.append('Resolution must be 1..32767 PPQ')
    if not song.tempos or song.tempos[0][0]!=0: errors.append('Tempo map must start at zero')
    for tick,tempo in song.tempos:
        if not 0<=tick<=0x0fffffff or not 1 <= tempo <= 16777215: errors.append('Invalid tempo or tempo position')
    if len({t for t,_ in song.tempos}) != len(song.tempos): errors.append('Conflicting tempo changes at the same tick')
    if song.tempos != sorted(song.tempos): errors.append('Unsorted tempo map')
    for t,n,d in song.signatures:
        if t<0 or not 1<=n<=255 or d<1 or d>128 or d & (d-1): errors.append('Invalid time signature')
        if d!=4: warnings.append('TheGHOST chart parser treats time signatures as /4; verify this meter in-game')
    if len({t for t,_,_ in song.signatures}) != len(song.signatures): errors.append('Conflicting time signatures')
    if any(t<0 for t,_ in song.events): errors.append('Negative global event position')
    try: float(song.metadata.get('Offset','0'))
    except ValueError: errors.append('Invalid audio Offset')
    for diff,notes in song.tracks.items():
        seen=set(); ends={}
        for note in sorted(notes):
            if note.tick<0 or note.length<0 or note.tick+note.length>0x0fffffff or not 0<=note.lane<5: errors.append(f'Invalid note in {diff}')
            if diff=='Medium' and require_medium and note.lane==4: errors.append('ORANGE IS PROHIBITED IN MEDIUM')
            key=(note.tick,note.lane)
            if key in seen: errors.append(f'Duplicate gem in {diff} at {note.tick}')
            seen.add(key)
            if ends.get(note.lane,0)>note.tick:
                (warnings if learning_only else errors).append(f'Same-lane sustain overlap in {diff} at {note.tick}')
            ends[note.lane]=max(ends.get(note.lane,0),note.tick+note.length)
        for p in song.phrases.get(diff,[]):
            if p.tick<0 or p.length<=0 or p.tick+p.length>0x0fffffff or p.kind not in (0,1,2): errors.append('Invalid special phrase')
        for kind in (0,1,2):
            previous_end=-1
            for p in sorted((p for p in song.phrases.get(diff,[]) if p.kind==kind),key=lambda p:p.tick):
                if p.tick<previous_end: errors.append(f'Overlapping phrases in {diff}')
                previous_end=p.tick+p.length
    if require_medium and not song.tracks.get('Medium'): errors.append('Medium contains no notes')
    if require_medium and song.modifiers.get('Medium'): errors.append('Unsupported Medium modifiers')
    if sum(len(v) for v in song.tracks.values())>100000: warnings.append('Over 100,000 gems: review memory and import behavior; no proven GH3 limit asserted')
    return {'errors':sorted(set(errors)),'warnings':sorted(set(warnings))}

def without_flips(song):
    """Copy without TheGHOST HOPO flip markers (N 5 / E *), for strict checks that
    predate flip support. Every other marker is still reported."""
    import copy
    from .hopo import is_flip
    result=copy.copy(song)
    result.modifiers={d:[(t,m) for t,m in markers if not is_flip(m)] for d,markers in song.modifiers.items()}
    return result


def ensure_valid(song, require_medium=False, *, learning_only=False):
    report=validate(song,require_medium,learning_only=learning_only)
    if report['errors']: raise ChartError('\n'.join(report['errors']))
    return report
