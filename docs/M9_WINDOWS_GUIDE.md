# 0.9.0 — Bulk four-fret Medium

1. Close the old app, extract GH3_Chart_Studio_v0_9_0.zip to a fresh folder, run START_WINDOWS.cmd.
2. Open **Four-fret Medium**, then **Bulk folder conversion…**.
3. Select **Expert then Hard** (Expert preferred, Hard fallback), **Expert**, or **Hard**. Keep **Preserve Orange sustains on four frets** enabled if desired. Changing either option after a scan rescans the original collection and resets the queue selection.
4. Click **Choose song folder…** and select the parent collection. Nested artist/album/song directories are scanned recursively (up to 2,000 song folders). Audio and song.ini are matched within each song folder. notes.chart is preferred over MIDI when available; ambiguous files are flagged.
5. Review songs, selected source and Medium changes. Use **Select all**, **Ready only**, individual checkboxes, or Clear. Search/filter does not limit Select all: selection applies to the whole queue. Missing required difficulty or audio is reported per song. Edit details or choose audio/chart for a flagged row when needed.
6. Set Save to outside the scanned tree. Tick **Replace Medium and apply its listed repairs**, then **Create Medium · N songs**. This starts processing without a second folder dialog. Progress is displayed and Cancel stops between songs; the active song may finish first.
7. Each successful song receives a new numbered Artist - Title folder containing notes.chart, song.ogg, song.ini and validation/import reports. The batch's cleanup.log and cleanup_summary.json list successful and failed songs. Click **Open results / logs**. Failures do not stop other songs.
8. Test one output in TheGHOST/Dolphin before importing the whole collection. Confirm Medium has no Orange, keeps the source rhythm, and retains useful sustains. Check both a source with Expert and a Hard-only song if using fallback.

## Behavior and limits

Bulk conversion copies selected authored Expert/Hard notes to Medium, removes Orange taps, optionally transfers Orange sustains reproducibly to suitable G/R/Y/B lanes (seed 0), then removes unsupported Medium markers and shortens incompatible Medium/chord sustains. Each repair is listed before approval and logged. Existing Medium is replaced in the OUTPUT copy only. No arbitrary note-density thinning or generated missing difficulties.

Expert/Hard/Easy notes/phrases are not cleaned by bulk conversion. Automatic song.ini delay normalization translates every track and tempo/event map together when needed, as in 0.8.1; synchronization itself preserves durations. Unrelated compatibility issues in retained tracks are not a promise of all-track game acceptance: Clean Songs remains the separate all-difficulty cleanup workflow.

Original chart/audio/metadata files remain untouched. Output must be outside source, and existing folders are never overwritten. Cancelled scans may show a partial queue. Cancel is cooperative between songs, not immediate during audio encoding. Conversion exports .chart, not a paired MIDI. Single full-mix audio only: separate guitar/backing stem preservation is still not implemented.

Native Windows/Dolphin testing of this release is pending. Next milestone: validate a real nested collection and tune per-song review based on results; paired-stem support remains separate work.
