# Milestone 3 — audio analysis and onset drafts

Version 0.3.0 is a first working audio-analysis pipeline, not verified guitar
transcription. Audio is analyzed locally and is never re-encoded or overwritten.

## Windows workflow

Run START_WINDOWS.cmd. It installs pinned dependencies, including NumPy, SciPy
and SoundFile, then runs tests and launches the app.

1. Select **Audio Analysis** and open WAV, FLAC, OGG or MP3. A single audio file can
   also be dropped onto the main window. Decode/analysis runs in a cancellable worker.
2. Review the waveform, attack markers, estimated beat grid, BPM candidates and
   warnings. Sensitivity 1–6 changes the attack threshold. Minimum spacing suppresses
   attacks too close together. Changing analysis settings requires reanalysis.
3. If the tempo estimate is wrong, enter a BPM override from 30–300 and reanalyze.
   Zero selects automatic estimation. The override changes the grid, not attack times.
4. Optionally load an authored chart in Chart Converter, then keep **Use open chart
   tempo map when available** selected. Its resolution, tempo positions and values are
   preserved. Without a template, the draft uses 960 PPQ and one estimated/manual tempo.
5. **Draft shift** moves new notes relative to audio: positive values place them later;
   negative values earlier. A shift that creates negative note times is rejected.
6. Optional **Use local learned patterns** transfers stored shapes onto the detected
   attacks. Scan a pattern corpus first. Empty corpora produce an error, not fake learning.
7. Click **Create four-fret draft**. It opens in Chart Converter and can be exported via
   the existing paired .chart/MIDI exporter. Source difficulties remain intact when
   a template is used. Audio-generated Medium always uses lanes G/R/Y/B only.
8. Compare the actual current chart with the recording using **Compare timing with
   current chart**. If a converted Medium is active it is compared; otherwise the
   selected Expert/Hard source is compared. This measures its existing timing and
   does not apply Draft shift a second time.
9. **Save analysis / diagnostics…** writes JSON. Converter **Save settings…** saves the
   active audio draft's settings. Loading those settings restores controls; select the
   matching recording and reanalyze. Use the same tempo template/corpus for reproduction.

The waveform is a read-only overview with horizontal scrolling and zoom. It is not
an audio player or chart editor; synchronized playback/editing are Milestone 4.

## What the analysis does

SoundFile/libsndfile decodes PCM to mono, with a strongest-channel fallback when
stereo phase cancellation would otherwise look like silence. SciPy resamples to
22,050 Hz. A 1,024-sample Hann window and 128-sample hop measure spectral change,
energy and spectral centroid. Adaptive peaks in combined spectral/energy rise are
candidate attacks; a local amplitude-rise refinement estimates their timestamps.

Autocorrelation proposes constant tempos between about 60 and 200 BPM. Manual BPM
accepts 30–300. Beat phase is fitted to detected attacks. **Beat fit** means the
fraction of detected attacks within 50 ms of that grid; it is not a probability that
the tempo is correct. Half/double-time ambiguity, syncopation, rubato, percussion and
variable tempo can all undermine this estimate.

The report includes quiet spans and coarse energy-change review points. These are
not verified musical phrases, guitar solos, instrument identities or source separation.
The system does not infer guitar pitch, chords, sustained-note lengths or Star Power
from mixed audio. Each retained attack becomes one zero-length gem. Without learned
patterns, a deterministic timbre-rank heuristic chooses the lane; it is not pitch-to-fret
transcription. With learned patterns, the Milestone 2 transfer chooses the lane shape.

No onset is snapped blindly to a beat subdivision. Only representation in integer
chart ticks introduces rounding; measured rounding error is included in the report.
No attacks means no draft: silence is never padded with arbitrary notes.

## Alignment diagnostics

For each distinct chart onset, the analyzer finds the nearest audio attack and records
its signed residual. Positive residual: the chart note occurs early. Suggested additional
shift is the median residual among matches within ±250 ms. At least three distinct
matched attacks are required before a correction is suggested.

Residual medians across time thirds provide a rough drift slope. Consistent residuals
suggest a global offset; a changing trend suggests tempo-map error; scattered residuals
suggest individual timing/transcription issues. These are review hints, not automatic
repairs. No chart is changed by running diagnostics.

Nearest-attack matching can choose a drum hit or the wrong beat, particularly with
large offsets or dense passages. The ±250 ms gate is not a reliable large-offset search.
Listen before accepting a suggested shift. Authored Offset is not silently applied;
nonzero template Offset is rejected for draft generation, consistent with paired export.

## Verified evidence and limits

The original fixture examples/audio/onset-study.wav contains 15 synthesized attacks
at half-second intervals. It is not a commercial song. All 15 were detected; estimated
BPM was 120.034 versus known 120. Max absolute attack error was 0.181 ms on this fixture.
These measurements are fixture-specific and must not be generalized to mixed music.

Unit/integration tests also cover actual WAV/FLAC/OGG/MP3 encode/decode, silence,
8/44.1/48 kHz resampling, opposite-polarity stereo, malformed/non-finite audio, cancellation,
offbeat preservation, authored tempo maps, offsets/drift, learned-shape transfer and
real paired exports. Windows and real-song/gameplay acceptance remain pending.

Analysis limits: 512 MiB source file, 20-minute duration, 128 MiB raw mono working data,
8–192 kHz input and 1–8 channels. The renderer caps waveform buckets at about 4,000
and beat/attack lines at 10,000 each. Those render limits do not truncate exported notes.
No manual tempo-map editor or automatic variable-tempo extraction is implemented.
MP3 encoder padding/decoder differences may affect alignment in TheGHOST; validate
against the exact audio import path. WAV/FLAC copies can simplify such diagnosis.

All existing GH3 compatibility restrictions remain. Neither successful export nor
low onset residuals establish playable GH3 compatibility or musical accuracy.
