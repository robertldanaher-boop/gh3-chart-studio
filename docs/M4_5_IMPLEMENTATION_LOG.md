# Milestone 4.5 implementation log — November 14, 2026

Problem: strict paired-export gates could reject marked Expert/Hard sources before copying, leaving original Medium available for viewing. Display source and output were ambiguous. The supplied user's session is not reproduced directly; this failure path was reproduced in regression tests.

Changes:
- editing.py: selected Expert/Hard/Medium/Easy can be copied in review mode, removing only Orange and preserving all surviving gems/phrases/markers. Strict legacy mode retained.
- playback.py: copies actual displayed track, clears stale exports on failed copy, labels output provenance and exact-note status.
- chartio.py: preserves nonplayable N marker lengths and writes valid three-field markers, including older in-memory marker strings.
- patterns.py: accepts preserved N5/N6 lengths; extraction version v3 invalidates old extraction fingerprints. Rescanning old libraries can add new-version entries; no automatic deletion of ratings/history.
- song_export.py and song_export_gui.py: explicit Medium-only marker/sustain review; atomic new folder with chart, PCM16 audio, ini, settings, validation and import instructions; reopens/verifies chart and audio. Expert/Hard/Easy remain untouched. Offset/delay fails safely.
- gui.py/audio_gui.py/service.py: song-folder workflow, stale audio cleared on chart load, input ini delay retained for safety gate.
- tests/test_song_export.py, test_gui.py, test_editing.py, test_patterns.py: selected-source copy, cleanup isolation, metadata/audio/chart round trip, rollback, stale output, GUI review and marker preservation regressions.
- Version metadata, Windows guide, this log, test evidence and handoff updated. No new dependency or copied external implementation.

Testing: see M4_5_TEST_RESULTS.txt for complete pytest result using Python 3.11.18/Qt offscreen on Linux. Real supplied notes(1).chart: 902 Expert gems -> 868 Medium gems; notes(2).chart: 1469 -> 1315. Surviving notes were exactly equal before cleanup. Both exported/read back after explicit Medium cleanup, preserving original source notes/markers. Export integration used synthetic onset-study.wav, not the songs' missing actual recordings.

Limitations: native Windows startup, audible sync, TheGHOST conversion and Wii/Dolphin play untested. Medium cleanup may shorten sustains/remove gameplay markers only after review. Unedited source difficulties are not certified. PCM16 conversion changes sample precision; timing/sample count are preserved. Guitar-only format support and tempo representation limits remain. No built-in instrument separation, tablature search or tap guarantees were added.

Next: user acceptance with original audio and TheGHOST, followed by importer-verified HOPO behavior. Full Windows steps in M4_5_WINDOWS_GUIDE.md.
