"""SMF type 1; TheGHOST legacy per-difficulty phrase pitches on output."""
import json
from fractions import Fraction
from pathlib import Path
import mido
from .model import Song, Note, Phrase, ChartError, BASES

META_PREFIX = 'GH3CS_METADATA '

# Lead guitar first; co-op/rhythm guitar only when no lead guitar track exists.
GUITAR_TRACK_PRIORITY = ('PART GUITAR', 'T1 GEMS', 'PART GUITAR COOP', 'PART RHYTHM')


def _track_key(name):
    """'Part Guitar', 'PART_GUITAR', ' part  guitar ' -> 'PART GUITAR'."""
    return ' '.join(str(name or '').replace('_', ' ').upper().split())


def _choose_guitar_track(names):
    keys = [_track_key(n) for n in names]
    for wanted in GUITAR_TRACK_PRIORITY:
        if wanted in keys:
            return keys.index(wanted), wanted
    found = ', '.join(n for n in names if n) or 'none'
    raise ChartError(f'No guitar part in this MIDI (looked for PART GUITAR, T1 GEMS, PART GUITAR COOP, PART RHYTHM; found tracks: {found})')

def read_midi(path, phrase_mode='modern'):
    mid = mido.MidiFile(path)
    if mid.type == 2 or mid.ticks_per_beat <= 0: raise ChartError('Only synchronous PPQ MIDI type 0/1 is supported')
    song = Song(resolution=mid.ticks_per_beat)
    tempos, signatures = [], []
    names = [next((m.name for m in track if m.type=='track_name'), '') for track in mid.tracks]
    guitar_index, guitar_kind = _choose_guitar_track(names)
    if guitar_kind not in ('PART GUITAR', 'T1 GEMS'):
        song.warnings.append(f'No lead guitar track; used {names[guitar_index]} instead.')
    overlaps = 0
    for track_index, track in enumerate(mid.tracks):
        absolute = 0
        name = names[track_index]
        if track_index==0 and _track_key(name) not in ('', 'TEMPO', 'EVENTS', *GUITAR_TRACK_PRIORITY):
            song.metadata.setdefault('Name',name)
        guitar = track_index == guitar_index
        events_track = _track_key(name) == 'EVENTS'
        active = {}
        early_ends = {}  # note-offs still to come for notes we ended early
        spans = []
        for msg in track:
            absolute += msg.time
            if msg.type == 'set_tempo': tempos.append((absolute, Fraction(msg.tempo)))
            elif msg.type == 'time_signature': signatures.append((absolute,msg.numerator,msg.denominator))
            elif msg.type == 'text' and msg.text.startswith(META_PREFIX):
                song.metadata.update(json.loads(msg.text[len(META_PREFIX):]))
            elif events_track and msg.type in ('text','marker'):
                song.events.append((absolute,msg.text.strip('[]')))
            elif guitar and msg.type in ('note_on','note_off'):
                key = (msg.channel, msg.note)
                if msg.type=='note_on' and msg.velocity>0:
                    if key in active:
                        # Same fret restarted before its note-off (common in downloaded
                        # charts): end the earlier note here, as Clone Hero/Moonscraper do.
                        start = active.pop(key)
                        if absolute == start:
                            song.warnings.append(f'Ignored duplicate MIDI note-on {msg.note} at {absolute}')
                        else:early_ends[key] = early_ends.get(key, 0) + 1
                        if absolute > start:
                            spans.append((start,msg.note,absolute-start)); overlaps += 1
                        # A repeated note-on at the same tick is the same note.
                    active[key] = absolute
                else:
                    if key not in active:
                        if early_ends.get(key):
                            early_ends[key] -= 1; continue  # original end of a note already ended
                        song.warnings.append(f'Ignored stray MIDI note-off {msg.note} at {absolute}'); continue
                    if early_ends.get(key):
                        early_ends[key] -= 1; continue  # FIFO: original note-off must not shorten its restart
                    start = active.pop(key)
                    spans.append((start,msg.note,absolute-start))
            elif guitar and msg.type=='sysex':
                raise ChartError('Guitar SysEx mechanics are unsupported in this version')
        if guitar and active:
            # A note still sounding when the track ends: end it at the track end.
            for key,start in active.items():
                if absolute <= start:raise ChartError('Unterminated MIDI notes have no positive span before track end; review source')
                spans.append((start,key[1],absolute-start))
            song.warnings.append(f'{len(active)} MIDI notes had no note-off; ended at the end of the track.')
        if guitar:
            modern_sp = []
            for tick, pitch, length in spans:
                if pitch == 116:
                    modern_sp.append(Phrase(tick,2,length)); continue
                diff = next((d for d,b in BASES.items() if b <= pitch <= b+10), None)
                if diff is None:
                    if pitch in (59,71,83,95): raise ChartError('Open notes are unsupported')
                    song.warnings.append(f'Ignored non-playable MIDI pitch {pitch}'); continue
                lane = pitch-BASES[diff]
                if lane < 5:
                    song.tracks.setdefault(diff,[]).append(Note(tick,lane,length))
                elif lane in (7,9,10) and phrase_mode=='legacy':
                    song.phrases.setdefault(diff,[]).append(Phrase(tick,{7:2,9:0,10:1}[lane],length))
                elif lane==7 and phrase_mode=='modern':
                    song.warnings.append(f'Modern solo marker {pitch} omitted; not treated as Star Power')
                else:
                    song.modifiers.setdefault(diff,[]).append((tick,f'MIDI {pitch}'))
            if modern_sp:
                for diff in song.tracks:
                    song.phrases.setdefault(diff,[]).extend(modern_sp)
    if overlaps:song.warnings.append(f'{overlaps} overlapping MIDI notes on the same fret were ended where the next one starts; note-offs paired in FIFO order (review repaired sustains).')
    song.tempos = sorted(set(tempos)) or song.tempos
    song.signatures = sorted(set(signatures)) or song.signatures
    if song.tempos[0][0] != 0: song.tempos.insert(0,(0,Fraction(500000)))
    if song.signatures[0][0] != 0: song.signatures.insert(0,(0,4,4))
    for notes in song.tracks.values(): notes.sort()
    for phrases in song.phrases.values(): phrases.sort(key=lambda p:(p.tick,p.kind,p.length))
    return song

def write_midi(song, path):
    if any(song.modifiers.values()): raise ChartError('MIDI export cannot preserve forced/tap modifiers; use .chart or remove modifiers in a chart editor')
    mid = mido.MidiFile(type=1,ticks_per_beat=song.resolution)
    def track(name, entries):
        tr=mido.MidiTrack(); tr.append(mido.MetaMessage('track_name',name=name,time=0))
        last=0
        for tick,priority,msg in sorted(entries,key=lambda e:(e[0],e[1])):
            tr.append(msg.copy(time=tick-last)); last=tick
        tr.append(mido.MetaMessage('end_of_track',time=0)); mid.tracks.append(tr)
    track(song.metadata.get('Name','TEMPO').encode('latin-1',errors='replace').decode('latin-1'), [(t,0,mido.MetaMessage('set_tempo',tempo=round(us))) for t,us in song.tempos]+
          [(t,1,mido.MetaMessage('time_signature',numerator=n,denominator=d)) for t,n,d in song.signatures]+
          [(0,2,mido.MetaMessage('text',text=META_PREFIX+json.dumps(song.metadata,ensure_ascii=True)))])
    entries=[]
    for diff, notes in song.tracks.items():
        spans=[(n.tick,BASES[diff]+n.lane,max(1,n.length)) for n in notes]
        spans += [(p.tick,BASES[diff]+{2:7,0:9,1:10}[p.kind],p.length) for p in song.phrases.get(diff,[])]
        for tick,pitch,length in spans:
            entries += [(tick,1,mido.Message('note_on',note=pitch,velocity=100)),
                        (tick+length,0,mido.Message('note_off',note=pitch,velocity=0))]
    track('PART GUITAR',entries)
    track('EVENTS',[(t,0,mido.MetaMessage('text',text='['+e+']')) for t,e in song.events])
    mid.save(path)
