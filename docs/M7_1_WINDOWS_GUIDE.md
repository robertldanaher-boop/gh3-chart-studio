# Version 0.7.1 — Windows startup and layout retest

This fixes application layout constraints exposed by the five failed size checks
in 0.7.0. The reported run installed dependencies and ran the tests successfully;
it was blocked by GUI minimum widths, not a missing Python runtime. Reinstalling
Python is not needed for this error. No tests were bypassed or loosened.

## Install and launch
1. Close all older GH3 Chart Studio and startup windows.
2. Extract the complete GH3_Chart_Studio_v0_7_1.zip into a fresh writable folder,
   for example Desktop\GH3_Chart_Studio_0_7_1. Do not overlay an older folder or
   copy its .venv. Your original song folders can stay where they are.
3. Double-click START_WINDOWS.cmd. The same file checks the existing Python 3.11
   x64 runtime, installs pinned requirements as needed, runs the tests, and launches.
   Initial dependency download needs an internet connection. Let all three stages finish.
4. Confirm version 0.7.1 in the application header. The complete suite contains
   225 test cases; platform-specific tests can be skipped on Windows, but no
   failures are expected. Record the actual result rather than assuming our Linux
   result proves native Windows behavior.

## Check the affected interface
1. At your usual Windows display scale, reduce the application to roughly 1024x700.
   The automated startup checks enforce exact Qt logical dimensions; the Windows
   frame adds physical pixels around the client area. Brand/version may wrap.
2. Visit Home, Clean songs and Four-fret Medium. Start cleaning and Review / export
   song should remain accessible below the scrolling work area.
3. In Four-fret Medium, confirm Review source and Review Medium share the first
   footer row. Review / export song is in the second row; Open exported folder
   joins it after export. Buttons must have readable labels and be clickable.
4. Open each tool through Tools in reserve. Extra content may scroll, but a hidden
   tool must not force the entire window wider. Return to essentials when finished.
5. Follow M7_WINDOWS_GUIDE.md from Clean a song or collection onward, using this
   0.7.1 package. Export one known song to a new folder and confirm that all footer
   actions still fit after Open exported folder appears. Check song.ogg, notes.chart,
   song.ini and the validation report. Confirm Medium contains no Orange.

## If startup still fails
Keep start_windows.log and startup_bootstrap.log from this new folder. Failed size
assertions now add a JSON layout report showing the Qt version, platform, font,
DPI, minimum sizes and widest controls. Send the full failure section with those
logs and your Windows display scale. Do not edit the tests or remove the startup
test step to make the failure disappear.

## Evidence, limits and next milestone
225 passed in 23.83s on Python 3.11.18/Linux with Qt offscreen. The focused layout
selection passed 7 cases. New stress tests reproduced the old header failure with
160% font stretch and then passed with the fix, including 18px text and every
workspace. Inspected a 1024x700 screenshot with the wider/larger text and all four
Medium footer buttons shown. Logs are in M7_1_TEST_RESULTS.txt and
M7_1_REPRODUCTION.txt; the implementation log lists the changed files.

Native Windows, Windows audio devices, PyInstaller compilation, TheGHOST and
Wii/Dolphin gameplay are not tested here. Chart transformation and dependency
policies are unchanged. Existing compatibility limitations remain in README.md.
Next milestone is Windows acceptance, followed by one exported song in the actual
importer/game and diagnosis of the real collection's remaining blockers.
