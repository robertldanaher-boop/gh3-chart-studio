# 0.6.2 — Cleaner metadata edits retained

1. Close older copies, extract the complete ZIP into a new folder and run START_WINDOWS.cmd. No Python reinstall is needed.
2. Open Clean charts for GH3 and scan your song directory.
3. Select the affected song, choose Edit selected metadata, enter title/artist/album and click OK.
4. Verify title and artist update in the table. The detail panel lists the edited metadata. Status confirms edits are retained and separately identifies any remaining chart errors.
5. Reopen Edit selected metadata: your entries should still be present, even if the chart is malformed, has nonzero timing offsets or fails compatibility checks.
6. Once errors are resolved and reviewed, export a new folder; verify notes.chart and song.ini contain the corrected metadata.

Edits belong to the current review session until exported. They do not rewrite originals and are not a saved project across app restarts or a fresh scan. Cancelling the metadata dialog keeps the previous values. Selecting a replacement chart for the same queue row retains editable song identity, but does not carry stale resolution/offset fields into the replacement.

If the chart still shows Needs correction, copy its separate error text. Metadata editing does not repair chart syntax or synchronization offsets. Native Windows confirmation is pending; next milestone is successful metadata edit/reopen/export with your affected song.
