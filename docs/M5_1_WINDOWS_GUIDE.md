# Version 0.5.1 Windows verification

1. Close older copies of GH3 Chart Studio. Extract the complete ZIP into a new writable folder.
2. Confirm Python 3.11 x64 is installed with `py -3.11 --version`.
3. Double-click START_WINDOWS.cmd. Allow setup and automated tests to finish, then the application opens. First setup needs internet.
4. Select About / credits, then License & disclaimer. Confirm the notice scrolls to the full MIT License, including Robert Danaher's copyright notice. Check Credits remains available.
5. Close the dialog and confirm the current song and selected difficulty remain available. No license acceptance prompt should appear at startup.
6. For gameplay acceptance, follow M5_WINDOWS_GUIDE.md with one song. Check surviving Green/Red/Yellow/Blue notes against the selected Hard or Expert source, review metadata and export, then verify in the intended importer/game.

Troubleshooting: preserve startup_bootstrap.log and start_windows.log. Close all older app instances before retrying. Do not disable Windows protections.

This release was tested on Linux with Qt offscreen. Native Windows startup, PyInstaller output, audio hardware and Wii/TheGHOST execution were not tested here. The notice is not legal advice or a guarantee of enforceability. Public distribution requires review of the licenses and actual distributed components.
