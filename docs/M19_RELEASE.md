# Milestone 19 — clear repair and adaptation workflows (0.19.0)

## Behavior

Home has two goals, both opening the same Songs queue: Repair existing charts and
Create challenging Medium. The queue also offers Check charts — report only.
One file and recursive collections use the same inspection, review and export.

The main adaptation defaults to Orange removal only: surviving G/R/Y/B notes keep
their authored ticks/lengths. Easy is retained; missing Hard/Expert stay missing;
other difficulties are retained. Optional sustain transfer, Easy creation,
difficulty filling, other-track repair and sustain shortening are independent
visible choices. Incompatible retained tracks block export rather than being
silently repaired. Main-workflow empty Medium blocks; no random replacement.

Prepared editing uses the existing editor with Apply edits to review, not another
export screen. Playback uses Original/Prepared comparison and compensates the
prepared chart for export-only audio padding. The queue export stores a readable
per-difficulty summary in validation.json and IMPORT_README.txt.

The 0.18.6 baseline reproduced 1 failure, 388 passes and 5 skips on Linux/3.11:
test_unpaired expected a failure for a note with no duration before end of track.
Such notes are blocked again. Recoverable dangling notes still end at track end.
Same-pitch overlaps now pair releases FIFO; an earlier note's late release cannot
shorten the restarted note. Duplicate same-tick note-ons do not swallow its release.
The FIFO assumption is reported because the original pairing is ambiguous.

## Files changed

- gh3studio/cleaner.py: shared file/folder inspection, scoped options, readiness
  checks, per-difficulty summary and export reporting.
- gh3studio/cleaner_gui.py: shared goals/queue, explicit optional choices, check-only
  gate, preview/editor entry and readable review controls.
- gh3studio/difficulty_set.py: selectable Easy/filling/repair scope and sustain
  policy; explicit main-workflow empty-output gate. Legacy defaults retained.
- gh3studio/gui.py, welcome.py: Home/Songs navigation, drag/drop and resume routing;
  older workflows isolated under Advanced / experimental.
- gh3studio/review_gui.py: shared Original/Prepared player and queued editor changes.
- gh3studio/playback.py, editor_gui.py: reuse editor without a second export path;
  preview/editor coordinate compensation for audio lead-in.
- gh3studio/midiio.py: reported FIFO overlap repairs and unrecoverable duration gate.
- gh3studio/song_export.py: validate complete sets only when requested; output summary.
- tests/test_song_workflow.py and test_midi_tolerance.py: preservation, consent,
  actual export/read-back, no Orange, FIFO durations, shared UI and small-window tests.
- Existing GUI/bulk/sync tests: exercise new primary routing and explicitly opt in
  where their fixtures require sustain repairs; legacy regressions remain covered.
- README.md, CHANGELOG.md, HANDOFF_LATEST.md, docs/archive/HANDOFF_v0_18_6.md:
  current usage replaces historical feature claims; old handoff retained.
- gh3studio/__init__.py and pyproject.toml: version 0.19.0.

## Verification

Final full local suite: **405 passed, 5 skipped in 47.03 seconds**. See M19_TEST_RESULTS.txt for the full executed result. A preceding full run stalled without a summary and was manually interrupted; M19_INTERRUPTED_TEST_RUN.txt retains its partial progress. The successful diagnostic rerun does not establish the cause or eliminate intermittent Qt/media hangs. Python 3.11.18 with real pinned app
libraries on Linux; Qt offscreen. PowerShell is unavailable, so five installer
integration tests are skipped locally. No dependency stubs used. Windows Actions
must be checked on the final commit before a Windows pass/build claim.

## Exact Windows test instructions

1. Close the installed app. Check out this change's branch or extract its complete
   source into a fresh writable directory outside the installed application.
2. Double-click START_WINDOWS.cmd. It installs/checks dependencies, runs the suite
   and launches. Preserve logs if it fails. Do not skip a failing test.
3. Home → Repair existing charts → Choose chart. Use a song with existing Easy,
   Medium, Hard and Expert. Inspect the summary. No difficulty is generated.
4. With a chart requiring overlapping-sustain repairs, confirm export is blocked
   until Optional changes → Allow listed sustain shortening / chord repairs is
   enabled. Rescan completes; inspect each listed shortening before approval.
5. Home → Create challenging Medium. Choose Expert, then Hard in separate runs.
   With all optional choices off, confirm Easy and source tracks stay unchanged,
   Medium contains only G/R/Y/B and Orange sustains/taps are removed. A source of
   only Orange taps must block, including when other difficulty options are enabled.
6. Enable Easy/fill missing slots independently and verify the summary reflects
   exactly those choices. Enable other-track repairs only if needed.
7. Preview / edit → compare Original/Prepared, select tracks, listen at beginning,
   middle and end. Apply an edit to review; approval must clear. Export from Songs.
   Use a negative ini delay too: preview should match the original audio while the
   exported chart/audio receive a shared lead-in. Check audible sync manually.
8. Goal → Check charts — report only. Save scan report; export must stay disabled.
9. Repeat with a recursive collection, then drop a second collection after export.
   Verify no stale filters hide songs. Test at 1024×700 and larger text sizes.
10. Import notes.chart and song.ogg together into TheGHOST; use HOPO measure 2.95,
    zero extra importer delay for normalized output, and inspect all difficulties.
    Test one song in Dolphin before accepting a collection. Charts are not ISOs.

## Limits and next milestone

This profile cannot repair every chart mechanic or infer the correct musical
intent. No instrument transcription or controller recording is added. Forced
HOPO interpretation still needs TheGHOST/game acceptance. FIFO MIDI repair is a
stated assumption. Other instruments/artwork are omitted; metadata must be checked.

Changing options/goal regenerates the queue and clears unsaved review edits. Choose
options first. Blocked prepared candidates cannot be manually edited in the queue;
use listed repair choices or an external source editor, then rescan. Legacy tools
remain available for advanced workflows and retain their broader conversion defaults.
No new license-bearing code/dependencies introduced. Installer backup retention and
rebuild costs are unchanged. Set-list tier handling remains outside this milestone.

Next: Windows and one-song game acceptance; then improve blocked-candidate editing
and persistent review sessions before adding new transcription features.
