# 0.11.3 — Import collections from the Medium workspace

## Files and working behavior

- gh3studio/workspace.py: persistent Choose folder button beside compact mode selector; disabled while busy.
- gh3studio/gui.py: start_medium_collection opens a directory picker, selects the embedded collection view and scans recursively. Directory drops in Four-fret Medium and explicit guided directory paths use it. Opening a chart file switches to single-song view.
- gh3studio/cleaner_gui.py: preserve the four-fret workflow identity during scans.
- tests/test_bulk_medium.py: three regression routes (button, drag/drop, guided directory), each with two songs including deeply nested folders, Expert/Hard fallback, and valid populated Medium/Easy tracks.
- Version files, README, CHANGELOG, HANDOFF_LATEST and this release/test evidence updated.

## Tests and limitations

Focused bulk/workspace suite: 18 passed in 4.94s. Full suite: 292 passed in 27.72s. Full-suite results in M11_3_TEST_RESULTS.txt. Tests use Linux/Python 3.11/Qt offscreen. Native Windows directory picker, drag/drop and Dolphin confirmation remain pending. Existing recursive scan cap of 2,000 song folders and unsupported-source blockers remain. No changes to note conversion, audio export or overwrite policy.

## Exact Windows steps

1. Close the app. Extract GH3_Chart_Studio_v0_11_3.zip into a fresh application folder and run START_WINDOWS.cmd inside GH3_Chart_Studio.
2. Select Make a challenging Medium from Home.
3. Click Choose folder… beside the mode selector. Select the parent containing your song folders. The view automatically switches to Folder collection and scans nested folders.
4. Alternatively, drag that parent folder onto the Four-fret Medium workspace. It should stay in this workspace, not switch to Clean songs.
5. Review source selection (Expert then Hard by default), song rows and repairs. Scroll through the queue, use Select all or Ready only, and check Replace Medium + Easy; fill missing slots.
6. Set Save to to the desired output parent, outside the source tree. Click Create Medium. Check results/logs. Recognized prior outputs are updated; original source folders stay protected.
7. Return to One song when you want preview/editing for an individual chart.

Next milestone: confirm a real multi-folder Windows import and repeat export, then verify all difficulty slots in Dolphin. If import still fails, send the visible error and scan report or cleanup.log.
