# GH3 Chart Studio 0.5.2 — Export acceptance audit

November 15, 2026. Existing implementation tested; no application behavior changed.

## Results

| Supplied chart | Source | Source gems | Medium gems | Orange removed | Sustain shortenings in separate cleanup | Markers removed in separate cleanup |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| notes(1).chart | Expert | 902 | 868 | 34 | 15 | 601 |
| notes(1).chart | Hard | 741 | 720 | 21 | 3 | 499 |
| notes(2).chart | Expert | 1469 | 1315 | 154 | 1 | 295 |

For all three tracks, the Orange-only working copy exactly matched the selected source's surviving Green/Red/Yellow/Blue notes, including onset and sustain. Source objects and input file hashes were unchanged. No Hard track was available in notes(2).chart.

The exact copies triggered compatibility review. Separate temporary test copies were explicitly cleaned with marker removal and sustain trimming. These are separate operations: cleaned exports no longer promise exact source sustains or marker behavior. Marker removals can alter HOPO/tap behavior. The counts above describe the tested broad cleanup option, not a requirement that every marker must be removed in every export profile.

All three cleaned test exports passed chart reopen comparisons, zero Orange in Medium, preservation of Expert/Hard/Easy source tracks, metadata checks and Ogg encoding checks. Measured tempo-map drift at exporter probes was 0 ms. Output contained notes.chart, song.ogg, song.ini, validation.json and IMPORT_README.txt.

## Limits

Exports used the application's synthetic onset-study.wav solely to exercise the audio/file pipeline. It is not the recording for either chart. Temporary exports were removed and are not offered as playable songs. No listening/synchronization, Windows audio device, TheGHOST, Wii or other-game acceptance is established. The prior complete suite result remains 183 passing tests; no code changes required a repeat suite.

## Windows acceptance steps

1. Use v0.5.2, close older instances and run START_WINDOWS.cmd.
2. Agree on first launch. Choose an existing chart and its matching full recording.
3. Display Expert or Hard and choose Remove Orange to Medium. Select Medium and compare it to the source: only Orange should be missing at this stage.
4. Preview the actual audio. Check a recognizable attack near the beginning, middle and end for drift.
5. Export to a new folder. Review every cleanup option: sustain trimming and marker removal go beyond removing Orange. If exact sustains are required, do not approve trimming merely to bypass validation.
6. Verify artist/title, notes.chart, song.ogg and song.ini. Inspect validation.json for actual changes.
7. Import the folder through the intended tool. For the experimental TheGHOST HOPO profile use measure 2.95. Check timing, sustains, chord behavior and strum/HOPO behavior in actual gameplay.

Next milestone: matching-recording and native Windows/game acceptance for one song before batch development. Supply the matching audio and any failing startup/export logs if further diagnosis is needed.
