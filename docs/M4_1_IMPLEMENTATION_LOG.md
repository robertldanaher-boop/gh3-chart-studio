# 0.4.1 — guided audio workflow and horizontal listening map

Changed gh3studio/audio_gui.py, playback.py, gui.py, __init__.py, pyproject.toml,
tests/test_gui.py, README and handoff. Added onset_review.py, this implementation
log, M4_1_WINDOWS_GUIDE.md, M4_1_TEST_RESULTS.txt and INSTRUMENT_AND_TAB_ROADMAP.md.

Audio Studio contains numbered choose/review/listen/export actions, visible next-step
instructions and fixed create controls outside the scrolling analysis area. Creation
stays in this workspace. Optional settings are explicitly labeled and collapsed.
Listen / timing from Converter routes into the same workspace. The horizontal map
matches Converter lanes and uses media time with a moving time window.

Attack selection uses a Qt table model instead of creating a widget for each onset.
Deselected attacks never enter the draft; excluded times are written to reports.
Changing selection invalidates a prior audio draft. Reanalysis resets selection.
An already-separated instrument file may be analyzed while the original mix remains
the playback source. This is NOT automatic separation or verified stem alignment.

129 automated tests passed on Linux CPython 3.11.18 / PySide6 6.8.3. New coverage:
whole guided flow in one workspace, 15→14 onset exclusion and paired export, stale
output invalidation (including an unrelated prior conversion when starting audio), external analysis file vs original playback, horizontal lane/time
geometry, and visible create controls at 1024x700 with optional settings expanded.
Rendered both review/listening pages at 1024x700 and inspected them. Existing real
media seek/stop/close and queued worker tests still run in the full suite.
No Windows execution, audible-output or GH3/Dolphin/Wii acceptance claim is made.

Limits: no separator, tab search/import, pitch transcription or per-note chart editor.
A source stem must share the recording's time origin; this is not automatically
verified. Candidate strength is not instrument confidence. Timeline retains normal
five-lane display only for source tracks containing Orange; generated Medium is four.

Windows steps are in M4_1_WINDOWS_GUIDE.md. Next: verify this workflow with Bob's
recording/stem, then implement a separately tested separation/transcription and
structured tablature alignment milestone. Existing source charts remain the stronger
input when available; no arbitrary note-density inflation is added.
