# Version 0.4.3 — Windows path comparison regression

User evidence: START_WINDOWS.cmd successfully installed pinned dependencies on
Windows and ran the suite: 127 passed, 1 failed, 1 skipped. The failed assertion
compared two strings naming the same original audio file: Qt returned forward
slashes and pathlib returned backslashes. No evidence of an incorrect playback
source or installation failure appeared in this log. The skip reason was not shown.

Changed tests/test_gui.py to compare resolved Path objects instead of raw strings.
It still verifies that original-mix playback is retained when a different stem is
analyzed. No test was disabled, weakened to accept a different file, or newly skipped.
Updated version metadata, README, current Windows guide and Claude handoff.
App analysis/conversion/playback and startup-gate code are unchanged.

Verification: the exact reported strings compare equal as PureWindowsPath objects,
while a different stem path compares unequal. Full local regression results are
in M4_3_TEST_RESULTS.txt. This is not a claim of native Windows execution here;
the corrected Windows run is pending user confirmation.

Windows: extract GH3_Chart_Studio_v0_4_3.zip into a new folder and double-click
START_WINDOWS.cmd. It should complete tests and reach stage 3/3 to open the app.
If it stops again, send the failure section of start_windows.log. No Python reinstall
is needed. Obsolete separate startup scripts remain removed.

Next milestone: confirm corrected Windows startup, then resume GUI/song acceptance.
