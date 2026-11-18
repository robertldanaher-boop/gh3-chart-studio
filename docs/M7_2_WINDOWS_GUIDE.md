# Version 0.7.2 — Synchronization and tempo-anchor review

## Install and open
1. Close the old application and startup window. Extract the complete
   GH3_Chart_Studio_v0_7_2.zip into a fresh writable folder.
2. Run START_WINDOWS.cmd. Let setup, tests and launch finish. Confirm version 0.7.2.
   Existing Python 3.11 x64 can be reused; requirements install into the new folder.
3. Choose Clean my songs and scan your song folder or parent collection again.
   Reviews are session-only; rescanning clears earlier review choices.

## Resolve nonzero Offset or song.ini delay
1. Click the affected song row, then Review synchronization below the song list.
   If unavailable, first resolve the chart/audio error or choose the correct recording.
2. The dialog shows the original chart Offset in seconds and song.ini delay in
   milliseconds. Choose a timing interpretation. Positive total shift means notes
   later relative to the original recording; negative means earlier.
   - Use song.ini delay uses that value alone.
   - Use chart Offset × 1000 uses that value as a notes shift, without adding delay.
   - Use opposite chart Offset tests the opposite direction for a legacy source.
   - Custom total shift lets you enter the total intended correction, including any
     stored offsets. Zero is an explicit choice to use the existing BPM timeline.
   Do not assume two nonzero fields should be added: they may describe the same
   correction. The tool does not infer the right choice from the music.
3. Select Expert or Hard (other existing difficulties are also available). Choose
   your audio output, then Play / pause. The horizontal chart uses the original
   recording clock. Drag the seek slider and compare beginning, middle and end.
   Change to Custom total shift to fine-tune in milliseconds. Changing timing
   clears the confirmation checkbox. A constant shift cannot fix increasing drift
   or a different recording; cancel rather than approving a bad match.
4. Read the proposed chart lead-in and audio silence. No recording is trimmed;
   exact chart tick lengths and the tempo/meter relationships are retained. A new
   shared lead-in can make the exported file longer. Existing cleanup sustain
   repairs are separate and remain listed in the selected-song details.
5. Check I checked the beginning, middle and end, then Use reviewed timing.
   The song is rechecked. Other errors may still require attention. Cancel leaves
   the row unchanged. Editing title/artist retains the timing review; changing
   chart, recording or song.ini invalidates it and requires another review.
6. Check the song's Use box (a previously blocked row may remain unchecked), or
   click Ready only. Review its changes, check Apply the cleanup changes I reviewed,
   then Start cleaning. The displayed output parent is used; a new folder is created.

## Resolve SyncTrack tempo anchors
A valid paired editor anchor whose timestamp agrees with the current BPM map to
within 1 ms becomes a listed cleanup change. No musical tempo or note timing is
changed when removing that anchor. Approve the usual cleanup changes and export.

If an anchor timestamp differs, the song remains blocked for review. Click Review
synchronization. The dialog shows anchor ticks, stored times and current BPM-map
times. Choose Custom total shift = 0 to audition that map without an additional
shift, or review the song's offset/delay if present. If the existing BPM map is
correct throughout the song, also check Keep existing BPM map; discard editor
anchors, confirm your listening review and apply. This removes the editor locks;
it does NOT reconstruct a tempo map from their timestamps. If timing drifts or
is incorrect around tempo changes, cancel and correct the map externally.

Malformed, duplicate or unpaired anchors remain blocked with an explanation.
The reported tick 13824 identifies a position, not necessarily a damaged note.
Its actual chart has not been supplied, so it cannot be certified from the error alone.

## Verify the exported folder
- notes.chart and song.ini have zero Offset/delay. Import the exported notes.chart
  WITH its exported song.ogg; do not mix the new chart with the original audio.
- Do not apply the old delay again in TheGHOST. Check the importer has no inherited
  manual delay for this song, and listen again after import.
- validation.json records source values, reviewed total shift, translated chart
  ticks, added audio frames, sample rounding error and individual anchor removals.
  cleanup.log also records each synchronization plan.
- Source files must remain unchanged. Verify title/artist and all exported
  difficulties; Medium must contain only Green, Red, Yellow and Blue.
- Verify timing at beginning, middle, end and both sides of tempo changes in
  TheGHOST and Wii/Dolphin. Structural tests cannot certify audible or game behavior.

## Evidence and limits
257 tests passed in 23.15 seconds on Python 3.11.18/Linux, Qt offscreen. Focused
GUI-only checks also cover the wording/layout. See M7_2_TEST_RESULTS.txt and
M7_2_GUI_TEST_RESULTS.txt. Tests include actual Vorbis decoding, impulse placement,
source hashes, tempo-crossing sustains, positive/negative shifts, zero-offset export,
anchor conflicts, dialog confirmation and larger/wider fonts at 1024x700.

No native Windows build, audible-device test or Wii/TheGHOST execution here. Bob
confirmed that 0.7.1 launched on Windows; 0.7.2 still needs native acceptance.
Review is per song, not bulk automatic synchronization. Shifts are limited to
±60 seconds; an unusual initial tempo requiring over two minutes of audio padding
is rejected. Audio is re-encoded to Vorbis when silence is added. Padding is rounded
to the nearest sample; no source samples are removed or resampled. No new runtime
packages were added. This is a source release with Windows build instructions.

Next milestone: test one affected song and its export on Windows, then verify it
in TheGHOST/Wii before approving the rest of the collection.
