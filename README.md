# GH3 Chart Studio 0.3.0 — Milestones 1–3

A Python 3.11 / PySide6 desktop converter for authored Expert or Hard guitar tracks.
Expert Medium is written into **MediumSingle** and MIDI **PART GUITAR pitches 72–75**.
Orange (chart lane 4 / MIDI pitch 76) is blocked in Medium at conversion and export.

This is a tested **source release**. Windows, TheGHOST, Dolphin and Wii execution have
not been tested here. No prebuilt Windows EXE is included.

## Start on Windows 10/11 x64

1. Extract the complete ZIP into a normal writable folder (not inside the ZIP viewer).
2. Install **Python 3.11 x64**, including the Python launcher (`py`).
3. Double-click **setup_windows.cmd**. Internet is required for the first installation.
4. Double-click **test_windows.cmd** to run the automated suite.
5. Double-click **launch_windows.cmd**.
6. Open or drag in `examples/technical-study.chart`.
7. Select Expert, leave Density at 6, and click **Convert & validate**.
8. Review the counts/warnings and preview. Select Source to compare.
9. Click **Export .chart + MIDI…**, then choose a parent folder. A new dated folder is
   created containing both formats, metadata, settings and a validation report.

For your own song, import its original audio separately in TheGHOST and choose
**either notes.chart or notes.mid**. Prefer `.chart` for short sustains. Do not rely
on folder auto-detection when both files are present. Reimporting our MIDI requires
**Legacy MIDI / TheGHOST** mode. The default Modern mode handles pitch 116 phrases.

## New in 0.3.0

The **Audio Analysis** tab imports WAV/FLAC/OGG/MP3, detects candidate attacks,
estimates constant tempo, supports manual BPM and draft shifts, shows a real waveform,
and creates reviewable four-fret onset drafts. It can preserve an authored tempo map
and use local learned patterns. Timing diagnostics distinguish possible offset/drift
issues. See `docs/AUDIO_ANALYSIS.md`. This is not verified guitar transcription.

## Added in 0.2.0

The **Pattern Library** tab recursively scans chart folders into local SQLite storage,
extracts reusable patterns, supports similarity search and preference ratings, and
generates three seeded variations. See `docs/PATTERN_LIBRARY.md` for the exact workflow.
This is statistical pattern retrieval, not neural training or audio analysis.

## Implemented

- Strict .chart parsing and MIDI type 0/1 PPQ import for guitar.
- Expert/Hard conversion with deterministic contour-aware four-fret mapping.
- Density, chord and movement controls; maximum 1–3 simultaneous gems.
- Default density retains all authored onsets. No notes inserted to increase density.
- Original guitar difficulties retained; existing Medium replaced in the new output only.
- Tempo positions, retained onsets and sustain ticks preserved in the internal model.
- Legacy per-difficulty Star Power and face-off serialization; modern SP import.
- Metadata from chart, MIDI internal metadata and adjacent song.ini.
- Real note preview, single-file drag/drop, background workers, conversion cancellation.
- Save/load settings, diagnostic log, atomic new-folder export and read-back checks.

The preview is read-only and limited to 2,000 gems. The engine uses authored chart
structure, stored patterns and the optional onset-analysis pipeline; it does not train
a neural model or claim measured real-song musical quality.

## Controls

| Control | Actual behavior |
|---|---|
| Density 6 | Preserve every source onset |
| Density 1–5 | Suppress close events, retaining quarter-note anchors and section/phrase starts |
| Chords 1–2 / 3–4 / 5–6 | Up to 1 / 2 / 3 gems, also bounded by Max chord gems |
| Movement 1–6 | Reduce travel at low settings; favor contour at high settings |

Chord reduction keeps outer voices (plus a middle voice when three are allowed).
A deterministic candidate score favors contour and avoids collapsing changed source
patterns into repeated target shapes. This is a first heuristic, not proven musical
understanding or a trained model. Every removed gem/event is reported.

## Limitations and compatibility

Read `docs/COMPATIBILITY.md` before importing songs. Forced HOPOs, modern taps,
open notes, disjoint/extended source sustains, tempo anchors and nonzero chart Offset
are not safely translated in this version. Some block conversion, others paired export.
Other instruments are not exported. Audio is neither modified nor copied.

Binary packaging: run **build_windows.cmd** after setup. It runs tests before
PyInstaller. Keep the resulting `dist/GH3ChartStudio` folder intact. The build recipe
is provided but has not been executed on Windows. It is dependency-pinned, not a
claim of byte-identical executables on different Windows machines.

## Project files

- `gh3studio/`: data model, parsers, converter, validator, export service, GUI,
  pattern database, scanner, variation engine and audio-analysis pipeline.
- `tests/`: unit/integration/GUI regression tests.
- `examples/`: original synthetic study and verified paired exports (no commercial music).
- `presets/`: working JSON presets.
- `requirements-windows.lock`: transitive Windows dependencies pinned with hashes.
- `docs/`: architecture, compatibility research, Windows acceptance steps and implementation log.
- `tools/`: optional independent parser check and license collection utility.
- `licenses/`: collected dependency notices; `THIRD_PARTY.md` explains use.
- `repository.bundle`: Git history supplied with the ZIP. To restore a checkout:
  `git clone repository.bundle GH3-Chart-Studio-repo`.

Recommended next step: run the Windows/TheGHOST acceptance checks on one real song,
evaluate learned variations against a real chart, then begin Milestone 4's editor and playback. Fix import or gameplay regressions
before expanding features. The current relay checkpoint is `HANDOFF_LATEST.md`. No Claude handoff has occurred.
