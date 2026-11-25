# 0.19.0 — Clear repair and challenging-Medium workflows

- One Songs queue for single charts and recursive collections. Home clearly separates Repair existing charts from Create challenging Medium; Check charts — report only cannot export.
- Main adaptation keeps authored Easy/Hard/Expert unless explicitly selected otherwise. Optional Easy replacement, missing-slot copies, other-track repair, Orange sustain transfer and sustain shortening are visible choices, initially off.
- Unapproved sustain repairs and invalid retained tracks block export. Main workflow blocks an empty Medium instead of inventing notes. Medium remains G/R/Y/B only.
- Original/Prepared playback and the existing editor feed back into the queue; Apply edits clears approval and export stays in Songs. Preview/editor account for export-only audio padding. Reports include per-difficulty summaries.
- MIDI FIFO release pairing preserves restarted sustains; duplicate note-ons are handled and dangling notes with no recoverable duration block again, addressing the reproduced 0.18.6 test failure.
- Current feature/usage documentation replaces stale historical claims. Previous handoff archived; advanced/experimental tools remain available with their broader legacy behavior documented.
- See docs/M19_RELEASE.md, docs/M19_TEST_RESULTS.txt and HANDOFF_LATEST.md for evidence, limits and exact Windows checks. Native Windows/game acceptance is a separate step.

# 0.18.6 — Downloaded MIDI charts no longer blocked by overlaps or track names

Bob: songs blocked with "No PART GUITAR or T1 GEMS track found" and "Overlapping MIDI pitch 84 at 166464".
- Same-fret overlaps (a fret restarted before its note-off; pitch 84 = Hard green) end the earlier note where the next starts, like Clone Hero/Moonscraper, instead of blocking the song. Stray note-offs are ignored and notes without a note-off end at the track end; each is listed in the song's warnings.
- Guitar track names are matched regardless of capitalization, spaces or underscores (Part Guitar, PART_GUITAR). Lead guitar (PART GUITAR, T1 GEMS) is preferred; PART GUITAR COOP or PART RHYTHM is used only when there is no lead guitar, with a warning.
- A MIDI with no guitar part at all is still blocked, but the message now lists the tracks it does contain (e.g. PART DRUMS, PART VOCALS).
- Note: TheGHOST "Star Power 0 (Forced)" is TheGHOST's ForceNoStarPower setting (Project screen > Default Settings > 3. Notes), not an export problem.

# 0.18.5 — Keep forced HOPO/strum notes for TheGHOST

- Bob: TheGHOST's chart edit step showed 0 forced notes for every song. Cleanup removed every source marker, including forced notes (N 5 / E *), which TheGHOST supports, so songs played with automatic HOPO guesses instead of what the charter wrote.
- Each note's authored intent is now kept: what it was meant to be in Clone Hero (its natural HOPO guess, flipped by a forced marker; song.ini hopo_frequency / eighthnote_hopo honoured). Tap notes, which GH3 does not have, become forced HOPOs. Open notes are still removed.
- TheGHOST forced flips (N 5) are then written wherever TheGHOST's own guess at HOPO measure 2.95 would differ, on Easy, Medium, Hard and Expert (Medium/Easy follow their source difficulty), so the four-fret conversion keeps the intent even where removing Orange changes the automatic guess.
- Applies to Prepare my songs (single song and collections) and Clean only. Songs without forced or tap notes export exactly as before.
- Set TheGHOST's HOPO measure to 2.95: the flips are calculated for that setting.
- Timing shifts and synchronization move forced flips with their notes. Each song's changes list the authored forced/tap counts and flips written.
- Tests: tests/test_hopo_intent.py (6 cases incl. every difficulty after Orange removal); five existing tests updated from "no markers after export" to "only TheGHOST flips on real notes, playing as authored".

# 0.18.4 — Safer updates and correct shared audio streams

- Script installer stages the complete payload before touching the installed app, retains the complete previous installation (including its environment), and restores it if setup or tests fail. Failed files/logs are retained separately. New dependencies are installed at the final path. Concurrent installers are locked out. Backups intentionally require manual removal after a successful upgrade.
- Compiled installer delegates to that same transaction instead of deleting live files itself. Shortcuts/registration are published after setup passes.
- Update download is modal; completion rechecks chart jobs and cancellation before launching the installer. App close rejection is respected.
- Audio discovery includes each physical recording once across stream roles, including hard links. Distinct recordings remain distinct even when their bytes match. Exclusions are reported.
- Added real PowerShell transaction and parser tests plus GUI update-race and audio-level regression tests. See docs/M18_4_RELEASE.md for evidence and Windows checks.

# 0.18.3 — Next batch after an export shows its songs

Bob: after finishing one folder, dropping the next folder did not produce songs.
- The collection screen's search box and "Save to" box accepted dropped folders as typed text (the search text then hid every row, or the output path was replaced) instead of letting the window scan the folder. They no longer accept drops.
- Each new scan clears the search text, resets the Needs help / Ready filter and shows the selected-song details, so leftovers from the previous batch cannot hide new songs.
- Exporting from Prepare my songs left the app in Clean only mode, so Home's Continue opened the empty Clean only page and progress went to the wrong screen. It now stays in Prepare my songs.
- New test: two batches back to back (drop, export, drop the next folder).

# 0.18.2 — Check for updates at every start

- The update check now runs every time the studio opens (about 1.5 s after the window appears) instead of once a day. When a newer GitHub release exists it shows the Download and install prompt; choosing Later asks again next start. Nothing is shown when up to date, offline or when releases are not visible.

# 0.18.1 — Prefer the release ZIP Bob attaches

- Download and install now uses a GH3_Chart_Studio_*.zip attached to the GitHub release when present (the package Bob drops on each release), and falls back to GitHub's automatic source ZIP otherwise. Either way the version inside must match the release, or nothing is installed.

# 0.18.0 — Download and install updates from inside the app

- When a newer GitHub release exists (daily check, or About -> Check for updates), the prompt offers Download and install.
- The app downloads the release's source ZIP (GitHub creates it automatically for every release), checks it is undamaged, has no unsafe paths and is exactly the announced version, closes, and starts "Install GH3 Chart Studio.cmd" from it. The installer waits up to 30 s for the app to close, then installs as usual (setup and tests once; Start menu entries kept).
- Download problems are reported and the app stays open. A running job blocks the update until it finishes.
- Requirement: the app must be able to see the releases. While the repository is private, the check reports that no public release was found.

# 0.17.0 — Remove track-number prefixes from Artist and Title

- Bob: 0.16.7 installed and running. Renaming tools add "1. ", "3." etc. to Artist or Title to mark track order; almost no artist names contain such numbers.
- Song scans (Prepare my songs and Clean only, single songs and collections) and the single-song export review remove a leading 1-3 digit number followed by a period from Artist and Title: "1. Metallica" -> "Metallica", "03.Enter Sandman" -> "Enter Sandman", "3. 1979" -> "1979".
- Names that only start with numbers are kept: "3 Doors Down", "311", "The 1975", "10.000 Maniacs", "2.0", "5.5 Hours".
- Each removal is listed in the song's warnings and changes. A value typed by hand in the metadata editor is kept as typed. Album and other fields are not changed.
- The cleaned names flow into notes.chart, song.ini, song.ogg tags and the "Artist - Title" folder name.

# 0.16.7 — Root cause of the install-time test freeze

- Bob's 0.16.6 install froze again in tests/test_stems_gui.py, this time with the worker inside soundfile's open (0.16.5: inside realpath). The worker stops wherever it is when the deadlock forms, so the location is not the cause.
- Cause: since v0.3.0, test_gui.py has an autouse fixture that disposes closed windows (and their Qt media players) between tests, because media-player teardown during another test's busy worker can deadlock. It only applies to modules that import it; the new test_stems_gui.py and test_playback_source.py did not.
- tests/conftest.py now disposes closed Qt windows after EVERY test, in every module, so new test files cannot miss it. The 150 s hang safety net stays.
- No application code changed in this release.

# 0.16.6 — Install-time test hang: fix and safety net

- Bob's install of 0.16.5: 293 tests passed, including test_external_stem_analyzed_original_mix_retained (the 0.16.4 fix held). Then tests/test_stems_gui.py hung 60 s with the worker thread inside Path.resolve() (Windows realpath) at the start of stems.cached_mix.
- cached_mix builds its cache key with os.path.abspath + os.stat instead of Path.resolve().
- New tests/conftest.py: any single test running 150 s prints all thread stacks to the log and ends the run (exit 3), so setup reports a failure instead of freezing until cancelled. Verified locally with a deliberately stuck test.

# 0.16.5 — Bug review fixes

Review of everything changed since 0.13.1 (stems, lean export, playback, installer, updates):
- Playback: the 0.16.4 "already loaded" shortcut would also skip a recording that had FAILED to load, so choosing it again could never retry. It now reloads unless the current load succeeded.
- Separate tracks: a file named in the chart (MusicStream/GuitarStream...) now always wins over a same-role file found by name (e.g. MusicStream=backing.mp3 beside song.ogg used song.ogg before).
- Separate tracks: cached preview mixes in the temp folder (tens of MB each) were never deleted; only the 6 most recent are kept now.
- Single-song view: songs made of separate tracks lost title/artist tags from the main track (the temporary mix has none); they are filled from the main track again.

Known minor gaps (not changed): mixing runs before a song's chart checks, so a blocked song still spends time mixing; editor exports of separate-track songs do not record audio_stems; script-installer shortcuts have no taskbar app ID (the Inno installer sets it).

# 0.16.4 — Avoid reloading an already-open recording

- Bob's install run of 0.16.2/0.16.3 hung for 60 s in test_external_stem_analyzed_original_mix_retained (restore_mix -> open_path -> show_analysis) and was cancelled. The same test passed in his two earlier runs that day and hung once before in 0.5.6: an intermittent Qt multimedia (FFmpeg backend) freeze.
- Playback no longer re-sets the media source when the requested recording is already loaded; re-setting rebuilt the FFmpeg backend for no reason, the most likely trigger of the freeze. New test: tests/test_playback_source.py.
- Not proven fixed: the hang is intermittent. If it recurs, the trace in start_windows.log is needed.

# 0.16.3 — Uninstall in the Start menu

- New Start menu entry "GH3 Chart Studio - Uninstall" (script installer and the Inno Setup installer). It removes the shortcuts, the Settings > Apps entry and the program folder, including its private Python environment. Songs and exported song folders are never touched.
- Uninstall is still also available in Settings > Apps > Installed apps.

# 0.16.2 — Test correction

- Windows run of 0.16.1: 334 passed, 1 failed with KeyError 'padded_frames'. The audio fix worked (the clip check passed); the test itself checked padding on the longest track (guitar), which is never padded. It now checks that the two shorter tracks are padded to the mix length. No app code changed.

# 0.16.1 — Mixed tracks never clip after Ogg encoding

- Bob's Windows install of 0.16.0: 334 passed, 1 failed. The stem-mix test decoded song.ogg with a 1.023 peak: the mix was limited to 0.98, and lossy Vorbis encoding overshot it.
- Mixes of separate tracks are now kept at or below -1 dBFS (0.891) before encoding; the whole mix is turned down evenly only when needed. FFmpeg Vorbis check of the worst case (flat signal at 0.891) decodes at 0.921.
- The test now uses realistic tones and still requires the decoded song.ogg to stay below full scale.

# 0.16.0 — Lean, guitar-only GH3 export

- Exported song folders contain only what Guitar Hero III guitar play uses (no drums, microphone/vocals, keys, bass or 6-fret data).
- notes.chart: the four guitar difficulties only (as before), [Events] keeps practice sections and end; lyrics, vocal phrase markers, crowd/venue and other Rock Band/Clone Hero cues are removed. [Song] header keeps identity, Offset, Resolution, preview times and MusicStream.
- song.ini: identity, song length, delay, preview times and guitar settings only; drum/vocal/keys/bass/GHL difficulties, pro-drums, video, icon and similar keys are removed.
- song.ogg is unchanged in principle: it is still the complete song, including the sound of drums and vocals.
- Everything removed is listed per song in validation.json (gh3_lean). Applies to single songs, collections and editor exports.
- Policy change: extra song.ini fields were previously preserved; they are now dropped unless GH3 uses them.

# 0.15.0 — Songs with separate audio tracks

- Songs downloaded as separate tracks (song/backing + guitar, rhythm, bass, keys, drums, vocals) are detected and mixed into one song.ogg for both single songs and collections. Before, song.ogg alone was used, which drops the guitar, or the song was blocked.
- Mix keeps every track at its original level, places mono tracks in both channels, pads shorter tracks with silence, resamples a track with a different sample rate, and turns the whole mix down evenly only if it would clip.
- preview and crowd tracks and unrecognized files are left out and listed. Duplicate formats of the same track prefer Ogg. Chart MusicStream/GuitarStream/... entries are honoured.
- A track libsndfile cannot decode is recovered with FFmpeg (header-checked); an unreadable track blocks the song with its file name.
- Single-song view mixes once (cached in the temp folder) so preview playback and export use the same mix. validation.json records every track, hash, padding, resampling and gain as audio_stems; cleanup.log notes the mix.
- A lone audio file named like an instrument (e.g. guitar.ogg) is still treated as the full song, with a warning.
- Source files are never modified.

# 0.14.1 — Installer that works straight from the ZIP

- New "Install GH3 Chart Studio.cmd" (installer/install.ps1): double-click after extracting the ZIP. No compiled setup .exe needed.
- Installs per user to %LOCALAPPDATA%\Programs\GH3 Chart Studio, runs setup and tests once, creates Start menu entries (GH3 Chart Studio, GH3 Chart Studio - Repair) and a desktop icon, and registers in Settings > Apps with Uninstall (installer/uninstall.ps1).
- Uses the same Apps entry as the Inno Setup .exe, so the two never appear twice. The Inno Setup .exe built by GitHub Actions remains the preferred installer when available.

# 0.14.0 — Windows installer, app icon and update check

- New per-user Windows 10/11 installer (Inno Setup, installer/GH3ChartStudio.iss): no administrator prompt; installs to %LOCALAPPDATA%\Programs\GH3 Chart Studio.
- Setup and the full automated test suite run once during installation (START_WINDOWS.cmd --install). Start menu and desktop shortcuts then open the studio directly with no setup or tests.
- Start menu: GH3 Chart Studio and GH3 Chart Studio - Repair (re-runs setup/tests). Optional desktop icon (on by default). Upgrades install over the old version and reuse unchanged dependencies; uninstall removes the program and its private Python environment.
- New app icon and logo from Bob's artwork: window/taskbar icon, shortcuts, installer and About screen.
- Check for updates: About screen button, plus a quiet once-a-day check that only speaks up when a newer GitHub release exists. Nothing downloads or installs automatically. A private repository or no internet gives a plain message, never an error.
- GitHub Actions workflow runs the full test suite on Windows for each push to main and builds the installer; a published release gets the installer attached and must match the app version.
- START_WINDOWS.cmd without arguments behaves exactly as before (setup + tests + launch) for source checkouts.

# 0.13.1 — Combined release: 0.13.0 plus the window fit fix

- Brings the 0.11.4 window fix (made in parallel from 0.11.3) into the 0.13.0 line; no other behaviour changes.
- Main window sizes itself to the screen's usable area and opens centred with its title bar visible, instead of a fixed 1180x840.
- Dialogs (cleanup review, sync review, export review, editor, first-run notice, About) shrink to fit the screen when needed.
- Startup progress window fits small screens and opens centred.
- Version numbering: 0.11.4 existed only on GitHub and the v0.11.5 GitHub release tag pointed at that same commit; 0.13.1 supersedes both.

# 0.13.0 — Streamlined preparation interface

- One primary Home action, Prepare my songs, with secondary Clean only.
- Shared chart/folder toolbar; duplicate collection picker removed from view.
- Clear Choose songs / Review / Export steps and combined action labels.
- Home folder drops use combined preparation.

# 0.12.0 — Convert and clean in one workflow

- Four-fret conversion automatically cleans all four difficulties for single songs and collections.
- Single-song export applies song.ini delay automatically, with padding recorded once.
- Repair details remain reviewable; original source files stay unchanged.

# 0.11.3 — Direct collection import for challenging Medium

- Visible Choose folder action in Four-fret workspace; recursively scans nested song folders.
- Folder drops and guided folder paths route to the conversion queue, not Clean songs.
- Preserve orange workflow identity during scans; chart-file opens return to single-song view.

# 0.11.2 — Prevent clipped collection help

- Move collection source settings into the scroll area; wrapped explanation cannot shrink below its requested height.
- Keep output controls fixed and retain all layout assertions.

# 0.11.1 — Large-text startup layout fix

- Wrap collection source-difficulty help text so hidden/active pages fit small windows.
- Regression coverage checks long help text, both collection and single-song views, and visible export controls.
- Keep startup tests enabled; no dependency or chart/audio processing changes.

# 0.11.0 — Embedded bulk workflow and reusable exports

- Removed bulk popup; main Four-fret workspace switches between single-song and collection views.
- Stable output directories; validated replacement with normal-error rollback, preserved extras and append-only run log.
- Recognize source identities to update correct folders without overwriting unrelated same-title songs.

# 0.10.0 — Three-fret Easy and complete difficulty slots

- Single/bulk four-fret conversion now produces Easy G/R/Y and Medium G/R/Y/B.
- Retains existing Hard/Expert; fills missing slots with selected source.
- Preserves source rhythm in all-removed fallback and rejects empty converted slots before export.

# 0.9.1 — Song identity folder names

- All song-folder exports use Artist - Song Title; no numbered prefix or timestamp.
- Case-insensitive collision suffixes protect existing files; metadata remains intact.

# 0.9.0 — Bulk four-fret Medium

- Recursive collections, Expert/Hard source policy and optional sustain transfer.
- Shared queue selection, metadata/audio repair, worker progress, cancellation and per-song logs.
- Medium-only conversion/repairs; source files unchanged and other tracks retained with shared sync translation.

# 0.8.1 — Automatic song.ini delay

- Clean Songs normalizes stored delay automatically, without per-song synchronization confirmation.
- Chart Offset is ignored by this user-selected policy; missing delay is zero. Source files unchanged.
- Optional manual timing tool and adjustment logs retained; eight new regression cases.

# 0.8.0 — Interactive chart editing

- Transactional preview editor, note/sustain drags, star power, HOPO/strum and pattern actions.
- Undo/redo, audio navigation, full-song export preserving source files and four-fret Medium.
- User reports 0.7.3 playing in Dolphin; new editor acceptance pending.

# Changelog

## 0.7.3 — November 18, 2026

Built-in strict FFmpeg fallback for source audio decoding failures, verified header
frame/rate/channel preservation, atomic Ogg export and clearer stage/file errors.
Automatic setup of pinned imageio-ffmpeg; recovery shown in results and logs.
263 tests passed, plus the supplied original Opus recovered through the cleaner
with a synthetic chart. Native Windows/game acceptance pending.

## 0.7.2 — November 18, 2026

Per-song synchronization review in Clean songs; normalize an explicitly selected
shift with exact chart translation and audio padding, zero exported delay and
logged changes. Safely remove matching editor anchors; conflicting timestamps
require explicit retention of the existing BPM map. Thirty-two new tests; 257 passed
on Linux/offscreen. Native Windows/game acceptance pending. See
docs/M7_2_IMPLEMENTATION_LOG.md.

## 0.7.1 — November 18, 2026

Fix shared-header minimum width after Windows startup reported five small-window
failures. Stack/wrap branding and split the Medium footer actions into two rows.
Keep the existing size limits and startup test gate. Add wide-font regressions
and detailed layout reports on assertion failure. 225 tests passed on Linux with
Qt offscreen; native Windows acceptance remains pending. See
docs/M7_1_IMPLEMENTATION_LOG.md and docs/M7_1_WINDOWS_GUIDE.md.

## 0.3.0 — November 14, 2026

Local audio decoding, spectral/energy attack analysis, tempo/beat estimates, manual
BPM and draft shift, waveform preview, onset-aligned four-fret drafts, authored
tempo preservation, learned-pattern transfer and offset/drift diagnostics.
Unicode title handling and Qt disposal fixes. See docs/M3_IMPLEMENTATION_LOG.md.

## 0.2.0 — November 14, 2026

Local pattern library: recursive scans, SQLite storage, deduplication/resume,
feature and repeated-motif extraction, similarity search, pattern preferences,
three seeded variation modes and a dedicated GUI workspace. 74 tests passed,
with additional GUI stress and independent export checks. Windows/gameplay
acceptance remains pending. See docs/M2_IMPLEMENTATION_LOG.md.

## 0.1.0 — November 13, 2026

Initial Milestone 1 source release: authored-chart conversion, four-fret Medium,
PySide6 GUI, paired chart/MIDI export, compatibility validation, 53 automated tests,
independent format checks, Windows scripts and pinned dependency lock.
Windows executable and in-game acceptance remain pending.
