# Milestone 6 — Reviewed single-folder and collection cleanup

November 17, 2026

## Files

New: gh3studio/cleaner.py, gh3studio/cleaner_gui.py, tests/test_cleaner.py, docs/M6_WINDOWS_GUIDE.md, docs/M6_TEST_RESULTS.txt and this log.
Changed: gh3studio/gui.py, welcome.py, chartio.py, service.py, audio_export.py, song_export.py, __init__.py; tests/test_gui.py; pyproject.toml, README.md and HANDOFF_LATEST.md.

## Functionality

New Start goal and Clean charts tab, folder drag/drop, recursive collection scan, review queue, metadata editor/audio/chart selection, per-song error isolation, progress, cancellation between songs, atomic per-song folders, incremental collection summary and source fingerprint checks. Originals are unchanged. Export is refused inside the scanned source tree or into an existing collection folder.

Conservative guitar-only cleanup removes modifiers and repairs sustains across all included difficulties; no missing difficulties are invented. Medium Orange is removed with sustain transfer before reviewable repair. Unsupported .chart special phrases can be captured as removable events only in explicit cleanup mode; ordinary reader remains strict. Existing conversion export path remains separate. Clean export supports charts without Medium and reopens chart/audio/ini outputs. Vorbis metadata reconciliation reuses unchanged assets or re-encodes when tags differ.

## Verification

Full suite: 206 passed in 19.80 seconds on Linux/Qt offscreen; regression output is M6_TEST_RESULTS.txt. Added tests cover recursive two-song export with no generated Medium; source hashes; all-difficulty repairs and tempo preservation; missing metadata/audio correction; unsupported phrase removal and four-fret Medium; source changes, existing/nested output rejection; ambiguous charts; cancellation; offset/meter blocking; corrected Vorbis tags; GUI review/export and folder-drop routing. Offscreen 1024x700 UI inspected; export/review footer kept outside scrolling content. Startup/dependency bootstrap from v0.5.6 retained after restoring its release commit from the published package into the working checkout.

## Limits and next step

No actual Windows, Wii, TheGHOST or audio-device acceptance. Metadata truth must be verified by the user; optional missing fields are flagged. Conservative marker removal changes forced-HOPO behavior. Sustains can be shortened only as listed in review; onset/tempo unchanged. Invalid timing structures remain blocked. Guitar-only output excludes stems/artwork/other instruments. Collection cancellation waits for the current song. No new third-party dependencies or borrowed source code.

Next: native acceptance of one actual song and a small mixed collection; verify timing/metadata and cleanup gameplay before larger collections. Exact steps and edge cases: M6_WINDOWS_GUIDE.md.
