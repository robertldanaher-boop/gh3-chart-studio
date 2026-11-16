# 0.5.6 — Automatic first-run dependency setup

## Normal use

1. Extract the complete ZIP into a writable folder. Close older copies.
2. Double-click START_WINDOWS.cmd. It first checks Python 3.11 x64, Tk, venv and ensurepip using the local environment, current-user standard Python location, system standard location, then the Python launcher if available.
3. If a usable runtime is absent, the console downloads the official Python installer, verifies its Authenticode status and Python Software Foundation publisher, and opens its passive progress UI. The installation includes pip and Tcl/Tk for the current user. It does not replace Python 3.13, change PATH, request elevation or disable Windows protections.
4. Once the runtime passes the same probe, the startup GUI creates the app environment, restores pip if missing, installs pinned hash-verified packages when needed, runs tests and launches the app. Internet is needed for missing downloads. Later runs reuse the verified package snapshot when unchanged.
5. First application launch still presents Agree / Disagree. Runtime and dependency installation precede that application notice.

## Windows acceptance matrix — not yet executed here

- Existing Python 3.11 x64 with working Tk: verify no runtime download and successful setup.
- Windows account with only Python 3.13 or no Python: verify download, signature check, per-user installation, then setup/test/launch without a manual Python command.
- Standard per-user Python 3.11 but missing py launcher: verify direct discovery.
- Fresh extracted folder: verify automatic .venv/dependency installation. Repeat launch: verify unchanged dependencies are reused.
- Network disconnected before a required download: verify visible error, retained log, no launch or partial installer execution.
- Signature verification fails: installer must not execute. No verification bypass is offered.
- Older/mismatched copied .venv: startup may stop with an explicit environment version error; use a newly extracted folder rather than copying old environments.

Logs: startup_bootstrap.log, python_install.log (and installer component logs if generated), start_windows.log. The temporary installer is deleted after success or failure. A restart-required exit stops setup and asks for a restart. If an existing newer 3.11 installation lacks Tk or is damaged, the fallback installer can reject a downgrade; repair using the matching Python installer instead. This is not automatic repair of every possible Python installation.

## Runtime choice and limits

Fallback is python.org's signed Python 3.11.9 x64 traditional installer. It is the final traditional 3.11 Windows installer, not the latest 3.11 security release. Existing newer usable 3.11 runtimes are reused. This fallback is pinned for reproducibility and must be revisited as the supported runtime/build strategy evolves.

Official references: https://www.python.org/downloads/release/python-3119/ and https://docs.python.org/3.11/using/windows.html#installing-without-ui

No native Windows installer execution, Authenticode acceptance or clean-machine setup was tested in the Linux environment. Next milestone: clean Windows setup acceptance, then one-song preview/export/gameplay.
