# Milestone 4 / 0.4.0 — listening, cleanup and timing review

## Files and features

New: gh3studio/editing.py (reviewable cleanup, timing shift, HOPO candidates),
cleanup_gui.py (change review), playback.py (Qt media player/note highway),
tests/test_editing.py, tests/test_minimal.py, tools/check_environment.py,
tools/check_user_charts.py and M4 guide/results/log documents.

Changed: gui.py, audio_gui.py, converter.py, variations.py, tests/test_gui.py,
tests/test_patterns.py, version metadata, README, THIRD_PARTY, compatibility and
handoff documents. Includes the separately committed/tagged v0.3.1 learning fix
in docs/M3_1_IMPLEMENTATION_LOG.md.

- Audio-only creation is exposed on the first screen; no chart or corpus is needed.
- QMediaPlayer/QAudioOutput playback, seeking, volume, pause/stop, note highway.
- Signed preview timing offset, explicit application to output, exact undo/redo.
  Tempo/meter unchanged; note/phrase/event endpoints rounded to nearest tick.
- Cleanup previews every stripped marker/open event and shortened sustain. Only
  explicit Apply changes the working copy. Restore Original reverts cleanup.
- Pattern style filter for learned variants, existing category browser and ratings.
- Estimated natural HOPO highlights. No forced-HOPO/tap synthesis, no gameplay proof.

## Verification

Full suite: 124 passed on Linux CPython 3.11.18 / PySide6 6.8.3, offscreen Qt.
Dependency-light subset: 3 passed. It does NOT cover MIDI/audio/GUI.
Real WAV backend: 9,000 ms duration, media clock advance, pause, seek to 2,500 ms,
close. A separate decode probe observed 8,192 decoded PCM frames. No output device
was available, so audible output/latency is unverified. The initial test probe's
QAudioBufferOutput attachment caused a native stop hang after immediate seek;
production does not attach that probe. Repeated production-path testing also
exposed an intermittent shutdown timeout; media notifications were changed to
explicit queued main-thread slots. A further full-suite run still caught native
FFmpeg stop/seek contention; Stop now pauses and rewinds, while close pauses and
lets deferred QObject deletion release the backend instead of calling stop()
synchronously. Final playback checks exercise production
QMediaPlayer/QAudioOutput directly, including immediate close. See the separate
M4_GUI_STRESS_RESULTS.txt for fresh-process repeat results.

Both user charts imported and rescanned as duplicates with unchanged SHA-256s.
Each also passed cleanup → conversion plus 3 learned variants → paired exports
(8 paired bundles total), with strict four-fret Medium read-back checks.
See M4_USER_CHART_RESULTS.json and tools/check_user_charts.py to reproduce.
The source songs/audio are not included in the release.
GUI layouts inspected at 1120x800 in offscreen captures.

## Limits and next milestone

Windows build/listening, TheGHOST, Dolphin/Wii, actual HOPO and device latency need
user acceptance. No individual note editing, controller scoring, looping or tempo
map editor. Cleanup changes source gameplay and, when selected, sustain lengths;
those changes are listed and require Apply. Audio drafts use full-mix attack
candidates, not instrument separation/transcription. Preview HOPO threshold affects
visualization only. Compiled Qt/FFmpeg redistribution requires platform license audit.

Exact Windows instructions: M4_WINDOWS_GUIDE.md. Next milestone: validate a real
song on Windows/TheGHOST, then add per-note/sustain editing and a verified HOPO
profile without sacrificing MIDI/chart equivalence or the no-Orange Medium rule.
