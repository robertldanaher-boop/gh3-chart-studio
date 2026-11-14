# 0.4.4 — automatic corpus rows, difficulty selection and Orange-only copy

Changed library_gui.py and patterns.py: scanning now retrieves newest rows in its
background job; the main-thread completion callback populates the table and resets
category filters. Existing browsing still supports the original sort order. The
summary distinguishes imported charts from displayed pattern rows (max 200).

Changed playback.py: Open chart control, available-difficulty dropdown and Remove
Orange → Medium button in Audio Studio's listening page. Difficulty display changes
are non-mutating. Successful copying switches to Medium. Errors remain visible in
the playback panel via gui.py; audio_gui.py gives a chart-appropriate next step.

Changed editing.py: separate remove_orange_to_medium operation, with deep-copy
preservation of Expert/Hard, exact remaining lane/tick/sustain preservation, source
phrase copy and explicit output counts. It does not invoke contour mapping/density
reduction or silent cleanup. Unsupported markers/sustains and empty results are
rejected. Paired export uses the existing strict reopen checks.

Changed version metadata, tests/test_editing.py, tests/test_gui.py, README, handoff.
Added this log, M4_4_WINDOWS_GUIDE.md and M4_4_TEST_RESULTS.txt. No new dependency.

Tests: full local regression results in M4_4_TEST_RESULTS.txt. Added coverage for
both Expert and Hard copies, Orange-only and mixed chords, empty/unsupported cases,
source immutability, copied phrases/tempo, chart/MIDI reopening, automatic table fill,
GUI difficulty selection and exported source-track preservation. Playback layout
inspected at 1120x800. Windows and TheGHOST/Dolphin/Wii testing remain pending.

Next: test these controls on Windows; add an explicitly reviewed Medium-only repair
and source-preserving chart-only profile if needed for marked modern source charts.
