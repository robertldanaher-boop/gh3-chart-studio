# 0.9.1 — Artist and song folder names

All song-folder exports now use **Artist - Song Title** from the reviewed metadata: Clean Songs, bulk four-fret conversion, single-song Medium export, and the interactive editor. Numeric prefixes, Medium tags, edit tags and timestamps are removed from individual song folder names. Batch parent directories still have timestamps to keep separate runs organized.

Collisions use **Artist - Song Title (2)**, then (3), etc. Existing files and directories are checked case-insensitively for Windows compatibility. The exporter still refuses to overwrite a destination if it appears after the name was chosen. Windows-invalid characters become underscores; each identity component is limited to 48 characters so both artist and title remain represented. Actual song metadata is not altered or truncated. Existing exported folders are not renamed automatically.

## Files changed

- gh3studio/song_identity.py: shared identity name and available-destination helper.
- gh3studio/cleaner.py, gui.py, editor_gui.py: use the shared destination helper.
- tests/test_song_identity.py, tests/test_cleaner.py: exact names, Unicode, collisions and duplicate-song batch export.
- Version files, README, CHANGELOG, HANDOFF_LATEST; this guide and M9_1_TEST_RESULTS.txt.

## Windows test steps

1. Close the old app. Extract GH3_Chart_Studio_v0_9_1.zip into a fresh folder and run START_WINDOWS.cmd.
2. Export a song through Clean Songs or Four-fret Medium → Bulk folder conversion. Verify its child folder is Artist - Song Title, matching the displayed metadata.
3. Include two charts with identical artist/title metadata in a batch. Verify both export into separate folders, with (2) on the second.
4. Repeat a single-song/editor export into the same parent. Verify it adds a suffix rather than overwriting the existing song folder.
5. Open song.ini and confirm the full original title/artist remain intact even if the folder name required sanitizing/truncation.

## Validation / next milestone

280 tests passed in 25.67s. Full automated suite results are in M9_1_TEST_RESULTS.txt. No native Windows/Dolphin execution for this release. Musical conversion behavior is unchanged. Next: verify real collection folder names on Windows, continuing bulk conversion acceptance.
