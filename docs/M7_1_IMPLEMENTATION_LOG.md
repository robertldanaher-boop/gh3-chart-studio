# Milestone 7.1 implementation log — November 18, 2026

## Problem and functional fix
Windows startup correctly stopped after five GUI size assertions failed. The
reported widths were 1083px at normal text and 1208px at 18px text. The shared
single-row header combined branding, version and navigation minimum widths.
Using 160% font stretch on Linux reproduced the same failure class at 1049/1173px;
this is a text-metric stress test, not a native Windows reproduction.

Stacked, wrapping brand/version labels now share space with the navigation. The
Medium footer places its four review/export actions in two rows, keeping their
labels and full clickable areas visible after export as well. A read-only layout
diagnostic adds actionable evidence to any future failing size assertion. The
existing startup log captures it through pytest output.

## Files created or changed
- Changed gh3studio/gui.py: shared header layout and diagnostic entry point.
- Changed gh3studio/workspace.py: two-row Medium action grid.
- Added gh3studio/layout_debug.py: Qt/font/DPI/minimum-size/scroll diagnostics.
- Changed tests/test_focused_workspace.py: wider-font regression cases and diagnostic assertions.
- Changed tests/test_gui.py: diagnostics on existing size failures, same limits retained.
- Changed gh3studio/__init__.py and pyproject.toml: version 0.7.1.
- Updated README.md, HANDOFF_LATEST.md, CHANGELOG.md and docs/WINDOWS_TEST.md.
- Added this log, M7_1_WINDOWS_GUIDE.md, M7_1_TEST_RESULTS.txt,
  M7_1_REPRODUCTION.txt and screenshots/m7_1-wide-font.png.
- Release ZIP includes the versioned source, Git bundle and RELEASE_COMMIT.txt.

## Tests and results
The two new parameterized regression cases failed against the old header, proving
the stress scenario detects the bug; recorded in M7_1_REPRODUCTION.txt. After the
fix, the targeted layout selection passed 7 tests (39 deselected) in 2.42s.
Full suite: 225 passed in 23.83s. Environment: Python 3.11.18, PySide6 6.8.3,
Linux, QT_QPA_PLATFORM=offscreen. Full output is in M7_1_TEST_RESULTS.txt.

Tests visit all six workspaces with 160% font stretch, both normal and 18px text;
they check client width <=1024 and height <=700 and all four Medium footer buttons
fully visible with enough label width. The original strict 1024x700 and hidden
library checks remain. No tests were skipped or relaxed to pass this fix. The
startup full-suite gate remains unchanged. Visually inspected the 1024x700 stress
screenshot, including all post-export footer buttons. Chart, MIDI, Ogg, metadata,
sustain and four-fret Medium regressions are part of the passing complete suite.
A manual diagnostic smoke check parsed the report as valid JSON and confirmed
all eight named page/widget entries, row constraints and widest-widget details.

## Limits and exact Windows testing
No native Windows execution, Windows build, audio device or game test was possible
here. Offscreen tests cannot certify Windows DPI/font behavior. If a Windows
assertion fails again, its layout report will identify the actual local constraint.
No new dependency, borrowed project code, musical algorithm or export format was
introduced. Previously documented chart/import/game limitations are unchanged.

Follow M7_1_WINDOWS_GUIDE.md: close old processes, extract to a fresh folder, run
START_WINDOWS.cmd, confirm 0.7.1 and inspect essential/reserved pages and post-export
controls at the user's usual display scale. Keep full startup logs if anything fails.

## Recommended next milestone
Confirm this startup/layout fix on Bob's Windows computer, then accept one authored
song through cleanup/Medium export and TheGHOST/Wii. Use the actual scan/cleanup
report to diagnose the collection's blockers before expanding features. Prepared
an updated handoff; no Claude participation is claimed.
