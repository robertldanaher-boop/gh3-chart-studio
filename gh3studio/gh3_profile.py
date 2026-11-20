"""Keep exported song folders lean: only what Guitar Hero III (via TheGHOST) uses.

Bob plays guitar only on GH3 Wii: no drums, microphone, keys or 6-fret. Charts
already contain only the four guitar difficulties (other instrument sections are
never written). This module also trims:

* [Events]: keeps practice sections ("section ...", prc_...) and "end"; removes
  lyrics, vocal phrase markers, crowd/lighting/venue cues and other Rock Band /
  Clone Hero events GH3 does not use;
* chart [Song] header: song identity, Offset, Resolution, preview times and
  MusicStream only (drops other instrument streams, Player2, Difficulty, ...);
* song.ini: identity, length, delay, preview times and guitar settings only
  (drops drums/vocals/keys/bass/GHL difficulties, pro-drums, video, icons ...).

Audio is untouched: song.ogg stays the complete song (drums and vocals are part of
the music even when nobody plays them). Everything removed is listed in
validation.json under gh3_lean.
"""
from collections import Counter

from .song_identity import FIELDS

CHART_SONG_KEYS = set(FIELDS) | {'Offset', 'Resolution', 'PreviewStart', 'PreviewEnd', 'MusicStream'}
INI_KEYS = set(FIELDS.values()) | {
    'frets', 'song_length', 'delay', 'preview_start_time', 'preview_end_time',
    'diff_guitar', 'hopo_frequency', 'eighthnote_hopo', 'sustain_cutoff_threshold'}


def _event_kept(text):
    value = str(text).strip().strip('[]').strip()
    lower = value.lower()
    return lower.startswith('section ') or lower.startswith('section_') or lower.startswith('prc_') or lower == 'end'


def _event_kind(text):
    value = str(text).strip().strip('[]').strip().lower()
    return value.split(' ', 1)[0].split('_', 1)[0] or 'empty'


def lean_events(events):
    kept, removed = [], Counter()
    for tick, text in events:
        if _event_kept(text):
            kept.append((tick, text))
        else:
            removed[_event_kind(text)] += 1
    return kept, dict(sorted(removed.items()))


def lean_chart_metadata(metadata):
    kept = {k: v for k, v in metadata.items() if k in CHART_SONG_KEYS}
    return kept, sorted(k for k in metadata if k not in CHART_SONG_KEYS)


def lean_ini(values):
    kept = {k: v for k, v in values.items() if k.lower() in INI_KEYS}
    return kept, sorted(k for k in values if k.lower() not in INI_KEYS)


def omitted_sections(warnings):
    prefix = 'Other instrument/section omitted from export: '
    return sorted({w[len(prefix):] for w in warnings if w.startswith(prefix)})
