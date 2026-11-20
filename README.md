# GH3 Chart Studio 0.18.1 — Wii chart workshop

**Streamlined workspace:** Home → Prepare my songs. Choose chart or folder from one toolbar, review, then export. Clean only is the secondary option when you want to retain existing difficulty choices. [Windows steps](docs/M13_RELEASE.md).

**Convert and clean together:** Make a challenging Medium now creates Medium + Easy, fills missing slots and cleans all four difficulties. Exported Hard/Expert receive compatibility repairs; originals remain unchanged. No separate Clean songs pass needed. [Windows steps](docs/M12_RELEASE.md).

**Startup layout fix:** The collection source explanation now wraps at large text sizes, preventing a hidden page from widening the entire window. [Fix details and Windows test steps](docs/M11_1_RELEASE.md).

**Collection import:** Make a challenging Medium → Choose folder… scans a parent and all nested song folders. Dropping a folder into Four-fret Medium uses the same conversion queue. [Windows steps](docs/M11_3_RELEASE.md).

**One workspace, reusable exports:** Choose One song or Folder collection within Four-fret Medium. Repeated runs update recognized Artist - Song Title output folders without another timestamped directory. [Windows steps](docs/M11_WINDOWS_GUIDE.md).

**Complete converted difficulties:** Four-fret conversion now also creates three-fret Easy and fills missing Hard/Expert from the selected source. [Windows steps and behavior](docs/M10_WINDOWS_GUIDE.md).

**Song folder naming:** exports use Artist - Song Title, with (2), (3), etc. only for collisions. [0.9.1 release and Windows steps](docs/M9_1_RELEASE.md).

**Bulk four-fret conversion:** Four-fret Medium → Bulk folder conversion scans nested song folders, copies Expert/Hard into Medium and exports new song folders with per-song logs. [Windows steps](docs/M9_WINDOWS_GUIDE.md).

**Automatic timing:** Clean Songs now uses song.ini delay without a per-song timing prompt. Chart Offset is not added; missing delay means zero. Manual overrides remain under Timing tools (optional). See [0.8.1 Windows steps](docs/M8_1_WINDOWS_GUIDE.md).

**New: interactive chart editor.** Right-click the playback preview or choose Edit displayed chart. Edit notes, sustains, star power and patterns in a working copy, then export a new song folder. See [Windows editor guide](docs/M8_WINDOWS_GUIDE.md) and [implementation details](docs/M8_IMPLEMENTATION_LOG.md).

Prepare existing authored song folders for GH3 Wii, or create a challenging
four-fret Medium from Expert/Hard. The primary interface has **Home**, **Clean only** and **Prepare songs**. Audio generation and pattern tools remain under
**Tools in reserve**; they are not part of the main workflow.

## Start on Windows 10/11 x64

1. Close the old application. Extract the complete ZIP into a new writable folder.
2. Double-click **START_WINDOWS.cmd**. It checks Python 3.11 x64, sets up dependencies,
   runs automated tests, and launches. Missing runtimes trigger the existing signed
   installer bootstrap; internet is needed for initial setup. See
   [bootstrap details](docs/M5_6_WINDOWS_GUIDE.md).
3. Choose **Prepare my songs** (conversion + cleanup) or **Clean only** from Home.
4. Follow the numbered steps in the selected workspace.

See [0.7.3 Windows test steps](docs/M7_3_WINDOWS_GUIDE.md), including small-window,
playback, export and reserved-tool checks. Setup failures are recorded in
`start_windows.log` and `startup_bootstrap.log`.

## Clean existing songs

Choose one song folder or a parent collection; scanning is recursive. The queue
matches assets inside each song folder, displays planned repairs and blocked
songs, and supports title/artist search plus **Needs help**/**Ready** filters.
**Select all**, **Ready only** and **Clear** operate on the entire queue, including
filtered-out rows. Review each relevant song, correct metadata or ambiguous assets,
check **Apply the cleanup changes I reviewed**, then **Start cleaning**. The output
location is already shown; Start does not open a location picker.

Every successful output contains `notes.chart`, `song.ogg`, `song.ini`, validation
and import reports. Per-run `cleanup.log` and `cleanup_summary.json` record outcomes.
**Open results / logs** also works after an all-failed run if a report folder exists.
**Save scan report** collects blockers before export. Original folders stay untouched.

## Automatic audio recovery

If the source decoder fails while exporting a recording, the app now retries with
packaged FFmpeg, validates decoded length/rate/channels, and continues the Ogg export.
No manual conversion is required. Results and cleanup.log identify recovered audio;
validation.json records both the original error and recovery checks. Sources remain
untouched. Startup installs the new pinned decoder dependency automatically.
Unrecoverable audio remains a reported failure; errors now name the file and stage.
See [Windows recovery test](docs/M7_3_WINDOWS_GUIDE.md) and
[dependency/licensing notes](docs/FFMPEG_DEPENDENCY.md).

## Resolve synchronization blockers

Select a song in Clean songs and click **Review synchronization…**. Inspect Offset
and song.ini delay, choose the intended total shift, listen using the selected
track/recording, and confirm before applying. Export uses a reviewed chart lead-in
and audio silence so both delay fields can be zero without trimming audio. Import
the resulting chart and Ogg together; do not apply the original delay again.
Matching editor tempo anchors are listed for cleanup. Conflicting anchors require
an explicit choice to keep the existing BPM map after listening; their timestamps
are not used to invent a new tempo map. Malformed/unpaired anchors remain blocked.
See the [step-by-step guide](docs/M7_2_WINDOWS_GUIDE.md). Reviews are per song and
session-only; changing source assets invalidates them. No automatic sync detection.

## Create four-fret Medium

Choose a supported `.chart` or game-chart MIDI file, select **Expert** or **Hard**,
then **Create four-fret Medium**. The focused workflow does not apply automatic
density thinning. Orange taps are removed. Sustain preservation is enabled by
default in this workflow: Orange sustains transfer to allowed frets using the
existing repeatable random placement; unresolved conflicts require export review.

Use **View track**, **Review source** and **Review Medium** to compare the actual
source and prepared output. **Play preview audio** plays the matched recording
or asks you to choose it. **Playback & timing options** exposes output device,
volume, estimated HOPO display, explicit timing edits and sustain regeneration.
**Review / export song…** opens metadata, recording and compatibility review before
asking where to save a new song folder. Expert/Hard source tracks are retained.

Medium must contain only Green, Red, Yellow and Blue. The existing chart/MIDI
export validators continue enforcing this rule. Other target difficulty profiles
are not implemented. A source's existing Medium is replaced only in the new output.

## Limits and verification

263 tests passed in 25.48 seconds on Python 3.11/Linux with Qt offscreen. See
[recorded results](docs/M7_3_TEST_RESULTS.txt). Existing 1024x700 and wider-font checks
remain; new checks exercise the synchronization dialog, tempo preservation and
actual padded Ogg exports. The user confirmed 0.7.1 launches on Windows; this new
release still needs Windows acceptance. No native Windows build, audible device,
TheGHOST or Wii/Dolphin tests here. No signing/SmartScreen guarantee.

The conservative cleaner removes forced/tap/open-note markers and repairs reported
sustain overlaps across all guitar difficulties. Other instruments, separate stems
and artwork are omitted. A sole instrument-named recording may be auto-matched;
verify it is the full mix. Stems are not automatically mixed. Nonzero offset/delay requires the new synchronization review.
Non-/4 meter and other unresolved chart errors may still block export. Do not assume every
source is supported. HOPO assistance remains experimental and requires importer/
game verification. Edits and selections are session-only until export.

For legacy game-chart MIDI, use **Tools in reserve → Advanced converter** to choose
**Legacy MIDI / TheGHOST** before importing; the default reader is Modern MIDI.
General instrumental MIDI is not automatically a guitar-game chart. See the
[compatibility notes](docs/COMPATIBILITY.md) and each export's import report.

## Build, history and credits

Run **build_windows.cmd** after setup. It tests, collects licenses and builds with
PyInstaller. Keep the entire `dist/GH3ChartStudio` directory together. This Windows
build recipe has not been executed here; it does not promise byte-identical builds.
See [Windows acceptance](docs/WINDOWS_TEST.md).

The ZIP includes `repository.bundle` and `RELEASE_COMMIT.txt`. Restore history with
`git clone repository.bundle GH3-Chart-Studio-repo`. Source modules live in
`gh3studio/`; tests in `tests/`; synthetic examples in `examples/`. No commercial
recordings are bundled. [Project direction](docs/PROJECT_DIRECTION.md),
[implementation log](docs/M7_3_IMPLEMENTATION_LOG.md) and [handoff](HANDOFF_LATEST.md)
record scope, limitations and next work.

Credits to Nanook and TeamGHOST and the format-reference authors remain under
**About** and in [credits](docs/CREDITS.md). Dependency notices are in `licenses/`
and `THIRD_PARTY.md`. Version 0.7.3 adds imageio-ffmpeg for automatic audio recovery;
its wrapper and native decoder have distinct licenses.
