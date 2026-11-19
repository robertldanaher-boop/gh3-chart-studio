# 0.11.1 — Startup layout repair

## Diagnosis and implemented fix

The supplied Windows startup log reports 3 failed, 283 passed and 1 skipped in
58.60 seconds. All failures are large-text layout assertions: the window grew
to 1094 pixels instead of fitting 1024. The diagnostic tree identifies the
collection source-difficulty explanation with a 1008-pixel minimum width.
Its hidden stacked page imposed that minimum on the whole application.

The explanation now wraps. This fixes the contributing control rather than
changing the test limit, shrinking text or skipping startup checks. There are
no dependency, conversion, audio, metadata or output-replacement changes.

## Files created or changed

- gh3studio/cleaner_gui.py: named, wrapping source-difficulty explanation.
- tests/test_focused_workspace.py: two regression cases using long explanation
  text to reproduce wide font metrics independently of installed fonts. Checks
  hidden/visible collection pages, export controls and return to single-song view.
- gh3studio/__init__.py and pyproject.toml: version 0.11.1.
- README.md, CHANGELOG.md and HANDOFF_LATEST.md: release and handoff updates.
- docs/M11_1_RELEASE.md and docs/M11_1_TEST_RESULTS.txt: this log and test evidence.

## Tests performed

- Local reproduction before the fix: long unwrapped source explanation caused
  a 1103-pixel window with a requested width of 1024.
- Focused workspace suite: 12 passed in 3.23 seconds.
- Full suite: 289 passed in 26.51 seconds on Linux, Python 3.11.18,
  PySide6 6.8.3 with QT_QPA_PLATFORM=offscreen.
- An earlier combined GUI-only run was interrupted after stalling; it was not
  counted as a pass. The subsequent full suite completed, including those tests.
- ZIP integrity is checked during packaging. No Windows executable was compiled.

## Exact Windows test steps

1. Close the old GH3 Chart Studio application and startup window.
2. Extract GH3_Chart_Studio_v0_11_1.zip into a NEW application folder. Keep song
   sources and previous exported song folders where they are.
3. Double-click START_WINDOWS.cmd inside the extracted GH3_Chart_Studio folder.
   Let setup, tests and launch complete. First setup may need internet downloads.
4. Confirm the app opens. The full suite now collects 289 tests; a platform-specific
   skip may remain. There must be no failed tests. If it stops, send the new
   start_windows.log and startup_bootstrap.log.
5. Resize the app to approximately 1024 by 700. Check Home, Clean songs and
   Four-fret Medium. Repeat with your usual Windows display/text scaling.
6. In Four-fret Medium, switch between One song and Folder collection. Confirm
   the source explanation wraps, collection export controls remain visible, and
   returning to One song still shows Review / export song.
7. Scan a small collection, review it, select the existing output parent, and
   export. Run it again to verify recognized Artist - Song Title outputs update
   without new timestamped directories. Original input folders remain protected.

## Known limitations and next milestone

Native Windows font/rendering verification is pending; the uploaded log is
Windows evidence for the original defect, not proof of this fix on Windows.
No new TheGHOST, Wii or Dolphin validation was performed here. Existing
replacement/locking limitations are documented in M11_WINDOWS_GUIDE.md.
Next milestone: confirm startup and both collection views on Windows, then
verify repeat exports and all four difficulty slots in Dolphin.
