# Version 0.7.3 — Automatic audio decoding recovery

## Install and test the original file
1. Close the older app and startup window. Extract GH3_Chart_Studio_v0_7_3.zip
   into a fresh writable folder. Keep your song folders where they are.
2. Run START_WINDOWS.cmd. It installs the new pinned imageio-ffmpeg dependency
   automatically, runs the tests and launches. Internet is needed for the initial
   installation; the Windows decoder wheel is approximately 31 MB. Do not copy an
   older .venv. Confirm version 0.7.3 in the header.
3. Open Clean songs and scan the ORIGINAL Lost in the Dark folder containing
   song.opus. Select the row and verify the Audio path ends in song.opus. If you
   previously selected the downloaded Ogg workaround, use Choose audio to select
   the original Opus for this test.
4. Review metadata and cleanup changes as usual. Check the song, check Apply the
   cleanup changes I reviewed, and click Start cleaning. No repair toggle or manual
   conversion is necessary. Any unrelated chart/synchronization blockers still
   need the normal review; see M7_2_WINDOWS_GUIDE.md.
5. The source decoder should fail on this Opus, automatically retry with FFmpeg,
   and finish exporting. Results should say Audio recovered automatically with
   FFmpeg. Open results / logs: cleanup.log includes AUDIO RECOVERED, and the new
   song folder's validation.json contains audio_export.fallback with the original
   error and recovered frame count/rate/channels.
6. Expect song.ogg, notes.chart, song.ini and the normal reports. Original files
   remain untouched. Listen to the output and verify synchronization with the
   actual chart in TheGHOST/Wii. Import matching exported chart/audio together.

## What the repair does
The primary SoundFile decoder is retained. A source-opening, metadata-reading or
sample-decoding LibsndfileError triggers one strict alternate decode to temporary
floating-point PCM, followed by the existing Ogg export and complete read-back.
No network operation occurs during recovery. No ignored-error or discard-corrupt
flags are used. No audio samples are intentionally trimmed and no sample-rate or
channel conversion is requested. When the source header was readable, recovered
frame count, sample rate and channel count must all match it exactly.

Requested synchronization padding and reviewed metadata are applied once after
recovery. Existing healthy Vorbis files can still be copied without re-encoding.
The failed partial output is replaced inside the normal atomic export staging
folder; unsuccessful song exports are removed. Temporary PCM is removed on exit.

Errors now identify the audio file and stage (source decoding, writing, output
validation, etc.). Write/permission errors and generated-output validation failures
are not treated as source-decoder problems. If both decoders fail, the song stays
failed and both reasons are logged; other selected songs can continue.

## Test evidence and limits
263 tests passed in 25.48s on Python 3.11.18/Linux/Qt offscreen. The supplied original
Opus was also tested through inspect_chart + export_cleaned with a synthetic chart:
recovery succeeded, 9,710,324 stereo frames at 48 kHz (202.2984167s), complete Ogg
read-back, source hash unchanged and recovery logging verified. The real user chart
was not provided. Evidence: M7_3_REAL_OPUS_RESULT.json and M7_3_TEST_RESULTS.txt.

Six new automated cases exercise forced primary-decoder failure with real synthetic
Opus/FFmpeg decoding, mono/stereo and padding, failed writes without an inappropriate
retry, both decoders failing with atomic rollback, duration mismatch and timeout.
The private uploaded song is not included in the source ZIP or automated tests.

Windows wheel existence, hash and contained FFmpeg executable were checked. Native
Windows execution, Windows packaging, audible playback and Wii/TheGHOST acceptance
remain pending. Some files still cannot be recovered: scan-time header errors,
unresolved stream inconsistencies or corrupt data may block export. This release
addresses the reproduced decode failure; it is not a universal media repair tool.

FFmpeg has a 180-second per-attempt timeout. Cancellation remains between songs;
the current decode attempt may finish or time out first. Temporary PCM needs disk
space (roughly 78 MB for the supplied song). Vorbis encoding remains lossy. If a
failure persists, send cleanup.log and the affected file; no protection bypasses.

Next milestone: confirm this automatic path on Bob's Windows machine using the
original Opus, then verify one exported song in TheGHOST/Wii.
