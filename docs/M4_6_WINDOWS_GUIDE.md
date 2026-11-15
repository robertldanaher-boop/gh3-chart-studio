# 0.4.6 — visible startup progress

1. Extract GH3_Chart_Studio_v0_4_6.zip into a new folder. Double-click START_WINDOWS.cmd. Keep Python 3.11 x64 installed with its standard Tcl/Tk component; no extra GUI package is needed to show startup progress.
2. A startup window displays steps 1–3 (setup, automated tests, application launch), a progress bar and estimated percentage, elapsed MM:SS, estimated remaining time, a randomly chosen friendly message, and live output. First-run ETA is approximate; later starts use the last successful run's step durations. The bar never reaches 100% solely because time passed.
3. During tests each test name/result appears. Watch the last-log-activity counter if progress slows. A test taking over 60 seconds prints diagnostic thread stacks; this is diagnostic output, not an automatic failure or skipped test. Wait or use Cancel startup to stop. No tests are bypassed to launch.
4. The startup window reaches 100% and closes only after the application window reports ready through its event loop. First-time setup can take much longer than subsequent launches. On repeat starts, an unchanged dependency lock and exact installed-package version snapshot skip the package installer. The full test suite still runs every time.
5. For a failure or unusually slow start, use Open troubleshooting log. Send start_windows.log and, if present, startup_bootstrap.log. The prior run is retained as start_windows.previous.log. A stopped startup remains visible for review. Application output continues into start_windows.log after the startup window closes. Avoid starting two copies simultaneously because these files are shared.
6. To compare performance, close the application and start it a second time. Look for “Dependency lock and installed versions unchanged” and compare logged step durations. Delete startup_timings.json only if you want to reset ETA history. Do not delete the test suite or bypass failed tests.

If no progress window opens, the console displays bootstrap diagnostics. Run py -0p to confirm Python 3.11. If Tcl/Tk is missing, modify the Python installation and enable it. Python 3.11.0 specifically is not required.

Acceptance checks on Windows: first install, unchanged second launch, live timer during tests, log opening, graceful cancel, failed tests stopping launch, and final window readiness. These native Windows checks are pending; automated workflow tests and an actual Qt readiness handshake passed on Linux. Current documentation does not establish the cause of Bob's reported longer load time without his startup log.

Recommended next milestone: capture Bob's first and second startup logs to measure the actual slow stage and optimize it without weakening test gates.
