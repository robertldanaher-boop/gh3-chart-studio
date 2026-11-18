# Milestone 8 — Direct chart editor, 0.8.0

## Functional changes

Independent, transactional working copy; per-difficulty edits; snapped note insertion, move/delete; chord-consistent sustain resizing; star-power add/remove; TheGHOST 2.95 HOPO/strum/natural actions; editable pattern presets; drag feedback; exact Undo/Redo; audio-clock navigation; discard warning; background export to new complete song folder. No Medium Orange and no silent overlap repair. Source recording/chart untouched. Export validates all difficulties without inventing Medium and retains approved HOPO flip markers. Existing cleaner behavior unchanged.

## Files

Created gh3studio/chart_editor.py (edit engine), gh3studio/editor_gui.py (interactive preview/dialog), tests/test_chart_editor.py, docs/M8_WINDOWS_GUIDE.md, docs/M8_IMPLEMENTATION_LOG.md, docs/M8_TEST_RESULTS.txt.
Changed gh3studio/playback.py (entry points), gh3studio/song_export.py (editor-specific validation and folder export), gh3studio/__init__.py and pyproject.toml (version), README.md, CHANGELOG.md, HANDOFF_LATEST.md. Git bundle/release commit included in package. No new dependencies or borrowed code.

## Verification

Five new tests cover immutable source and untouched tracks/tempo, exact undo/redo, transactional rejection of Orange/duplicates/overlaps, chord lengths, overlapping star power, pattern insertion, HOPO/strum states and orphan cleanup, .chart/OGG/INI round-trip including Expert-only output, and Qt mouse-based note/sustain drags plus difficulty switching. Full regression: 268 passed in 24.04s; output is M8_TEST_RESULTS.txt. Editor screenshot also visually inspected at 960×680. Existing strict window-size checks retained. Linux Python 3.11, Qt offscreen; no native Windows binary built or executed.

User reports 0.7.3 tested and playing in Dolphin (November 18, 2026). New editor mechanics still need separate Windows/Dolphin acceptance. Full steps, limitations and next milestone: M8_WINDOWS_GUIDE.md.
