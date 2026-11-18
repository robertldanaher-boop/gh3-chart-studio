# Milestone 7.2 — November 18, 2026

## Functional changes
Added per-song synchronization review to Clean songs. Stored Offset/delay values
are visible, interpretations are explicit, and preview offers difficulty, device,
volume, play/pause/stop and seeking. An acknowledgement enables applying the review;
Cancel leaves the row unchanged. No independent audio-generation work is added.

A reviewed total shift is normalized to zero-offset output using whole initial-bar
chart translation and leading audio silence. Every note, sustain endpoint, phrase,
modifier, event and subsequent tempo/meter change translates together. Tick lengths
and tempo values remain exact. Audio padding alone is rounded to the nearest sample.
This handles negative shifts without negative note ticks or audio trimming. The
usual cleaner's explicitly reviewed sustain repairs remain a separate operation.

Reviews bind to chart/audio paths and content hashes, including song.ini. Metadata
edits can retain a review; changed source assets expire it. Export records the plan
in validation.json and cleanup.log, and verifies the padded Ogg frame count and
full decode. Metadata, preview timestamps and duration are carried into the export.
The old delay warning is replaced with a zero-importer-delay instruction after review.

Cleaner import now preserves parsed editor anchors for inspection. Matching paired
anchors (within 1 ms of the BPM map) are listed for removal without tempo changes.
Conflicting timestamps block until the user explicitly retains the existing BPM
map after listening. No tempo is guessed or synthesized from anchor timestamps.
Invalid, duplicate or unpaired anchors remain blocked. Strict converter reads and
unreviewed chart writes still reject anchors. No tests or startup gates were removed.

## Files created or changed
Created gh3studio/synchronization.py and gh3studio/sync_gui.py; created
tests/test_synchronization.py and tests/test_sync_gui.py.
Changed gh3studio/cleaner.py, cleaner_gui.py, audio_export.py, song_export.py,
chartio.py, model.py, validation.py, __init__.py and pyproject.toml.
Updated README.md, CHANGELOG.md, HANDOFF_LATEST.md, docs/WINDOWS_TEST.md and
COMPATIBILITY.md. Added this log, M7_2_WINDOWS_GUIDE.md, M7_2_TEST_RESULTS.txt,
M7_2_GUI_TEST_RESULTS.txt and screenshots/m7_2-sync-review.png.
The release includes a Git bundle and exact RELEASE_COMMIT.txt.

## Tests performed
Initial targeted run exposed an existing expectation that blocked offset rows
have no exportable Song. Kept that invariant and retained a separate read-only
source for synchronization preview. Original tests were unchanged.

Final full suite: 257 passed in 23.15s on Python 3.11.18/Linux, PySide6 6.8.3,
QT_QPA_PLATFORM=offscreen. Thirty-two new cases cover:
- All chart-object timestamps across multiple tempo/meter changes, both shift signs,
  zero and ±60-second boundaries, sustain lengths and unchanged source objects.
- Invalid/nonfinite shift rejection.
- Decoded stereo impulses at their original sample positions plus exact padding;
  full frame counts, metadata and original file hashes.
- Real cleaner folder export with zero Offset/delay, reports and source preservation.
- Review invalidation for chart, song.ini, audio contents or audio path changes;
  metadata-only rechecks without double shifting.
- Matching/conflicting/malformed/unpaired anchors and unsafe unreviewed writes.
- GUI presets, preview track selection, Cancel, confirmation reset, row recheck,
  actual export, independent converter state and wide/larger-text dialog dimensions.

A focused GUI-only run passed 15 cases in 3.45s; see its separate log.
The final full run also includes the preview-timestamp and duplicate-anchor checks.
A supplemental real export check confirmed chart Length matches the padded Ogg
duration (2.8s for a 1s recording with the reviewed 200ms shift).
Visually inspected the actual dialog at 940x660. Prior small-window regressions
remain in the complete suite. No native Windows execution or game acceptance here.

## Reference and license review
The existing format reference project GuitarGame_ChartFormats is CC0-1.0; consulted
its documentation, not copied implementation code. No new dependency or borrowed
source was introduced. Existing Nanook/TeamGHOST credits remain.
https://github.com/TheNathannator/GuitarGame_ChartFormats/blob/main/README.md
https://thenathannator.github.io/GuitarGame_ChartFormats/Chart-File-Formats/chart-format/Format-Overview/
https://github.com/TheNathannator/GuitarGame_ChartFormats/blob/main/docs/Chart-File-Formats/song-ini/Standard-Tags.md
Anchor documentation describes editor timing locks paired with BPM events; some
source tools treat timing fields differently. We require explicit shift selection
and never add both timing fields automatically. Conflicts do not rewrite the map.

## Limits, Windows testing and next milestone
Follow M7_2_WINDOWS_GUIDE.md for exact install, review, export and importer checks.
This is per-song human review, not automatic acoustic alignment or tempo-map repair.
No affected user chart/recording was supplied; the tick 13824 case is not certified.
Session-only reviews, ±60-second shifts, two-minute padding cap, Ogg re-encoding
when padding, conservative marker/sustain cleanup and other prior limitations remain.
Native Windows, audio devices, TheGHOST and Wii/Dolphin require user testing. No
actual Claude participation is claimed. Next: one affected song end-to-end, then
remaining collection errors based on the logs.
