# Milestone 9 — Recursive bulk Medium conversion

## Files / features

Added gh3studio/bulk_gui.py: modal bulk queue reached from Four-fret Medium; reuses existing song queue, selection, metadata edits, output controls, worker progress and logs. Added tests/test_bulk_medium.py, this log, M9_WINDOWS_GUIDE.md and M9_TEST_RESULTS.txt.

Changed gh3studio/workspace.py: Bulk folder conversion entry point. Changed gh3studio/cleaner_gui.py: optional four-fret queue configuration, source/fallback and sustain controls, recursive scan settings, recheck propagation. Changed gh3studio/cleaner.py: optional Medium conversion inspection, selected source/fallback, per-song export mode and logged conversion report. Standard Clean Songs behavior remains separate. Changed version files gh3studio/__init__.py and pyproject.toml plus README, CHANGELOG, HANDOFF_LATEST. Git bundle supplied. No new dependencies.

Source tracks stay unchanged except shared synchronization translation. Only Medium receives conversion/compatibility repairs. New output folders include metadata and Ogg audio. Failures are per-song; cancellation and source hash guards reuse existing behavior.

## Testing / limitations

Focused tests: 15 passed (new bulk and existing cleaner). New tests cover recursive nested collections, Expert-to-Hard fallback, explicit missing-source rejection, four-fret output, sustain transfer, unchanged other tracks and source file hashes, partial failure continuation, audio/metadata folder output, cancellation/output-tree protection, and GUI scan/selection/export without mutating the single-song workspace. Full regression: 279 passed in 26.08s; results in M9_TEST_RESULTS.txt. Linux Python3.11/Qt offscreen; no Windows build/game execution claimed.

Exact Windows steps, limitations and recommended next milestone are in M9_WINDOWS_GUIDE.md.
