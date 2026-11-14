# GH3 Chart Studio — current relay checkpoint

Prepared November 14, 2026 for Robert (Bob) Danaher.
This supersedes the Milestone 2 handoff. No Claude execution/contribution has occurred.

## Transfer and source identity

Give the next assistant this file AND GH3_Chart_Studio_M3_v0_3_0.zip.
The file alone does not contain source. Extract the ZIP, or restore its Git bundle:

    git clone repository.bundle GH3-Chart-Studio-repo

Use one checkout for edits/tests. Version 0.3.0, tag v0.3.0, branch
milestone-3-audio-analysis. The exact release commit is in RELEASE_COMMIT.txt beside
this file in the ZIP; the tagged Git bundle is authoritative. Release tree is clean.
Previous baseline: v0.2.0, 17f00c1fc4f22fbbeec9102c47894ddc7c6f50c0.

Read README.md, docs/PROJECT_REQUIREMENTS.md, docs/M3_IMPLEMENTATION_LOG.md,
docs/AUDIO_ANALYSIS.md and docs/COMPATIBILITY.md before editing.

Suggested prompt: "Continue GH3 Chart Studio from this checkpoint. Verify the source
and tests, preserve working features, and follow the next task below. Return updated
source, Git history, actual test evidence, limitations and a fresh handoff."

## Mandatory rules

Python 3.11, PySide6, Git, pytest, modular design; Windows 10/11 x64 desktop app.
Primary target: GH3 Wii through TheGHOST. Bob uses Windows 7 separately for TheGHOST;
the new application must not require it.
Expert Medium must be ACTUAL Medium, only Green/Red/Yellow/Blue:
.chart MediumSingle lanes 0–3; MIDI PART GUITAR playable pitches 72–75; never Orange 76.
Preserve tempo maps, retained onset/sustain timing and valid chords. Do not add notes
into silence to reach a quota. Event counts and gem counts are distinct.
Never overwrite original songs. Keep charts/training data local. Check code/model
licenses before reuse. No placeholder controls or invented tests/compatibility claims.

## Implemented state

M1: authored .chart/MIDI import, Expert/Hard-to-four-fret conversion, controls, preview,
validated paired exports, metadata/settings and no-overwrite source protection.
M2: recursive scans, SQLite v1 patterns, deduplication/resume, feature/motif extraction,
category browsing, bounded similarity, preference ratings and seeded variation modes.
M3: WAV/FLAC/OGG/MP3 decoding, spectral/energy onset candidates, constant BPM/beat
estimation, manual BPM, draft shift, waveform preview, quiet/energy-change review
markers, four-fret onset drafts, authored tempo-map preservation, optional learned
lane shapes, alignment diagnostics and report/settings persistence.

New audio modules: gh3studio/audio_analysis.py, audio_chart.py, audio_gui.py.
Existing architecture: model.py, chartio.py, midiio.py, converter.py, validation.py,
service.py, gui.py, patterns.py, variations.py, library_gui.py.
Tests: test_core.py, test_gui.py, test_patterns.py, test_audio.py.
Pinned audio dependencies: NumPy 2.2.4, SciPy 1.15.2, SoundFile 0.13.1.
SoundFile/libsndfile covers required formats without a separate FFmpeg binary.
Updated requirements-windows.lock has transitive versions and hashes.

## Actual test evidence

103 pytest tests passed on Linux CPython 3.11.18 / PySide6 6.8.3 / NumPy 2.2.4 /
SciPy 1.15.2 / SoundFile 0.13.1. All 74 prior tests remain included.
Ten fresh GUI test processes passed 60 GUI tests, including audio analysis/draft/
comparison/export, settings and 120 main-thread callback assertions.
See docs/M3_TEST_RESULTS.txt for final captured output.

Original synthetic fixture: 15/15 tone-burst attacks detected; estimated 120.034 BPM
versus known 120; maximum absolute onset error 0.181 ms. These measurements do not
establish real-song accuracy. Source fixture/truth and sample exports are in examples/audio.
The prior M2 synthetic stress test covered 1,000 files/6,000 windows without errors.

Independent parsehero reads both audio draft formats with no warnings or Orange.
Its MIDI conversion rounds each delta to 192 PPQ, so it is NOT an exact timing oracle.
The independent midi-file raw SMF parser verified 960-PPQ MIDI ticks/lanes match the
.chart draft exactly. See docs/M3_INDEPENDENT_TEST_RESULTS.jsonl.

NOT RUN: Windows runtime/build, TheGHOST runtime import, Dolphin/Wii gameplay,
a real-user song corpus or subjective musical-quality assessment. No Windows EXE.

## Regression fixes to preserve

- Worker results must route through explicit queued QObject slots on the GUI thread.
- Closed windows use WA_DeleteOnClose; completed worker callbacks/operations release
  references. GUI tests flush deferred native deletion on the main thread before a
  new allocation-heavy worker starts. This fixed a repeated-run Qt cleanup crash.
- MIDI track-title Latin-1 fallback is reported; full Unicode titles remain in
  song.ini and private MIDI metadata. Standard event text still has format limitations.
- Source hashing streams file bytes rather than reading an entire recording at once.

## Current limitations

Audio detection sees the entire mix, not isolated guitar. It does not infer pitches,
chords, note sustains or Star Power. Drafts have one zero-length gem per detected attack.
Without learned patterns, lanes follow a timbre-rank heuristic. No neural training.
Constant-tempo estimates have half/double-time ambiguity; no automatic variable-tempo
map or tempo editor. Energy-change markers are review hints, not verified phrases.
No audio playback, synchronized editor, undo/redo or batch song generation yet.

Draft shift is positive for later notes. Generation rejects negative resulting times.
Timing comparison measures the current chart and does not apply Draft shift again.
Nearest-attack matching can associate the wrong beat/instrument; ±250 ms matching
and residual trends are review aids, not automatic repairs. At least three distinct
matched attacks are required for a correction suggestion.

Analysis limits: 512 MiB input, 20 minutes, 128 MiB raw mono working data, 8–192 kHz,
1–8 channels. Preview waveform/marker caps do not truncate exported notes.
MP3 encoder padding/decoder differences may require real-path synchronization checks.

M2 windows are fixed eight-quarter-note blocks, not inferred musical phrases.
Similarity ranks a bounded pool of 512 candidates, ratings are single 1–5 scores,
old snapshots remain, and small corpora may produce identical variation modes.
The full eight-axis feedback system and prune UI are not implemented.

M1 conservative restrictions remain: modern forcing/taps/opens, disjoint/extended
source sustains, tempo anchors and nonzero template Offset can block operations.
Natural HOPO behavior can change. Other instruments are omitted with warnings.
TheGHOST MIDI uses legacy Medium Star Power pitch 79, not shared 116. Reopen our
MIDI in Legacy mode. TheGHOST can alter short/cross-tempo sustains; prefer chart.
Upstream behavior reviewed at Nanook/TheGHOST commit
27f143205d3698a1fca49f34c0710bd8347e8cb3; no TheGHOST code was copied.

## Next executable task

1. Inspect source/Git status, reproduce tests and record the actual environment.
2. If Windows is available, run docs/WINDOWS_TEST.md and build_windows.cmd. Do not
   represent Linux tests as Windows execution. Verify packaged libsndfile/NumPy/SciPy.
3. With a legally usable user song/chart, compare timing against the recording and
   run TheGHOST/Dolphin acceptance. Fix specific regressions before broader features.
4. If external validation is unavailable, document it and begin Milestone 4's smallest
   functional editor: editable note timeline, insertion/deletion, sustain editing,
   undo/redo and synchronized playback. Preserve data/tempo rules and exporter checks.
5. Keep checkpointed commits, update implementation log, return a new ZIP with Git
   history and HANDOFF_LATEST.md. Do not silently rewrite released tags/history.

## Quick Windows demo

Install Python 3.11 x64 with launcher. Extract fresh ZIP; run setup_windows.cmd,
test_windows.cmd, launch_windows.cmd. Audio Analysis -> examples/audio/onset-study.wav.
Expect 15 attacks and about 120 BPM. Create draft -> inspect four lanes -> export.
For pattern transfer, first scan a folder containing only technical-study.chart;
expect six patterns, then enable learned patterns for audio generation.
Detailed checks, offsets and expected values are in docs/WINDOWS_TEST.md.

## Continuity

ChatGPT remaining allowance/reset time is not visible. No automatic quota monitor,
Claude handoff, background continuation or automatic resumption is configured.
Checkpoint after every working milestone and before stopping, not just at a warning.
Use one active developer and one chosen checkout at a time.
Every return handoff must include version/branch/commit, clean/dirty state, changes,
actual test commands/results, environment, untested areas, blockers and next tasks.
Return portable source/Git history; never embed credentials or secrets.
To resume in ChatGPT, upload the latest ZIP/handoff and ask to verify before continuing.
