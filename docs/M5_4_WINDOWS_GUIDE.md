# 0.5.4 — Randomized Orange sustain preservation

1. Close older copies. Extract the ZIP into a new writable folder and run START_WINDOWS.cmd with Python 3.11 x64 installed.
2. Open your chart and select Expert or Hard under Display / copy source in Audio Studio / Listen & sync.
3. Check **Preserve Orange sustains on random Green / Red / Yellow / Blue frets**. It replaces the Blue-only checkbox; unchecked still performs plain Orange removal.
4. Leave Sustain placement seed at 0 or enter another number, then click Remove Orange → Medium.
5. Display Medium. Each Orange sustain keeps its original onset and at least its full duration. Clear simultaneous frets are preferred; otherwise a clear fret is selected randomly from G/R/Y/B. If an existing simultaneous note is selected, its duration becomes the longer of the two. Orange taps disappear and Expert/Hard remain unchanged.
6. Click Regenerate sustain placement to increment the seed and regenerate from the original selected track. The same source and seed reproduce the same result. A different seed may still yield the same placement where choices are constrained; regeneration is not a promise that every note will move.
7. Review and listen with matching audio. If all lanes conflict, the full sustain is retained and the report flags the lane conflict. Cross-lane holds and unequal sustained chords can also need target-specific cleanup. No duration is silently trimmed by placement.
8. Export a new folder. Review cleanup changes before accepting; trimming changes the preserved sustain. validation.json records settings.sustain_seed, sustain_transfers (tick, selected lane, durations and conflict), and sustain_lane_conflicts. A saved seed can be entered again in the GUI; this is not a complete project/session save.
9. Reopen notes.chart, confirm Medium has only four frets, and test the result in the intended importer/game. The chart/audio export remains notes.chart, song.ogg, song.ini and validation/import documentation.

No native Windows, audible playback or Wii test was performed here. Next milestone: one matching recording and chart tested through Windows preview and actual target gameplay before batch work.
