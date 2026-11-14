# One-file Windows startup

Added START_WINDOWS.cmd; updated README.md. Delivered as a standalone add-on for
0.4.1: place beside run_app.py in the extracted app directory. No GUI/version changes.
Setup -> tests -> launch runs sequentially without intermediate pauses. It uses the
same Python 3.11 x64 check and hash-locked dependencies as setup_windows.cmd. Every
failing stage stops before later stages and prints the latest start_windows.log.
Qt's offscreen test setting is cleared before launch. Paths are quoted; pushd/popd
supports launches outside the app working directory. Originals are not modified.

Validation: reviewed CMD branch order, failure guards, environment restoration,
CRLF line endings and required-file checks against the existing three scripts.
No Windows command interpreter is available; no Windows execution test is claimed.
The unchanged Python GUI suite is not rerun for this launcher-only change.

Windows acceptance: copy the file next to run_app.py, double-click, expect stages
1/3, 2/3 and 3/3 followed by the GUI. Failure must leave a diagnostic window and log.
Next milestone: Windows acceptance of this launcher and the guided audio workflow.
