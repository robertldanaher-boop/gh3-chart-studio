# Windows testing — version 0.4.0

Extract this ZIP into a new writable folder. Do not merge it into the old folder.
Python 3.11 x64 is already installed on Bob's machine; `py -3.11 --version` confirms
it. Run setup_windows.cmd, then test_windows.cmd, then launch_windows.cmd.
No Python 3.11.0 downgrade is required. No EXE is supplied.

## Audio only — no source chart required

1. Click Start from audio and select WAV/FLAC/OGG/MP3. Analysis starts automatically.
2. Leave Use open chart tempo map unchecked. Leave Use local learned patterns
   unchecked unless the pattern database contains successful imports.
3. Review attacks/BPM; set BPM override and reanalyze if needed. With no detected
   attacks or unknown BPM, the app explains what needs correcting.
4. Click Create four-fret draft. The Converter shows an exportable Medium result.
5. Open Listen & Sync. The selected audio is already loaded. Click Play / pause.
   Notes descend to the white line according to the media playback clock. Adjust
   volume, seek, or stop. The first known fixture attack is at 0.5 seconds.
6. Try +100 ms in Preview shift: notes should arrive later while audio is unchanged.
   Click Apply shift to output, then Undo shift and Redo shift to compare.
   Apply changes all note/phrase/event times, not tempo/meter. Tick rounding applies;
   negative positions are rejected. Applying a shift invalidates older variant choices.
7. Return to Converter and export. To generate three learned variations, first scan
   a library, then choose a style and Generate 3 learned variations. Regenerating
   starts from the unshifted source; timing edits affect the selected output only.

Audio onset drafts are full-mix attack estimates, not verified guitar transcription.
No sustain/chord/Star Power inference or instrument isolation is claimed.

## Existing chart with unsupported actions or sustains

1. Open the chart. Structural problems other than overlaps still block loading.
2. Click Review GH3 cleanup. Read the list of exact changes and remaining errors.
3. Marker stripping removes forced-HOPO/tap/solo/other unsupported markers and
   open-note events; it does not invent frets for open notes.
4. If necessary, enable sustain shortening. It uses each chord's shortest duration
   and trims to the next onset, across all retained difficulties. This explicitly
   changes durations; cancel if that result is not acceptable.
5. Apply the reviewed copy. The source file is untouched. Restore original chart
   discards the working-copy cleanup. Convert or generate variations, inspect the
   outcome, and export to a new folder. validation.json includes source_cleanup.
6. In Listen & Sync choose the matching audio, then review timing as above.

The two uploaded songs scan into 200 and 228 windows on a fresh database. Existing
failed entries can be rescanned. The extraction version changes source hashes;
older successful corpus snapshots and ratings remain in the database. To avoid
mixing snapshots, choose a new database via Pattern Library.

## HOPOs and gameplay acceptance

Natural HOPOs are not disabled. The preview outlines conservative candidates:
consecutive single notes on different frets within the displayed beat threshold.
Changing this threshold or the highlight checkbox affects visualization ONLY.
A quick blue-yellow-blue may qualify; repeated same-fret notes/chords are not
highlighted. Actual no-strum behavior depends on game/import settings and a valid
preceding hit. No modern tap marker or forced-HOPO export is synthesized.
TheGHOST supports a legacy chart HOPO convention, but equivalent paired MIDI
behavior has not been verified. Do not substitute tap markers as a fallback.

Test the exported Medium on TheGHOST, then Dolphin/Wii: confirm four lanes, audio
alignment, tempo changes, sustain endings and actual HOPO behavior. Record the
importer's HOPO settings and any discrepancy. No runtime compatibility is certified.

## Playback limitations

No audio-device output was available in the development environment. Playback clock,
duration, pause/seek and decode were checked; audible sound and latency need Windows
acceptance. Codec/backend availability can differ. Try the bundled original
examples/audio/onset-study.wav first. A missing device or decoder error is displayed.
No controller input, hit scoring, per-note editor, loop points or playback-rate
control is implemented. This is a review simulation, not a GH3 engine.
