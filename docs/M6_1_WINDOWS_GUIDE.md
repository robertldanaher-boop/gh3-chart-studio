# 0.6.1 — Windows encoding and compact-layout fixes

1. Close older copies and extract the complete 0.6.1 ZIP into a new writable folder.
2. Run START_WINDOWS.cmd. Existing Python 3.11 can be reused; no Python reinstall is required. A new folder creates its own dependency environment.
3. Confirm setup tests finish and the application opens. The suite includes 207 cases; platform-specific skips can change the passed count.
4. Resize the app to roughly 1024x700. Check Audio Studio's draft footer stays visible, including with optional settings expanded. Pattern Library can now scroll if controls are wider than the available area. The main navigation buttons are on a separate header row; tabs support scrolling.
5. Clean a test song whose title contains non-ASCII characters, such as † or accented letters. Inspect song.ini with a UTF-8-capable editor and reopen notes.chart. Source and export metadata should agree.
6. In Clean charts, the review checkbox now reads Review complete; its tooltip explains that metadata/audio and cleanup changes must be verified. Export checked songs is the same action with a shorter label.

If startup still fails, send start_windows.log and Windows Display scale/resolution. Do not disable the tests. No chart cleanup or audio conversion algorithms were changed by this release.

These fixes were verified with Linux/Qt offscreen tests and a rendered 1024x700 larger-text view. Native Windows behavior still needs your confirmation. Next milestone: successful Windows startup, then one-song cleanup/import acceptance.
