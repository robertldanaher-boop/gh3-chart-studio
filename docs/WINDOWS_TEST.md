# Windows 10/11 acceptance — current release 0.7.1

Follow [M7_1_WINDOWS_GUIDE.md](M7_1_WINDOWS_GUIDE.md) for the startup layout fix, then
[M7_WINDOWS_GUIDE.md](M7_WINDOWS_GUIDE.md) for the two essential workflows,
small-window checks, audio preview and reserved tools. Older M*_WINDOWS_GUIDE files
are historical instructions; tab names in them may have moved under Tools in reserve.

## Build acceptance
After START_WINDOWS.cmd succeeds, close the app and run build_windows.cmd. It runs
tests, collects license notices and builds using PyInstaller. Launch
`dist\GH3ChartStudio\GH3ChartStudio.exe` and repeat the M7 GUI/one-song checks. Keep
the full distribution directory together. This recipe has not been executed here
on Windows; no compilation, signing or Windows reputation guarantee is implied.

## TheGHOST / Dolphin / Wii acceptance (still pending)
1. Start with one authored song and its matching recording. Export to a new folder.
2. Import notes.chart explicitly and select the intended difficulty. Use song.ogg
   as the recording and verify the title/artist metadata in the importer.
3. Check beginning, middle and end synchronization, including both sides of tempo
   changes. Resolve offset/delay deliberately rather than changing tempo to conceal it.
4. Verify four-fret Medium has no Orange; test fast runs, repeated frets, chords,
   sustained chords, transferred holds, Star Power and whammy behavior.
5. HOPO highlighting is an estimate. If using the experimental export assistance,
   follow the output import report's TheGHOST settings and verify strum/HOPO behavior.
6. Test game-chart MIDI separately if required, with the appropriate import profile.
   Prefer .chart for the main song-folder path and inspect short-sustain handling.
7. Record tool/game version, hardware/emulator, warnings and timing/gameplay results.
   A successful import alone does not establish successful in-game behavior.
