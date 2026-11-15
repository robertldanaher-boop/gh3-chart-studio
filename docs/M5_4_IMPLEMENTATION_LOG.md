# Milestone 5.4 — Random four-fret sustain placement

November 15, 2026

Files changed: gh3studio/editing.py, gh3studio/playback.py, gh3studio/__init__.py, pyproject.toml, tests/test_orange_sustains.py, tests/test_gui.py, README.md, HANDOFF_LATEST.md and milestone guide/log/test output.

Implemented: deterministic seeded random placement among four playable lanes; prefer clear simultaneous notes, otherwise clear lanes; reject lanes occupied by a prior hold or later onset inside the transfer; preserve full durations and explicitly record conflicts when no lane is clear. Existing simultaneous duration uses the maximum, never a duplicate gem. Expert/Hard unchanged. UI replaces Blue-only option with random preservation, displays seed and provides regeneration using the original selected track. Reports retain seed and per-note placement. Legacy internal Blue-mode parameter remains for backward-compatible calls; the GUI uses random mode.

Tests: 194 passed in 19.09 seconds (M5_4_TEST_RESULTS.txt). Coverage includes deterministic repeats, multiple seeds, all four lanes, simultaneous-note preference, prior/future conflicts, clear-lane fallback, impossible placement without truncation, chart/MIDI round trips, GUI conversion and regeneration from Expert while Medium is displayed. Existing first-run, export, audio and pattern tests passed. Git whitespace and ZIP integrity verified during packaging.

Limits: lane clearance alone does not establish GH3 sustain/chord compatibility. Explicit export review remains necessary; optional cleanup may shorten durations. Random choices may coincide across seeds. Seed is exported in validation.json, not a complete persisted GUI session. Native Windows/audio hardware/Wii not tested. No dependencies added.

Windows test instructions: M5_4_WINDOWS_GUIDE.md. Next milestone: one-song native audio/import/game acceptance before batch support.
