# 0.4.5 — exact displayed-track copy and song-folder export

1. Extract GH3_Chart_Studio_v0_4_5.zip into a NEW folder. Do not overlay an older installation. Double-click START_WINDOWS.cmd. It sets up Python 3.11 dependencies, runs tests, then launches. On failure keep start_windows.log. Python 3.11 x64 is already installed on Bob's PC; 3.11.0 specifically is not required.
2. Open your chart in Chart Converter, then Audio Studio → 3. Listen / timing. Select Expert (or any available difficulty) in Display difficulty.
3. Click Remove Orange → Medium. The display switches to Medium. The label says OUTPUT copied from Expert (or your selected difficulty). Every surviving G/R/Y/B note retains its lane, tick and sustain. Orange-only events disappear. Original Medium is replaced only in the output copy. Expert/Hard/Easy stay unchanged.
4. Switch Display difficulty between Expert and Medium to compare. Merely switching difficulty does not regenerate or change the output. Select the matching full-mix recording using Choose preview audio and check synchronization.
5. Click 4. Export song folder. Confirm the audio path. The review initially applies NO cleanup. If Medium has unsupported markers, explicitly check Remove unsupported Medium markers. If it has overlapping/extended/disjoint sustains, review the listed changes before checking/accepting sustain shortening. These are separate gameplay changes, not part of Remove Orange. Cancel retains the exact preview.
6. Click Export reviewed song folder and choose a parent directory. A new timestamped folder contains notes.chart, song.wav, song.ini, validation.json, settings.json and IMPORT_README.txt. The preview updates to the exported Medium after successful export. An existing folder is never overwritten.
7. In TheGHOST select notes.chart, map Medium, and use song.wav as the full mix. Verify title/artist, timing, sustains and HOPO behavior in the importer and Dolphin/Wii. This folder is import material, not a ready-to-run Wii archive. No game assets or artwork are fabricated.

Audio is converted to PCM16 WAV without resampling, retaining sample rate, channel count and frame count. Choose the original mix, not an analysis stem. Opening a different chart clears the previous preview audio to prevent accidental reuse. Nonzero chart Offset or song.ini delay blocks folder export pending explicit synchronization resolution. Only mono/stereo recordings supported by SoundFile can be exported.

Medium checks do not certify the retained source difficulties: their original markers/sustain issues are deliberately preserved. Other instruments are outside the existing guitar-only parser and are not exported. GH3 natural-HOPO behavior may change when Orange notes are removed. Forced/tap behavior is not promised. Tempo representation is checked within 1 ms at boundaries and song end. No native Windows/TheGHOST/Wii validation was available for this release.

The previous paired chart/MIDI export API remains tested for supported charts; the song-folder GUI uses notes.chart to retain authored source markers faithfully. It does not place a competing MIDI chart in the folder.

Recommended next milestone: complete this Windows import/playback acceptance test using the actual matching recording, then refine supported HOPO handling based on verified importer behavior.
