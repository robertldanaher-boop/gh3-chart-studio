# Milestone 5.1 — License and disclaimer

Date: November 15, 2026

## Files and behavior

- gh3studio/welcome.py: tabbed About dialog with existing credits and a scrollable license/disclaimer, followed by the complete MIT License. Reads documentation from source or PyInstaller bundle; reports missing documentation explicitly.
- docs/LICENSE_AND_DISCLAIMER.md: warranty/liability limitations, content rights, synthetic fixtures, independence, compatibility limits and third-party licensing rights. No click-through agreement.
- build_windows.cmd: includes root LICENSE in the PyInstaller data alongside existing documentation.
- gh3studio/__init__.py and pyproject.toml: version 0.5.1.
- README.md, HANDOFF_LATEST.md and this milestone's guide/results: release documentation.

## Verification

- Existing automated suite: 177 passed in 17.45 seconds; full output in M5_1_TEST_RESULTS.txt.
- Manual Python verification: source document loading, simulated frozen bundle document loading, and rendered About dialog text/tab assertions passed.
- Offscreen screenshot visually inspected: readable, scrollable license tab and Close action.
- No gameplay, chart export, audio processing or startup agreement changes.

## Limits and next milestone

No native Windows build/runtime or Wii/importer verification was performed. Simulated frozen path loading does not establish a successful PyInstaller build. The release remains an unsigned source package. Notices do not guarantee legal enforceability, licensing compliance or acceptance by Windows protections.

Next milestone: one-song Windows audio-preview, source-preserving four-fret conversion and importer/game acceptance before adding batch workflows. Exact steps: M5_1_WINDOWS_GUIDE.md and M5_WINDOWS_GUIDE.md.
