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

## Version 0.2.0 pattern-library acceptance

Run setup_windows.cmd, test_windows.cmd and launch_windows.cmd from the new release.
The Linux reference has 74 passing tests. A symlink test may be skipped on Windows
when symlink privileges are unavailable; other failures require investigation.

1. Create a test folder and copy only examples/technical-study.chart into it.
2. Open Pattern Library. Choose a new test SQLite database path.
3. Scan the test folder; expect 1 imported chart content, 6 windows and no failures.
4. Scan it again; expect 1 duplicate and no additional windows.
5. Browse patterns; select one and save a rating of 5. Close/reopen the app, select
   the same database and confirm the rating persists.
6. Add a malformed .chart to the folder and rescan. Expect completed_with_errors,
   with that file marked failed. The existing six windows must remain available.
7. Open the original study in Chart Converter. Choose Expert, Density 6, Chords 6,
   Movement 5, Max chord gems 3, seed 42. Generate the three variation modes.
8. Select each variant; confirm four preview lanes, 31 retained events and no Orange.
   Export each to a separate new folder. Check donor/seed/corpus details in validation.json.
9. Regenerate with unchanged settings and database. Compare actual notes; they should
   match. Changing ratings/database can intentionally change output.
10. With only this tiny corpus, expect a warning if two modes produce the same notes.
    Different labels alone are not proof of distinct arrangements.
11. Test a larger folder; cancel while scanning, then rescan. Fully imported files
    should be reused and unprocessed/failed files retried. Save the scan report.
12. Repeat the TheGHOST/Dolphin acceptance steps above with a legally usable real song.

Do not copy the examples/variations outputs into the training folder for the minimal
six-window check; each exported file is a separate content snapshot.

## Version 0.3.0 audio-analysis acceptance

1. Extract the new release into a fresh folder. Run setup_windows.cmd to install the
   audio dependencies, then test_windows.cmd and launch_windows.cmd.
2. Open Audio Analysis -> examples/audio/onset-study.wav. With defaults, expect
   15 attacks, approximately 120 BPM and a visible waveform/grid. Compare truth.json.
3. Enter manual BPM 120 and reanalyze. Confirm the grid changes without quantizing attacks.
4. With no authored chart loaded, create a draft. Verify 15 Medium notes, only G/R/Y/B,
   no inferred sustains/SP, and then export both formats to a fresh folder.
5. Use Compare timing with current chart; the fixture should show very small residuals.
6. Set Draft shift to +120 ms and regenerate. Comparison measures the already-shifted
   chart; expect a suggested additional correction near -120 ms, not a second +120 shift.
7. Save analysis/diagnostics and settings. Reload settings, select the recording and reanalyze.
8. Load an authored chart, then generate with the template checkbox on. Confirm the original
   tempo map and source difficulty remain in the exported file.
9. Scan a pattern corpus and test the optional learned-pattern checkbox.
10. Try a legally usable real recording in WAV, FLAC, OGG and MP3; verify codec availability,
    responsiveness, cancellation and timing against the actual audio import path.
11. Run build_windows.cmd and repeat steps 2–5 using the packaged executable. Verify that
    NumPy/SciPy and libsndfile load. The source-release build recipe has not been run here.

A low fixture error does not certify real-song guitar transcription or in-game playability.
