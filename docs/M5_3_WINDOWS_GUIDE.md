# 0.5.3 — Orange sustains to Blue

1. Close older copies, extract this ZIP into a new writable folder, and run START_WINDOWS.cmd with Python 3.11 x64 installed.
2. Open an existing chart. In Audio Studio / Listen & sync, choose Expert or Hard under Display / copy source.
3. Enable **Move Orange sustains to Blue (button 4) before removing Orange** beneath the source controls. It is unchecked by default so ordinary Orange-only removal remains available.
4. Click **Remove Orange → Medium**. Select Medium for review. Orange notes with positive sustain length become Blue at their original ticks and durations; Orange notes with zero sustain are removed.
5. If Blue already starts at the same tick, the result is one Blue note using the longer of the two sustains. Source Expert/Hard tracks are unchanged. The output label and report identify how many sustains were transferred.
6. Listen with the matching recording and export to a new song folder. Same-lane overlaps or unequal chord sustains still require explicit compatibility review. Trimming changes durations; do not approve it if you require the exact transferred sustain. Export uses notes.chart, song.ogg and song.ini plus validation/import instructions.
7. Reopen notes.chart and verify Medium contains no Orange, Blue carries the expected sustains, and Expert/Hard are unchanged. Test the intended importer/game before relying on gameplay compatibility.

Button 4 means the fourth playable fret, Blue (chart lane index 3). It does not mean chart lane index 4, which is Orange.

Known limits: no automatic solution for physically conflicting Blue sustains, no native Windows/audio-device/Wii test here. The first-run agreement remains per-user and persists across updates.
