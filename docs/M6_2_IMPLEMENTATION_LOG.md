# Milestone 6.2 — Preserve metadata across failed chart rechecks

November 17, 2026

Cause: inspect_chart initialized an empty metadata record, then could fail before applying manual overrides. The GUI replaced its queue row with that empty result after OK. Malformed chart syntax and early offset/meter/no-note errors could therefore discard edits.

Files changed: gh3studio/cleaner.py (retain editable overrides before load; collect parsed identity/audio before later validation; restrict overrides to identity fields), gh3studio/cleaner_gui.py (apply edits immediately, refresh row/detail view and display explicit saved-review/error status; keep identity when replacing selected chart), tests/test_cleaner.py, tests/test_gui.py, version files, README.md, HANDOFF_LATEST.md and milestone docs/results.

Behavior: entered metadata survives parse and compatibility errors. Title/artist update in table; reopening dialog retains fields. Validation errors remain separate and block export. Identity overrides cannot restore obsolete timing/resolution metadata after the source is corrected. Originals remain unchanged. No persistent project format or automatic writeback to original song.ini was added.

Tests: 211 passed in 20.09 seconds on Linux/Qt offscreen; full output in M6_2_TEST_RESULTS.txt. Regression coverage includes malformed chart and nonzero-offset edits, repeated rechecks, actual GUI edit/OK/reopen with a broken chart, source unchanged, and corrected offset not overwritten by stale review metadata. Existing valid-row metadata/export checks retained. Native Windows and affected user's chart not available here.

Exact retest: M6_2_WINDOWS_GUIDE.md. Next: user's metadata edit/reopen/export acceptance; obtain remaining chart error if export is still blocked.
