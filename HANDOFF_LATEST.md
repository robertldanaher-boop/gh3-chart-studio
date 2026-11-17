# GH3 Chart Studio — 0.6.0 handoff

Prepared November 15, 2026 for Bob Danaher. Give the next assistant this file and
GH3_Chart_Studio_v0_6_0.zip. Restore Git with `git clone repository.bundle studio`.
Release commit is RELEASE_COMMIT.txt in the ZIP; tag v0.6.0 is authoritative.
The intermediate learning fix is tagged v0.3.1. Prior full baseline was v0.3.0.

## Current 0.6.0 update

New Clean charts goal/tab supports folder drop, recursive song collection review,
metadata/audio correction, conservative all-guitar-difficulty cleanup and Ogg folders.
No missing Medium generated. Existing Medium Orange removed with seeded sustain
transfer before explicit sustain repair. Required title/artist; optional fields flagged;
no factual metadata verification. Review acknowledgement required before exporting.
Outputs are new folders outside source tree; per-song errors/cancel summarized.
Existing Ogg tags reconciled by re-encoding only when needed; other audio to Vorbis.
No native Windows/game acceptance; read docs/M6_WINDOWS_GUIDE.md and
M6_IMPLEMENTATION_LOG.md. 206 tests passed in19.80s; result M6_TEST_RESULTS.txt. Startup/dependency
bootstrap v0.5.6 preserved. This user-authorized collection cleanup supersedes the
prior blanket deferral of batch work; large-collection/game acceptance still pending.
No actual Claude collaboration occurred. Next one-song and small-collection acceptance.

## Prior 0.5.6 update

START_WINDOWS.cmd probes Python3.11 x64/Tk/venv/ensurepip directly and via py.
Missing usable runtime calls tools/install_python_windows.cmd: python.org signed
3.11.9 installer, verified PSF Authenticode, per-user passive setup with pip/Tk,
no PATH/elevation/policy changes. Existing usable newer3.11 reused. Application
bootstrap then ensures pip, installs pinned hashed requirements as needed, tests
and launches. Errors logged. Fallback3.11.9 is not latest security patch; newer
broken installations can require matching-installer repair. Windows bootstrap is
statically reviewed but NOT executed/verified here. Read docs/M5_6_WINDOWS_GUIDE.md
and M5_6_IMPLEMENTATION_LOG.md. 197 tests passed in22.11s on fresh run; one
earlier run hung in existing external-stem GUI test (trace retained). Next:
clean-machine Windows setup acceptance.

## Prior 0.5.5 update

User Windows startup failed compact-window test: width1282 instead of1024; 192
passed,1 skipped. Python now installed for BobD; do not reuse Robert paths.
Split Audio Studio workflow and footer rows, hidden Pattern Library action rows;
header/title wrap. Large-text Linux reproduction exposed hidden-tab width1046;
fixed result1024x700 with footer visible. 195 tests passed incl added 18px variant.
No bypass or chart/audio changes. Read docs/M5_5_WINDOWS_GUIDE.md,
M5_5_IMPLEMENTATION_LOG.md and M5_5_TEST_RESULTS.txt. Native Windows fix pending
user retest. Next: Windows startup then actual one-song/importer/game acceptance.

## Prior 0.5.4 update

Random four-fret sustain preservation replaces Blue-only in the GUI. Prefer clear
simultaneous frets; else choose a clear lane. If none is clear preserve full length
and record conflict; no silent trimming. Seed and placements are exported in report.
Regenerate increments seed and uses the original selected track, not processed Medium.
194 tests passed incl seeded placement, conflicts, chart/MIDI round trips and GUI
regeneration. See docs/M5_4_WINDOWS_GUIDE.md, M5_4_IMPLEMENTATION_LOG.md and
M5_4_TEST_RESULTS.txt. Cross-lane/gameplay acceptance remains pending. Next real-song
Windows/importer/game acceptance before batch. No actual Claude handoff occurred.

## Prior 0.5.3 update

Audio Studio has an optional unchecked Orange sustain → Blue checkbox. Button 4
means Blue (lane 3). Positive-length Orange notes transfer at original tick/length;
zero-length Orange taps disappear. Simultaneous Blue uses the longer sustain with
no duplicate gem. Later overlaps remain for explicit export review. Expert/Hard
unchanged; report records transfers and the preview labels this mode. Chart/MIDI
round trips and GUI wiring covered by tests. See docs/M5_3_WINDOWS_GUIDE.md,
M5_3_IMPLEMENTATION_LOG.md and M5_3_TEST_RESULTS.txt. Native runtime still pending.
Prior supplied-chart audit is docs/M5_2_ACCEPTANCE_AUDIT.md; it used synthetic audio
for packaging checks, not actual song synchronization. Next: one real song test.

## Prior 0.5.2 update

User requested a one-time first-launch agreement, superseding the prior no-prompt decision.
Agree saves per-user QSettings and opens studio; decline/close exits without acceptance.
Normal upgrades retain acceptance. Notice covers Wii and other compatible open-source
chart-based games without promising compatibility. Ready handshake includes the visible
agreement so startup never times out while reading. Missing notice disables Agree;
settings write errors keep the gate open. Source setup installs dependencies/tests before
first launch; this is not an installer EULA. No Windows/native build certification.
See docs/M5_2_WINDOWS_GUIDE.md, M5_2_IMPLEMENTATION_LOG.md and M5_2_TEST_RESULTS.txt.

## Prior 0.5.1 update

About / credits has Credits and License & disclaimer tabs, including full MIT text.
No startup acceptance or additional EULA. Documentation accurately identifies
synthetic fixtures, user content rights, independence and compatibility limits.
PyInstaller data now includes root LICENSE; no actual Windows build performed.
177 tests passed; source/simulated frozen path and offscreen dialog manually verified.
Read docs/M5_1_WINDOWS_GUIDE.md, M5_1_IMPLEMENTATION_LOG.md and M5_1_TEST_RESULTS.txt.
No signing, Defender acceptance or legal enforceability/compliance certification.
Next: one-song Windows/importer/game acceptance before batch.

## Prior 0.5.0 update

Read docs/M5_WINDOWS_GUIDE.md, M5_IMPLEMENTATION_LOG.md and M5_TEST_RESULTS.txt.
New dark studio theme and Start screen: existing chart → Orange-only Medium;
audio-only → review attacks → draft; advanced converter and pattern tools remain.
Context-specific NEXT guidance, resume, small-window scrolling and export-complete
folder action. Startup adds decorative animated equalizer, pause/resume and credits;
its test/setup/progress gates remain. Native Windows/Tk animation still unverified.
Credits name Nanook/TeamGHOST as compatibility references, not copied source or
endorsement; libraries and bundled notices are separate. No new dependencies,
no batch, no gameplay algorithm changes. Prior identity/Ogg/HOPO behavior remains.
Next: Windows guided-workflow acceptance with one song before batch.

## Prior 0.4.9 update

Read docs/M4_9_WINDOWS_GUIDE.md, M4_9_IMPLEMENTATION_LOG.md and M4_9_TEST_RESULTS.txt.
Identity preserved/reviewed in chart/ini and Artist - Title folder. Existing Ogg
copied with original tags; new encodes tagged, mismatches reported. Extra ini fields
retained. Hard/Expert selection remains the displayed source before Orange copy.
Optional experimental TheGHOST chart HOPO profile in export review: half/one-beat
changing-single runs, no note thinning or timing edits. Set importer HOPO measure
2.95; N5 is a flip, not unconditional HOPO/tap. Visible estimate/count and exact
notes retained. Dense repeated/chord charts may not reach a majority. Actual game
acceptance required; metadata and HOPO/source tests do not prove Wii behavior.
User reported startup-log lock, then identified an older app running and asked to
disregard. No startup changes made. No batch or actual Claude execution. Next: one
song acceptance using actual recording and TheGHOST/game before batch development.

## Prior 0.4.8 update

Read docs/M4_8_WINDOWS_GUIDE.md, M4_8_IMPLEMENTATION_LOG.md and M4_8_TEST_RESULTS.txt.
User requires song.ogg output and wants one song verified BEFORE batch development.
Folder has notes.chart, song.ogg (Vorbis), song.ini, validation.json, IMPORT_README.txt.
Existing Ogg Vorbis copied byte-identically; other formats encoded without resampling.
Output fully decoded and checked. No WAV duplicate or redundant settings.json;
settings retained in validation.json. Export uses preview audio selection by default.
Native Windows/TheGHOST/Wii acceptance remains pending. Batch intentionally deferred.
No new dependency or Claude execution. Need actual one-song import/playback result.

## Prior 0.4.7 update

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
