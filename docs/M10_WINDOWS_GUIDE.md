# 0.10.0 — Three-fret Easy and complete converted difficulty sets

The four-fret conversion workflow now outputs:

| Game slot | Behavior |
| --- | --- |
| Easy | Replace with a three-fret G/R/Y version of the selected source |
| Medium | Replace with four-fret G/R/Y/B version of the selected source |
| Hard | Retain existing notes/phrases; copy selected source if absent or empty |
| Expert | Retain existing notes/phrases; copy selected source if absent or empty |

“Four-fret Expert” remains in the Medium slot: it retains the authored source challenge on four buttons. Both lower-fret tracks come directly from the selected source rather than cascading through a previously reduced difficulty. No arbitrary density thinning. Unsupported-fret taps are removed normally; sustain transfer is repeatable with the placement seed and respects the target lane count. Easy chord/extended sustain incompatibilities are repaired and logged. If removal would leave either target completely empty, all authored source event times are remapped to legal frets instead of inserting a one-note placeholder. This fallback is explicitly recorded.

## Windows test steps

1. Close the old app, extract GH3_Chart_Studio_v0_10_0.zip into a fresh folder and run START_WINDOWS.cmd.
2. In Four-fret Medium, open an Expert-only or Hard-only chart. Choose the source and click **Create Medium + Easy**. Keep sustain preservation enabled to retain excluded-fret holds where possible.
3. Select Easy in the preview: only Green, Red and Yellow should appear. Medium must contain no Orange. Verify Hard and Expert are both populated; previously existing tracks must remain authored (shared synchronization adjustments in bulk are separately logged).
4. Review/export to a new Artist - Song Title folder. Inspect validation.json → difficulty_completion (single song) or conversion → difficulty_completion (bulk) for copied slots, note counts, sustain transfers, repairs and fallback.
5. Repeat via Bulk folder conversion. The approval now explicitly replaces Medium + Easy and fills missing slots. Existing Easy/Medium in source FILES remain untouched; they are replaced only in outputs.
6. Import in TheGHOST. Verify it maps all four exported guitar difficulties. In Dolphin select each difficulty, including Easy, and verify loading, fret limits, synchronization, sustain endings and star power. Populated tracks address missing-chart cases but are not proof against all importer/game crashes.

## Limits / next milestone

This applies to single-song and bulk four-fret conversion. Clean Songs alone remains an all-difficulty cleanup tool and does not generate absent difficulties. The reserved density converter/audio generator and direct editor are separate workflows. Existing Hard/Expert unsupported markers or sustain issues are retained as before; use cleanup where needed. Copied Hard/Expert may be equally challenging; no claim of conventional difficulty balancing. Easy sustains may be shortened for compatibility; every repair is logged. Empty source charts remain errors. No native Windows/Dolphin execution for this release.

Next: test one Expert-only and one Hard-only source, selecting all four output slots in Dolphin. Only then broaden the batch.
