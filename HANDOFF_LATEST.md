# GH3 Chart Studio — 0.16.4 handoff

Prepared November 20, 2026 for Bob Danaher, for the next assistant (ChatGPT or
Claude). Give the next assistant this file and GH3_Chart_Studio_v0_16_4.zip, or
point it at the GitHub repo below. The ZIP's repository.bundle holds the full
history: `git clone repository.bundle studio`, then `git checkout main`.
Release commit is RELEASE_COMMIT.txt in the ZIP.

## READ FIRST — version and source-of-truth rules

Two assistants worked from the same 0.11.3 at the same time: Claude made 0.11.4
(window fit) while ChatGPT made 0.12.0 and 0.13.0, so 0.13.0 lacked the fix and
version numbers collided. 0.13.1 joins both lines. To prevent a repeat:

1. GitHub `main` is the only starting point:
   https://github.com/robertldanaher-boop/gh3-chart-studio (private).
   If you can reach it, start from the newest `main`. If you cannot, start only
   from the newest ZIP/bundle Bob gives you, and check its commit against `main`
   with Bob before changing anything. Never start from an older ZIP.
2. Before writing code, run `git log --oneline -5` and read the top of
   CHANGELOG.md. If either shows a version you do not recognize, stop and
   reconcile it first.
3. The version is the number in gh3studio/__init__.py (also pyproject.toml and
   the README title). Each release bumps it once, from the highest version on
   `main`. The GitHub release name and tag must equal that number exactly.
4. Every release ends with its commit on GitHub `main` before Bob switches
   assistants. If you cannot push, return a ZIP + bundle and tell Bob to upload
   it; the next assistant must import it into `main` (fast-forward or merge,
   never overwrite) before new work.
5. A GitHub release created in the browser tags whatever `main` holds at that
   moment. Attaching a ZIP to a release does NOT put its code on `main`.

6. GitHub Actions (.github/workflows/windows.yml) runs the FULL test suite on
   real Windows for every push to main and builds the installer. Check the
   Actions tab result before claiming a release passes; it is the only Windows
   test evidence besides Bob's PC. A published release fails the workflow if
   its tag does not equal the app version.

GitHub state when 0.13.1 was pushed (0.14.0 pushed on top the same way):
- `main` = 0.13.1 (merge of the 0.13 line and the 0.11.4 line).
- Tags on GitHub: v0.11.3 (2e287db), v0.11.4 and v0.11.5 (both e093849, the
  0.11.4 window-fix line; v0.11.5 is a mislabel — its release has the 0.13.0
  ZIP attached but the tag is not 0.13.0 code). Bob may delete the v0.11.5
  release and tag now that 0.13.1 is on main. Other tags, including v0.12.0,
  v0.13.0 and v0.13.1, are only in the bundle: Claude's session cannot push tags
  (proxy HTTP 403). If you can push tags: `git push origin --tags`. Otherwise
  Bob creates v0.13.1 in the browser: Releases → Draft a new release → tag
  v0.13.1 on main.
- Old branches milestone-2-pattern-learning / milestone-3-audio-analysis are
  ancestors of main; ignore them.
- Bob uploads through the browser: give browser steps; the uploader skips
  dot-files and takes 100 files per batch; never upload .venv, __pycache__,
  logs or music.

## Current 0.16.4 update — intermittent media hang mitigation

Bob's install-time test run (start_windows.log 10:03, Python 3.11.9): everything
through test_gui.py::test_guided_audio_review... passed, including all new stem
and gh3_lean tests and test_separate_tracks_export_one_mixed_song_ogg (0.16.2
fix confirmed on Windows). Then test_external_stem_analyzed_original_mix_retained
hung: faulthandler 60 s dump shows main thread in audio_gui.show_analysis line
109 (pages.setCurrentWidget) <- open_path <- restore_mix; one native thread with
no Python frame. Bob cancelled. Same test hung once in 0.5.6 history; passed in
Bob's two earlier runs on Nov 20. Mitigation: playback.open_audio skips
player.setSource when the same local file is already loaded (restore_mix re-opens
the current mix). Test: tests/test_playback_source.py. NOT proven: intermittent.
Note pytest 8.3.5 faulthandler_timeout only dumps; a hung test blocks install
until the user cancels (pytest-timeout is not in the lock).

## Previous 0.16.3 update — Start menu Uninstall

Bob asked for an uninstall option. install.ps1 now also creates "GH3 Chart
Studio - Uninstall.lnk" (powershell -WindowStyle Hidden -ExecutionPolicy Bypass
-File installer\uninstall.ps1); uninstall.ps1 removes that shortcut too. The
Inno .iss gets an {uninstallexe} Start menu entry. Settings > Apps uninstall was
already registered. Scripts hand-checked only (no PowerShell here).

## Previous 0.16.2 update — test correction

Bob's Windows run of 0.16.1: 334 passed, 1 skipped, 1 failed — KeyError
'padded_frames' in test_separate_tracks_export_one_mixed_song_ogg (line 173),
AFTER the decoded-peak assertion passed (so the -1 dBFS fix works on Windows).
The test wrongly expected the longest track (guitar.ogg) to be padded; fixed to
check song.wav and rhythm.wav padding == mix frames - 4410. Test-only change.
Lesson: run new end-to-end tests fully before release; locally this was done
with a WAV shim and a stubbed Ogg step (all three new cleaner stem tests pass).

## Previous 0.16.1 update — stem mix headroom

FIRST FULL WINDOWS RESULT FOR THE 0.14-0.16 WORK: Bob installed 0.16.0 with
"Install GH3 Chart Studio.cmd" (installed to %LOCALAPPDATA%\Programs\GH3 Chart
Studio; the script installer and install-mode tests ran). 334 passed, 1 skipped,
1 failed: test_separate_tracks_export_one_mixed_song_ogg decoded peak 1.0229 >
1.0 (constant 0.98 mix overshot by Vorbis). Fix: stems.HEADROOM 0.98 -> 0.891
(-1 dBFS); test signals changed from DC to 440 Hz tones, assertion kept strict
(< 1.0). Local FFmpeg libvorbis check: DC at 0.891 decodes at 0.921.
Not yet re-run on Windows.

## Previous 0.16.0 update — lean guitar-only GH3 export

Bob: "exclude any features that aren't supported by guitar hero 3 ... we don't
use the drums controller or microphone so we want a clean file that's lean."
Interpreted as chart/ini data; song.ogg stays the complete song (drums/vocals
are part of the music). If Bob wants instrument audio removed, that is a
separate change: ask first.

New gh3studio/gh3_profile.py (lean_events, lean_chart_metadata, lean_ini,
omitted_sections), applied in song_export._export_song_folder for every export
mode: [Events] keeps "section ...", prc_*, "end"; [Song] keeps FIELDS +
Offset/Resolution/PreviewStart/PreviewEnd/MusicStream (Length and SongIniDelay
no longer written); song.ini keeps FIELDS values + frets, song_length, delay,
preview_start/end_time, diff_guitar, hopo_frequency, eighthnote_hopo,
sustain_cutoff_threshold. Removed items -> validation.json gh3_lean.
Chart read-back now compares events with the lean output. Star power (S 2)
and face-off phrases (S 0/1) are kept (GH3 supports them); modifiers were
already required empty by the clean export checks. Policy change (authorized):
tests/test_song_identity no longer expects custom ini tags to be preserved.

Evidence: tests/test_gh3_profile.py pure cases pass (run with the local WAV
shim, since gh3_profile imports song_identity -> soundfile). The full export case
passed with export_ogg stubbed (chart/ini output shown lean); real Ogg path
not run here. Full suite NOT run.

## Previous 0.15.0 update — separate audio tracks (stems)

Bob (Nov 20): conversions tested successfully in Dolphin. Formal .exe installer
deferred by Bob ("skip that for now"); the Inno .iss and Actions workflow stay.
He asked that songs downloaded with separate tracks be cleaned/converted too.

Bug fixed by this: a folder with song.ogg + guitar.ogg exported song.ogg alone
(Clone Hero song.ogg is the backing track WITHOUT guitar), and folders with only
instrument tracks were blocked.

New gh3studio/stems.py: find_song_audio() (Clone Hero names + chart *Stream
entries; preview/crowd/unknown left out and listed; duplicate formats prefer
.ogg) and mix_stems() (original levels, mono->both channels, pad shorter, resample
other rates, uniform turn-down only above 0.98 peak, FFmpeg recovery for
undecodable tracks, two streamed passes, PCM_24 WAV), cached_mix() for the GUI,
describe(). Wired into cleaner.inspect_chart (row['audio_stems'], every track
validated and hashed), song_export.export_song_folder (accepts a list; mixes to
temp WAV; validation.json audio_stems), cleaner.export_cleaned (log + result
'audio_mixed') and gui.open_path/export_song_to (mix once, preview the mix).
Policy change, authorized by Bob: tests/test_cleaner's "multiple unidentified
stems require full-mix choice" became "separate instrument tracks are mixed".
Details: docs/M15_STEMS.md.

Evidence (exact): Linux, Python 3.13, no PySide6/soundfile/mido.
tests/test_stems.py 11 passed (+1 real-file case skipped); with a throwaway local
WAV-only soundfile shim (not committed) all 12 passed and a 3-track mix with
resampling and -1.77 dB turn-down produced the expected samples. test_cleaner
under that shim: the new export test reaches Ogg validation, which the shim cannot
satisfy (3 older export tests fail identically under the shim without these
changes) — so real export is NOT verified here. Full suite NOT run; GitHub
Actions / Bob's install is the first real run.

## Previous 0.14.1 update — script installer from the ZIP

Bob: 0.14.0 logo and update check work, but he got no Start menu entry or
desktop icon. He had only the source ZIP (which holds the .iss recipe, not a
compiled .exe) and asked Claude to build the installer. Claude's environment
cannot compile Windows installers (no Windows/Wine/Inno Setup, outbound network
blocked; GitHub Actions results are not visible to it). So 0.14.1 adds an
installer that runs directly from the extracted ZIP:
- "Install GH3 Chart Studio.cmd" (root, CRLF) -> powershell -WindowStyle Hidden
  -ExecutionPolicy Bypass installer/install.ps1 (Windows PowerShell 5.1, ASCII).
- install.ps1: confirm dialog; refuses if the installed copy is running; removes
  old code dirs (keeps .venv); robocopy to %LOCALAPPDATA%\Programs\GH3 Chart
  Studio; runs START_WINDOWS.cmd --install hidden and checks exit 0 plus
  .venv/installed.json; creates .lnk shortcuts via WScript.Shell (Start menu
  app + Repair, desktop; icon app.ico); writes HKCU Uninstall key
  {2E998221-C3C3-4195-9C31-6047FBBDDE0E}_is1 (same as Inno, so one entry) with
  UninstallString -> installer/uninstall.ps1; launches the app on success.
  Shortcuts lack an AppUserModelID (the Inno version sets it).
- uninstall.ps1: removes shortcuts, registry key and the program folder.
Evidence: no PowerShell available to Claude; scripts were only reviewed by hand
(ASCII, quoting, balanced braces). NOT executed anywhere yet.
Still open: whether the 0.14.0 GitHub Actions run passed and produced the
Inno .exe — ask Bob to check the Actions tab.

## Previous 0.14.0 update — installer, icon, update check

Bob asked for a formal Windows 11 installer: setup and tests only at install,
Start menu entry, desktop icon, update checks, and his artwork (a dog in a
superhero costume, his own image) as the icon/logo. He did not choose a build
method or update source; assumptions: GitHub Actions builds, and the update
check reads the GitHub repo's latest release (fails gracefully while private).

New/changed files:
- installer/GH3ChartStudio.iss (Inno Setup 6.3+): per-user, no admin, installs
  to %LOCALAPPDATA%\Programs\GH3 Chart Studio, fixed AppId
  {2E998221-C3C3-4195-9C31-6047FBBDDE0E} (never change), MinVersion 10.0.17763,
  x64. [InstallDelete] removes old code dirs before upgrade, keeps .venv.
  ssPostInstall runs `START_WINDOWS.cmd --install` hidden; non-zero exit shows
  a message naming the log folder and the Repair shortcut. Shortcuts launch
  .venv\Scripts\pythonw.exe run_app.py with app.ico and AppUserModelID
  GH3ChartStudio.Studio. Uninstall deletes .venv, code and logs.
- installer/build_installer.cmd (local build), installer/wizard_*.bmp.
- START_WINDOWS.cmd: optional --install argument passed to the Tk tool; no
  `pause` in install mode. No argument = unchanged behaviour.
- tools/startup_windows.py: Startup(root, install) — install mode runs the
  same venv/deps/tests, writes .venv/installed.json, emits 'installed', exits
  0/1, never launches. getattr guard keeps old tests' __new__ objects working.
- gh3studio/assets/{app.ico, app_icon.png, logo.png} from Bob's image;
  gh3studio/branding.py (window icon, AppUserModelID); About dialog shows the
  logo and a Check for updates button.
- gh3studio/updates.py (pure: parse_version, interpret, check_for_update,
  due) and updates_gui.py (QThread + queued slot; automatic check once a day,
  4 s after launch, silent unless newer; GH3_NO_UPDATE_CHECK disables).
  Window.closeEvent waits for the check thread.
- .github/workflows/windows.yml; pyproject package-data for assets;
  build_windows.cmd (PyInstaller) gets the icon and assets.
- Tests: tests/test_updates.py (offline, fake fetchers; Qt checker case),
  two install-mode cases in tests/test_startup.py, real-app startup test now
  sets GH3_NO_UPDATE_CHECK.

Evidence (exact): Linux, Python 3.13, no PySide6. Executed test_updates,
test_window_fit, test_minimal and the two new install-mode startup tests:
all non-Qt cases passed; Qt cases skipped. Workflow YAML parses. The .iss has
NOT been compiled and the installer has NOT been run anywhere yet; the first
GitHub Actions run is the first real build and Windows test.

Known limits: unsigned (SmartScreen warning); setup needs internet; update
check cannot see a private repo.

## Previous 0.13.1 update — 0.13.0 plus the window fit fix

Code is 0.13.0 (09324b2) plus one commit carrying the 0.11.4 window fix, then a
merge commit joining the 0.11.4 history (no content from it beyond the fix).
No workflow, conversion, cleanup, chart or audio behaviour changed.

Window fix (gh3studio/window_fit.py, new):
- fit_geometry(): pure arithmetic — shrink preferred client size to the
  screen's available area, never below the layout minimum, centre the frame,
  always keep the frame's top-left (title bar) on screen. Frame allowance 16x48.
- place_on_screen(): main() calls it before show and again after show
  (QTimer.singleShot(0)) when real frame margins are known.
- fit_size(): dialogs clamp to the screen; Qt still centres them.
- Applied to: main window (gui.py, PREFERRED_MAIN_SIZE 1180x840), cleanup,
  sync, song export (including 0.12's conversion_report signature), editor,
  first-run and About dialogs. tools/startup_windows.py Tk window clamps to
  screen (−40 w, −120 h) and centres.
- tests/test_window_fit.py: 8 pure cases + 1 Qt case.
Known limit: layouts still need about 1024x700; on a smaller usable area the
title bar stays visible but the bottom can run off-screen (maximize as a
workaround; a scroll-area wrapper would be the real fix if Bob needs it).

Merge conflicts resolved: version files (took 0.13 then bumped to 0.13.1),
CHANGELOG (0.13.1 entry added above 0.13.0), HANDOFF (this file),
song_export_gui.py (kept 0.12's new __init__ signature, swapped its fixed
resize for fit_size).

Evidence (exact): Claude's environment = Python 3.13 Linux, NO PySide6,
SoundFile or Mido, installs blocked. Executed: tests/test_window_fit.py +
tests/test_minimal.py → 11 passed, 1 skipped (Qt case, missing PySide6). All
modules byte-compile. Full suite: 19 collection errors, all missing
dependencies — NOT a result. ChatGPT reported 296 passed for 0.13.0; the full
suite has NOT been run on 0.13.1. Bob's Windows START_WINDOWS.cmd run is the
first full verification.

## Open items (in order)

0. Check the GitHub Actions run for 0.14.0 (Actions tab). Fix any Windows test
   or Inno Setup compile failure first. Then Bob installs from the artifact:
   SmartScreen -> More info -> Run anyway; confirm setup/tests run once, Start
   menu + desktop icon, icon shows on window/taskbar, launch is fast, About ->
   Check for updates gives a sensible message, Repair works, uninstall cleans.
1. (Superseded by 0.14 install, same checks) Bob runs START_WINDOWS.cmd. Confirm the
   startup and studio windows open fully on screen, title bar drag and corner
   resize work, and the 0.13.0 Prepare my songs / Clean only flows still work.
   If a startup test fails, get start_windows.log; fix causes, never skip tests.
2. If sizing still looks wrong, ask for resolution and Windows display scale.
3. Get v0.13.1 onto GitHub as a tag/release; optionally delete v0.11.5.
4. Then the existing roadmap: Dolphin acceptance of combined conversion on
   Expert-only/Hard-only songs selecting all four slots; two consecutive
   collection runs; one song TheGHOST/Wii end to end.

## Previous 0.13.0 update (ChatGPT)

Streamlined Home to primary Prepare my songs and secondary Clean only. Tabs Home/Prepare songs/Clean only. AdaptPanel shared Choose chart / Choose folder toolbar and One song/Collection selector; duplicate embedded folder picker hidden. Single action Prepare song, collection Prepare & export. Combined guidance and approval labels; Home folder drops route to combined scan. Internal original goal keys retained. 296 tests passed in 28.51s. See docs/M13_RELEASE.md and M13_TEST_RESULTS.txt. Native Windows confirmation pending.

## Previous 0.12.0 update (ChatGPT)

User authorized combining cleanup and conversion to eliminate separate passes. complete_conversion now cleans every output difficulty, strips original unsupported markers, repairs sustains, resolves agreeing anchors and blocks conflicting anchors. Original Song remains unchanged. Reports all_difficulty_cleanup, updated operation/status and source compatibility errors separately. Existing Hard/Expert no longer promised unchanged in output; valid notes remain intact and repairs logged. Bulk exports enforce clean_all. Combined single-song dialog hides redundant manual repair toggles, displays automatic repair list and normalizes timing using song.ini delay once when audio available; export passes corresponding audio padding and guards all tracks. Optional newly requested HOPO assistance uses existing editor validator after cleanup. Legacy reserved workflows retain their previous paths. 294 tests passed in 27.12s. See M12_RELEASE.md and M12_TEST_RESULTS.txt. Native Windows/Dolphin confirmation pending.

## Parallel 0.11.4 update (Claude, merged into 0.13.1)

Made from 0.11.3 at the same time as 0.12/0.13, so 0.13.0 did not contain it.
Bob: 0.11.3 works; window opened with title bar above the screen, could not move
or resize. Cause: fixed 1180x840 main window and 860x700 Tk startup window with
no screen check. See the 0.13.1 section for the change. Commits 68896ce (fix) and
e093849 (handoff) remain in history via a merge; docs/M11_4_RELEASE.md kept.

## Previous 0.11.3 update

Added persistent Choose folder button in AdaptPanel mode row. Window.start_medium_collection handles picker, workspace selection and recursive bulk scan. start_guided orange with directory and directory drops on adapt now route here. CleanerPanel.scan retains orange goal in four_fret mode. Chart file opens explicitly switch to single-song page. Three route regressions cover nested Expert/Hard song folders, populated Medium/Easy lane restrictions, no clean queue misrouting. See M11_3_RELEASE.md and M11_3_TEST_RESULTS.txt. Windows confirmation pending.

## Previous 0.11.2 update

Windows v0.11.1: 287 passed, 1 skipped, 1 failed: long wrapped source hint allocated 57px but needed 81px. Source controls now inside collection scroll content; hint vertical QSizePolicy.Minimum prevents compression while scroll contains minimum height. Footer remains fixed. Tests unchanged, no bypass. See docs/M11_2_RELEASE.md and M11_2_TEST_RESULTS.txt. Native Windows confirmation pending.

## Previous 0.11.1 update

User Windows startup log: 3 failed, 283 passed, 1 skipped; all failures were large-text width assertions (1094px instead of 1024). Diagnostic tree identifies the hidden bulk source explanation with a 1008px minimum width, propagating through stacked pages. cleaner_gui.py now gives this QLabel a stable name and word wrapping. Regression test stretches the explanation through text length independent of installed fonts, checks hidden and active collection view, fully visible export controls and return to single-song view. No test bypass or dependency/conversion changes. See docs/M11_1_RELEASE.md and M11_1_TEST_RESULTS.txt. Focused suite: 12 passed in 3.23s; full suite: 289 passed in 26.51s (Linux/Python3.11.18/Qt offscreen). Native Windows/Dolphin execution remains pending.

## Previous 0.11.0 update

BulkDialog removed. AdaptPanel contains single/collection pages and a mode selector; embedded CleanerPanel shares owner worker busy/errors. Stable Save to output parent; no timestamp subfolder per run. export_folder_path recognizes same source path via validation.json or older source_hashes and reuses destination; separate songs still suffix. export_song_folder overwrite flow stages/validates, preserves extras, temporarily renames previous output and restores on normal installation failure. Old notes.mid removed as managed stale output. Original inputs protected; unknown/unmatched folders not overwritten. Log appends, summary latest. See M11_WINDOWS_GUIDE.md, M11_IMPLEMENTATION_LOG.md and M11_TEST_RESULTS.txt. 287 tests passed in 27.81s. Native Windows locks/Dolphin acceptance pending; test two consecutive collection runs.

## Previous 0.10.0 update

Single/bulk four-fret conversion uses difficulty_set.complete_conversion: replaces Easy with 3 lanes, Medium with 4 lanes, fills missing/empty Hard/Expert from selected original source while retaining existing tracks. Excluded sustain transfer is seeded; Easy compatibility repairs logged. All-removed target fallback remaps authored event rhythm instead of empty output or placeholder. Export guards require all 4 slots and target fret limits when difficulty_completion report exists. Standard Clean Songs alone remains cleanup-only, no new difficulties. See M10_WINDOWS_GUIDE.md, M10_IMPLEMENTATION_LOG.md, M10_TEST_RESULTS.txt. 284 tests passed in 27.81s. Native Windows/game acceptance pending; no blanket crash guarantee. Next: Expert-only/Hard-only tests selecting all four slots in Dolphin.

## Previous 0.9.1 update

All song-folder exports use Artist - Song Title via shared export_folder_name/export_folder_path. No per-song numbering/timestamps/Medium/editor tags. Batch parent keeps timestamp. Case-insensitive collision detection appends (2), (3), etc. Windows-invalid characters sanitized; each identity component capped at 48 characters; metadata remains complete. Existing folders untouched. 280 tests passed in 25.67s. See docs/M9_1_RELEASE.md and M9_1_TEST_RESULTS.txt. No native Windows execution. Next: real collection naming acceptance.

## Previous 0.9.0 update

Added bulk four-fret queue under Four-fret Medium, with recursive scan (2,000 song cap), Expert then Hard fallback/Expert only/Hard only, optional seeded Orange sustain transfer. Reuses CleanerPanel in four_fret mode and scan_charts inspect_options. inspect_chart medium_source branch preserves non-Medium tracks (shared sync translation still applies), prepares only Medium repairs; export_cleaned uses Medium export validation and records conversion details. Selection, per-song edits, failed-song continuation, cancellation and logs reused. See docs/M9_WINDOWS_GUIDE.md, M9_IMPLEMENTATION_LOG.md and M9_TEST_RESULTS.txt. 279 tests passed in 26.08s. No separate stems yet, no Windows/Dolphin acceptance of this release. Next: real nested collection acceptance.

## Previous 0.8.1 update

User says reviewed songs have correct timing and explicitly requests automatic Use song.ini delay without prompts until an in-game issue occurs. Clean Songs now normalizes offset/delay using delay alone; missing/zero delay = zero, chart Offset never added. Manual review takes precedence and hash expiry still applies. Automatic plans are recomputed from originals, not stored as manual overrides. Optional timing tool retained; details/log report automatic policy. Anchor conflicts, malformed timing and existing bounds remain distinct blockers. See M8_1_WINDOWS_GUIDE.md, M8_1_IMPLEMENTATION_LOG.md and M8_1_TEST_RESULTS.txt. 276 tests passed in 25.15s. No new dependency or native Windows/game testing. Next: collection acceptance in Dolphin, revisit timing only upon real issue.

## Previous 0.8.0 update

Bob reports 0.7.3 tested and playing in Dolphin on November 18, 2026.
Added working-copy editor launched from playback preview/button. EditSession validates transactional edits; ChartEditorDialog supports drag notes/tails, star power, HOPO profile 2.95, patterns, undo/redo, audio navigation, and worker-based new-folder export. Medium Orange prohibited. Source unchanged; output not merged into converter: reopen exported chart. Clean incompatible sources first. 268 tests passed in 24.04s; five new tests plus full regression results in docs/M8_TEST_RESULTS.txt. See docs/M8_WINDOWS_GUIDE.md and M8_IMPLEMENTATION_LOG.md for exact changed files and acceptance steps. Native Windows/new editor gameplay not tested here. Next: Windows/Dolphin acceptance, then multi-select/copy/paste and autosave. No actual Claude involvement.

## Previous 0.7.3 update

Implemented automatic source-decoder fallback via imageio-ffmpeg 0.6.0. export_ogg
catches eligible stage-specific LibsndfileError, decodes strictly to temporary PCM,
checks frames/rate/channels against readable original header, then exports/validates
Ogg with padding and metadata applied once. No source changes or discarded-error
flags. Write/output-validation failures do not retry the source decoder. Atomic
song staging and temporary PCM cleanup retained. FFmpeg timeout180s, cancellation
still between songs. Source scan header failures remain unsupported.

Setup lock adds only imageio-ffmpeg; Windows wheel hash checked and FFmpeg7.1.exe
inspected, not run. Linux provider FFmpeg7.0.2 tested. Wrapper BSD2, native binary
GPLv3+; separate notices included, compiled redistribution source obligations still
need arranging. Source ZIP has no decoder binaries or private/commercial music.
Build script collects provider data; notice collector records binary -L/-version.

Results show Audio recovered automatically; cleanup.log includes AUDIO RECOVERED;
validation.json audio_export.fallback records original error and recovery checks.
263 tests passed in25.48s (Python3.11.18/Linux/offscreen). Six new synthetic recovery
cases plus the actual user's original Opus through inspect_chart/export_cleaned
with a synthetic chart: 9,710,324 stereo frames at48kHz; input hash unchanged and
complete Ogg read-back. Actual user chart not supplied, Windows/game test pending.
See docs/M7_3_WINDOWS_GUIDE.md, M7_3_IMPLEMENTATION_LOG.md, M7_3_TEST_RESULTS.txt,
M7_3_REAL_OPUS_RESULT.json and FFMPEG_DEPENDENCY.md. Next original-Opus Windows
acceptance and one-song TheGHOST/Wii test. No actual Claude handoff occurred.

## Historical post-release audio diagnosis — November 18, 2026

User supplied song.opus for Lost in the Dark (Left to Suffer / Paleface Swiss).
Reproduced SoundFile/libsndfile 1.2.2 decoding failure after 524288 returned frames.
FFmpeg 7.1.5 strict full decode succeeds. Delivered separate song.ogg recovery;
9,710,324 stereo frames at48kHz (202.2984167s), zero alignment lag at5/100/195s,
and actual application export_ogg with metadata reconciliation/read-back passed.
No runtime source change or automatic fallback shipped; v0.7.2 remains current.
See docs/OPUS_DECODING_DIAGNOSTIC.md for hashes, commands and acceptance steps.
Do not bundle user recording in releases or tests. Next implement stage/file-specific
errors and a licensed/tested Windows decoding fallback; no silent frame skipping.
No actual user's chart or song.ini was supplied. Full song/game acceptance pending.

## Prior 0.7.2 update

Bob confirmed 0.7.1 runs on Windows, then reported nonzero Offset/song.ini delay
and a SyncTrack anchor at tick 13824. No actual affected song assets were provided.
New per-song Review synchronization dialog in Clean songs shows stored values,
explicit presets/custom total (+ notes later), independent difficulty/audio preview,
seeking, device/volume and acknowledgement. Values are never auto-summed.

normalize() translates chart objects by whole initial bars and pads audio, preserving
all tick lengths and the tempo/meter relationships; metadata delay becomes zero.
Negative shifts need no negative ticks or audio trimming. Padding rounds to samples.
Shift limit ±60s, padding cap 120s. Existing cleanup sustain repairs remain separate.
Reviews bind to chart/audio paths and hashes including song.ini; metadata-only edits
retain them, changed assets require another review. Source files remain untouched.
Plans are logged in validation.json and cleanup.log; export must use the paired
new chart/audio and zero importer delay. Session-only, per-song; no auto alignment.

Cleaner parses paired editor A anchors. Matching timestamps within 1ms are listed
for removal without changing BPMs. Conflicts remain blocked until explicit listening
review and Keep existing BPM map acknowledgement. No BPM reconstruction from anchors.
Malformed/duplicate/unpaired anchors stay blocked; strict imports/writes still refuse
unresolved anchors. Added Song.anchors and validation/export guards.

257 tests passed in23.15s (Python3.11.18/Linux/Qt offscreen), 32 new cases. Final GUI
wording/layout checked separately; see docs/M7_2_GUI_TEST_RESULTS.txt. Read
M7_2_WINDOWS_GUIDE.md, M7_2_IMPLEMENTATION_LOG.md and M7_2_TEST_RESULTS.txt. User's
Windows/audio/TheGHOST/Wii acceptance still needed. No new dependency or third-party
code copied; format docs are the existing CC0 reference. Next one affected song
end-to-end, then actual collection logs. No Claude handoff occurred.

## Prior 0.7.1 update

Bob's Windows startup reported 5 layout failures, 217 passed, 1 skipped: window
width 1083px normally and 1208px with 18px text, exceeding the unchanged 1024px
limit. Wider font metrics on Linux reproduced the same failure class (1049/1173px)
and identified the shared single-row header as the limiting layout. Brand and
version now stack and wrap, keeping navigation alongside them. The four Medium
footer actions use a two-row grid so post-export controls also fit.

Original size assertions and startup's full-test gate remain. Two new regression
cases apply 160% font stretch, with/without 18px text, visit all six pages and
check every post-export footer action. Both failed against the old header; see
docs/M7_1_REPRODUCTION.txt. All 225 tests passed in 23.83s on Python 3.11.18/Linux,
Qt offscreen; no native Windows execution. Inspected 1024x700 wide-font screenshot.
Failure assertions now include JSON layout diagnostics (fonts, DPI, style, minimum
sizes, pages and scroll ranges) in the existing startup log. No music/export or
dependency behavior changed. See docs/M7_1_WINDOWS_GUIDE.md,
M7_1_IMPLEMENTATION_LOG.md and M7_1_TEST_RESULTS.txt.

Next: run this release's START_WINDOWS.cmd on Bob's Windows machine, then verify
the essential workflows and one song in TheGHOST/Wii. Diagnose collection blockers
from actual scan/cleanup logs before adding features. No Claude handoff has occurred.
Account usage limits are not observable here; keep this handoff current each release.

## Prior 0.7.0 update

Focused GUI implemented: Home, Clean songs, Four-fret Medium. Tools in reserve
reveals advanced converter, patterns and audio lab on demand. New AdaptPanel uses
existing Orange-removal service, defaults sustain preservation ON in the focused
workflow, has independent Expert/Hard source selection and explicit source/output
comparison. Cleaner adds search/status filters, side-by-side inspector/results,
pinned destination/Start and readable outcomes; logs open even after all failed.
Playback transport is above the chart; extra settings collapsed. Dropped audio
on the main path is preview-only. Export dialog explains blockers in plain text.
Global operation/elapsed/count display and refreshed startup branding. No new deps.
223 tests passed in23.28s on Linux/Python3.11/Qt offscreen. Small-window/large-text
assertions retained; screenshots inspected. Windows build/audio/game tests pending.
Read docs/M7_WINDOWS_GUIDE.md, M7_IMPLEMENTATION_LOG.md and M7_TEST_RESULTS.txt.
Next user acceptance of the essential workflows, actual54-song blockers, one-song
Wii acceptance. Session persistence/retry/additional profiles still unimplemented.

## Accepted scope update after v0.6.4

Prioritize existing-chart cleanup for GH3 Wii and challenging lower difficulties
from Expert/Hard by reducing fret requirements. Preserve rhythm, tempo, valid
sustains/chords and verified mechanics; no automatic density reduction or target
note count. Medium must contain only G/R/Y/B. Retain seeded random sustain transfer
within legal choices. Audio playback/sync/export stays; transcription, separation,
tablature search and learned generation are deferred. Authored game-chart MIDI
still supported: parsing authored notes is distinct from audio transcription.
See docs/PROJECT_DIRECTION.md for complete policy, acceptance and known gaps.
The scope decision was initially documentation-only. The 0.7.0 update above
implements its focused GUI; native Windows/game verification remains pending.

## Prior 0.6.4 update

Includes Save scan report (all discovered blockers) and per-run cleanup.log
(timestamped per-song outcomes, error traceback and completion/cancel counts).

True Select all plus ready-only option, visible blocked-song errors and exact
failure reasons in cleanup_summary.json. Start now runs directly using visible
output parent (defaults beside source); separate Change output folder opens picker.
Preflight destination check and cleaner goal routing expose errors/progress.
Mixed selected rows export valid songs while recording blocked rows as failures.
215 tests passed in 21.92s; 1024x700 offscreen screenshot inspected.
Native Windows and user's 54-song collection not tested. The 10 blocked errors
have not been provided; do not claim they are resolved. See docs/M6_4_WINDOWS_GUIDE.md,
M6_4_IMPLEMENTATION_LOG.md and M6_4_TEST_RESULTS.txt. Next collect actual error
report and verify one exported song in the target importer/game.

## Prior 0.6.3 update

Cleaner bulk selection (ready rows only), checked/error counts, fixed top START
CLEANING and approval controls. Start explains unmet prerequisites. Results opens
only after successful export. Metadata rechecks preserve unchecked selections.
A sole non-preview audio file beside a chart is now automatically matched even
when called guitar.wav/ogg, with a warning to verify it contains the full mix.
Multiple unidentified files still require review; no automatic stem mixing.
214 tests passed in 21.54s; offscreen 1024x700 screenshot inspected. Native Windows
and game acceptance pending. See docs/M6_3_WINDOWS_GUIDE.md,
M6_3_IMPLEMENTATION_LOG.md and M6_3_TEST_RESULTS.txt. Next: one packaged song
end-to-end acceptance, then a small recursive collection. No Claude handoff occurred.

## Prior 0.6.2 update

Fixed manual metadata disappearing after OK when chart recheck failed before
identity was populated. Preserve editable fields before parsing; table/editor retain
values even on error. Status distinguishes retained edits from remaining blockers.
Rechecks cannot carry stale offset/resolution metadata over corrected source files.
Tests cover malformed/offset charts, GUI OK/reopen, and stale timing fields.
See docs/M6_2_WINDOWS_GUIDE.md, M6_2_IMPLEMENTATION_LOG.md and M6_2_TEST_RESULTS.txt.
Edits are session-only until export; original files untouched. Native Windows/user
song confirmation pending. Next edit/reopen/export acceptance and remaining errors.

## Prior 0.6.1 update

User Windows failure: UTF-8 test read used platform default; larger-text window
was1227px. Explicit UTF-8 reads/writes in cleaner tests; shorter cleaner footer
labels, separate header action row, scrollable Pattern Library content and tabs.
New wide-hidden-control regression; previous strict size checks retained.
Read docs/M6_1_WINDOWS_GUIDE.md, M6_1_IMPLEMENTATION_LOG.md and M6_1_TEST_RESULTS.txt.
No gameplay/cleanup algorithm changes. Exact native Windows acceptance pending;
next user startup retest then one-song import/game acceptance.

## Prior 0.6.0 update

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
