# Windows 10/11 x64 acceptance test

1. Install Python 3.11 x64 with the launcher. Extract the ZIP to a writable directory.
2. Double-click setup_windows.cmd. Require a successful setup message.
3. Double-click test_windows.cmd. Save any failure output. The automated GUI tests
   run offscreen; they do not replace the visible checks below.
4. Double-click launch_windows.cmd. Confirm the full window is visible at your DPI.
5. Drag examples/technical-study.chart into the window. Confirm the title/artist,
   Expert 38 gems and Hard 14 gems appear.
6. Convert Expert with defaults. Expect 31 timed events, 37 Medium gems, one removed
   chord gem, and zero removed events. Source contains 31 timed events / 38 gems.
7. Confirm the Medium preview shows only four lanes. Switch to Source; it has five.
8. Set Chords to 6 and reconvert. Expect 38 Medium gems. All 31 onsets remain.
9. Set Density to 1; reconvert and confirm a lower count. Restore defaults.
10. Export into a new folder. Open validation.json: both files must have reopened,
    Medium orange count must be zero, and drift must be at most 1 ms.
11. Reopen notes.chart and convert Hard. Reopen notes.mid using Legacy MIDI mode.
12. Verify source chart timestamps/content remain unchanged. Test an invalid file:
    it must display an error and must not enable export for stale content.
13. Save/load a preset; save the diagnostic log.
14. Run build_windows.cmd. If successful, launch dist/GH3ChartStudio/GH3ChartStudio.exe
    and repeat steps 5–10. Keep all files beside the executable together.

## TheGHOST / Dolphin / Wii (pending)

Use a backup of a personally owned game image and a song you can legally modify.
Do not start by replacing a full setlist.

1. Select one supported Expert/Hard chart with matching original audio, no special
   modifiers and known offset. Convert and inspect the compatibility report.
2. In TheGHOST, import **notes.chart explicitly**, select the actual Medium difficulty,
   and import the original audio separately. Apply the known offset there.
3. Inspect beginning/middle/end note timing and both sides of every tempo change.
4. Confirm no Orange notes; check fast runs, repeated notes, two/three-note chords,
   sustains, Star Power phrases and whammy interaction.
5. Test MIDI separately, selecting Legacy output and checking 79-based Medium SP.
   Expect TheGHOST's documented short-sustain differences; prefer chart when relevant.
6. Record TheGHOST build, emulator/hardware, source/export hashes, import warnings,
   offset, timing observations and any gameplay failure in a diagnostic report.

A successful import alone does not prove in-game compatibility.
