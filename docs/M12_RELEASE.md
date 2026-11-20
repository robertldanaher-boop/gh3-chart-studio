# 0.12.0 — One conversion and cleanup workflow

## Functional changes

Make a challenging Medium now creates four-fret Medium and three-fret Easy, fills missing difficulty slots, then cleans ALL four output difficulties. Unsupported source markers/open-note events are removed; incompatible chord/overlapping sustains are shortened with exact changes reported. Valid Expert/Hard notes remain intact; those tracks now receive necessary repairs. Original inputs remain unchanged. Natural HOPO behavior can change when source markers are removed.

Single-song and collection conversion share the same cleanup implementation. Collection export validates all tracks. Single-song export review hides redundant marker/sustain cleanup toggles and displays automatic repairs. It also uses song.ini delay automatically with matching audio, recording leading silence once. Explicit optional HOPO assistance remains available after cleanup and is validated separately. Existing timing limits, anchor conflicts and unreadable audio remain blockers rather than guessed repairs. Clean songs remains useful for cleanup without replacing lower difficulties.

## Files changed

- gh3studio/difficulty_set.py: shared cleanup, anchor checks, repair reporting.
- gh3studio/cleaner.py: combined batch repair list and all-track export checks.
- gh3studio/song_export.py: automatic timing helper, combined export validation and accurate import instructions.
- gh3studio/song_export_gui.py and gui.py: automatic single-song preparation/review and report propagation.
- gh3studio/workspace.py and cleaner_gui.py: explain combined scope and approval.
- tests/test_difficulty_set.py, test_bulk_medium.py, test_gui.py: all-track repairs, original protection, one-pass export, delay/padding and GUI readiness.
- Version files, README, CHANGELOG, HANDOFF_LATEST and this release/test evidence.

## Tests and limitations

Full regression: 294 passed in 27.12s. Full results are in M12_TEST_RESULTS.txt. Linux/Python 3.11/Qt offscreen only; native Windows, TheGHOST and Dolphin confirmation remain required. The earlier test requiring manual marker cleanup was updated because the requested behavior now cleans automatically; its source-preservation and export assertions remain. No new dependencies or borrowed projects. Factual metadata accuracy still requires user review. Automatic cleanup cannot repair every malformed input or resolve contradictory tempo anchors safely.

## Windows testing

1. Close the old application. Extract GH3_Chart_Studio_v0_12_0.zip fully into a fresh application folder. Run START_WINDOWS.cmd inside GH3_Chart_Studio.
2. Choose Make a challenging Medium. Click Choose folder… and select a parent containing song folders, or choose an individual chart in One song mode.
3. For a collection, review rows and repairs, select songs, check Create Medium + Easy; clean all difficulties, and click Create Medium. Do NOT run Clean songs first.
4. For one song, select Expert or Hard, click Create Medium + Easy, compare the preview, and choose Review / export song. Choose matching audio if necessary. Automatic repairs appear in the review; separate cleanup toggles are hidden.
5. Export to your existing output parent outside the source tree. Check notes.chart, song.ogg, song.ini and validation.json. Repairs to Hard/Expert must be listed alongside target-track changes. Input files must remain unchanged.
6. Verify all four difficulties and synchronization in TheGHOST/Dolphin. Repeat export to the same parent to confirm existing recognized outputs update.

Next milestone: validate the combined workflow on a real Windows collection and verify repaired sustains, natural HOPOs, timing and difficulty selection in Dolphin.
