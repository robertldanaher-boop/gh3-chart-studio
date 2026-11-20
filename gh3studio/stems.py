"""Find and mix multi-track ("stem") song audio into one full mix.

Downloaded Clone Hero style songs often ship the recording as separate files:
song.ogg (the backing track WITHOUT the separate instruments), guitar.ogg,
rhythm.ogg, bass.ogg, drums*.ogg, vocals*.ogg, keys.ogg ... Exporting song.ogg
alone would silently drop the guitar. GH3/TheGHOST export here uses one
song.ogg, so the stems are mixed:

* every stem at its original level (no re-balancing), sample-accurate start;
* mono stems are placed in both channels; shorter stems are padded with silence;
* a stem at a different sample rate is resampled to the main rate;
* if the summed peak would exceed -1 dBFS (room for Ogg encoding overshoot), the
  whole mix is turned down evenly (never up);
* preview and crowd tracks are left out;
* a stem that libsndfile cannot decode is recovered with the bundled FFmpeg
  (same strict, header-checked recovery used for single recordings).

Source files are only read. Everything is reported for validation.json.
"""
import hashlib
import tempfile
from math import gcd
from pathlib import Path

import numpy as np

from .model import ChartError

AUDIO_SUFFIXES = ('.ogg', '.opus', '.flac', '.wav', '.mp3')  # preference order for duplicates
# Clone Hero / Phase Shift stem names, in mixing/report order. 'song' is the backing track.
STEM_ORDER = ('song', 'guitar', 'rhythm', 'bass', 'keys', 'drums', 'drums_1', 'drums_2', 'drums_3',
              'drums_4', 'vocals', 'vocals_1', 'vocals_2', 'harmony')
INSTRUMENT_STEMS = set(STEM_ORDER) - {'song'}
LEFT_OUT = {'preview': 'preview clip, not part of the song',
            'song_preview': 'preview clip, not part of the song',
            'crowd': 'crowd noise track; GH3 supplies its own crowd'}
STREAM_KEYS = {'MusicStream': 'song', 'GuitarStream': 'guitar', 'RhythmStream': 'rhythm',
               'BassStream': 'bass', 'KeysStream': 'keys', 'DrumStream': 'drums',
               'Drum2Stream': 'drums_2', 'Drum3Stream': 'drums_3', 'Drum4Stream': 'drums_4',
               'VocalStream': 'vocals', 'CrowdStream': 'crowd'}
# -1 dBFS: lossy Ogg Vorbis encoding can overshoot the mixed peak by a few
# percent, so leave room or decoded playback would clip (seen on Windows: 0.98 -> 1.023).
HEADROOM = 0.891
BLOCK = 65536


def _audio_files(folder):
    return [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in AUDIO_SUFFIXES]


def find_song_audio(chart_path, metadata=None):
    """Decide which recording(s) make up the song.

    Returns {'kind': 'stems'|'single'|'none', 'paths': [...], 'left_out': [...],
    'notes': [...]}; for 'stems', paths[0] is the main track (song.* if present).
    """
    folder = Path(chart_path).resolve().parent
    metadata = metadata or {}
    files = _audio_files(folder)
    notes, left_out = [], []
    by_role = {}
    # Chart [Song] stream entries name files explicitly.
    for key, role in STREAM_KEYS.items():
        value = str(metadata.get(key, '')).replace('\\', '/').strip()
        if not value:
            continue
        candidate = (folder / value).resolve()
        if candidate.is_relative_to(folder) and candidate.is_file() and candidate.suffix.lower() in AUDIO_SUFFIXES:
            by_role.setdefault(role, [candidate])
    # Conventional file names.
    for path in files:
        role = path.stem.lower().replace(' ', '_')
        if role in STEM_ORDER or role in LEFT_OUT:
            if path not in by_role.get(role, []):
                by_role.setdefault(role, []).append(path)
    chosen = {}
    for role, paths in by_role.items():
        paths = sorted(set(paths), key=lambda p: AUDIO_SUFFIXES.index(p.suffix.lower()))
        chosen[role] = paths[0]
        if len(paths) > 1:
            notes.append(f'{role}: used {paths[0].name}; ignored duplicate ' + ', '.join(p.name for p in paths[1:]))
    for role, reason in LEFT_OUT.items():
        if role in chosen:
            left_out.append({'file': chosen.pop(role).name, 'reason': reason})
    instruments = [r for r in STEM_ORDER if r in chosen and r in INSTRUMENT_STEMS]
    if len(instruments) == 1 and 'song' not in chosen:
        # A lone file named e.g. guitar.ogg is usually the whole song, mislabelled.
        only = chosen[instruments[0]]
        notes.append('Automatically matched the only non-preview audio in this song folder: ' + only.name +
                     '. Verify it contains the full song, not an isolated instrument.')
        return {'kind': 'single', 'paths': [only], 'roles': ['song'], 'left_out': left_out, 'notes': notes}
    if instruments:
        roles = (['song'] if 'song' in chosen else []) + instruments
        paths = [chosen[r] for r in roles]
        if 'song' not in chosen:
            notes.append('No song/backing track found; mixing the instrument tracks that are present.')
        known = {q for group in by_role.values() for q in group}
        for p in (p for p in files if p not in known):
            left_out.append({'file': p.name, 'reason': 'unrecognized file name; not mixed'})
        return {'kind': 'stems', 'paths': paths, 'roles': roles, 'left_out': left_out, 'notes': notes}
    if 'song' in chosen:
        return {'kind': 'single', 'paths': [chosen['song']], 'roles': ['song'], 'left_out': left_out, 'notes': notes}
    others = [p for p in files if p.stem.lower() not in LEFT_OUT]
    if len(others) == 1:
        notes.append('Automatically matched the only non-preview audio in this song folder: ' + others[0].name +
                     '. Verify it contains the full song, not an isolated instrument.')
        return {'kind': 'single', 'paths': others, 'roles': ['song'], 'left_out': left_out, 'notes': notes}
    return {'kind': 'none', 'paths': [], 'roles': [], 'left_out': left_out, 'notes': notes}


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


class _ArraySource:
    """In-memory (resampled or recovered) audio exposed like a SoundFile."""

    def __init__(self, data, samplerate):
        self.data = data
        self.samplerate = samplerate
        self.channels = data.shape[1]
        self.frames = data.shape[0]
        self.position = 0

    def read(self, frames, dtype='float32', always_2d=True):
        block = self.data[self.position:self.position + frames]
        self.position += len(block)
        return block

    def seek(self, frame):
        self.position = frame

    def close(self):
        pass


def _soundfile_open(path):
    import soundfile as sf
    return sf.SoundFile(path)


def _read_all(source):
    blocks = []
    while True:
        block = source.read(BLOCK, dtype='float32', always_2d=True)
        if not len(block):
            break
        blocks.append(np.asarray(block, dtype=np.float32))
    return np.concatenate(blocks) if blocks else np.zeros((0, source.channels), np.float32)


def _resample(data, source_rate, target_rate):
    from scipy.signal import resample_poly
    divisor = gcd(int(source_rate), int(target_rate))
    up, down = int(target_rate) // divisor, int(source_rate) // divisor
    return resample_poly(data, up, down, axis=0).astype(np.float32)


def _recover(path, workdir):
    """Strict FFmpeg decode (header-checked) for a stem libsndfile cannot read."""
    from .audio_fallback import decode_to_pcm
    import soundfile as sf
    info = sf.info(path)
    decoded = Path(workdir) / (Path(path).stem + '-recovered.wav')
    details = decode_to_pcm(path, decoded, (info.frames, info.samplerate, info.channels))
    return decoded, details


class _StemReadError(Exception):
    def __init__(self, index, cause):
        super().__init__(str(cause))
        self.index = index
        self.cause = cause


def _load(path, target_rate, opener, workdir, entry):
    """Open one stem for block reading; resample/recover into memory when needed."""
    try:
        if entry.get('force_recover'):
            raise ChartError('decode failed during mixing')
        source = opener(path)
        if source.channels not in (1, 2) or source.frames <= 0:
            raise ChartError(f'{Path(path).name}: audio must be nonempty mono or stereo')
        if source.samplerate == target_rate:
            return source
        data = _read_all(source)
        source.close()
    except ChartError as exc:
        if not entry.get('force_recover'):
            raise
        if opener is not _soundfile_open:
            raise ChartError(f'{Path(path).name}: {exc}') from exc
        recovered, details = _recover(path, workdir)
        entry['recovered'] = details
        source = opener(recovered)
        if source.samplerate == target_rate:
            return source
        data = _read_all(source)
        source.close()
    except Exception as exc:
        if opener is not _soundfile_open:
            raise ChartError(f'{Path(path).name}: {exc}') from exc
        recovered, details = _recover(path, workdir)
        entry['recovered'] = details
        source = opener(recovered)
        if source.samplerate == target_rate:
            return source
        data = _read_all(source)
        source.close()
    entry['resampled_from'] = int(entry['sample_rate'])
    resampled = _resample(data, entry['sample_rate'], target_rate)
    entry['frames_after_resample'] = int(resampled.shape[0])
    return _ArraySource(resampled, target_rate)


def _blocks(source, channels):
    while True:
        block = np.asarray(source.read(BLOCK, dtype='float32', always_2d=True), dtype=np.float32)
        if not len(block):
            return
        if not np.isfinite(block).all():
            raise ChartError('Stem contains nonfinite samples')
        if block.shape[1] != channels:
            block = np.repeat(block[:, :1], channels, axis=1)
        yield block


def _mix_pass(sources, channels, length, write=None, gain=1.0, cancel=lambda: False):
    generators = [_blocks(s, channels) for s in sources]
    peak, done = 0.0, 0
    while done < length:
        if cancel():
            raise ChartError('Cancelled while mixing audio stems')
        count = min(BLOCK, length - done)
        mix = np.zeros((count, channels), np.float32)
        for index, generator in enumerate(generators):
            try:
                block = next(generator, None)
            except ChartError:
                raise
            except Exception as exc:
                raise _StemReadError(index, exc) from exc
            if block is not None:
                mix[:len(block)] += block[:count]
        if write is not None:
            write(mix * gain)
        peak = max(peak, float(np.abs(mix).max(initial=0.0)))
        done += count
    return peak


def mix_stems(paths, destination, *, opener=None, writer=None, cancel=lambda: False, roles=None):
    """Mix stems into one WAV (PCM 24-bit) at the main stem's sample rate.

    opener(path) -> object with samplerate/channels/frames/read/seek/close
    writer(path, samplerate, channels) -> object with write(block)/close
    (both default to soundfile; injectable for tests).
    """
    paths = [Path(p) for p in paths]
    if len(paths) < 2:
        raise ChartError('Stem mixing needs at least two audio files')
    opener = opener or _soundfile_open
    report = {'action': 'mix separate audio tracks into one full mix', 'stems': [],
              'policy': 'original levels; mono to both channels; shorter tracks padded with silence; '
                        'resampled to the main track rate if needed; turned down evenly only to keep peaks at or below -1 dBFS'}
    with tempfile.TemporaryDirectory(prefix='gh3-stems-') as workdir:
        entries = []
        for index, path in enumerate(paths):
            try:
                source = opener(path)
                entry = {'file': path.name, 'role': (roles or [None] * len(paths))[index] or path.stem.lower(),
                         'sample_rate': int(source.samplerate), 'channels': int(source.channels),
                         'frames': int(source.frames)}
                source.close()
            except Exception as exc:
                raise ChartError(f'Cannot read audio track "{path.name}": {exc}') from exc
            if opener is _soundfile_open:
                entry['sha256'] = sha256(path)
            entries.append(entry)
        target_rate = entries[0]['sample_rate']
        channels = 2 if any(e['channels'] == 2 for e in entries) else 1

        def open_all():
            return [_load(p, target_rate, opener, workdir, e) for p, e in zip(paths, entries)]

        while True:
            sources = open_all()
            lengths = [int(s.frames) for s in sources]
            length = max(lengths)
            try:
                peak = _mix_pass(sources, channels, length, cancel=cancel)
                break
            except _StemReadError as failure:
                entry = entries[failure.index]
                if opener is not _soundfile_open or entry.get('force_recover'):
                    raise ChartError(f'Cannot decode audio track "{entry["file"]}": {failure.cause}') from failure.cause
                entry['force_recover'] = True
                entry['original_error'] = str(failure.cause)
            finally:
                for s in sources:
                    s.close()
        gain = 1.0 if peak <= HEADROOM else HEADROOM / peak
        sources = open_all()
        out = writer(destination, target_rate, channels) if writer else _soundfile_writer(destination, target_rate, channels)
        try:
            _mix_pass(sources, channels, length, write=out.write, gain=gain, cancel=cancel)
        finally:
            out.close()
            for s in sources:
                s.close()
        for entry, frames in zip(entries, lengths):
            entry.pop('force_recover', None)
            if frames < length:
                entry['padded_frames'] = length - frames
            report['stems'].append(entry)
    report.update(sample_rate=target_rate, channels=channels, frames=length,
                  seconds=round(length / target_rate, 3), peak_before=round(peak, 4),
                  gain=round(gain, 4), gain_db=round(float(20 * np.log10(gain)), 2) if gain < 1 else 0.0,
                  turned_down=gain < 1)
    return report


def _soundfile_writer(path, samplerate, channels):
    import soundfile as sf
    return sf.SoundFile(path, 'w', samplerate=samplerate, channels=channels, format='WAV', subtype='PCM_24')


def describe(report):
    """One readable line for logs and the GUI."""
    names = ', '.join(s['file'] for s in report['stems'])
    text = f'Mixed {len(report["stems"])} audio tracks ({names}) into one full mix'
    if report.get('turned_down'):
        text += f'; turned down {abs(report["gain_db"])} dB to prevent clipping'
    resampled = [s['file'] for s in report['stems'] if 'resampled_from' in s]
    if resampled:
        text += '; resampled ' + ', '.join(resampled)
    recovered = [s['file'] for s in report['stems'] if 'recovered' in s]
    if recovered:
        text += '; recovered with FFmpeg ' + ', '.join(recovered)
    return text + '.'


def cached_mix(paths, roles=None, cancel=lambda: False):
    """Mix once into the temp folder for preview/single-song export; reuse while
    the stems are unchanged. Returns (wav_path, report)."""
    import json
    key = hashlib.sha256('|'.join(f'{Path(p).resolve()}:{Path(p).stat().st_size}:{Path(p).stat().st_mtime_ns}'
                                  for p in paths).encode('utf-8')).hexdigest()[:24]
    folder = Path(tempfile.gettempdir()) / 'gh3-chart-studio-mixes'
    folder.mkdir(parents=True, exist_ok=True)
    wav, meta = folder / f'{key}.wav', folder / f'{key}.json'
    if wav.exists() and meta.exists():
        try:
            return wav, json.loads(meta.read_text(encoding='utf-8'))
        except ValueError:
            pass
    partial = folder / f'{key}.partial.wav'
    report = mix_stems(paths, partial, cancel=cancel, roles=roles)
    partial.replace(wav)
    meta.write_text(json.dumps(report), encoding='utf-8')
    return wav, report
