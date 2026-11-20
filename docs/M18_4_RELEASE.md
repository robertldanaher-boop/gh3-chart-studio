# v0.18.4 — Update recovery and shared audio streams

## Changes
- `installer/transaction.ps1` (new), `installer/install.ps1`: stage the payload, exclusively lock installation, retain the whole previous folder, create the new environment at its final path, restore the previous folder if setup/tests fail. Failed files/logs remain in a sibling `.failed-*` folder. Successful upgrades retain `.previous-*` for manual cleanup after acceptance.
- `installer/GH3ChartStudio.iss`: compiled setup delegates to the same script transaction. Script owns shortcuts/uninstall registration; Inno only stages the payload and presents the installer UI.
- `gh3studio/updates_gui.py`: modal download, completion-time busy/cancel checks, respect rejected window close.
- `gh3studio/stems.py`: one physical recording per mix across roles, hard links included; report excluded roles. Separate files with identical bytes are still separate recordings.
- `tests/test_installer_transaction.py` (new), `tests/test_updates.py`, `tests/test_stems.py`: regression coverage.
- Version and documentation: `gh3studio/__init__.py`, `pyproject.toml`, `README.md`, `CHANGELOG.md`, `HANDOFF_LATEST.md`, this file, `docs/IMPLEMENTATION_LOG.md`.

## Verification
Baseline 0.18.3: 368 tests passed. Final 0.18.4 Linux run: **379 passed in 41.57s**, Python 3.11.18, actual PySide6 6.8.3/SoundFile/Mido/FFmpeg dependencies, PowerShell 7.4.6. No stubs. Transaction tests exercise new installs/upgrades, success and deliberately failed validation, original environment/user-file restoration and preservation of diagnostic logs. Parser test checks both PowerShell scripts. Audio integration verifies expected sample amplitude when two roles reference the same recording.

Command (PowerShell must be on PATH for transaction tests):

```sh
QT_QPA_PLATFORM=offscreen GH3_NO_UPDATE_CHECK=1 python -m pytest -q -o faulthandler_timeout=60
```

Windows CI is requested by the GitHub push. Native Windows installer UI, cancellation/recovery on a physical Windows system, compiled installer execution and Dolphin gameplay are not verified by the Linux test run. Do not call these checks complete without their actual results.

## Windows acceptance steps
1. Close GH3 Chart Studio. Extract the entire v0.18.4 ZIP into a new folder outside the installed program folder.
2. Run `Install GH3 Chart Studio.cmd`. Let dependency installation and all tests finish. A new environment is intentional: the previous environment is retained for recovery.
3. Confirm the app opens as 0.18.4. Scan/export one song, then a second collection; verify both populate correctly. Confirm Medium contains only Green/Red/Yellow/Blue and Easy only Green/Red/Yellow; Expert/Hard remain available.
4. For an isolated installer regression run, open Command Prompt in the extracted folder and run `.venv\Scripts\python.exe -m pytest -q tests\test_installer_transaction.py tests\test_updates.py tests\test_stems.py` after `START_WINDOWS.cmd` has created that folder's environment. These transaction tests use temporary directories, not your installed app.
5. To build the compiled installer, install Inno Setup 6.3+ and run `installer\build_installer.cmd`; test the produced EXE in a Windows test account. It must use the same transaction and launch only after tests pass.
6. Failed setup must report recovery status and a `.failed-*` folder containing logs. The original installed app should launch again. Successful update retains a `.previous-*` folder beside the installed folder; remove it only after confirming the update works. Do not launch a Python environment from the backup path (it contains absolute original paths).
7. Import an exported song through TheGHOST and play in Dolphin. Confirm full mix, sync, sustains and difficulty selection. This release changes no chart conversion or gameplay mechanics.

## Limits and next milestone
- Sudden power loss or forced termination during folder switching is not automatically recovered; the previous folder remains available. Disk space must cover both installations. A Windows file lock can prevent restoration; the error then identifies both recovery paths.
- Setup/test failures roll back; failures while creating shortcuts/registration after successful validation leave the tested app and retained backup, and report an error.
- Start-menu Repair (START_WINDOWS.cmd --install) remains an in-place dependency repair; it is not the update transaction. Use a freshly extracted ZIP outside the install folder for upgrades.
- Installer backups are intentionally not deleted automatically. Qt jobs cannot be interrupted by update completion, but downloaded temporary payload cleanup remains future housekeeping.
- Next milestone: Windows installer upgrade/rollback acceptance and compiled installer smoke test, followed by Bob's single-song Dolphin check. No new chart/audio-generation features in this release.
