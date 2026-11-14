# Architecture

`model.py` stores notes/phrases as integer ticks, with rational microseconds-per-beat
for exact .chart input tempo representation. `chartio.py` and `midiio.py` translate
file formats into that shared representation. `converter.py` creates a deep copy
with a replacement Medium track. It is deterministic and contains no UI or ML code.
`validation.py` enforces structural rules. `service.py` handles load/metadata and
transactional new-folder export plus read-back verification. `gui.py` owns controls,
read-only preview, logging and worker threads; widgets are only updated on the UI thread.

Conversion checks cancellation per event group. Import/export show indeterminate
progress and are not cancellable; closing waits for the operation to finish.
No external data uploads or telemetry are part of the application.

The heuristic enumerates increasing four-fret subsets for each source chord and
scores target position, motion and contour relative to the preceding event. A local
transition cache makes repeated transitions consistent. Density thinning selects
existing events only and prioritizes quarter-note anchors and phrase/section starts.

Future milestones can consume/produce Song without replacing the GUI or exporters.
Milestone 2 now provides a SQLite pattern store and separate extraction/scoring modules.
Audio analysis should be an independent pipeline feeding proposed tick events, with
explicit uncertainty and offset handling. The initial onset pipeline is implemented in version 0.3.0.

Dependencies are pinned in requirements-windows.lock with SHA-256 hashes. Setup
uses binary wheels only. The lock targets Windows/Python 3.11; Linux QA uses matching
primary versions. Updating dependencies requires rerunning tests and Windows checks.

## Milestone 2 modules

patterns.py owns exact fractional-beat extraction, SQLite schema v1, content snapshots,
ratings, scanner transactions and bounded similarity queries. Every worker opens and
closes its own SQLite connection; connections are not shared across threads.
variations.py retrieves seeded candidate patterns and transfers their lane shapes
onto the converter's existing Medium events. library_gui.py supplies the library tab
and delegates work to the main window's explicit queued result/progress slots.
No new third-party dependency is introduced; sqlite3 is Python standard library.

## Milestone 3 audio pipeline

audio_analysis.py owns guarded decoding, spectral/energy feature extraction and an
AudioAnalysis result with source hash, measured candidates and warnings. audio_chart.py
converts detected seconds through a rational tempo-map clock and provides non-mutating
alignment diagnostics. audio_gui.py provides preview and controls while the shared
worker owns long operations. No widget access occurs inside analysis code.
SoundFile/libsndfile replaces the need for a separate FFmpeg decoder in this first
implementation; NumPy/SciPy provide CPU-only analysis. All dependencies are pinned.
