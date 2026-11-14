# 0.3.1 — corpus import correction

Changed patterns.py, service.py, validation.py, library_gui.py, test_patterns.py,
version metadata and test_windows.cmd.

Learning-only validation records overlapping sustains as warnings without changing
source notes. Known tap/forced-HOPO/solo markers are retained in pattern metadata;
lane/rhythm extraction does not reproduce their gameplay. Unknown/open markers
still exclude that difficulty with explicit diagnostics. Conversion/export remain
strict. Extraction version participates in the source hash to avoid stale corpus
results. Existing database rows/ratings are retained.

User-file regression: notes(1).chart (†elepa†hy) imports 200 windows; notes(2).chart
(Tender Surrender) imports 228. Both rescan as duplicates, and original SHA-256s
remain unchanged. Using that corpus, all three variations of technical-study.chart
passed paired chart/MIDI reopen validation. User songs are not redistributed.

Windows: extract a fresh folder, run setup_windows.cmd, test_windows.cmd, then
launch_windows.cmd. Scan the two song folders in Pattern Library; expect 200 and
228 windows on a new database. Switch to Chart Converter to generate variations.
A successful corpus scan does not mean the song is ready for conversion.
110 automated tests passed on Linux CPython 3.11.18 before starting M4.
Windows/real-device acceptance is still pending.
