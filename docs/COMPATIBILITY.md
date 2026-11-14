# Supported interchange profile and evidence

## Grounded source review

TheGHOST upstream reviewed at commit `27f143205d3698a1fca49f34c0710bd8347e8cb3`:
https://github.com/Nanook/TheGHOST

Files inspected directly: `TheGHOSTCore/Notes/Chart.cs`, `Mid.cs`, `MidNote.cs`.
No TheGHOST code is incorporated or redistributed. This is a behavioral reference.

Findings used in this implementation:

- Chart difficulty names use MediumSingle, ExpertSingle and HardSingle.
- Chart S 2 is Star Power; S 0 / S 1 are face-off player 1 / player 2.
- MIDI difficulty bases are 60/72/84/96. Five playable gems occupy base+0..4.
- TheGHOST reads per-difficulty SP at base+7 (Medium 79), face-off at base+9/+10.
  Output deliberately uses that legacy profile. Modern shared SP 116 is supported
  on input but not emitted. Modern solo marker 103 is not mistaken for SP in Modern mode.
- Its MIDI parser discards note lengths below 160 ticks, independent of PPQ.
- Its chart parser uses the first gem's duration for a chord, treats meters as /4,
  and computes sustain lengths using the starting tempo rather than integrating
  all changes. Both readers add/normalize durations internally.
- Chart N 5 / E * participate in its HOPO mask. Equivalent modern MIDI forcing
  is not faithfully implemented by this old importer. Forcing/tap/open source
  modifiers therefore block this converter, rather than inventing equivalence.
- No battle-power synthesis or purple tap-note emulation is implemented.

Modern format reference:
https://github.com/TheNathannator/GuitarGame_ChartFormats
Read .chart Format-Overview and MIDI Tracks/5-Fret-Guitar. This documentation is
used as a specification reference, not copied implementation code.

## Guarantees established by automated tests

The generated Medium has only G/R/Y/B. Source difficulties are retained as guitar
tracks; the original input file is never written. Retained event tick positions,
sustain lengths, tempo positions, signatures and supported phrases are preserved.
MIDI has explicit balanced note-on/off pairs, off-before-on ordering at shared ticks,
and PART GUITAR naming. Source onsets are not quantized.

Formats have different tempo precision. .chart BPM is in 0.001 BPM increments;
MIDI tempo is integer microseconds per quarter. Export measures absolute time drift
at tempo boundaries and the last note tail and rejects drift above 1 ms. This is
representation validation, not an audio alignment measurement. Non-sustained
chart notes become 1-tick MIDI notes; existing MIDI note durations remain intact.

Paired export writes to a temporary sibling, reopens both files, validates their
content, then renames to a new destination. It refuses any existing destination.
If validation/writing fails, no complete output folder is reported.

## Deliberate restrictions

- Only lead guitar difficulty tracks are represented; other instruments are omitted
  with warnings. No claim of lossless full-band conversion.
- Forced HOPOs/taps/opens and other source instrument events block conversion.
  Unsupported modifiers on retained difficulties also block paired MIDI export.
- Disjoint chord tails and extended sustains in the selected source block conversion.
- Chords exceeding the selected cap are reduced and counted, not silently merged.
- Nonzero chart Offset blocks paired export because TheGHOST does not apply it
  consistently across formats. Apply the original offset explicitly in TheGHOST.
  song.ini delay is reported for manual application, never silently applied twice.
- Non-/4 meters export structurally but carry a TheGHOST warning.
- Same-lane sustain overlap, duplicate gems and conflicting tempo changes are errors.
- Natural HOPO eligibility can change when lanes change. No claim of exact source
  HOPO preservation. This release prioritizes valid notes and exact retained timing.
- MIDI metadata beyond a standard title is application metadata plus song.ini;
  other applications may ignore the private text event. Use song.ini for interchange.
- No audio analysis, neural training, playback, full chart editor or batch generation UI.
  Version 0.2.0 adds folder scanning for the pattern library; see PATTERN_LIBRARY.md.
- MIDI export is TheGHOST-oriented. Clone Hero/YARG compatibility is not certified.
- Import is limited to 32 MiB. A 100,000-gem warning is a review threshold, not a
  researched hard limit for GH3.

## Not yet verified

Windows launch/build, TheGHOST import, Dolphin/Wii playability, subjective difficulty,
audio sync, real-user chart corpus coverage and controller HOPO/whammy behavior.
Source review and format checks do not replace these tests.
