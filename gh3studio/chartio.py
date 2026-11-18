"""Strict .chart reader/writer; unsupported content is visible, never guessed."""
import json
import re
from fractions import Fraction
from pathlib import Path
from .model import Song, Note, Phrase, ChartError, BASES

def read_chart(path, *, cleanup=False):
    text = Path(path).read_text(encoding='utf-8-sig')
    sections = {}
    current = None
    pending = None
    for number, raw in enumerate(text.splitlines(), 1):
        # Strip comments only outside quoted strings.
        line = re.split(r'//(?=(?:[^"\\]*(?:\\.[^"\\]*)*"[^"\\]*(?:\\.[^"\\]*)*")*[^"\\]*$)', raw, maxsplit=1)[0].strip()
        if not line: continue
        if line.startswith('[') and line.endswith(']') and current is None:
            pending = line[1:-1]
        elif line == '{' and pending is not None and current is None:
            if pending in sections: raise ChartError(f'Duplicate section {pending}')
            current = pending; pending = None; sections[current] = []
        elif line == '}' and current is not None:
            current = None
        elif current is not None:
            sections[current].append(line)
        else:
            raise ChartError(f'Invalid chart syntax at line {number}')
    if current is not None or pending is not None: raise ChartError('Unclosed chart section')
    song = Song()
    for line in sections.get('Song', []):
        key, sep, value = line.partition('=')
        if not sep: raise ChartError('Invalid Song metadata')
        value = value.strip()
        if value.startswith('"'):
            try: value = json.loads(value)
            except ValueError: value = value[1:-1]  # legacy Windows paths
        song.metadata[key.strip()] = str(value)
    try: song.resolution = int(song.metadata['Resolution'])
    except (KeyError, ValueError): raise ChartError('Song Resolution is required')
    tempos, signatures = [], []
    for section, lines in sections.items():
        if section == 'Song': continue
        difficulty = section[:-6] if section.endswith('Single') else None
        if difficulty in BASES:
            song.tracks[difficulty] = []; song.phrases[difficulty] = []
        elif section not in ('SyncTrack', 'Events'):
            song.warnings.append(f'Other instrument/section omitted from export: {section}')
            continue
        for line in lines:
            match = re.fullmatch(r'(\d+)\s*=\s*(\w+)\s+(.+)', line)
            if not match: raise ChartError(f'Malformed event in {section}: {line}')
            tick, typ, args = int(match[1]), match[2], match[3]
            parts = args.split()
            try:
                if section == 'SyncTrack':
                    if typ == 'B':
                        bpm = int(parts[0])
                        if bpm <= 0: raise ChartError('Tempo must be positive')
                        tempos.append((tick, Fraction(60000000000, bpm)))
                    elif typ == 'TS':
                        exponent = int(parts[1]) if len(parts)>1 else 2
                        if not 0 <= exponent <= 7: raise ChartError('Invalid time signature denominator')
                        signatures.append((tick, int(parts[0]), 2**exponent))
                    elif typ == 'A':
                        if not cleanup:raise ChartError('Tempo anchors need manual resolution before import; use Clean songs')
                        if len(parts)!=1 or int(parts[0])<0:raise ChartError('Invalid tempo anchor')
                        song.anchors.append((tick,int(parts[0])))
                    else: raise ChartError(f'Unsupported sync event {typ}')
                elif section == 'Events':
                    if typ != 'E': raise ChartError('Unsupported global event')
                    song.events.append((tick, json.loads(args)))
                elif typ == 'N':
                    lane, length = map(int, parts)
                    if 0 <= lane <= 4: song.tracks[difficulty].append(Note(tick, lane, length))
                    else: song.modifiers.setdefault(difficulty, []).append((tick, f'N {lane} {length}'))
                elif typ == 'S':
                    kind, length = map(int, parts)
                    if kind not in (0, 1, 2):
                        if cleanup:
                            song.modifiers.setdefault(difficulty, []).append((tick, f'S {kind} {length}'))
                            continue
                        raise ChartError(f'Unsupported phrase S {kind}')
                    song.phrases[difficulty].append(Phrase(tick, kind, length))
                else:
                    song.modifiers.setdefault(difficulty, []).append((tick, typ+' '+args))
            except (ValueError, IndexError) as exc:
                raise ChartError(f'{section}, tick {tick}: {exc}') from exc
    song.tempos = sorted(tempos) or song.tempos
    song.signatures = sorted(signatures) or song.signatures
    if song.tempos[0][0] != 0: song.tempos.insert(0, (0, Fraction(500000)))
    if song.signatures[0][0] != 0: song.signatures.insert(0, (0,4,4))
    tempo_ticks={t for t,_ in tempos}
    if len({t for t,_ in song.anchors})!=len(song.anchors):raise ChartError('Duplicate tempo anchors need external review')
    for tick,_ in song.anchors:
        if tick not in tempo_ticks:raise ChartError(f'SyncTrack, tick {tick}: anchor has no paired BPM marker; review externally')
    for notes in song.tracks.values(): notes.sort()
    for phrases in song.phrases.values(): phrases.sort(key=lambda p:(p.tick,p.kind,p.length))
    return song

def write_chart(song, path):
    if song.anchors:raise ChartError("Resolve tempo anchors in Clean songs before writing a chart")
    meta = dict(song.metadata, Resolution=str(song.resolution))
    lines = ['[Song]', '{']
    for key, value in meta.items():
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', key): continue
        rendered = value if key in ('Resolution', 'Offset') else json.dumps(value, ensure_ascii=False)
        lines.append(f'  {key} = {rendered}')
    lines += ['}']
    def section(name, entries):
        lines.extend(['['+name+']', '{'])
        lines.extend(f'  {tick} = {value}' for tick, _, value in sorted(entries))
        lines.append('}')
    section('SyncTrack', [(t,0,f'B {round(Fraction(60000000000)/us)}') for t,us in song.tempos] +
            [(t,1,f'TS {n} {d.bit_length()-1}') for t,n,d in song.signatures])
    section('Events', [(t,0,'E '+json.dumps(e, ensure_ascii=False)) for t,e in song.events])
    for diff, notes in song.tracks.items():
        entries = [(p.tick,0,f'S {p.kind} {p.length}') for p in song.phrases.get(diff,[])]
        entries += [(n.tick,1+n.lane,f'N {n.lane} {n.length}') for n in notes]
        entries += [(t,9,v+' 0' if v.startswith('N ') and len(v.split())==2 else v) for t,v in song.modifiers.get(diff,[])]
        section(diff+'Single', entries)
    Path(path).write_text('\n'.join(lines)+'\n', encoding='utf-8')
