# Lost in the Dark — audio decoding diagnosis

November 18, 2026. GH3 Chart Studio 0.7.2 runtime code unchanged.

The supplied song.opus reproduces the user's SoundFile/libsndfile failure. The
header reports stereo 48 kHz Opus, but block decoding raises "Supported file
format but file is malformed" after 524288 successfully returned frames (10.923s).
This establishes which decoder fails; it does not prove the source is irreparably
corrupt or identify a specific Opus packet defect.

FFmpeg 7.1.5 completed a strict full decode (-xerror -err_detect explode) with no
reported errors. Converted the original directly to Ogg Vorbis quality 6, copying
source metadata, without requesting any resampling, trimming or timing adjustment.
Original artist tag is Left to Suffer; original title is Lost in the Dark. The
cleaner can reconcile tags to the reviewed song.ini metadata during export.

Verification performed
- Fully decoded the recovered Vorbis with the application's SoundFile environment.
- Both the FFmpeg-decoded reference and recovered Ogg contain 9,710,324 stereo
  frames at 48,000 Hz: 202.2984167 seconds. All decoded output samples are finite.
- Cross-correlation of two-second windows at 5, 100 and 195 seconds found zero-sample
  alignment lag. This checks conversion alignment, not chart synchronization.
- Exercised GH3 Chart Studio's actual export_ogg with metadata reconciliation,
  including re-encoding and full read-back. It passed with the same frame count.
- Input and output hashes and detailed results are below. The original upload was
  never modified. Opus-to-Vorbis conversion is lossy, not bit-identical audio.

Windows steps
1. Download the recovered song.ogg to a convenient folder; retain the original Opus.
2. In GH3 Chart Studio 0.7.2, select this song in Clean songs.
3. Click Choose audio and explicitly select the downloaded Ogg. The row rechecks.
4. If a prior synchronization review expires because the audio file changed,
   review it again. Then check the song, approve cleanup changes and Start cleaning.
5. Listen to the export and verify it with the chart in TheGHOST/Wii. Do not use
   the original Opus with a timing-normalized chart from another export.

Limits and next development milestone
The chart/song.ini were not supplied, so full song-folder and in-game acceptance
remain untested. No new application release or automatic decoder fallback is
included in this recovery. No full suite rerun was needed: application code is
unchanged. The installed FFmpeg build's license output was inspected (GPL-enabled
Debian build); it was used locally, not bundled or redistributed.

Next application work: stage/file-specific audio errors and a tested fallback
strategy for Windows. Any distributed decoder must have its specific license,
source availability and packaging reviewed; do not silently skip bad frames or
change timing. Keep this user's recording out of application packages and tests;
create a synthetic regression fixture or an opt-in external-file reproduction.

Files created: recovered_lost_in_dark/song.ogg and this diagnostic report.
Project documentation and handoff updated; runtime source unchanged.

## Verification data

```json
{
  "input_sha256": "d7a23cd0767a3867150bc0919822b341b95554b33006cc4a04fb6f17f73d8a43",
  "output_sha256": "cda59a96e86e2e3f9f552bc552c85009606e3031d9653c92a89972dbfbce553c",
  "sample_rate": 48000,
  "channels": 2,
  "frames": 9710324,
  "duration_seconds": 202.29841666666667,
  "alignment_checks": [
    {
      "start_seconds": 5,
      "lag_samples": 0
    },
    {
      "start_seconds": 100,
      "lag_samples": 0
    },
    {
      "start_seconds": 195,
      "lag_samples": 0
    }
  ],
  "current_app_export_test": {
    "embedded_tags": {
      "title": "Lost in the Dark",
      "artist": "Left to Suffer, Paleface Swiss",
      "date": "2024-02-06;2024",
      "album": "Lost in the Dark"
    },
    "metadata_warnings": [],
    "file": "song.ogg",
    "format": "OGG",
    "codec": "VORBIS",
    "operation": "encoded_to_vorbis",
    "frames": 9710324,
    "sample_rate": 48000,
    "channels": 2,
    "fully_decoded": true,
    "resampled": false,
    "timing_shift_applied": false,
    "padding_frames": 0,
    "trimmed_frames": 0
  },
  "decoder": "FFmpeg strict decode succeeded; SoundFile/libsndfile 1.2.2 fails after 524288 completed frames on source"
}
```
