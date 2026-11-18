# GH3 Chart Studio — Focused product direction

Accepted direction from Bob Danaher, November 17, 2026. This document supersedes
older feature-priority lists. It defines intended work; it is not a statement that
all behavior below is implemented or that arbitrary imports are Wii-compatible.
This direction was accepted at v0.6.4. The focused GUI is delivered in v0.7.0;
see M7_WINDOWS_GUIDE.md for current workflows and test evidence.

## Purpose

Prepare existing authored rhythm-game song folders for Guitar Hero III on Wii.
Offer challenging lower-difficulty tracks derived from an authored Expert or Hard
track by reducing the required fret buttons while retaining musical timing and
playfulness. Challenge comes from the existing phrases, rhythms and sustains;
there is no fixed low note-count target or automatic density reduction by default.
“Accelerate” means enrich the lower-level chart, not speed up playback or tempo.

## Two primary workflows

1. Clean for GH3 Wii: discover nested song folders, identify supported authored
   chart formats and associated assets, review exact repairs/blockers, export a
   new coherent song folder with chart, Ogg audio, metadata and diagnostic reports.
2. Clean and create a challenging lower difficulty: choose source Expert or Hard
   (suggest highest populated supported track, visibly), choose target difficulty
   and permitted frets, review the result against its source, then export. Keep
   source difficulties available; never overwrite source files. If sanitation is
   needed for an exported source track, report it separately from target conversion.

Authored game-chart MIDI remains a valid input format. Reading its authored note
positions is separate from estimating notes from a recording. General instrumental
MIDI is not automatically a game chart. Audio remains useful for listening, timing
review, metadata and Ogg export. Audio transcription, instrument separation,
tablature search and learned-pattern generation are deferred. Existing experimental
features need not be deleted in this documentation change; they should no longer
lead the product workflow or receive priority over compatibility defects.

## Musical rules

- Medium output must contain only Green, Red, Yellow and Blue, in both .chart and
  game-chart MIDI. Orange is forbidden regardless of preview appearance.
- Preserve tempo maps, note onsets and valid sustain ends. Do not move notes or
  shorten holds silently. Timing conflicts need explicit repair records/review.
- Remove unavailable fret gems without thinning otherwise playable notes. A chord
  loses only excluded gems; its surviving gems retain timing and valid lengths.
- Preserve sustains on excluded frets by assigning them to allowed frets. Retain
  the approved random/seeded choice, but choose only among musically playable,
  collision-free candidates. Prefer suitable simultaneous notes; otherwise create
  an allowed-fret sustain at the same tick. No hard lock to Blue.
- If no legal assignment preserves the sustain, report the conflict for a specific
  repair decision; neither lose it silently nor claim the conflict is compatible.
- Unsustained notes on excluded frets may disappear under the strict removal mode;
  disclose lost onsets. An optional rhythm-preserving remap is a future proposal,
  not an implemented promise or an authorized default replacement of this mode.
- Keep supported HOPO/strum behavior where the chosen importer/game path verifies
  it. Re-evaluate after fret remapping; a repeated fret is not automatically a
  no-strum note. High note count alone does not establish HOPO eligibility. Do not
  substitute an unsupported tap mechanic or claim untested Wii behavior.
- Additional lower-difficulty profiles need explicit permitted-fret/chord rules,
  authored fixtures and importer/game acceptance before becoming selectable.
  Four-fret Medium is the first acceptance target. User-selected optional density
  or chord simplification must be separate from the default button reduction.

## Experience and diagnostics

Use a guided song queue: choose goal, drop a song folder or collection, review
exceptions, process, listen/compare and open results. Show each song's readiness,
exact blockers and repairs; always make it clear whether processing started.
Show source/target difficulty, playable frets, note events versus fret-gem counts,
sustains retained/transferred/repaired, and timing/marker changes. Before/after
comparison must use the actual output track. Save metadata edits and selections
in a future review project; retry failures without redoing successful exports.

Per-run logs and scan reports must explain blocked songs and failures. No claim
that every source is supported. No files or media downloaded without a separate
request; no recordings are bundled in distributed application packages except
existing synthetic test fixtures.

## Next milestones and acceptance

1. Reliability: use the user's 54-song scan/cleanup logs to identify the ten actual
   blockers; verify output processing on Windows and one song through TheGHOST
   into Wii/Dolphin. The specific ten errors have not yet been supplied.
2. Four-fret adaptation: focus the GUI on these two workflows, preserve comparison
   and synchronization playback, and test sustain/chord/HOPO conflict handling.
   Audit the existing conservative cleaner's forced-marker stripping before
   promising preservation of verified supported mechanics.
3. Additional lower-difficulty profiles, saved review sessions and failure retry
   only after the preceding acceptance checks. Collection cleanup already exists;
   its large-collection behavior still needs real acceptance testing.

Automated checks must exercise exported artifacts, not just the screen: Medium
has no Orange; tempo/onsets remain stable; sustain ends survive or have explicit
repair records; charts round-trip; assets and metadata agree; failures do not
masquerade as successful exports. Runtime acceptance remains a separate step.

## This scope update

Files: docs/PROJECT_DIRECTION.md (new), docs/IMPLEMENTATION_SCOPE_UPDATE.md (new),
README.md, HANDOFF_LATEST.md and docs/INSTRUMENT_AND_TAB_ROADMAP.md (updated).
No application code changed; no new runtime features, build or compatibility claim.
Validation: documentation reviewed and git diff --check. Full tests not rerun for
this documentation-only change; v0.6.4's last recorded run was 215 passed.
Windows testing remains the v0.6.4 workflow in docs/M6_4_WINDOWS_GUIDE.md; no reinstall
is necessary for this scope update. Next milestone is reliability item 1 above.
