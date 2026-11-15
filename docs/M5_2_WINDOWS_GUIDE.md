# Version 0.5.2 — First-run agreement

1. Close older instances. Extract the complete ZIP into a writable folder and run START_WINDOWS.cmd with Python 3.11 x64 installed.
2. After setup and tests, the first-run License & disclaimer window should appear. The startup progress window should finish; reading the notice has no time limit.
3. Choose Disagree and close (or close the window). The studio must not open.
4. Run START_WINDOWS.cmd again. Choose Agree and continue. The studio should open.
5. Close and restart. The prompt should not appear again. Acceptance is local to the Windows user, shared by source and packaged versions, and survives normal application updates. Other Windows accounts see their own first-run prompt. Clearing application settings causes it to appear again.
6. The notice remains available in About / credits → License & disclaimer.

This source distribution has no separate installer: the agreement appears on first application launch after setup/tests. It does not block dependency installation. Acceptance is stored using Qt user settings (on Windows, under HKEY_CURRENT_USER\Software\GH3ChartStudio\GH3ChartStudio, onboarding/license_notice_accepted). Do not edit settings unless intentionally testing a fresh user state.

If the notice cannot be loaded, Agree is disabled. Extract the full ZIP. If saving acceptance fails, an error is displayed and the studio stays closed. Preserve startup_bootstrap.log and start_windows.log for other startup failures.

Native Windows, PyInstaller, audio output and target-game tests remain pending. Other chart-based games may accept exports, but no blanket compatibility claim is made. Next: complete the one-song workflow in M5_WINDOWS_GUIDE.md and verify the selected target importer/game before batch work.
