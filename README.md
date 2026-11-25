# GH3 Chart Studio 0.20.0 — Wii chart workshop

Repair an existing guitar-game chart, or turn Expert/Hard into a challenging
four-fret Medium. One **Songs** queue handles a single chart or a folder collection.
Original files are never edited. Reviewed exports may change gameplay.

## MSIX packaging and signing (0.20.0)

The new binary packaging path builds a self-contained x64 **MSIX bundle**. See
[MSIX/signing instructions](docs/MSIX_AND_SIGNING.md) for Windows build commands,
certificate configuration and the installation/upgrade checklist. Signed builds
require your real signing identity; no certificate or guaranteed Defender/Store
approval is supplied. Public native-binary publication is gated on signing and
the existing bundled dependency source/license review. PR CI uploads MSIX validation
reports rather than redistributing an unreviewed runtime.

The source workflow below remains available. Inno Setup is retained as a signed
fallback; explicit -Unsigned builds are labelled as development artifacts. MSIX
uses Windows-managed updates and does not run the source/Win32 updater.

## Start on Windows 10/11 x64

1. Close the old app. Extract the complete source package into a new writable folder.
2. Double-click **START_WINDOWS.cmd**. It checks Python 3.11 x64, installs missing
   requirements through the existing bootstrap, runs tests and launches. Internet
   is needed for initial setup. See [bootstrap details](docs/M5_6_WINDOWS_GUIDE.md).
3. On Home choose **Repair existing charts** or **Create challenging Medium**.
4. Choose a chart or a folder. Review each song, approve the changes and export.

For installation/upgrade use **Install GH3 Chart Studio.cmd** from an extracted
folder outside the installed app. Failed setup rolls back to the previous install;
previous/failed installations are retained. Logs: `start_windows.log`,
`startup_bootstrap.log`, and the installer logs.

## Choose what you want to do

| Goal | What it does | What it does not do |
| --- | --- | --- |
| Check charts — report only | Scan and list compatibility, audio, metadata and timing issues; save a scan report | Export or modify source files |
| Repair existing charts | Retain existing difficulty arrangements; propose compatibility repairs | Generate Easy/Medium or fill missing difficulty tracks |
| Create challenging Medium | Copy Expert or Hard to Medium, remove Orange and preserve surviving G/R/Y/B notes | Automatically replace Easy, fill Hard/Expert, or thin note density |

Use the goal selector in **Songs** to switch between these tasks. A folder scan is
recursive. A single `.chart`, `.mid` or `.midi` uses exactly the same review queue.
General instrumental MIDI is not automatically a guitar-game chart.

**Medium output must contain only Green, Red, Yellow and Blue. Orange is blocked.**
Removing Orange can remove entire note events; this is a challenging adaptation,
not a promise that every source attack survives.

## Optional changes are explicit

Expand **Optional changes** before scanning/reviewing. All these choices start off
in the main workflow:

- **Move Orange sustains to allowed frets:** transfers holds using repeatable
  placement, listed in the report. Orange taps are still removed. This is not
  musical-context remapping of every Orange note.
- **Also create / replace three-fret Easy:** replaces Easy from the selected source.
- **Fill missing Hard / Expert with source copies:** fills empty slots, without
  claiming a separately authored difficulty or reducing density.
- **Allow repairs to other difficulties:** allows compatibility edits outside the
  generated difficulties. Retained invalid tracks otherwise block export.
- **Allow listed sustain shortening / chord repairs:** permits hold-length changes
  required by the conservative GH3 profile. Review those changes before approving.
- **Remove Orange from existing Medium:** available in Repair mode. Without this
  approval an existing Medium containing Orange is blocked.

If removing Orange would leave Medium empty, the main workflow blocks instead of
inventing replacement notes. Some valid modern chart mechanics are unsupported by
this GH3 export profile; a blocker does not necessarily mean the source is corrupt.

Changing the goal or options rescans and clears unsaved review edits. Choose these
first, then correct metadata, preview, edit and approve.

## Review, listen and export

1. Read the **Selected song** page. Each difficulty shows unchanged, changed,
   created or not present, with before/after gem counts. Read the exact changes,
   warnings and blockers; counts alone do not describe gameplay.
2. Correct title/artist, audio matching or an ambiguous chart selection. Choose
   **Replace selected chart** to change the chart for a row.
3. **Preview / edit** opens one player with Original/Prepared comparison and a
   difficulty selector. Edit the prepared copy, then **Apply edits to review**.
   Approval is cleared. Export remains in the Songs queue. Blocked candidates can
   be inspected where parsing succeeded, but need repair choices/source correction
   before prepared editing. Edits are session-only until exported.
4. **Timing tools** previews stored Offset/delay and permits a reviewed override.
   The existing default uses `song.ini` delay, ignores chart Offset, and may add
   shared chart/audio lead-in. This is not automatic synchronization detection.
5. Approve the listed changes and **Export songs**. Check-only mode
   cannot export. Open results/logs for failures as well as successful outputs.

Output: an **Artist - Song Title** folder containing `notes.chart`, `song.ogg`,
`song.ini`, `validation.json` and `IMPORT_README.txt`. Recognized prior exports in
the selected output location are updated; originals cannot be used as output.
`cleanup.log` and `cleanup_summary.json` record each batch. Supported song/artist/
charter metadata and extra ini fields are retained; verify factual accuracy.

Separate audio streams are mixed into one full recording, with stream deduplication
and audio recovery checks. Vorbis reuse or re-encoding depends on metadata and
padding. Artwork and other instrument chart sections are omitted.

Forced-note intent is translated into TheGHOST flips; taps become HOPOs. Use
**TheGHOST HOPO measure 2.95** and verify in game. MIDI overlaps use a reported FIFO
repair policy; ambiguous original note pairing cannot be known with certainty.
Unterminated notes with no recoverable duration remain blocked.

## Advanced / experimental tools

These are outside the recommended Songs workflow:

- **Legacy single-song converter:** retained comparison/regression tools; its older
  conversion populates the full difficulty set and cleans all difficulties.
- **Advanced converter:** density/chord/movement controls and paired chart/MIDI
  export. MIDI export cannot preserve forced/tap modifiers and may be blocked.
  Legacy MIDI phrase interpretation is selectable here.
- **Audio drafting lab:** full-mix onset drafts, not verified guitar transcription.
- **Local pattern library:** pattern extraction, ratings and seeded variations.

A MIDI export from a generic music program is not necessarily a GH3 chart. Audio
experiments do not identify every guitar note. No controller recording is added.

## Verification and building

See [0.19.0 milestone and Windows checks](docs/M19_RELEASE.md),
[latest handoff](HANDOFF_LATEST.md), and [change history](CHANGELOG.md).
Automated checks establish structural behavior, not audible quality or Wii/Dolphin
acceptance. Native Windows CI and manual game acceptance are reported separately.

`build_windows.cmd` runs tests, collects licenses and builds the PyInstaller app;
keep the complete output directory. GitHub Actions tests on Windows and builds the
Inno Setup installer. See [Windows acceptance](docs/WINDOWS_TEST.md).

Credits: Nanook/TeamGHOST and the format-reference authors are acknowledged under
**About**, [credits](docs/CREDITS.md), `THIRD_PARTY.md` and `licenses/`.
No new external project code or dependency is introduced in 0.19.0.
