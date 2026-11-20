# 0.15.0 — Separate audio tracks (stems)

Bob confirmed 0.13/0.14 conversions play correctly in Dolphin (Nov 20) and asked
that songs downloaded with separate tracks be cleaned and converted too.

## Detection (gh3studio/stems.py find_song_audio)
Clone Hero names: song (backing), guitar, rhythm, bass, keys, drums, drums_1-4,
vocals, vocals_1-2, harmony. Chart [Song] *Stream entries are honoured.
Left out: preview, song_preview, crowd, unrecognized names (listed).
Two or more tracks -> mix. song alone, or one lone instrument-named file -> single
recording (the latter with a verify warning). Several unrecognized files -> blocked
(choose the full mix), as before.

## Mixing (mix_stems)
Two streamed passes (peak, then write) in 65,536-frame blocks; PCM 24-bit WAV at
the main track's rate; stereo if any track is stereo. Original levels; uniform
gain = 0.98/peak only when peak > 0.98. Different rates: scipy resample_poly into
memory. Decode failure mid-file: FFmpeg recovery (audio_fallback.decode_to_pcm,
header frames/rate/channels must match) and retry once.

## Integration
- cleaner.inspect_chart: row['audio_stems'], all tracks validated and hashed
  (changed tracks force a rescan), change entry + warnings. row['audio'] is the
  main track (sample rate for timing normalization = mix rate).
- song_export.export_song_folder accepts a list: mixes to a temp WAV, adds
  report['audio_stems'] and a warning, then the normal Ogg/validation path.
- gui.open_path: mixes in the worker via cached_mix (temp folder, keyed by
  path/size/mtime); preview plays the mix; export_song_to attaches audio_stems.

## Tests
tests/test_stems.py (detection, mixing maths with fake reader/writer, clipping,
resampling, errors, real-file round trip), test_cleaner (collection export with
3 tracks; unreadable track names the file; old "multiple stems require a choice"
test replaced by the new mixing policy), tests/test_stems_gui.py.

## Not verified
Listening balance in game. Stems mixed at authored levels; if a song sounds
unbalanced, that is how the tracks were supplied.
