# 0.11.2 — Collection help height repair

## Changes and files

Updated gh3studio/cleaner_gui.py: move the source explanation, source dropdown and sustain option into scroll content. Give the wrapped explanation Minimum vertical size policy to prevent compression. Export controls remain outside the scroll area. This avoids both clipped explanation text and increasing the minimum window height. No chart, audio, metadata or replacement behavior changes.

Updated version files gh3studio/__init__.py and pyproject.toml, README.md, CHANGELOG.md, HANDOFF_LATEST.md. Added this release log and M11_2_TEST_RESULTS.txt. Existing regression assertions remain unchanged.

## Tests and limitations

Focused workspace tests: 12 passed in 2.99s. Full suite: 289 passed in 26.73s on Linux/Python 3.11.18/Qt offscreen. Full results in M11_2_TEST_RESULTS.txt. Initial policy-only fix failed the window-height test; moving the controls into scroll content resolved that failure. Native Windows and Dolphin execution not available here. The user Windows log proves v0.11.1 width checks passed but the long-label height check failed (57 vs 81 pixels).

## Windows verification

1. Close the application and startup window.
2. Extract GH3_Chart_Studio_v0_11_2.zip into a fresh application folder.
3. Run START_WINDOWS.cmd inside GH3_Chart_Studio. Tests must finish without failures; a platform-specific skip may remain.
4. Open Four-fret Medium, choose Folder collection. Source settings are now inside the scroll area below the numbered steps. Scroll to reach the song queue and review controls.
5. Resize to approximately 1024 by 700. Verify source help is readable and Save to / conversion controls stay visible at the bottom. Switch back to One song and check its export controls.
6. If startup fails, send start_windows.log. Do not disable the failing test.

Next milestone: native Windows layout confirmation, then a small collection exported twice to the same output parent and all four difficulties checked in Dolphin. Existing output replacement limitations remain in M11_WINDOWS_GUIDE.md.
