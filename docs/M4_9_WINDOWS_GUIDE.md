# 0.4.9 — identity preservation, Hard/Expert sources and HOPO review

1. Extract GH3_Chart_Studio_v0_4_9.zip into a NEW folder; close older running copies and run START_WINDOWS.cmd.
2. Open one chart. In Audio Studio → Listen / timing, use Display / copy source to select **Hard or Expert**, whichever exists in that file. Click Remove Orange → Medium. The new Medium has exactly the selected track's surviving G/R/Y/B gems, ticks and sustains. Original Hard/Expert tracks stay intact. Switching the display alone does not create a new copy—click Remove Orange after choosing a different source.
3. Choose/check the matching recording and timing before export. Click Export song folder.
4. Review Title, Artist, Album, Year, Genre, Charter, TrackNumber, AlbumArtist and Copyright. These values start from imported chart/song.ini metadata; supported audio tags fill missing fields. Changes affect the exported working copy, not source files. Extra original song.ini fields are retained; duration/delay are regenerated for the export.
5. Review any Medium-only marker removal or sustain repair. Then optionally check **Favor HOPOs in Medium runs**. Choose **Fast runs: up to ½ beat**, or **More generous: up to 1 beat**. Read the estimated event count and percentage above the detailed change report. This is not a promise that every chart can have mostly HOPOs.
6. Export. The folder is named **Artist - Title [Medium] - timestamp**, with Windows-invalid filename characters replaced and excessively long names shortened. Unicode identity is retained in metadata. Files inside remain notes.chart, song.ogg, song.ini, validation.json, IMPORT_README.txt for consistent import. No duplicate audio/MIDI/settings file is added.
7. In TheGHOST import notes.chart and song.ogg and map Medium. **Set the HOPO measure to 2.95** when using this assistance profile. Changing it changes how flip markers behave. Check notes in TheGHOST's viewer and then on Dolphin/Wii before accepting the song.

## What HOPO assistance does

N 5 0 is a HOPO/strum flip, not a playable Orange note and not an unconditional tap. The model follows the inspected TheGHOST viewer's natural-state rule at measure 2.95, integer millisecond timing, meter numerator and quarter-note fret periods. It replaces any reviewed existing Medium flip markers, retains naturally predicted HOPOs, and adds flips only for eligible changing-fret consecutive single-note events within the selected gap that are not already predicted HOPOs. It does not newly force first notes, repeated-fret runs or chords. A natural single-note HOPO following a chord can still occur if its fret differs from every fret in the chord.

HOPO assistance changes modifiers only. It does not thin a 900+ note chart, move notes, remap frets, shorten sustains, or edit Expert/Hard. Any sustain cleanup is a separate checkbox and change list. HOPOs require successfully starting/restarting the combo with a strum; this is not Clone Hero tap-note behavior. N 6 taps are not generated. Dense repeated-note/chord charts can remain below 50% HOPOs. Results are estimates, not verified game physics.

After export the Medium preview includes the flip markers and uses the profile's fixed threshold. Earlier candidate-gap preview controls do not override this profile. The paired MIDI exporter and explicit timing-shift operation remain strict about modifiers: complete timing adjustments before applying HOPO assistance. Use notes.chart for this profile.

## Metadata details and limitations

Title/artist and supported chart fields are written and read back from notes.chart and song.ini. Extra original ini values and the reviewed identity are recorded in validation.json. Existing asset filenames in custom ini fields are retained as metadata only; extra artwork/stems are not copied automatically.

Newly encoded Ogg files get supported title, artist, album, date/year, genre, track number and copyright tags, retaining other supported input audio tags. Existing Ogg Vorbis is copied byte-for-byte to avoid re-encoding: all its original embedded tags remain unchanged. If these differ from the reviewed chart/ini identity, validation.json reports the mismatch. The importer-facing chart and ini remain the reviewed identity. This version does not rewrite existing Ogg comments or embed charter/album-artist fields unsupported by the existing audio writer.

Tests run locally, including metadata, exact copies, marker round trips and a synthetic 1,000-note example; actual native Windows, TheGHOST conversion and Wii/Dolphin behavior remain pending. The supplied Tender Surrender chart yields estimated HOPO event proportions around 64.7% (half-beat) / 72.4% (one-beat) after reviewed cleanup. Those are not measured game results.

Next milestone: one real song passes identity, audible Ogg synchronization, four-fret gameplay and HOPO acceptance in TheGHOST/game. Batch features remain deferred.
