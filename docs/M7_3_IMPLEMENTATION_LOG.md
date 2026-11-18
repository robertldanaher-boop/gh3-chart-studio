# Milestone 7.3 — November 18, 2026

## Functional features
Automatic source-audio recovery integrated into export_ogg. On eligible SoundFile
errors, a packaged FFmpeg process strictly decodes to temporary floating-point WAV.
A readable source header must match decoded frames/rate/channels; the existing
Vorbis writer, synchronization padding, metadata reconciliation and full read-back
then run once on that PCM. Healthy Vorbis reuse remains. No network call during
recovery, no manual conversion, no modification to original audio or chart files.

The original failure and fallback details are recorded in validation.json. Cleaner
results identify automatic recovery, and cleanup.log records AUDIO RECOVERED.
Errors identify the file and processing stage. Write/metadata-output/validation
errors do not trigger inappropriate source recovery. If recovery fails, atomic
song export removes its stage and reports both errors. Temporary PCM is cleaned.
The decode subprocess has a 180-second timeout and hides its Windows console.

Startup's existing pinned dependency workflow installs imageio-ffmpeg 0.6.0.
No other dependency versions changed. The Windows wheel hash was checked against
the updated lock and its FFmpeg 7.1 executable and license strings inspected.
Windows builds collect the provider package data and executable license/build notices.

## Files created or changed
Created gh3studio/audio_fallback.py and tests/test_audio_fallback.py.
Changed gh3studio/audio_export.py, cleaner.py, cleaner_gui.py, __init__.py;
pyproject.toml, requirements.txt, requirements-windows.lock, build_windows.cmd,
tools/collect_licenses.py, README.md, CHANGELOG.md, HANDOFF_LATEST.md,
THIRD_PARTY.md, docs/CREDITS.md and docs/WINDOWS_TEST.md.
Added this log, M7_3_WINDOWS_GUIDE.md, M7_3_TEST_RESULTS.txt,
M7_3_REAL_OPUS_RESULT.json, FFMPEG_DEPENDENCY.md and provider/FFmpeg notices.
Release includes Git bundle and RELEASE_COMMIT.txt. No user recording is bundled.

## Tests performed and results
Focused audio suite: 42 passed. Complete suite: 263 passed in25.48s on Python
3.11.18/Linux, PySide6 6.8.3, Qt offscreen. Six new cases test real alternate decoding
of synthetic Opus after a simulated primary decoder failure (mono and stereo,
including padding), partial-output replacement, metadata, unchanged sources,
write errors without retry, both decoders failing and atomic rollback, rejected
header/frame mismatch, and subprocess timeout. Existing layout, timing, chart,
MIDI and four-fret Medium checks remain enabled.

Separately ran the actual user's original song.opus through inspect_chart and
export_cleaned with a synthetic Expert chart. Native SoundFile reproduced the
failure; automatic FFmpeg recovery succeeded, and the resulting Ogg fully decoded
with 9,710,324 frames at48kHz stereo. Header count matched, input SHA-256 unchanged,
recovery flag present in returned result and AUDIO RECOVERED present in cleanup.log.
Evidence in M7_3_REAL_OPUS_RESULT.json. This verifies the actual supplied recording,
not its missing real chart or in-game synchronization.

Dependency/licensing review: wrapper BSD-2-Clause; bundled native decoder GPLv3+,
not BSD. Added separate notices and distribution limitations. No binary is included
in this source ZIP; setup obtains the upstream pinned wheel. See FFMPEG_DEPENDENCY.md.
Native Windows executable was inspected but not run. No compiled Windows build or
game test occurred. No claim of Claude participation.

## Known limitations and next milestone
Readable-header/source decode failures are the primary supported recovery path.
Scan-time header rejection remains a blocker. Output-write and generated-output
validation problems are not repaired by changing the input decoder. Corrupt files
or mismatched decoded lengths may still fail intentionally. Cancellation is between
songs, with at most the 180-second FFmpeg decode timeout for the active fallback.
Temporary PCM disk space and Vorbis re-encoding are required when recovery is used.

Follow M7_3_WINDOWS_GUIDE.md exactly: fresh extraction, START_WINDOWS.cmd, scan the
original Opus folder, review/check/Start cleaning, verify automatic recovery logs
and exported Ogg. Next confirm this path on Bob's Windows computer and one exported
song in TheGHOST/Wii before expanding decoder behavior.
