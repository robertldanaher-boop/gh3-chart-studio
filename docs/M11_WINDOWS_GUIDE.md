# 0.11.0 — One workspace and reusable output folders

## Windows steps

1. Close the previous version. Extract GH3_Chart_Studio_v0_11_0.zip into a fresh application folder and run START_WINDOWS.cmd.
2. Open **Four-fret Medium**. At the top, choose **One song · preview and edit** or **Folder collection · convert selected songs**. Both views remain in the main window. The old bulk popup/module has been removed.
3. For a collection, choose the source policy and folder, review the list, select songs and approve conversion. The song list/details are scrollable on smaller screens; the export controls stay below the scroll area.
4. Set **Save to** to the permanent OUTPUT parent you want to reuse. It must remain outside the scanned source tree. If migrating from a previous timestamped batch, choose that existing run folder itself (the folder directly containing Artist - Song Title folders).
5. Click Create Medium. Song folders are created directly inside Save to, without a new timestamped run directory.
6. Run the same sources again with changed conversion settings. Confirm the same Artist - Song Title folders are updated instead of growing new copies. Existing generated notes.chart, song.ogg, song.ini, validation.json and import instructions are replaced together. An old notes.mid is removed to avoid a stale chart alternative. Unrelated artwork/user files are retained.
7. Open results/logs. cleanup.log appends runs; cleanup_summary.json shows the latest run. Verify a failed song retains its previously successful output. Single-song and editor exports also reuse recognized destinations when the same parent/source is selected.
8. Test the refreshed songs in TheGHOST/Dolphin. Existing Medium four-fret, Easy three-fret and completed-difficulty behavior is unchanged.

## Identity and replacement behavior

Prior exports are matched by source chart path recorded in validation.json (or source_hashes in older batch reports). Same-title different-source songs retain separate (2)/(3) names, and reruns find the correct folder even when selection order changes. Unknown folders without a matching report are not presumed to be ours: they receive a separate name. Changing the source path or song identity may also create a different destination. This prevents unrelated songs from being overwritten solely because their titles match.

Original input folders remain separate. Exporting directly over the input chart/audio folder is rejected. This release overwrites recognized PRIOR OUTPUTS, not the source library. It does not rename or consolidate all historical run directories automatically.

Audio and chart are fully written and checked in a staging folder before replacement. Existing output is temporarily renamed, then the validated stage is installed; if installation fails, the previous directory is restored. A Windows file lock may cause a failed replacement, or leave a .gh3-backup directory if cleanup after successful replacement cannot remove it. Such leftovers are not another intentional song export. This is rollback for normal errors, not a guarantee against power loss/filesystem failure. Cancellation remains between songs.

## Validation / next milestone

Linux Python 3.11/Qt offscreen tests include repeated output updates, duplicate identities with reversed selection order, artwork preservation/stale MIDI removal, simulated install failure with rollback, decode failure preserving prior export, source-change guards and embedded-queue GUI workflows. Native Windows locks and Dolphin acceptance remain pending. Full results in M11_TEST_RESULTS.txt.

Next: run a small collection twice on Windows and confirm folder count stays stable and the refreshed songs import correctly.
