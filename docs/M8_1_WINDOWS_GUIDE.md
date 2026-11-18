# 0.8.1 — Automatic song.ini synchronization

## Windows test steps

1. Close the previous version. Extract GH3_Chart_Studio_v0_8_1.zip into a fresh folder. Run START_WINDOWS.cmd; setup, tests and launch remain combined.
2. Open Clean Songs and scan the ORIGINAL folder/collection that previously showed “Nonzero Offset or song.ini delay needs manual synchronization review”.
3. Select an affected song. Details should show **Synchronization: automatic — song.ini delay only**. There is no synchronization confirmation dialog. A song with no unrelated errors is ready for the usual cleanup/export selection.
4. Select the songs, approve the normal cleanup changes and click Start cleaning. The ordinary cleanup approval remains; the per-song synchronization review is no longer required.
5. Inspect the export: notes.chart Offset=0, song.ini delay=0, audio is song.ogg. validation.json and cleanup.log record original Offset/delay, policy, chart translation and audio padding.
6. Import the new output with zero additional importer delay and check playback in Dolphin. Do not apply the old song.ini delay again.
7. If an actual timing issue appears, select the ORIGINAL song and open **Timing tools (optional)…**. This retains the previous listen/adjust/manual-review workflow and overrides the automatic policy for that song in the current session. Export a new copy.

## Policy

This implements Bob's explicit default after his reviewed songs were correctly timed with “Use song.ini delay”. The automatic total notes shift is song.ini delay in milliseconds. Positive means notes later relative to audio. Chart Offset is never added. If delay is absent or zero, the selected shift is zero even when chart Offset is nonzero. Both fields are zeroed in the output. Original files are unchanged.

The existing exact translation/padding algorithm is reused: chart objects and tempo/meter changes move together, sustain lengths remain intact through synchronization, and audio may receive leading silence without trimming source samples. Separate cleaner sustain repairs remain independently reported. Metadata edits reload the source and recompute; the normalized export does not receive a second adjustment when rescanned.

Manual overrides take precedence and remain bound to source hashes; changing their inputs expires that override. Rescanning without an override recomputes the automatic policy from current source files. Automatic synchronization does not decide conflicting editor anchors, fix malformed timing values, or bypass existing ±60-second shift and padding limits. These are distinct problems.

## Validation and next milestone

Automated tests cover positive/negative/missing/zero delay, conflicting chart Offset, complete export/read-back, input hashes, metadata rechecks, rescanning without double padding, manual overrides, changed inputs and retained anchor/limit checks. Full results: M8_1_TEST_RESULTS.txt. No native Windows/Dolphin execution performed for this release. Bob's prior Dolphin playback confirmation applies to 0.7.3.

Next milestone: confirm the previously blocked collection cleans without timing prompts and plays correctly in Dolphin. Revisit timing only if an actual issue is observed, as requested.
