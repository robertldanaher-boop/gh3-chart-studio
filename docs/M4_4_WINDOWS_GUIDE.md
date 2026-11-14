# 0.4.4 — pattern refresh and Orange-only Medium

Extract GH3_Chart_Studio_v0_4_4.zip into a new folder and double-click
START_WINDOWS.cmd. Python 3.11 x64 is already installed on Bob's machine.

## Pattern library

Scan a chart folder. The table now fills automatically when the scan completes.
The category filter resets to All categories. The newest 200 pattern rows are
shown, so fresh imports aren't hidden behind older rows. "1 new" means one chart
file was imported, not one table row; each row represents an extracted pattern
window/difficulty. Browse patterns and category filtering remain available.

## Copy Expert or Hard to Medium, deleting only Orange

1. Open Audio Studio and click 3. Listen / timing, or open a chart in Chart Converter
   and click Listen / timing. The listening panel includes its own Open chart button.
   If no file is loaded and Step 3 is disabled, first use Chart Converter → Open chart.
2. Open the .chart or .mid and choose Expert or Hard in Display difficulty.
   Any available Easy/Medium/Hard/Expert track can be displayed; the Orange-copy
   action is enabled only for Expert/Hard. Viewing another difficulty doesn't edit it.
3. Click Remove Orange → Medium. This is a separate action from the contour-remapping
   converter. All Green/Red/Yellow/Blue gems keep their lanes, onset ticks and sustain
   lengths. An Orange-only onset disappears; a chord loses only its Orange gem.
4. Display switches to the new Medium. Select Expert or Hard to compare: those
   tracks remain intact in the output working copy. Existing Medium is replaced in
   the new output, not in the original source file. Source phrases copy to Medium.
5. Choose preview audio if you want to listen; no audio file is required to export.
6. Click 4. Export chart + MIDI. Choose a parent folder; a new folder is created.
   Both formats are reopened and checked. In TheGHOST select Medium from either
   notes.chart or notes.mid (prefer .chart for short sustains), then verify gameplay.

## Compatibility limits

Orange-only mode does not strip tap/forced/open markers, normalize sustained chords,
repair overlaps or remap remaining frets. Unsupported source/retained markers that
cannot be preserved in paired MIDI export cause an explicit error. A Medium track
with disjoint/extended sustains or no remaining notes is rejected. Other existing
validation gates remain, including nonzero Offset at paired export.

Do not use all-track cleanup if preserving the original Expert/Hard gameplay is
mandatory: that is a separate reviewed transformation. This release does not offer
Medium-only marker repair or a lossless source-preserving .chart-only export profile.
The two previously supplied marked charts may still need that future workflow;
we do not claim Orange-only mode exports them unchanged through the MIDI gate.
No in-game compatibility claim is made solely from a successful structural check.
