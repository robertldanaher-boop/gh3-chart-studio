# Milestone 7 — Focused GUI acceptance on Windows

## Setup and navigation
1. Close the old app. Extract GH3_Chart_Studio_v0_7_0.zip to a fresh writable folder.
2. Run START_WINDOWS.cmd. Wait for setup, automated tests and launch. Confirm 0.7.0.
3. Home should offer only Clean my songs and Make a challenging Medium. The main
   navigation should show Home, Clean songs and Four-fret Medium.
4. Resize to 1024x700 at your usual Windows display scale. Verify the bottom action
   remains accessible. Scroll the work area for optional controls. Report any clipping
   together with Windows scale, resolution and a screenshot.

## Clean a song or collection
1. Click Clean my songs, then Choose song folder. Start with one packaged chart and
   its full recording, or select your existing parent collection to inspect blockers.
2. Confirm the queue shows song, artist and status. Invalid charts use their folder
   name when no title can be read. Click a row for its asset paths, repairs and errors.
3. Type part of a title/artist or choose Needs help. Select all still checks the whole
   queue; Ready only selects all eligible rows, even if hidden by a filter.
4. Edit song details as needed. Choose audio/chart only for ambiguous or missing assets.
   Save scan report if anything remains blocked; it contains all discovered rows.
5. Check the visible Save to path outside the scanned tree. Tick Apply the cleanup
   changes I reviewed, then Start cleaning. No location dialog should open here.
6. Watch the current-operation status, elapsed clock and completion count. The Results
   tab should show each exported path or failure reason. Open results / logs should
   work even if all selected songs failed after an output report folder was created.
7. Inspect notes.chart, song.ogg, song.ini and reports in a successful song folder.
   Source files must remain unchanged. Send cleanup.log and/or the scan report for
   unresolved songs; the previously reported ten blockers are not yet diagnosed.

## Make and compare a challenging Medium
1. Click Make a challenging Medium, then Choose chart. Use your supported Expert/Hard
   chart first, or examples/technical-study.chart for a synthetic demonstration.
2. Choose Copy from Expert or Hard. Keep Orange sustains on playable frets starts
   checked. Click Create four-fret Medium; wait for the next-step message.
3. View track should show prepared Medium, with zero Orange in its summary. Check
   all four lanes and the holds. The existing transfer algorithm may flag conflicts;
   it does not guarantee every proposed hold is immediately exportable.
4. Click Review source, then Review Medium. Confirm the prepared Medium is restored,
   even if the input chart already had a different Medium. Source difficulties remain
   intact; no automatic density slider is involved in this focused workflow.
5. Click Play preview audio. If there is no unambiguous matched recording, choose the
   correct full mix. Confirm audible output, pause, stop and seeking. Playback & timing
   options includes output device/volume and optional explicit timing edits.
   The synthetic recording examples/audio/onset-study.wav is for playback testing;
   it is not a synchronized recording of technical-study.chart.
6. Click Review / export song. Check title/artist and recording; inspect exact errors
   and optional repairs. The readiness message explains why export is unavailable.
   Once eligible, Choose destination / export asks for the output parent folder.
7. Open exported folder. Inspect notes.chart, song.ogg, song.ini and validation reports.
   Verify source Expert/Hard, zero Orange in output Medium, timing and sustain outcomes.

## Reserved capabilities
Tools in reserve opens Advanced converter, Local pattern library or Audio drafting
lab. Their existing functions remain available and experimental limitations remain.
Return to essentials hides these extra tabs without deleting your working files.
A dropped audio file on Home/Four-fret Medium is now for listening; it does not
start transcription. Use the reserved lab explicitly if you need the old experiment.

## Test evidence and next milestone
223 passed in 23.28s (Python 3.11.18/Linux, Qt offscreen). Main screens inspected at
1024x700 and Home at1120x780; automated assertions include 18px text. Tests exercise
real chart/Ogg exports and exact source preservation, not only button visibility.
Windows native dialogs, DPI, audible device output, TheGHOST and Wii/Dolphin are
not tested here. This is source plus a Windows build recipe, not a built EXE.

Next milestone: accept these two workflows on Bob's Windows machine, inspect the
54-song collection's actual error report, then verify one song end-to-end in the
Wii import/game path before broadening features. Saved review projects, retry-only
failed exports and additional lower-difficulty profiles remain future work.
