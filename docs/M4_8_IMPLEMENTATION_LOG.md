# Milestone 4.8 — Ogg export and reduced duplication

November 14, 2026. User requires .ogg output and wants to finish one song before implementing batch support.

Files and features:
- New gh3studio/audio_export.py: single-song full-mix Ogg Vorbis export. Detects actual container/codec, copies existing Vorbis byte-for-byte, otherwise encodes in bounded blocks. Fully decodes output and validates finite samples, frame count, sample rate and channels. Rejects empty/surround audio.
- song_export.py: song.ogg replaces song.wav; chart MusicStream and import instructions agree. validation.json includes codec/copy-or-encode facts. Removed redundant settings.json from this folder format because settings already live in the validation report. Existing standalone paired MIDI service is unchanged.
- song_export_gui.py: uses preview recording by default, labels override Change recording, avoids repeating chart cleanup computations every time the path text changes.
- gui.py: successful export with a changed recording aligns the preview selection with the export input. No batch controls or additional persistent per-song state.
- tests/test_audio_export.py: mono/stereo at 22.05/44.1/48 kHz, frame/rate/channel preservation, zero correlation lag for a transient test signal, source preservation, byte-identical Vorbis reuse, extension-versus-codec detection, folder contents/settings/hash, surround rejection/rollback.
- test_song_export.py and test_gui.py: Ogg folder expectations, selected-recording consistency and avoiding redundant cleanup recomputation.
- Version metadata, README, handoff, Windows guide and this log updated.

Testing: docs/M4_8_TEST_RESULTS.txt, Linux/Python 3.11.18 with Qt offscreen. Ogg is fully encoded/decoded using installed SoundFile/libsndfile; no new library was introduced. The original four-fret, source-difficulty preservation and MIDI regression tests remain in the full suite. Lossy Vorbis is not claimed to preserve PCM sample values, only tested timing/format properties. Existing Vorbis copy is byte-identical.

Limits: native Windows encoder/device behavior and TheGHOST/Wii import remain untested. User-supplied matching recordings are not available here. No fixed quality slider or bitrate promise; current SoundFile encoder defaults used. Importer codec availability is outside this app. Existing timing/offset, Medium cleanup and guitar-only parser limits remain. Old milestone documents describe their historical WAV exports; this guide supersedes those export-format instructions.

Next milestone: complete ONE actual song acceptance cycle. Batch feature intentionally deferred, though audio_export and export_song_folder remain reusable single-song functions without GUI dependencies.
