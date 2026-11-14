# GH3 Chart Studio — current Claude / ChatGPT relay checkpoint

Prepared November 14, 2026. Owner: Robert (Bob) Danaher.
This supersedes the earlier Milestone 1 handoff. No Claude execution has occurred.

## Transfer instructions

Give the next assistant this file AND `GH3_Chart_Studio_M2_v0_2_0.zip`.
The file alone does not contain application source. Extract the ZIP; either use the
extracted project or restore its included repository.bundle to a separate checkout:

    git clone repository.bundle GH3-Chart-Studio-repo

Edit/test only one chosen checkout. Read README.md, docs/PROJECT_REQUIREMENTS.md,
docs/M2_IMPLEMENTATION_LOG.md, docs/PATTERN_LIBRARY.md and docs/COMPATIBILITY.md first.

Suggested prompt: "Continue GH3 Chart Studio from this checkpoint. Inspect the code
and reproduce the baseline tests before editing. Follow the next task below. Keep
working features intact and return updated source, test evidence and a handoff."

## Current version / source identity

Version: 0.2.0, tag v0.2.0.
Branch: milestone-2-pattern-learning.
Starting baseline: c08fb07cb987cec4eb1be2eb8614e4963c879bee (v0.1.0).
The release's exact commit is supplied in RELEASE_COMMIT.txt beside this handoff in
the ZIP. The tagged Git bundle is authoritative. The release working tree is clean.
Do not revert to the older v0.1.0 ZIP without comparing the newer implementation.

## Non-negotiable project rules

Python 3.11, PySide6, Git, pytest, modular design; Windows 10/11 x64 application.
Primary gameplay target: GH3 Wii via TheGHOST (Bob uses Windows 7 separately for it).
Expert Medium must be ACTUAL Medium, with only Green/Red/Yellow/Blue:
.chart MediumSingle lanes 0–3, MIDI PART GUITAR playable pitches 72–75. No Orange 76.
Preserve tempo maps, retained authored onset/sustain timing and valid chords.
Do not invent notes in silence or treat density as proof of musical accuracy.
Never overwrite original charts/audio. Keep user chart/training data local.
Check licenses and technical compatibility before adding third-party code/models.
No placeholder controls, fake successes or claimed runtime tests that were not run.

## Current implementation

Milestone 1 converter, GUI, parser/exporter and validation remain in place.
Milestone 2 now adds:
- Recursive chart scanning with progress, cancellation and per-file reports.
- Transactional SQLite v1 pattern store with GH3 application ID.
- Content/metadata deduplication and resumable rescans; failed files retried.
- Eight-quarter-note windows, exact fractional rhythm, tempo-aware rates, chord/
  sustain/movement features, repeated 2–4-event motifs and HOPO opportunity estimates.
- Category browsing, bounded similarity queries and local 1–5 pattern preferences.
- Three seeded variation modes using real retrieved donor shapes on existing events.
- Pattern Library tab, variant selection/preview, normal paired export and provenance.

Core modules: gh3studio/model.py, chartio.py, midiio.py, converter.py, validation.py,
service.py, gui.py. New modules: patterns.py, variations.py, library_gui.py.
Tests: tests/test_core.py, test_gui.py, test_patterns.py.
No new third-party dependency beyond Milestone 1; sqlite3 is Python standard library.
requirements-windows.lock remains the pinned, hashed Windows dependency set.

## Actual verification

74 pytest tests passed on Linux CPython 3.11.18 / PySide6 6.8.3 / Mido 1.3.3.
All original 53 baseline tests remain included.
Five fresh GUI test processes additionally passed 20 GUI tests, including the
scan/browse/rate/generate/export workflow and 60 main-thread callback assertions.
Independent parsehero 0.0.2 opened all six variation sample files without warnings
or Orange; counts matched the reports. It is external QA, not an app dependency.
A 1,000-file synthetic corpus produced 6,000 windows with zero errors; rescan skipped
all duplicates. These tests do not demonstrate real-song musical quality.
See docs/M2_TEST_RESULTS.txt, M2_BENCHMARK.json and M2_INDEPENDENT_TEST_RESULTS.jsonl.

An earlier Qt crash was fixed with explicit queued QObject slots for worker results.
Preserve this architecture and the shared QApplication test lifetime. Do not mutate
widgets from worker callbacks. Database connections open/close in their own thread.

NOT TESTED: Windows execution/build, TheGHOST runtime import, Dolphin/Wii gameplay,
audio synchronization or a real-user chart corpus. No Windows EXE is included.

## Known limits

Pattern learning is statistical retrieval/transfer, not neural training or audio analysis.
Windows are fixed eight-quarter-note blocks, not detected musical phrases. Similarity
ranks at most 512 candidates. Ratings adjust ranking; the full eight-axis feedback
system is not implemented. Old content snapshots are retained; no prune UI yet.
Three variation modes can produce fewer than three distinct arrangements on a small
corpus; this is explicitly reported. The tiny included sample produces two distinct
arrangements across its three modes. No arbitrary differences are inserted.

Modifiers in source difficulties can prevent conversion/learning. Open notes, modern
taps/forcing, disjoint/extended sustains, anchors and nonzero offsets retain the
conservative restrictions described in COMPATIBILITY.md. Natural HOPO behavior may
change. Other instruments are omitted with warnings. No waveform editor/playback,
audio generation, batch song generation, neural training or GPU requirement.

TheGHOST reference commit: 27f143205d3698a1fca49f34c0710bd8347e8cb3,
https://github.com/Nanook/TheGHOST — Chart.cs, Mid.cs, MidNote.cs reviewed; no code copied.
Legacy Medium Star Power is MIDI 79; modern shared 116 is input-only. Reopen our MIDI
in Legacy mode. TheGHOST MIDI discards sustain lengths below 160 ticks; prefer .chart
for short sustains. Runtime may alter lengths across tempo changes.

## Next executable task

1. Inspect the tagged source and run the test suite. Record your actual environment.
2. If Windows is available, execute docs/WINDOWS_TEST.md, including the new pattern
   workflow, then build_windows.cmd. Do not claim Windows success from Linux tests.
3. With a supplied, legally usable real song/chart, compare source and variants and
   perform TheGHOST/Dolphin acceptance. Fix specific failures before expanding scope.
4. If external game validation remains unavailable, record the blocker and proceed
   with useful local work: Milestone 3's smallest audio decoding/onset-analysis pipeline.
   Review licenses first, preserve authored charts, and measure alignment instead of
   claiming transcription accuracy. Keep audio analysis separate from fret generation.
5. Commit coherent changes; return a new source ZIP, Git bundle, updated logs and
   HANDOFF_LATEST.md. Do not silently rewrite this release's history.

## Quick demo

Install Python 3.11 x64 with launcher; run setup_windows.cmd, test_windows.cmd,
launch_windows.cmd. Copy only examples/technical-study.chart into a test folder.
Pattern Library -> select test database -> Scan folder -> expect 1 source, 6 windows.
Browse/rate patterns. Open the study in Chart Converter, set seed 42, and generate.
Select each mode and export it to a fresh folder. See the full Windows acceptance doc.

## Resource continuity and return requirements

ChatGPT account allowance/reset time is not visible to the assistant. There is no
reliable prediction, automatic quota monitor, background Claude handoff or automatic
resumption. Bob can switch when the app warns him or whenever convenient.
Checkpoint after each working milestone and before stopping, not only at a limit.
Use one active implementation owner and one chosen repository checkout at a time.

Each handoff must state version/branch/exact commit, clean/dirty status, changes,
actual test commands/results, environment, untested areas, blockers and next tasks.
Include portable source/Git history; never include credentials or secrets.
To return to ChatGPT, upload the updated ZIP and handoff and say:
"Resume GH3 Chart Studio from Claude's checkpoint. Verify state/tests before continuing."
