# Milestone 2 implementation log — 0.2.0

Date: November 14, 2026 (America/Chicago).
Base: v0.1.0, c08fb07cb987cec4eb1be2eb8614e4963c879bee.
Development branch: milestone-2-pattern-learning.

## Implemented and verified locally

- Recursive .chart/.mid/.midi scanning, progress, cancellation and per-file reports.
- Content-plus-metadata deduplication; rescans reuse committed files and retry failures.
- SQLite schema v1, application ID, per-file transactions and stored run states.
- Exact fractional-beat windows; tempo-aware density, chord/sustain/movement features,
  repeated 2–4-event motifs and natural-HOPO opportunity estimates.
- Category browsing, bounded similarity search and persistent 1–5 pattern preferences.
- Three seeded variation modes driven by retrieved pattern shapes. Actual retained
  onset/sustain timing and four-fret restriction remain enforced.
- Source/variant previews, variant selection and validated export through the existing
  exporter. Reports include donors, source hashes, seed, algorithm and corpus fingerprint.
- Dedicated Pattern Library tab sharing the existing queued main-thread worker handling.
- Sample exports and updated continuation handoff.

## Test results

74 pytest cases passed on Linux CPython 3.11.18, PySide6 6.8.3, Mido 1.3.3.
All original 53 baseline tests remain included. See M2_TEST_RESULTS.txt.
Five additional fresh GUI test processes passed 20 GUI tests and 60 main-thread
callback assertions. The new end-to-end GUI case scans, browses, rates, generates,
selects a variant and exports it to real files. Window layouts were rendered and inspected.

The new tests cover duplicate detection, recursive traversal, recoverable errors,
resumption, cancellation rollback, exact fractional timing, tempo-aware features,
ratings persistence/ranking, source/metadata changes, schema rejection, symlink
exclusion, seeded reproducibility, corpus influence on actual lanes, no-orange output,
paired exports, empty-corpus refusal, repeated motifs and modifier-track skipping.

Synthetic scalability check: 1,000 unique generated charts -> 6,000 stored windows,
zero errors. On this environment, scan 1.675 s; duplicate rescan 0.085 s; three-variant
generation 0.194 s. These are observed synthetic timings, not Windows/real-song guarantees.
See M2_BENCHMARK.json.

Independent parsehero 0.0.2 opened all six sample variation files (three .chart, three
MIDI) with zero warnings and no Orange. Event/gem counts matched their reports.
The tiny demo corpus produced only two distinct arrangements across its three modes;
this limitation is explicitly recorded in each report. No artificial distinction was added.

## Limitations

Statistical pattern extraction/retrieval is working; no neural training or audio analysis
is claimed. Eight-quarter-note windows are not detected musical phrases. Similarity
ranks at most 512 candidates and may favor earlier rows in a large corpus. Preference
feedback is one 1–5 score per pattern, not the full planned eight-axis feedback system.
Old content snapshots remain; there is no prune UI. Batch song generation is not implemented.

Windows execution/build, TheGHOST import, Dolphin/Wii gameplay and a real-user chart/audio
corpus remain untested. All conservative format/offset/modifier/sustain restrictions
from Milestone 1 still apply. Distinct outputs are not guaranteed for small corpora.

## Files added

- gh3studio/patterns.py, variations.py, library_gui.py.
- tests/test_patterns.py.
- docs/PATTERN_LIBRARY.md, M2_IMPLEMENTATION_LOG.md, M2_TEST_RESULTS.txt,
  M2_BENCHMARK.json, M2_INDEPENDENT_TEST_RESULTS.jsonl.
- examples/variations/manifest.json and three subfolders, each with notes.chart,
  notes.mid, song.ini, settings.json and validation.json.
- HANDOFF_LATEST.md.

## Files changed

- gh3studio/gui.py: library tab, progress, variants/seed, folder drop and safe callbacks.
- gh3studio/__init__.py, pyproject.toml: version 0.2.0.
- gh3studio/service.py: derive export version from package version.
- gh3studio/converter.py, midiio.py: current-version error/warning wording.
- tests/test_gui.py: library/variation workflow coverage.
- README.md, CHANGELOG.md, docs/ARCHITECTURE.md, COMPATIBILITY.md,
  IMPLEMENTATION_LOG.md, WINDOWS_TEST.md: current features and acceptance instructions.

## Next milestone

Validate Windows and one real song/corpus; fix any import or gameplay regressions.
Then Milestone 3: a small audio-decoding/onset pipeline with measured alignment,
manual BPM/offset controls and diagnostics. Review dependency licenses before adding
FFmpeg/librosa or model components. Do not claim audio transcription in this release.
