Latest checkpoint: version 0.3.0. See M3_IMPLEMENTATION_LOG.md and HANDOFF_LATEST.md.

# Implementation log — 0.1.0 / Milestone 1

Date: November 13, 2026 (America/Chicago).

## Completed and tested

- New modular Python 3.11 application and PySide6 main window.
- .chart and MIDI import; integer-tick shared model with rational tempo data.
- Expert/Hard → four-fret Medium, retaining source difficulty data in new exports.
- Real density/chord/movement controls, read-only source/Medium note preview.
- Single-file drag/drop, thread-based processing, conversion cancellation, diagnostics.
- .chart and TheGHOST legacy MIDI export, metadata/INI and settings output.
- Structural validation, format read-back, tempo drift budget and no-overwrite behavior.
- Source license review, TheGHOST importer source inspection and independent-parser QA.
- Git repository/tag and bundled history; pinned, hashed Windows dependency lock.

## Verification evidence

53 pytest cases passed on CPython 3.11.18 / Linux x64, PySide6 6.8.3, Mido 1.3.3,
pytest 8.3.5. GUI tests used Qt's offscreen platform and actual QThread operations.
See TEST_RESULTS.txt. Python compileall completed successfully.

Tests cover both source difficulties, timing/tempo/sustain retention, controls,
reproducibility, twelve randomized chord fixtures, MIDI pair ordering, legacy and
modern phrases, wrong-lane rejection, malformed data, cancellation, file protection,
staged failure cleanup, forced/tap rejection, nonzero offsets, GUI drop/convert/export,
GUI errors, non-integer tempo conversion, original Medium replacement and rejection
of a corrupted read-back before publication.

Independent parsehero 0.0.2 loaded both sample exports with zero warnings, 37 Medium
gems, no Orange, two Star Power phrases and identical tempos/onsets. See
INDEPENDENT_TEST_RESULTS.jsonl and tools/independent_check.mjs. It ran in a separate
Node process and is not bundled as an application dependency.

The actual Qt window was rendered and inspected. Its Medium preview has four lanes;
Source has five. This is Linux rendering, not Windows visual acceptance.

## Partially verified / limitations

Format-level compatibility is verified for the supported subset. TheGHOST source
behavior has been reviewed, but runtime import and gameplay are unverified.
No real-user chart/audio corpus was supplied. Fixtures are original synthetic
musical studies and randomized stress cases; there is no claim of real-song quality.
No Windows EXE was compiled in this Linux environment. Build scripts and a Windows
hash lock are provided. Windows, TheGHOST, Dolphin and Wii tests remain pending.

Special modifiers, complex sustain shapes and offsets are blocked when safe paired
translation is unavailable. Natural HOPO behavior can change. Full details in
COMPATIBILITY.md. Audio playback, chart editing, batching and ML are not implemented.

## Files created

Core: gh3studio/{model,chartio,midiio,converter,validation,service,gui,__init__,__main__}.py;
run_app.py; pyproject.toml.
Tests: tests/test_core.py, tests/test_gui.py; original examples/technical-study.chart;
examples/converted/{notes.chart,notes.mid,song.ini,settings.json,validation.json}.
Launch/build: setup_windows.cmd, launch_windows.cmd, test_windows.cmd,
build_windows.cmd; requirements.txt, requirements-dev.txt, requirements-windows.lock.
Documentation: README.md, CHANGELOG.md, LICENSE, THIRD_PARTY.md, docs/*;
presets/*.json; tools/collect_licenses.py, tools/independent_check.mjs; licenses/*.
The supplied master requirements are preserved in docs/PROJECT_REQUIREMENTS.md.

## Next milestone

First run docs/WINDOWS_TEST.md on one supported real song and fix any regression.
Then Milestone 2: recursive chart scanning, SQLite pattern storage, pattern feature
extraction, similarity queries and three constrained variations. No neural training
or Claude contribution is claimed. A Claude brief will be prepared only if warranted.

## Final GUI regression fix

An expanded test run exposed an intermittent Qt segmentation fault. Worker result
callbacks now route through explicit queued QObject slots on the main GUI thread,
and the GUI test QApplication lifetime is shared across tests. The final suite
passed 53 tests. An additional 10 fresh pytest processes passed all 30 GUI tests,
including 120 assertions that result callbacks execute on the main thread.
