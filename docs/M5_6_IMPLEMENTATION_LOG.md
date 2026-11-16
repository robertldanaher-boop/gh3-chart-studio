# Milestone 5.6 — First-run runtime and dependency setup

November 16, 2026

Files changed: START_WINDOWS.cmd (runtime discovery, usable-Tk probe and automatic installer handoff); tools/install_python_windows.cmd (new signed runtime download and passive per-user installer); tools/startup_windows.py (restore missing pip before dependency validation); tests/test_startup.py (pip-present/missing cases); gh3studio/__init__.py and pyproject.toml (0.5.6); README.md, HANDOFF_LATEST.md and milestone guide/log/results.

Functional changes: finds Python without requiring py launcher, checks 3.11/x64/Tk/venv/ensurepip, downloads official fallback only if no usable runtime is found, requires valid PSF Authenticode before execution, installs pip/Tk for current user, reprobes before proceeding. Existing pinned hash-verified app package installation and cache stay in place; missing pip is restored with ensurepip. Test failure still prevents launch. Download/installer failures produce diagnostics instead of mislabeling all errors as missing Tcl/Tk. No execution policy, antivirus, PATH or administrator escalation changes.

Validation: fresh complete application regression run passed all 197 tests in 22.11 seconds (M5_6_TEST_RESULTS.txt). Startup-worker tests now cover both cached/fresh setup with pip present/missing and verify ensurepip is only used when needed. First run of tests exposed old process mocks that did not handle the new pip probe; mocks were updated before final validation. A subsequent suite attempt stalled in the existing external-stem audio GUI test and was interrupted; its trace is retained in M5_6_INTERRUPTED_TEST_RUN.txt. A fresh complete run is recorded separately. Windows CMD/PowerShell scripts reviewed against official Python installer documentation; native execution and signature validation cannot be tested in this Linux environment. Do not report clean-machine Windows acceptance as completed.

Dependencies unchanged. Fallback Python 3.11.9 is the last traditional 3.11 Windows installer, not the latest security release; existing usable newer 3.11 is retained. Broken newer installations can require manual repair using their matching installer; no downgrade workaround. Internet required for downloads. See M5_6_WINDOWS_GUIDE.md for exact Windows use, failure paths and acceptance matrix.

Next milestone: Windows account with only 3.13 or no Python successfully completes automatic runtime installation, dependency setup, tests and launch; then one-song gameplay acceptance.
