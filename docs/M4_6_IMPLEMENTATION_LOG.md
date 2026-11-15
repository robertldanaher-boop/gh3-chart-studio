# Milestone 4.6 — startup visibility and repeated setup

November 14, 2026. Request: replace apparently frozen 1–3 console startup with live progress, ETA, elapsed timer, friendly messages and troubleshooting output.

Files changed/created:
- START_WINDOWS.cmd now bootstraps a standard-library Tk window, with a separate bootstrap log and actionable missing-Python/Tk message.
- tools/startup_windows.py provides three stages, estimated percentage/ETA, live elapsed/idle counters, random friendly message, streamed test/package logs, open-log action, cancellation of the child process tree, failure hold and verified application readiness.
- gh3studio/gui.py emits a startup-ready file after showing the window and entering the Qt event loop. No effect for normal direct launches without that environment variable.
- tests/test_startup.py covers estimates, history corruption, dependency fingerprint changes, cached/noncached setup paths, test failure blocking launch, and a real offscreen application readiness handshake.
- Version files, README, .gitignore, handoff, this log, Windows guide and test results updated.

Repeated startup optimization: reuse installed dependencies only when both the requirements-lock hash and the complete installed distribution/version snapshot match a prior successful installation and pip check. Still validate Python 3.11 x64 and run every automated test. New/modified environments invoke the hash-checked installer. Snapshot checks do not prove installed files are uncorrupted; tests remain the functional gate.

Measurement: previous script redirected every subprocess line, obscuring progress. It invoked pip each start and reran the complete suite. Those are observed design facts, not proof of the cause of Bob's slowdown. No user log from the slow run was supplied. Do not claim a measured Windows speedup yet.

Tests: docs/M4_6_TEST_RESULTS.txt. Linux/Python 3.11.18, Qt offscreen. Windows command execution/taskkill/Tk rendering, log-file opening and package installation are not exercised natively. Workflow unit tests substitute child processes; readiness integration starts the actual app. No Windows compilation or Wii compatibility claim.

ETA is explicitly estimated, based on prior successful stage durations (initial defaults otherwise). Test percentages use pytest output; setup/launch estimates are time-based and capped before completion. Overrun displays “taking longer than estimate” rather than a false countdown to completion. A real ready handshake is required for 100%. Launch has a 120-second readiness deadline; setup/tests can wait indefinitely with a live timer and cancellation.

Logs: current, previous, bootstrap; runtime stdout/stderr append to the current log. A single previous log retained. No monitoring of membership quotas and no Claude execution. Next milestone is native Windows first/repeat startup acceptance and measurement.
