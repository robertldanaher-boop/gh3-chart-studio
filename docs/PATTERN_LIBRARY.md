# Milestone 2 — local pattern library and variations

## Try it on Windows

Double-click START_WINDOWS.cmd to set up, test and launch.

1. Open **Pattern Library**. The database path is visible at the top. Choose a new
   location if desired; use the same database on subsequent sessions.
2. Click **Scan chart folder…** and select a parent folder containing .chart/.mid files.
   Subfolders are scanned. You can also drop a single folder onto the main window.
   Input MIDI mode follows the Modern/Legacy selector in Chart Converter.
3. Review new/duplicate/failed counts. **Save scan report…** saves each file's outcome.
   Cancellation retains fully committed files. Rescan the same folder to resume;
   duplicate content is reused and failed files are retried.
4. Click **Browse patterns**. Select a category to filter the next browse action.
   The table is limited to 200 rows. Select a pattern to inspect its extracted features.
5. Set its preference rating from 1–5 and click **Save rating**. This adjusts future
   candidate ranking. One score per pattern is stored; saving again replaces it.
6. Open a source chart in **Chart Converter**. Optionally use **Find matches for open
   chart** in the library tab to inspect candidates for its first occupied window.
7. Set conversion controls and a seed. Click **Generate 3 learned variations**.
8. Select Rhythm Technical, Melodic Technical or Adaptive Expert Medium. Compare
   their actual note previews and reports. Export the selected candidate normally.
9. Reusing the same chart, settings, seed, application algorithm and unchanged
   database reproduces results. The export records a corpus fingerprint and donor IDs.

For a minimal demonstration, scan a folder containing just
examples/technical-study.chart. This produces six stored windows (Hard and Expert).
A tiny corpus may produce fewer than three distinct arrangements. This is reported;
the program never inserts arbitrary notes merely to make outputs look different.

## What is actually learned

This is local statistical extraction, retrieval and constrained pattern transfer.
No neural network is trained and no audio is analyzed. Each stored example is an
occupied window of **eight quarter-note beats**, not a detected musical phrase or
an inferred bar. Time signatures do not alter window size in this version.

Stored information includes difficulty, metadata, source content identity, exact
fractional-beat onsets/durations, fret sequences, tempo changes within the window,
event/gem counts, tempo-aware event rates, average BPM, chord/sustain ratios, fret
movement, repeated 2–4-event motifs and estimated natural-HOPO opportunities.
HOPO opportunity is a timing/lane heuristic, not a forced-HOPO gameplay guarantee.

Categories are heuristic: steady rhythm, fast rhythm, repeating riff, technical run,
alternating chord pattern, sustained passage, and mixed passage. They are not
claims about which instrument or musical section is audible.

Candidate selection uses event density, chord ratio, fret movement and sustained-note
ratio. Ratings shift distance by up to 0.3. For speed, it ranks a bounded pool of at
most 512 rows near the query density, falling back to up to 512 rows if necessary.
Results are nearest within that candidate pool, not an exhaustive corpus search.
The first implementation can favor earlier rows in large corpora; broader indexing
and held-out quality evaluation remain future work.

## Variations

- Rhythm Technical retains the converted source's chord sizes and prefers chord-rich donors.
- Melodic Technical uses one gem per retained event and prefers moving single-note shapes.
- Adaptive Expert Medium follows donor chord sizes, capped by the converted source's size.

All use donor lane shapes on the existing target events. Source rhythm, retained
sustain durations, tempo map and Star Power positions stay fixed. No additional
onsets or gems beyond the baseline cap are invented. Density below 6 can remove
source events through the original converter before variation generation.

An identical input window reuses its chosen donor within a variant. Candidate/tie
sampling is seeded. Different seeds may still select the same arrangement.
Preferences change ranking, not neural weights. The full eight-axis feedback form
and long-term per-song enjoyment history are not implemented.

## Database and safety

SQLite schema v1 is identified by a GH3 application ID. Unknown/newer schemas and
unrelated databases are rejected. A new empty database is initialized transactionally.
Each imported file's source record, patterns and path status commit together.
Cancellation during extraction rolls that file back. Completed files survive a later
error or cancellation. Disk/database errors stop the run; recoverable chart errors
are recorded and scanning continues. A crashed run can remain marked running;
rescan creates a new run and skips content already committed.

Deduplication uses chart bytes, adjacent song.ini bytes, suffix, and MIDI mode.
It is content deduplication, not acoustic song identification. Equivalent .chart/MIDI
versions are separate sources. Byte changes or metadata edits create a new snapshot.
Old snapshots remain intentionally; there is no automatic prune/delete UI yet.
Changing the database or ratings changes the reproducibility fingerprint.

Symlinked files/folders and hidden subdirectories are skipped. Files are read only,
with a 32 MiB chart and 1 MiB song.ini scan limit. Supported guitar difficulties are
extracted; difficulties with unsupported modifiers are skipped with an explanation.
The library can describe patterns that the conservative converter later rejects
because of sustain restrictions; generation still runs the original safety gate.

Data never leaves the machine through these features. Keep a backup of your SQLite
file while the application is closed. Exported reports may include local source paths.
Use only charts you have permission to use; no corpus is downloaded or redistributed.

## Remaining validation

Automated tests use original synthetic fixtures and stress cases. No user chart/audio
corpus or Windows/TheGHOST/Dolphin/Wii runtime test has been supplied. Statistical
similarity is not proof of musical accuracy, playability, or enjoyment. Audio analysis
is Milestone 3; import/engine compatibility restrictions from Milestone 1 still apply.
