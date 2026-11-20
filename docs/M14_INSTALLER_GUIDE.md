# 0.14.0 — Installer, icon and updates

## For Bob: installing from the ZIP (0.14.1, no .exe needed)
1. Extract the whole ZIP.
2. Double-click "Install GH3 Chart Studio.cmd". If Windows asks about running a
   downloaded file, choose Run / More info -> Run anyway.
3. Click OK to install. A progress window runs setup and the tests once.
4. Done: Start menu -> GH3 Chart Studio (plus "- Repair" and "- Uninstall"),
   desktop icon, Settings -> Apps entry with Uninstall. You can delete the extracted ZIP folder afterwards.

## For Bob: installing with the setup .exe (from GitHub Actions)
1. Download GH3ChartStudio-Setup-<version>.exe from the GitHub release (or the
   Actions run's artifact).
2. Run it. Windows SmartScreen may say "Windows protected your PC" because the
   installer is not code-signed: choose More info -> Run anyway.
3. Click through: license, desktop icon option, Install.
4. Setup then installs Python 3.11 if needed, downloads the pinned libraries and
   runs every automated test once (several minutes the first time; a progress
   window shows each step). Internet is required for this step.
5. Finish -> "Open GH3 Chart Studio now". Afterwards use the Start menu entry or
   desktop icon; launches no longer run setup or tests.
If setup fails, the installer says so and names the log folder. Fix the cause
and run Start menu -> GH3 Chart Studio - Repair.

Upgrading: run the newer installer; it replaces the program files, keeps
unchanged dependencies and re-runs the tests once. Uninstall from Settings ->
Apps -> Installed apps.

## Updates
About -> Check for updates, and a quiet daily check. It reads the latest
published release of robertldanaher-boop/gh3-chart-studio. While that repository
is private, GitHub hides it and the check reports that it could not find a
public release (with a button to open the releases page in your browser, where
you are signed in). Making the repository public, or publishing installers to a
separate public repository and changing REPOSITORY in gh3studio/updates.py,
enables automatic notices.

## Building the installer
Automatic: .github/workflows/windows.yml on GitHub Actions (windows-latest):
pinned deps -> full pytest -> Inno Setup -> artifact; on a published release it
checks the tag equals the app version and attaches the installer.
Local: install Inno Setup 6.3+, run installer\build_installer.cmd.

## Layout
- installer/GH3ChartStudio.iss — script; fixed AppId (never change it).
- installer/wizard_*.bmp — wizard artwork from the logo.
- gh3studio/assets/app.ico, app_icon.png, logo.png — from Bob's image.
- gh3studio/branding.py — window icon + Windows AppUserModelID.
- gh3studio/updates.py (no Qt, tested offline), updates_gui.py (thread + queued slot).
- tools/startup_windows.py --install — set up and test once, write
  .venv/installed.json, exit 0/1 without launching.

## Limits / not verified
- Not code-signed (SmartScreen warning). Signing needs a certificate.
- Installer needs internet during setup (Python/libraries are downloaded,
  hash-checked). An offline installer would require bundling binaries (and
  FFmpeg GPL source obligations).
- Built and tested on Windows only through GitHub Actions or Bob's PC; the
  authoring environment had no Windows, Inno Setup or PySide6.


## Updates (0.18.0)
Publishing: for each version on main, create a GitHub release whose tag equals the
app version (v0.18.0, v0.18.1, ...). GitHub attaches "Source code (zip)"
automatically. If Bob attaches the GH3_Chart_Studio_vX_Y_Z.zip package to the
release, the app downloads that instead (0.18.1+). The repository must be public (or
releases must be published to a public repository and REPOSITORY in
gh3studio/updates.py changed) for installed copies to see releases.
In the app: About -> Check for updates, or the daily check -> Download and install.
