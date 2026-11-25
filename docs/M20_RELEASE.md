# Milestone 20 — MSIX bundle and Authenticode signing

Primary usage/build/configuration and exact Windows acceptance steps are in
MSIX_AND_SIGNING.md. This milestone builds on the unmerged workflow-consolidation
PR (#1), preserving the verified 0.19.0 work and its history. Version: 0.20.0.

## Implemented files/features

- packaging/build_msix.ps1, BUILD_MSIX.cmd, msix_manifest.py: self-contained x64
  desktop payload, generated package identity/icons, MakeAppx pack/bundle with
  validation, signed-release/explicit-unsigned paths, runtime smoke and JSON inventory.
- installer/windows_sdk.ps1, sign.ps1: SDK discovery, explicit certificate identity,
  SHA-256/RFC3161 signing, trust/timestamp/expected-signer verification, public reports.
- installer/build_installer.ps1/.cmd and GH3ChartStudio.iss: Inno internal signing
  hook and final verification. Direct anonymous builds require explicit unsigned
  selection; development filenames are marked. PFX/key patterns excluded.
- installer/import_ci_certificate.ps1 and .github/workflows/windows.yml: secure
  environment-based import, expected thumbprint, cleanup, native signing tests,
  MSIX frozen app/SDK validation, release gates and validation-only PR MSIX artifacts.
- tools/freeze_app.py and build_windows.cmd: common onedir/no-UPX build; explicit
  default signing for the standalone developer EXE too. Existing requirements reused.
- run_app.py and gh3studio/package_check.py: actual frozen executable self-test for
  Qt/assets, 1,000-note paired chart/MIDI output, Ogg encoding and native FFmpeg.
- gh3studio/package_runtime.py, gui.py, branding.py, updates_gui.py: MSIX identity
  detection, user-data working directory, package taskbar identity and refusal to
  run the source/Win32 updater inside a Windows-managed package.
- tests/test_msix.py and test_signing_windows.py: manifest/asset/identity and updater
  tests; real Windows SDK signing, timestamps, tamper rejection, PFX import, signed
  Inno hook and MSIX pack/bundle tests using isolated temporary test identities.
- Version files, README, CHANGELOG, handoff, .gitignore and these milestone docs.
  Previous handoff retained in docs/archive/HANDOFF_v0_19_0.md.

## Executed verification

Local Linux/Python 3.11.18: 414 passed, 8 skipped in 48.08 s with real dependencies.
Five skips need PowerShell; three new integration checks need Windows SDK and the
Windows certificate store. Full output: M20_TEST_RESULTS.txt. A source-mode smoke
run also passed chart/MIDI read-back, Ogg, FFmpeg and Qt/assets; this is not evidence
for a frozen Windows executable. The latest PR Windows result is authoritative for
native signing, compilation, frozen execution and MakeAppx validation.

No production signing credential exists in this checkout or was created by this
work. Native tests use a temporary self-signed identity trusted only inside the
isolated runner, remove it afterwards and never upload it. Test signatures do not
establish Bob's publicly verified publisher identity.

## Limits and next milestone

Signed MSIX sideload/upgrade/uninstall and public publisher trust remain acceptance
steps after identity configuration. No Store publication or .appinstaller feed.
The MSIX is x64 only. Signing cannot guarantee all Defender/reputation outcomes.

Existing Qt/FFmpeg corresponding-source and native license/relinking obligations
are a known prerequisite for compiled redistribution. CI builds the engineering
runtime for validation but uploads MSIX reports only on PRs. Production publication
requires real signing plus a completed source/license review. Do not represent a
review variable or build success as a compliance certification.

No music/chart algorithms changed. Medium must remain Green/Red/Yellow/Blue only;
previous preservation/compatibility regression tests remain enabled. Source and
classic installs remain available, and are not automatically removed or migrated.

Next: finish Windows build/signature checks, configure a real identity securely,
arrange native corresponding-source materials, then execute the signed-MSIX clean
VM installation/upgrade/uninstall and one-song TheGHOST/Dolphin tests listed in
MSIX_AND_SIGNING.md. Keep the PR unmerged/unpublished until accepted.
