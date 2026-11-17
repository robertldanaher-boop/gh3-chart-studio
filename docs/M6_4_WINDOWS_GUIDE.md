# Milestone 6.4 — Direct cleaner start and explicit blocked songs

## Windows test steps
1. Close the old version and extract GH3_Chart_Studio_v0_6_4.zip to a new folder.
2. Double-click START_WINDOWS.cmd and wait for setup/tests/launch.
3. Choose Clean charts and scan the directory containing your song folders.
4. Click Select all. Every row is checked, including blocked rows. Select ready only remains available separately. The count shows checked/total and blocked counts.
5. Inspect BLOCKED reasons in the Review column (hover for the complete text) or select a row and scroll to its details. These errors are not bypassed.
6. Review the output parent shown above START CLEANING. It defaults to GH3 Cleaned Output beside the scanned folder. Change output folder is optional; it is the only control that opens an output-location picker.
7. Tick Apply the reviewed cleanup changes, then START CLEANING. This begins processing directly, with no folder picker. A timestamped results folder is created beneath the displayed parent.
8. Valid checked songs export; blocked checked songs receive failed entries with their exact reasons in cleanup_summary.json. See the completion counts and details. Open results folder is enabled when at least one song exports.
9. Verify chart/audio/metadata for one output song and import/play it in your target environment. If some songs remain blocked, provide cleanup_summary.json for diagnosis.

## Implementation and verification
Changed gh3studio/cleaner_gui.py: real Select all plus separate ready-only selection, visible error text/tooltips, editable output path and separate chooser, direct Start, synchronous output-tree validation, explicit clean-goal routing so errors/progress display even after entering the tab manually.
Changed gh3studio/cleaner.py: preserve actual validation errors in per-song export failures.
Changed tests/test_gui.py: direct Start must not invoke a folder picker; mixed valid/blocked selection exports valid songs and reports errors; unsafe output inside source tree gives an immediate message.
Changed version files, README.md, HANDOFF_LATEST.md and milestone docs.

215 tests passed in 22.38s on Python 3.11/Linux with Qt offscreen. Inspected 1024x700 screenshot. ZIP includes Git history and test output. Native Windows dialogs/filesystem, audio playback, TheGHOST and Wii/Dolphin execution not verified here.

The prior 44-of-54 behavior is explained by ready-only filtering; the actual 10 source errors have not been supplied. The prior folder picker was an output-selection step, not file processing. Exact failure after that step is not reproduced from the user's report; this release removes the step from Start and exposes destination errors before launching a worker.

No validation or musical cleanup rules were relaxed. Original files stay untouched. Blocked songs are not playable exports; their reasons need correction. Existing single-audio ambiguity/stem limitations remain. Next milestone: Windows test on this 54-song collection, diagnose remaining errors from cleanup_summary.json, then one-song target-game acceptance.
