# GH3 Chart Studio — 0.20.0 MSIX/signing handoff

Prepared November 25, 2026. Repository: robertldanaher-boop/gh3-chart-studio.
Branch/PR: workflow-consolidation / PR #1. Base: 1fdbaf1580c07e1efada0c95fbe297e2cac8ad03
(the verified 0.19.0 consolidation; 411 native Windows tests passed and Inno built).
Main remains the older baseline until the PR is merged. Do not overwrite newer work.

Read docs/MSIX_AND_SIGNING.md, docs/M20_TEST_RESULTS.txt and the latest PR Windows
result. Prior handoff is in docs/archive/HANDOFF_v0_19_0.md. Full source history is
in GitHub; no actual Claude assistance was used for this milestone.

## New functionality

- Self-contained PyInstaller onedir build via tools/freeze_app.py (no UPX), followed
  by packaging/build_msix.ps1: manifest/icons, 1,000-note frozen chart/MIDI read-back,
  native Ogg/FFmpeg/Qt/assets smoke checks, MakeAppx pack + bundle with validation,
  optional production signing and public JSON/inventory reports.
- installer/sign.ps1 signs using CurrentUser/My certificate thumbprint, SHA-256,
  RFC3161 timestamp; validates trust, exact signer and timestamp. No PFX password
  is placed on a process command line. No unsigned fallback on a signed build.
- Inno build now uses its internal SignTool hook for setup/self-copies, verifies the
  final EXE, and explicitly marks development unsigned output. build_windows.cmd
  signs its standalone EXE by default too. Keys are excluded from Git/payload.
- Protected-environment-ready CI release import/cleanup for a user-supplied PFX.
  Production publisher/credential setup is NOT completed. Modern hardware/cloud
  keys may need local/provider/self-hosted runner setup; hosted PFX isn't universal.
- MSIX API/marker detection, user-data working directory, native package taskbar
  identity, and source/Win32 update refusal. No self-replacement of WindowsApps.

## Release constraints — do not misstate

A production signing identity has not been provided, purchased or issued. MSIX
is not an antivirus bypass or Store approval. User's exact Defender warning remains
unknown. CI self-signed identities are isolated test roots only and never uploaded.

The old THIRD_PARTY.md / FFMPEG_DEPENDENCY.md explicitly require matching-source/
relinking/native license review before compiled redistribution. This milestone
builds engineering bundles in CI but uploads MSIX JSON reports only on PR runs.
Production publication requires signing plus GH3_BINARY_REDISTRIBUTION_REVIEWED=true
AFTER the distributor arranges those materials. A boolean is not legal certification.
Source-install fallback EXEs do not embed that self-contained runtime.

Windows SDK/MSIX/signing and frozen-binary build results must be taken from the
latest CI job, not inferred from Linux unit tests. Manual signed MSIX installation,
startup, upgrade, uninstall, audible playback and TheGHOST/Dolphin acceptance remain
separate. x64 only; no Store registration or .appinstaller feed is implemented.

## Files and tests

Changed/new: installer/windows_sdk.ps1, sign.ps1, import_ci_certificate.ps1,
build_installer.ps1/.cmd, GH3ChartStudio.iss; packaging/build_msix.ps1,
BUILD_MSIX.cmd, msix_manifest.py; tools/freeze_app.py; run_app.py;
gh3studio/package_runtime.py, package_check.py, gui.py, branding.py, updates_gui.py;
.github/workflows/windows.yml, build_windows.cmd, .gitignore, version files;
tests/test_msix.py, test_signing_windows.py; README/CHANGELOG/this handoff and docs.

Local Linux/Python 3.11.18 result: 414 passed, 8 skipped in 48.08 s.
Read the full executed local result in M20_TEST_RESULTS.txt; Windows-only tests
are explicitly skipped locally. Tests use real Windows tools/certificate APIs on
Windows. The CI signs test PE/MSIX fixtures and a signed Inno fixture, then rejects
a modified executable; its private key/root are removed in finally. Test fixtures
are not release artifacts. The main CI also freezes and exercises the actual app,
then packs the actual runtime bundle; do not equate structural packaging with
successful OS deployment.

## Next action

Finish the latest Windows CI; fix any actual build/signature failures before
claiming success. Configure a real signing identity through secure local Windows
certificate storage or GitHub environment secrets (never in chat). Complete the
native dependency redistribution review, then follow every Windows step in
MSIX_AND_SIGNING.md. Do not publish a release or merge the draft without the
necessary review/acceptance. Medium must always remain G/R/Y/B only.
