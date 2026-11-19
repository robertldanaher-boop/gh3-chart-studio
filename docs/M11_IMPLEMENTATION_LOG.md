# Milestone 11 — Embedded collection workflow and output replacement

## Files changed

- Removed gh3studio/bulk_gui.py; updated workspace.py to host single/collection views in one stacked workspace with a mode selector. gui.py now handles embedded queue busy/error state. cleaner_gui.py uses stable output paths and a visible scrollable list region.
- Added gh3studio/output_replace.py: preserve unrelated extras, publish validated stage, restore previous folder on normal install failure.
- Updated song_identity.py to recognize prior export identity and reuse its path; cleaner.py accepts existing output parent and updates matched songs; song_export.py records source identity and supports controlled replacement. Updated gui.py/editor_gui.py to use the same replacement flow.
- Updated tests/test_bulk_medium.py for embedded GUI and tests/test_cleaner.py for the authorized rerun policy while retaining source-change rejection. Added tests/test_output_replace.py.
- Updated version files, README, CHANGELOG, HANDOFF_LATEST. Added this log, M11_WINDOWS_GUIDE.md and M11_TEST_RESULTS.txt.

## Implemented features

No bulk popup. Recursive collection selection and per-song repair controls stay in the main Four-fret workspace; single-song preview remains available through its mode. Reruns use the permanent output root. Prior exports are recognized by source path/report, including duplicate song names; invalid/unknown targets do not overwrite unrelated data. Existing managed song files replaced only after validation; logs append across runs, summary reflects latest run. Source tree remains protected.

## Tests / limitations

Focused replacement, bulk and focused-workspace tests passed (16). Full regression: 287 passed in 27.81s; results are in M11_TEST_RESULTS.txt. Main collection view visually checked at 1024×700. Native Windows/Dolphin test still required. Exact steps, recovery limits and next milestone are documented in M11_WINDOWS_GUIDE.md. No new dependencies or borrowed code.
