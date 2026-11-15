# GH3 Chart Studio — 0.4.7 handoff

Prepared November 14, 2026 for Bob Danaher. Give the next assistant this file and
GH3_Chart_Studio_v0_4_7.zip. Restore Git with `git clone repository.bundle studio`.
Release commit is RELEASE_COMMIT.txt in the ZIP; tag v0.4.7 is authoritative.
The intermediate learning fix is tagged v0.3.1. Prior full baseline was v0.3.0.

## Current 0.4.7 update

Read docs/M4_7_WINDOWS_GUIDE.md, M4_7_IMPLEMENTATION_LOG.md and M4_7_TEST_RESULTS.txt.
Preview no-source silent failure fixed: Play prompts for the recording. Chart loads
safe MusicStream/unambiguous song.* audio automatically. Added output-device selector,
visible playback errors, detailed app-log events and actual-state Play/Pause text.
No physical audio device available locally; Windows audible playback unverified.
Ask for Chart Converter → Save diagnostic log if still failing, plus whether the
seek clock moves and the selected output device. The no-source issue is confirmed,
not necessarily the sole cause of Bob's report. No Claude execution occurred.

## Prior 0.4.6 update

Read docs/M4_6_WINDOWS_GUIDE.md, M4_6_IMPLEMENTATION_LOG.md and M4_6_TEST_RESULTS.txt.
START_WINDOWS.cmd opens a stdlib Tk progress UI before PySide6 setup. Three stages,
estimated percent/ETA, elapsed and idle timers, randomized greeting, live log,
cancel/failure handling and actual Qt readiness handshake. Dependency installation
is reused only if lock hash and exact distribution snapshot match. Full automated
tests still run every startup. Logs: start_windows.log, start_windows.previous.log,
startup_bootstrap.log. ETA history: startup_timings.json. Native Windows/Tk/taskkill
acceptance remains pending. Need Bob's slow-start log before attributing the cause.

## Prior 0.4.5 update

Read docs/M4_5_WINDOWS_GUIDE.md, M4_5_IMPLEMENTATION_LOG.md and M4_5_TEST_RESULTS.txt.
Orange-only now copies the actual displayed difficulty in review mode, preserving
all surviving note triples exactly even on marked charts. Output provenance is
visible. Old Medium is replaced in the output; other difficulties stay intact.
Song-folder export adds notes.chart, PCM16 song.wav, song.ini and diagnostics.
An explicit dialog reviews Medium-only marker removal/sustain normalization;
these changes are never silently part of Orange removal. Source markers retain
lengths in chart read/write. Nonzero Offset/ini delay blocks folder export.
Actual supplied charts passed copy/export checks using synthetic audio; actual
recordings, native Windows and TheGHOST/Wii remain untested. No Claude execution
has occurred in this workspace. Membership quota cannot be monitored here.

## Prior 0.4.4 update

Read docs/M4_4_WINDOWS_GUIDE.md and docs/M4_4_IMPLEMENTATION_LOG.md.
Scans auto-populate newest pattern rows and reset category filters. Audio Studio
supports display difficulty selection and a separate Orange-only Medium copy,
which preserves Expert/Hard and remaining G/R/Y/B lanes/timing/sustains. It does
not silently strip markers or normalize sustains. Strict paired-export limits still
apply; the user's marked modern charts are not claimed compatible through this
mode. Future Medium-only cleanup/chart-only preservation must be explicit.
Latest full local evidence is M4_4_TEST_RESULTS.txt. Native Windows rerun is pending.

## Prior 0.4.3 Windows test correction

Bob ran START_WINDOWS.cmd on Windows. Dependency installation succeeded and the
launcher correctly stopped at a test failure: 127 passed, 1 failed, 1 skipped.
The failure compared Qt's C:/.../onset-study.wav string to pathlib's C:\...\onset-study.wav
string. Both identify the same file. test_external_stem_analyzed_original_mix_retained
now compares resolved Path objects, preserving the original-vs-stem check. No tests
were disabled or skipped to work around it. The skipped test's reason is not in
Bob's supplied log, so do not invent one. See M4_3_TEST_RESULTS.txt for the corrected
local suite and M4_3_IMPLEMENTATION_LOG.md. Corrected Windows rerun is pending.

## Prior 0.4.2 packaging update

START_WINDOWS.cmd now performs setup, tests and launch. The old setup_windows.cmd,
test_windows.cmd and launch_windows.cmd were removed at Bob’s request. The build
script remains for developers. The user has now verified setup and failure-stop behavior on Windows, as described above. Python
functionality is unchanged from the last 129-test run; see M4_1_TEST_RESULTS.txt.

## Prior 0.4.1 update

Read docs/M4_1_WINDOWS_GUIDE.md and docs/M4_1_IMPLEMENTATION_LOG.md first.
129 tests passed at that milestone; M4_1_TEST_RESULTS.txt is historical. The 124-test result below is
historical 0.4.0 evidence. Audio Studio now contains numbered steps and embedded
horizontal playback; there is no separate Listen & Sync tab. Creating a draft
stays in Audio Studio. The checkbox onset model permits candidate exclusions,
invalidates stale drafts and records excluded times. Optional settings are clearly
labeled. An external pre-separated stem can drive analysis while the original mix
remains the playback source. No automatic instrument separation or tab search/import
was built; research/next steps are in INSTRUMENT_AND_TAB_ROADMAP.md. Do not claim
all detected attacks are guitar notes, or that a tab MIDI is a GH3 game-chart MIDI.

## Actual handoff status and environment

Bob reports that he attempted the initial Claude handoff. Claude reported Git,
NumPy, SciPy and pytest available, but no PySide6, SoundFile or Mido and package
installation blocked. No Claude code changes or test results have been received.
Do not claim Claude reproduced the complete suite. Do not assume a new chat or
network setting will enable installs; inspect the actual next environment.

Run `python tools/check_environment.py` first. Full environment setup is in
START_WINDOWS.cmd / requirements-dev.txt. Python 3.11 x64 is the project baseline,
not Python 3.11.0 specifically. Bob already has 3.11, 3.13 and 3.15 installed.
The launcher setup chooses `py -3.11`; do not uninstall newer interpreters.

If installs are blocked, `python -m pytest tests/test_minimal.py -q` runs three
pure-Python/pytest checks (chart read/write, four-fret conversion and marker gate).
It does NOT verify MIDI, NumPy/SciPy audio analysis, PySide6 GUI, playback, Windows,
TheGHOST or Dolphin. Record exact executed checks, skipped/blocked checks and errors.
Do not silently replace dependencies with stubs and report the whole suite passed.

## Rules

Medium must contain G/R/Y/B only: chart lanes 0–3 and MIDI PART GUITAR pitches
72–75, never playable Orange 76. Preserve authored timing/tempo/sustains except
explicit, reviewed edits. Originals never overwritten. No random density inflation.
No false claims of Windows compilation, listening accuracy or game compatibility.
Use one active checkout/owner. Keep Git history, tests, logs and this handoff current.
No automatic quota monitoring is available; checkpoint at milestones or before limits.

## Current functionality

Read README.md, docs/M4_WINDOWS_GUIDE.md, docs/M4_IMPLEMENTATION_LOG.md,
docs/COMPATIBILITY.md, docs/AUDIO_ANALYSIS.md and docs/PROJECT_REQUIREMENTS.md.

- Expert/Hard to four-fret Medium with paired .chart/MIDI read-back validation.
- Local pattern extraction, style/category browsing, ratings and seeded variations.
- Corpus learning accepts known tap/forced/solo metadata and overlapping sustains
  without altering inputs; unknown/open modifiers still exclude affected tracks.
- Audio-only full-mix onset drafts; no authored chart/corpus required. Drafts include
  a working Expert seed for further variations. No guitar isolation/pitch guarantee.
- Review GH3 cleanup lists exact marker/open-event removals and optional sustain
  normalization across all retained difficulties. Apply acts on a copy; restore works.
- Qt audio playback with scrolling note preview, seek/volume/play/pause/stop.
- Preview signed timing shift, apply to output only, undo/redo; tempo/meter unchanged.
- Natural HOPO candidate highlighting is visualization only. No forced/tap synthesis.

Important code: editing.py, cleanup_gui.py, playback.py, audio_gui.py, gui.py,
patterns.py, variations.py, converter.py, service.py, validation.py.
Main-thread queued worker callbacks and deterministic Qt cleanup are essential.
Avoid direct worker-thread Python callbacks that mutate widgets.

## Evidence

124 automated tests passed on Linux CPython 3.11.18 / PySide6 6.8.3. See M4_TEST_RESULTS.
3 dependency-light checks passed. WAV backend loaded 9000 ms, advanced the media
clock, paused and sought to 2500 ms. Independent probe decoded 8192 PCM frames.
No audio output device existed: audible output and latency remain untested.
An extra QAudioBufferOutput test probe exposed a stop/seek hang; that probe is not
used in production. Repeated production-path testing also exposed an intermittent
shutdown timeout; all media notifications now use explicit queued GUI-thread slots.
A further full-suite run still caught native FFmpeg stop/seek contention. Stop
now pauses and rewinds; close pauses and lets deferred QObject deletion release
the backend, avoiding synchronous stop(). Do not revert these safeguards.
Final playback regression tests use the real production player;
see M4_GUI_STRESS_RESULTS.txt for repeated fresh-process runs.

Bob's notes(1).chart = †elepa†hy [chartgen]; 200 pattern windows, 1662 cleanup changes,
902 converted Medium gems. notes(2).chart = Steve Vai Tender Surrender; 228 windows,
443 cleanup changes, 1455 converted Medium gems. Each passed baseline plus 3 variant
paired exports. SHA-256s unchanged. See M4_USER_CHART_RESULTS.json. Original files
are not redistributed; ask Bob for them if needed to repeat that exact test.

## Remaining work

1. Windows listening/build acceptance and actual TheGHOST/Dolphin/Wii test on one song.
2. Individual note/sustain editing with undo, looped audition, clearer per-note review.
3. Investigate a verified forced-HOPO chart profile and MIDI equivalence. TheGHOST
   FAQ supports E * legacy forcing; do not equate modern tap notes with GH3 HOPOs.
4. Guitar-focused transcription quality remains unproven; current audio drafts are
   full-mix onset heuristics and need listening/editing.
5. Review actual compiled Qt/FFmpeg dependency licenses/source availability before
   distributing a binary; source ZIP contains no Qt/FFmpeg binaries.

Return updated source ZIP, Git bundle/tag/commit, executed test evidence, exact
Windows steps, limitations and a fresh handoff. Do not erase unverified items.
