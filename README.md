# GH3 Chart Studio 0.7.0 — Wii chart workshop

Prepare existing authored song folders for GH3 Wii, or create a challenging
four-fret Medium from Expert/Hard. The primary interface has **Home**, **Clean
songs** and **Four-fret Medium**. Audio generation and pattern tools remain under
**Tools in reserve**; they are not part of the main workflow.

## Start on Windows 10/11 x64

1. Close the old application. Extract the complete ZIP into a new writable folder.
2. Double-click **START_WINDOWS.cmd**. It checks Python 3.11 x64, sets up dependencies,
   runs automated tests, and launches. Missing runtimes trigger the existing signed
   installer bootstrap; internet is needed for initial setup. See
   [bootstrap details](docs/M5_6_WINDOWS_GUIDE.md).
3. Choose **Clean my songs** or **Make a challenging Medium** from Home.
4. Follow the numbered steps in the selected workspace.

See [exact Windows test steps](docs/M7_WINDOWS_GUIDE.md), including small-window,
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

223 tests passed in 23.28 seconds on Python 3.11/Linux with Qt offscreen. See
[recorded results](docs/M7_TEST_RESULTS.txt). Essential screens were inspected at
1024x700; automated checks also cover 18px text. This is a tested source package,
not a prebuilt or Windows-verified executable. Native Windows DPI/audio devices,
TheGHOST and Wii/Dolphin acceptance remain pending. No signing/SmartScreen guarantee.

The conservative cleaner removes forced/tap/open-note markers and repairs reported
sustain overlaps across all guitar difficulties. Other instruments, separate stems
and artwork are omitted. A sole instrument-named recording may be auto-matched;
verify it is the full mix. Stems are not automatically mixed. Nonzero offset/delay,
non-/4 meter and other unresolved chart errors may block export. Do not assume every
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
[implementation log](docs/M7_IMPLEMENTATION_LOG.md) and [handoff](HANDOFF_LATEST.md)
record scope, limitations and next work.

Credits to Nanook and TeamGHOST and the format-reference authors remain under
**About** and in [credits](docs/CREDITS.md). Dependency notices are in `licenses/`
and `THIRD_PARTY.md`. No new third-party dependency or artwork was added in 0.7.0.
