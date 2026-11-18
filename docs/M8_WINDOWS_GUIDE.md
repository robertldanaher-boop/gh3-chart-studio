# 0.8.0 — Interactive chart editing

1. Close the old version. Extract GH3_Chart_Studio_v0_8_0.zip into a new folder and run START_WINDOWS.cmd. Dependencies are installed as needed and the automated suite runs before launch.
2. Start with a cleaned chart. In Four-fret Medium, choose the chart and either review its source difficulty or create/review Medium. Select the desired displayed track.
3. Click **Edit displayed chart…**, or right-click the playback chart preview. A larger editor opens with an independent working copy. The small static converter overview remains read-only.
4. Choose Expert, Hard, Medium or Easy when present. Choose a snap interval. Use the horizontal time slider to reach any portion, with or without audio. Play/pause uses the selected recording; turn Follow audio off to inspect a fixed section while listening.
5. Right-click inside the editor: Add note, Delete note, Set sustain length, Prefer HOPO, Prefer strum, Natural state, Add/remove star power, or Insert pattern. Note edits use the clicked lane and snapped time. Pattern text accepts space-separated G R Y B (O outside Medium), up to 64 notes. Pattern spacing uses Snap. Purple bars show star power.
6. Drag a note head to change its time/fret. Drag a square sustain-tail handle to extend or shrink it. The dashed outline previews the drag. For a tap or very short sustain, use Set sustain length first. Chord sustain edits change all members to the same duration; invalid overlaps/duplicates are rejected with a message.
7. Undo/Redo or Ctrl+Z/Ctrl+Y restore exact chart state. Other difficulties are retained. Medium rejects Orange, including inside inserted patterns.
8. Click **Export edited song…**. Select matching audio if absent, then a parent folder. A NEW timestamped folder contains notes.chart, song.ogg, song.ini, validation.json and import instructions. Audio recovery from 0.7.3 remains available. Export failures appear in the editor status and the main diagnostic log. The editor never overwrites the source chart.
9. Listen and verify timing, sustain behavior, star-power boundaries and HOPOs in Dolphin. HOPO flips use TheGHOST measure 2.95 and still require an initial/recovery strum. They are not unconditional tap notes. Confirm a changed Expert/Hard and an edited four-fret Medium both behave as expected.
10. Close editor. If edits have not been exported, confirm discard or cancel closing. Edits are not automatically merged into the converter workspace: reopen the exported notes.chart for further work.

## Limits and next acceptance

No native Windows run or new editor/game acceptance has been performed by the developer. Bob reported 0.7.3 tested and playing in Dolphin on November 18, 2026; this is user-reported validation of that release, not proof of the new editor's mechanics.

Use Clean songs first for unresolved offsets/anchors, unsupported markers, Orange in an existing Medium, or incompatible sustains. The first editor refuses incompatible working copies rather than silently repairing unrelated notes. HOPO outcomes can change when surrounding notes change. Star-power phrase length is entered in beats; phrase dragging and multi-note selection are not included. No auto-save/project recovery yet; export before closing. Editing pauses playback when starting a drag or opening a context menu. Source audio and metadata are retained via the existing checked folder exporter. Editor export is .chart only; it does not create MIDI because explicit HOPO flips are not supported by the MIDI exporter.

Next milestone: user acceptance in Windows/Dolphin, followed by multi-note selection/copy/paste and recoverable editor sessions.
