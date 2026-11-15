# 0.4.8 — one-song Ogg export

1. Extract GH3_Chart_Studio_v0_4_8.zip into a new folder and run START_WINDOWS.cmd.
2. Open ONE chart. In Audio Studio → Listen / timing, select the difficulty you want, click Remove Orange → Medium, and confirm OUTPUT copied from the selected difficulty.
3. Choose the matching full-mix recording and verify preview playback and synchronization. Use the audio-output selector if needed.
4. Click Export song folder. The preview recording is already filled in; no need to select it again. Change recording only if correcting the selection. Review any Medium-only cleanup before accepting.
5. Export to a new folder. It contains exactly notes.chart, song.ogg, song.ini, validation.json and IMPORT_README.txt. There is no duplicate WAV, competing MIDI, or separate settings.json. Settings are retained in validation.json.
6. Import notes.chart and song.ogg into TheGHOST; select Medium. Verify title/artist, four frets, timing, sustains and audio in the importer and Dolphin/Wii. Test the entire song before adding batch conversion to the workflow.

Output is specifically Ogg Vorbis, not merely an .ogg extension. Existing readable mono/stereo Ogg Vorbis is copied byte-for-byte to avoid another lossy encode. Other supported inputs are encoded to Vorbis with the existing SoundFile encoder defaults; source files stay untouched. No resampling or timing shift is applied. The complete output is decoded again and its frame count, sample rate and channels must match. Conversion to Vorbis is lossy; this does not preserve every waveform sample.

If Change recording is used, successful export also updates preview to that chosen input recording. The app does not reload the encoded output automatically or claim that listening to the original verifies encoded audio on Windows. You can explicitly choose the exported song.ogg for a listening check.

Native Windows encoding/preview, TheGHOST's installed Ogg decoding support, and actual game playback require user acceptance. No batch queue, multi-song state, batch settings or concurrency was added. The single-song export module can be reused later once this workflow is verified.

For problems save the application's diagnostic log; for startup problems save start_windows.log. Keep validation.json with the exported folder. Next milestone: one complete song passes Windows preview → Ogg export → TheGHOST import → in-game timing/playability checks, then plan batch behavior.
