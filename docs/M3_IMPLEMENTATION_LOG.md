# Milestone 3 implementation log — 0.3.0

Date: November 14, 2026 (America/Chicago).
Base: v0.2.0, 17f00c1fc4f22fbbeec9102c47894ddc7c6f50c0.
Branch: milestone-3-audio-analysis.

## Implemented

- Local WAV/FLAC/OGG/MP3 decoding; mono/resampling and cancellation with size limits.
- Spectral/energy attack detection, onset refinement, constant-BPM candidates and beat grid.
- Manual BPM, draft offset, quiet spans and energy-change review markers.
- Four-fret onset drafts at integer ticks, optional authored tempo map preservation and
  optional local pattern transfer. No arbitrary onsets, sustain or Star Power inference.
- Signed onset residuals, offset suggestions and drift diagnostics without changing charts.
- Audio Analysis tab with real waveform/attack/grid preview, zoom, report saving and
  integration with the existing converter/exporter. Audio settings save/load supported.
- Unicode MIDI track-title fallback with complete title retained in song.ini/private metadata.
- Main-thread Qt disposal and completed-worker closure cleanup after a stress-test crash.

## Validation

See M3_TEST_RESULTS.txt for the final actual suite outcome and GUI stress checks.
The suite contains 103 tests, retaining all 74 prior tests. Tests cover supported codecs,
known audio timing, silence, resampling, stereo cancellation, malformed/NaN inputs,
settings, cancellation, four-fret paired export, fractional-tempo mapping, offsets,
drift, offbeats, source preservation, learned transfer, Unicode metadata and GUI settings.

Timing fixture: 15/15 attacks, 120.034 BPM versus known 120, maximum absolute attack
error 0.181 ms and median 0.091 ms. See M3_TIMING_RESULTS.json. This is synthetic audio,
not evidence of real-song transcription accuracy.

Independent parsehero 0.0.2 checks confirm both draft formats parse with 15 Medium
gems, no Orange and no warnings. Its MIDI reader rounds deltas to 192 PPQ; it is not
used to assert exact tick preservation. The independent midi-file raw SMF parser
confirmed the original 960-PPQ MIDI tick/lane pairs exactly match the .chart output.
See M3_INDEPENDENT_TEST_RESULTS.jsonl.

The initial expanded suite caught a MIDI title-encoding failure introduced by an em dash
in the default draft title. A plain title separator and explicit Latin-1 track-title
fallback fixed it; Unicode metadata remains intact and fallback is reported.
Repeated GUI tests then exposed deferred native-window disposal during allocation-heavy
workers. Windows now use delete-on-close, completed callbacks release references, and
tests flush native disposal on the main thread. Final stress results are recorded separately.

## Files added

- gh3studio/audio_analysis.py, audio_chart.py, audio_gui.py.
- tests/test_audio.py; tools/make_audio_fixture.py.
- examples/audio/onset-study.wav, truth.json, analysis.json and draft export folder.
- docs/AUDIO_ANALYSIS.md, M3_IMPLEMENTATION_LOG.md, M3_TEST_RESULTS.txt,
  M3_TIMING_RESULTS.json, M3_INDEPENDENT_TEST_RESULTS.jsonl.
- Dependency license notices for NumPy, SciPy, SoundFile, libsndfile, CFFI and pycparser.

## Files changed

- gh3studio/gui.py: Audio tab, drop import, progress, settings, Qt lifecycle cleanup.
- gh3studio/midiio.py, service.py: safe title handling, metadata warning and streamed source hash.
- gh3studio/__init__.py, pyproject.toml: version 0.3.0 and audio dependencies.
- requirements.txt, requirements-windows.lock: pinned audio stack with Windows hashes.
- tests/test_gui.py, tools/collect_licenses.py: workflow/disposal tests and libsndfile notices.
- README, changelog, compatibility/architecture/Windows instructions and current handoff.

## Limits and next task

This is a reviewable onset-draft pipeline, not instrument transcription. No neural training,
source separation, audio playback, chord/sustain/SP inference or automatic variable-tempo
map is implemented. Full chart editing remains Milestone 4. Linux-only runtime tests;
Windows build, TheGHOST, Dolphin/Wii, real-song timing and musical-quality acceptance
remain pending. SoundFile covers the required formats without a separate FFmpeg executable;
FFmpeg remains a potential future fallback, not an installed or bundled dependency.

Next: Windows and real-song validation, then Milestone 4's editable timeline with undo/redo
and synchronized playback. Preserve exact four-fret output and the verified exports.
