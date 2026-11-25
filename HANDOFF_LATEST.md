# GH3 Chart Studio — 0.19.0 workflow consolidation handoff

Prepared November 25, 2026 for Bob Danaher and the next assistant.
Repository: https://github.com/robertldanaher-boop/gh3-chart-studio
Working branch: workflow-consolidation. Base main: 175e6b0283895752aeeb9866b28011e65c2b2e3a.
This is a stabilization/workflow change, pending native Windows and game acceptance.
Do not publish a release or describe an installer as built until its CI result is checked.

## Read first

Read README.md, docs/M19_RELEASE.md, docs/M19_TEST_RESULTS.txt and CHANGELOG.md.
The full prior handoff is preserved in docs/archive/HANDOFF_v0_18_6.md.
Use GitHub's newest main/PR state before editing. Never overwrite concurrent work,
reuse an old ZIP baseline, or equate attached release ZIPs with committed main code.

## What changed

Home offers Repair existing charts and Create challenging Medium. Both use one
Songs queue, including single chart files and recursive collections. Check charts
— report only is a queue goal; it cannot export. Older converters, pattern tools
and audio drafts remain under Advanced / experimental rather than primary tabs.

The primary adaptation defaults to removing Orange from Expert/Hard into Medium:
Easy retained, missing Hard/Expert left absent, no other-track repairs, no sustain
shortening, no Orange sustain transfer. Each broader change is a separate option.
Invalid untouched tracks block export. Main workflow refuses an empty Medium even
when optional Easy/fill choices are enabled; legacy conversion still has its old
explicitly documented full-set/default behavior.

Preview / edit has Original/Prepared comparison. It reuses PlaybackPanel with an
isolated owner, and ChartEditorDialog uses Apply edits to review. No second export
path inside the queue editor. Edits clear approval and retain change logs. The
preview compensates export-only audio padding, including editor coordinate mapping.
Per-difficulty summaries are shown and saved in validation.json/IMPORT_README.txt.

The original 0.18.6 full local suite reproduced test_unpaired's failure: dangling
notes with no possible duration before track end were silently lost. They block
again; recoverable ones still end at track end. Overlap note-offs now use a reported
FIFO policy, preventing an old release from shortening a restarted note. Same-tick
duplicate note-ons don't consume the real release. FIFO is an assumption, not a
reconstruction guarantee.

## Tests and environment

Run under Python 3.11 with the real requirements-dev.txt dependencies. Local tests
use QT_QPA_PLATFORM=offscreen and GH3_NO_UPDATE_CHECK=1. Final full local suite: 406 passed, 5 skipped in 43.49 s. Full output is
in docs/M19_TEST_RESULTS.txt. A prior full run stalled and was interrupted; partial
output is retained in docs/M19_INTERRUPTED_TEST_RUN.txt. Its cause was not established,
and intermittent Qt/media hangs remain an acceptance concern. Five installer integration tests require PowerShell
and are skipped when unavailable. No dependency stubs or disabled failure checks.
A successful local suite does not certify Windows, audible output, TheGHOST or Wii.
Check the PR Windows Actions result separately. No Claude assistance was used for
this milestone; previous Claude-authored commits remain the baseline history.

## Acceptance and remaining limits

Follow all Windows steps in docs/M19_RELEASE.md. Prioritize one real song with
existing Easy/Medium/Hard/Expert, markers and sustains. Check the two goals, optional
choices, Original/Prepared playback, edited export, negative-delay lead-in, a second
batch after export, and 1024×700/large text. Import notes.chart + song.ogg together
in TheGHOST with HOPO measure 2.95; normalized exports use zero extra importer delay.
Then test in Dolphin before approving a collection.

Changing goal/options regenerates rows and clears unsaved review edits (visible
warning); choose options first. Prepared editing is available only after blockers
are resolved; parsing-successful originals can still be previewed. Session reviews
aren't persisted. Main MIDI import uses modern phrase interpretation; legacy mode
is still in the advanced converter. Generic music MIDI isn't a game chart.

Source files stay untouched, but reviewed exports may alter markers/holds/timing.
Medium must never contain playable Orange: .chart lanes 0–3 and MIDI pitches 72–75.
No arbitrary density inflation, automatic musical transcription, controller
recording, or proven musical remapping of Orange attacks was added. Source/tempo/
sustain mechanics must remain as authored except explicitly reviewed repairs.

Installer retention/rebuild issues, set-list tiers, broader import support and
blocked-candidate editing remain separate work. No new third-party dependency or
borrowed implementation introduced. Keep credits/licenses and bootstrap tests.

Next milestone: native Windows and one-song TheGHOST/Dolphin acceptance; then
persistent review state and safe editing of blocked candidates.

Initial Windows CI: 5 large-text layout failures, 404 other tests passed; installer build skipped. Footer action labels were shortened and a wider-font regression added. See docs/M19_WINDOWS_LAYOUT_FAILURE.txt (or M19_WINDOWS_LAYOUT_FAILURE.txt in this directory). Check the PR latest run for corrected Windows evidence.
