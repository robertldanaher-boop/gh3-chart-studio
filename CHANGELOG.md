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
