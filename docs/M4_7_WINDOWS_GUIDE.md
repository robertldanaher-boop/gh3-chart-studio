# 0.4.7 — preview audio selection and playback diagnostics

1. Extract GH3_Chart_Studio_v0_4_7.zip into a new folder and run START_WINDOWS.cmd.
2. Open the chart and go to Audio Studio → 3. Listen / timing. A safe, existing MusicStream path inside the chart folder is loaded automatically. Otherwise a single song.wav/ogg/flac/mp3/opus is selected. Multiple song files are ambiguous; guitar/bass stems are not guessed.
3. Click Play preview audio. If no recording is loaded, a file picker now opens. Select the actual song recording. The button changes to Pause preview audio when playback begins. Confirm the seek position and notes move.
4. Choose your speakers/headphones in Audio output; Windows / system default follows the default device when playback begins. Check the volume slider and Windows volume mixer if notes move but there is no sound. No output device and decoding failures are shown next to the output selector.
5. Test Pause, resume, Stop and seeking. Stop pauses and rewinds to avoid the known Qt FFmpeg stop/seek contention. Changing charts clears old audio then attempts to load the matching recording. No matching recording means Play will ask rather than silently do nothing.
6. If it still fails, use Chart Converter → Save diagnostic log. Send that log and describe whether the seek position advances, the selected output device, and any visible playback error. start_windows.log alone does not include all in-app playback events.

Supported preview file picker: WAV, FLAC, OGG, MP3, OPUS. Playback depends on the Qt backend and actual file encoding. Audio analysis/export format support is unchanged. Try a WAV copy if a specific recording cannot decode.

Known limits: local automated tests verify decoding, player clock, pause/seek, output selector presence and selection flow. This environment has no audio output device, so audible output and Windows routing must be verified on the user's machine. The no-source bug is reproduced; it is not proven to be the sole cause of the user's report.

Next milestone: confirm audible playback on Windows with the actual recording; use the new diagnostics to investigate any remaining codec/device issue.
