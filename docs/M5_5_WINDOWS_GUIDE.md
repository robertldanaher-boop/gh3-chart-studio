# 0.5.5 — Small-window startup test fix

1. Close all older GH3 Chart Studio windows.
2. Extract the complete 0.5.5 ZIP into a new writable folder (for example Desktop\GH3_Chart_Studio_0_5_5). Do not copy an old .venv into it.
3. Double-click START_WINDOWS.cmd. Keep your installed Python 3.11; no reinstall is needed. New-folder setup installs the pinned dependencies before testing.
4. Confirm automated tests finish and the application opens. The suite contains 195 cases; a platform-specific skip may change the passed count.
5. Open Audio Studio. Its four numbered actions are now in two rows. Create draft stays in a separate full-width footer row; Reanalyze and Cancel are above it.
6. Resize to approximately 1024 by 700. Confirm the draft action remains visible, including with Optional settings expanded. Check Pattern Library controls are accessible in their new two-row groups.
7. If startup still fails, save start_windows.log and startup_bootstrap.log, and report Windows Display scale and resolution. Do not disable the tests.

Chart conversion, randomized sustain placement, Ogg export and first-run acceptance are unchanged. Test one chart and matching recording through the intended importer/game as the next acceptance milestone.
