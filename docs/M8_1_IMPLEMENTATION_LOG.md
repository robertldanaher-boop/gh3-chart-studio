# Milestone 8.1 — Automatic stored-delay policy

Changed gh3studio/cleaner.py: normalize nonzero Offset/delay automatically using song.ini delay only when no manual override exists. Record automatic flag, exact chosen policy and source values in synchronization report. Missing delay is zero. Reuse existing padding/tempo-preserving implementation and export logs.

Changed gh3studio/cleaner_gui.py: label automatic timing in song details; retain manual tool as Timing tools (optional), with explanatory helper text. Changed gh3studio/sync_gui.py: manual tool opens with the automatic interpretation selected for comparison; it remains an explicit override workflow.

Updated tests/test_sync_gui.py (automatic export without dialog and optional manual override), tests/test_synchronization.py (seven additional cases and default-policy assertion) and tests/test_cleaner.py (replace obsolete offset-block assertion; preserve metadata-error test using unrelated meter failure). Updated version in gh3studio/__init__.py and pyproject.toml, README.md, CHANGELOG.md, HANDOFF_LATEST.md. Added this log, M8_1_WINDOWS_GUIDE.md and M8_1_TEST_RESULTS.txt. No dependency changes.

Focused synchronization/cleaner tests: 46 passed in 0.54s. Full regression: 276 passed in 25.15s, recorded in M8_1_TEST_RESULTS.txt. Source-preservation/export timing covered with synthetic fixtures; actual Windows/game acceptance pending. Exact Windows steps, limitations and next milestone are in M8_1_WINDOWS_GUIDE.md.
