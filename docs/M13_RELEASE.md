# 0.13.0 — Streamlined preparation interface

## Implemented changes and files

- gh3studio/welcome.py: one primary Prepare my songs card; secondary Clean only action. Removed the misleading two-step implication and outdated source-track preservation copy.
- gh3studio/workspace.py: one shared chart/folder toolbar, short One song/Collection selector, Prepare song button and consistent numbered guidance. Duplicate folder picker in embedded collection panel hidden.
- gh3studio/cleaner_gui.py: combined collection heading, scope, approval, export action and instructions.
- gh3studio/gui.py: primary Prepare songs tab before Clean only; Home folder drops enter combined conversion/cleanup.
- tests/test_focused_workspace.py, test_bulk_medium.py and test_gui.py: visible shared toolbar, hidden duplicate, tab order, Home folder drop and nested collection routing.
- Version files, README, CHANGELOG, HANDOFF_LATEST, this log and test results updated.

## Verification and limits

Local visual inspection at 1024 by 700 including large text confirms shared selection and fixed export controls fit. 296 tests passed in 28.51s (Linux/Python 3.11/Qt offscreen). Full automated results are recorded in M13_TEST_RESULTS.txt. An initial run stalled and was interrupted; it is not counted as a pass. Native Windows font/rendering and Dolphin confirmation remain pending. No changes to the conversion algorithm or export format. Large collections and review controls remain scrollable; advanced tools remain in reserve.

## Exact Windows testing

1. Close the app and extract GH3_Chart_Studio_v0_13_0.zip into a fresh application folder. Run START_WINDOWS.cmd inside GH3_Chart_Studio.
2. On Home, choose Prepare my songs. Choose chart… opens individual chart preview; Choose folder… recursively scans a parent collection and selects Collection automatically.
3. For one song, select Expert or Hard and click Prepare song. Review source/output, then Review / export song.
4. For a collection, review songs and repairs, select songs, set Save to, check Apply the reviewed conversion and repairs, then Prepare & export. The shared folder picker stays at the top; there is no duplicate picker within the queue.
5. Verify Home folder drag/drop follows the combined workflow. Clean only should remain available for compatibility repair without generating new difficulty tracks.
6. Resize to approximately 1024 by 700 and check both modes, visible export controls, scrollable review content, and Tools in reserve.

Next milestone: Windows usability acceptance with a real collection, then confirm repeat export and difficulty selection in Dolphin.
