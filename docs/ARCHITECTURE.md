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
Milestone 2 should add a SQLite pattern store and separate extraction/scoring modules.
Audio analysis should be an independent pipeline feeding proposed tick events, with
explicit uncertainty and offset handling. It is not implemented in this release.

Dependencies are pinned in requirements-windows.lock with SHA-256 hashes. Setup
uses binary wheels only. The lock targets Windows/Python 3.11; Linux QA uses matching
primary versions. Updating dependencies requires rerunning tests and Windows checks.
