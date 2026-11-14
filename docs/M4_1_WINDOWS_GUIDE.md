# 0.4.1 — guided Audio Studio test

Extract GH3_Chart_Studio_M4_1_v0_4_1.zip into a new folder. Use the installed Python
3.11 x64. Run setup_windows.cmd, then test_windows.cmd (129 tests), then
launch_windows.cmd. The title must say 0.4.1. This is a source release, not an EXE.

1. In Chart Converter, click Start audio workflow. Choose
   examples/audio/onset-study.wav first. Analysis runs in Audio Studio.
2. Remain in Audio Studio. The top message says Step 2. Expect 15 attacks and
   approximately 120 BPM for this fixture. Uncheck one attack in the Include column.
   The count changes to 14 of 15. Double-click a time/strength cell to audition from
   half a second before it; click 2. Review attacks to return to the checklist.
3. Click Create draft from selected attacks → Listen at the bottom. This button
   stays outside the scrolling area. The app stays in Audio Studio, now showing a
   horizontal note map: G/R/Y/B top to bottom, time left to right, notes scrolling
   left toward the white playhead. The generated fixture should have 14 Medium gems.
4. Test play/pause, volume, seek, stop and signed preview shift. +100 ms moves notes
   later. Apply shift, Undo and Redo work as in 0.4.0. The source is unchanged.
5. Click 4. Export chart + MIDI at the top. Choose a parent folder. Expect a new
   export folder with notes.chart, notes.mid, song.ini, settings.json and validation.json.
   validation.json includes attack_review and the excluded onset time.

No manual tab switching is required between steps 1–5. Pattern Library remains a
separate optional workspace. Existing-chart conversion remains in Chart Converter;
its Listen / timing button opens the same Audio Studio listening page.

## Optional settings

The visible Optional settings checkbox at the top of the review area reveals
Sensitivity, Minimum spacing, BPM override, Draft shift, Use the open chart’s tempo
map and Use local learned patterns. None is required for a basic audio-only draft.
Unknown BPM: set a manual value, then Reanalyze. An enabled tempo-map option with no
open chart now gives an explicit error. Learned patterns require a populated library.
Scroll within the review area as needed; the create button stays visible.

Changing attack selection after generation invalidates the old audio draft so it
cannot be accidentally exported. Recreate the draft after selection changes.
Attack exclusions are saved in validation.json and analysis diagnostics, but are
not a persistent editable project format; reanalysis resets the checklist.

## Instrument stem workflow

Choose the original mix in Step 1. Click Analyze a guitar / instrument stem and
choose an ALREADY separated WAV/FLAC/OGG/MP3. Analysis now uses that file while
listening uses the original mix. The source label names both. You can return with
Analyze original mix again. Both files must share the same time origin; no automatic
stem alignment or duration matching is performed. Confirm timing by listening.
The app does not run Demucs, UVR or any other separator in this release.

## Acceptance and limitations

Test audible output on Windows; no output device exists in development. The preview
is not a GH3 gameplay engine. HOPO highlighting is an estimate and does not force
no-strum gameplay. Full-mix attacks are not identified guitar notes. Stem analysis
can still contain artifacts and non-guitar sound. No pitch transcription, automatic
tablature search/import/alignment or per-note editor is claimed.

For failures, use Chart Converter → Save diagnostic log. Optional settings in
Audio Studio contains Save analysis / diagnostics. Include the step and exact error.
