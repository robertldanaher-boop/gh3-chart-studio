# Milestone 7 implementation log — November 18, 2026

## Functional changes
- New focused Home with two task cards and native Qt fret artwork.
- Three primary tabs; legacy converter, patterns and audio drafting explicitly reserved.
- Guided Medium workspace with independent Expert/Hard source selection, sustain
  preservation enabled by default, exact source/output comparison and pinned export.
- Cleaner queue with search, status filters, color plus text states, selected-song
  inspection beside results, visible destination and persistent bottom process action.
- Cleanup report access after zero successful exports when diagnostics exist.
- Compact playback transport above the horizontal chart; optional timing/device controls.
- Plain-language export readiness and repair review; always-visible application activity,
  elapsed time and count. Diagnostic log accessible through the reserve menu.
- Startup branding matches the workshop; bootstrap, tests, installer and animation logic
  retained. No new dependency or borrowed assets. Musical conversion/export engines unchanged.

## Files created or changed
Created gh3studio/workspace.py (StepStrip, AdaptPanel) and tests/test_focused_workspace.py.
Changed gh3studio/gui.py, welcome.py, cleaner_gui.py, playback.py, audio_gui.py,
song_export_gui.py, appearance.py, __init__.py; pyproject.toml; tools/startup_windows.py;
tests/test_gui.py. Updated README.md, HANDOFF_LATEST.md, docs/WINDOWS_TEST.md and added
M7_WINDOWS_GUIDE.md, M7_TEST_RESULTS.txt and this log. Included native application screenshots.

## Verification
Initial UI regression run exposed the new cleaner's minimum-height constraint and
an obsolete test expecting the retired primary Audio Studio route. The queue work
area now scrolls and its inspector sits beside the table. Updated the route assertion
to exercise the new Hard-to-Medium button; source/target output assertions retained.
Targeted final GUI suite: 44 passed. Full final suite: 223 passed in23.28s. Export
regressions confirm no Medium Orange, original Expert/Hard retention, transferred
sustain endpoints, Ogg creation, usable logs for blocked rows and actual comparison
between original Medium and prepared Medium. Full log in M7_TEST_RESULTS.txt.
Visually inspected Home, cleaner review and created Medium; all four preview lanes
visible at1024x700. git diff --check passes. No native Windows build or game executed.

## Limits
Session-only edits; conservative marker stripping remains; no additional difficulty
profiles. Sustains may still need explicit compatibility repairs. The user's actual
54-song collection and ten blocked charts were not supplied. Experimental tools remain
installed, so hiding them does not reduce dependency size or startup test time.
The native Windows bootstrap and installation policy are unchanged, including its
Python3.11.9 fallback limitations described in the prior guide.

## Windows test and next milestone
Follow M7_WINDOWS_GUIDE.md. Confirm the two essential workflows, Windows text scaling,
playback and one-song TheGHOST/Wii acceptance before adding more features. Diagnose
blocked user songs from scan/cleanup logs. Update the handoff; no Claude participation
is claimed.
