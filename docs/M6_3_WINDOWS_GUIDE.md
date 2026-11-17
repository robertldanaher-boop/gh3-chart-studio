# Version 0.6.3 — Cleaner selection and processing

1. Close the old application. Extract GH3_Chart_Studio_v0_6_3.zip into a new folder and double-click START_WINDOWS.cmd. Allow setup and automated tests to finish.
2. Choose Clean charts, then Choose folder to scan. Select one song folder or a parent directory containing song folders; scanning is recursive.
3. Click Select all ready. Clear selection unchecks everything. The count shows checked songs and songs needing correction.
4. Review the table and each song's cleanup details. Edit metadata where needed. Reopening the editor retains changes during this session; correcting a row preserves other selection choices.
5. Check Apply the reviewed cleanup changes, then click START CLEANING checked songs… in the fixed top area.
6. Choose a new output folder outside the scanned source tree. Wait for completion, then click Open results folder (after cleaning).
7. Inspect notes.chart, song.ogg, song.ini, validation.json and IMPORT_README.txt in each successful song folder, plus cleanup_summary.json. Test one song in your importer and Wii/Dolphin before a large collection.

Audio and song.ini are read from the chart's own folder. A valid chart audio reference, unique song.* match, or sole non-preview audio file can be matched automatically. A sole guitar.wav/guitar.ogg is now accepted with a warning to verify that it contains the full song. Multiple unidentified recordings require choosing the full mix; stems are not mixed automatically. Preview files are not used as the lone fallback recording.

Open results is intentionally disabled until a song has exported successfully. It is not the processing button. START CLEANING explains missing selection or review approval instead of silently remaining disabled.

Original files stay untouched. Manual metadata edits remain session-only until export. The existing conservative cleaner removes forced/tap/open-note markers, repairs reported sustain overlaps, and removes Orange from existing Medium; it does not generate missing difficulties. Other instruments, separate stems and artwork are omitted. Native Windows layout, audio playback and GH3 import/gameplay still require testing on your machine.

Automated verification: 214 passed in 21.54 seconds on Python 3.11/Linux with Qt offscreen; see M6_3_TEST_RESULTS.txt. This is a source package, not a verified Windows executable.
