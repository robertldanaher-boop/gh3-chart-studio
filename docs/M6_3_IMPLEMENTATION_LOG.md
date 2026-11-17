# Milestone 6.3 implementation log

Date: November 17, 2026

## Changes
- gh3studio/cleaner_gui.py: fixed top scan, bulk selection, selection count, review approval and START CLEANING controls; actionable readiness messages; preserve checkbox choices across metadata rechecks; enable results only after successful export.
- gh3studio/cleaner.py: automatically associate a sole non-preview audio file beside its chart, including instrument-named files, with a full-mix verification warning. Multiple unidentified files remain ambiguous.
- tests/test_cleaner.py: packaged guitar audio/preview discovery and ambiguous-stem regressions; update missing-audio fixture.
- tests/test_gui.py: ready-only bulk selection, clearing, small-window Start visibility and actual Start-to-export integration regression.
- gh3studio/__init__.py and pyproject.toml: 0.6.3.
- README.md, HANDOFF_LATEST.md and docs/M6_3_*: release, handoff and Windows acceptance instructions.

## Verification
Full suite: 214 passed in 21.54 seconds (Python 3.11, Linux, Qt offscreen). Screenshot inspected at 1024x700: top Start and bulk-selection controls visible. No native Windows, TheGHOST, Dolphin or Wii execution performed. Existing cleanup mechanics unchanged.

## Limits and next milestone
A single instrument-named recording may be an isolated stem; user must verify it is a full mix. No automatic stem mixing or persistent review projects. First validate one packaged song end-to-end on Windows and in the target importer/game, then a small recursive collection with missing/ambiguous assets. See M6_3_WINDOWS_GUIDE.md for exact steps.
