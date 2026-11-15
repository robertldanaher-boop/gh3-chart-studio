# Milestone 4.9 — November 15, 2026

Requests: preserve song/artist identity in folder structure and metadata; allow Hard/Expert choice; favor HOPOs for dense (900+) charts. No batch feature yet.

Files/features:
- song_identity.py: shared identity field mapping, supported audio-tag fallback, safe Unicode Artist - Title [Medium] folder names.
- model.py/service.py: retain original song.ini section, import recognized extended identity fields. Source files not modified.
- audio_chart.py: audio-only drafts use readable audio tags instead of discarding them in favor of the filename.
- audio_export.py: writes/read-verifies supported tags on new Vorbis encodes; preserves original tags byte-for-byte on reused Vorbis, reporting identity differences.
- song_export.py: writes and verifies chart/ini identity, retains extra original ini keys, accepts only recognized chart HOPO flip markers with valid note positions/no duplicates in Medium. Other modifiers remain gated. Import README includes 2.95 requirement.
- hopo.py: separate, conservative .chart-only TheGHOST profile. Estimates natural states, replaces reviewed prior flips and adds flips to changing-fret single runs within half/one beat. Retains all note triples, timing maps, source tracks and phrases. No tap synthesis. Requires measure 2.95.
- song_export_gui.py: scrollable metadata/cleanup/HOPO review with always-visible export controls, visible count/percent and folder preview. No automatic HOPO activation.
- editing.py/playback.py/gui.py: importer-informed preview including flips, clear Hard/Expert source choice, identity-based folder naming and fixed profile preview threshold after export.
- New tests/test_hopo.py and test_song_identity.py; extended GUI tests; prior natural-preview expectation updated for a disjoint single following a chord, as observed in the inspected importer viewer.
- Version, README, handoff, compatibility addendum, Windows guide and test evidence updated.

Source review: upstream TheGHOST commit 27f143205d3698a1fca49f34c0710bd8347e8cb3, Chart.cs GetNotes maps N5/E* to bit 5; NotesEditor.cs uses that bit to invert its natural state. Default HOPO measure is 2.95. Read as behavioral evidence only; no upstream source code was copied into or distributed with this repository. FAQ confirms legacy E* input. SoundFile's existing metadata properties/copy_metadata used; no new dependency introduced. These are model/source checks, not game-runtime verification.

References:
https://github.com/Nanook/TheGHOST/blob/27f143205d3698a1fca49f34c0710bd8347e8cb3/TheGHOSTCore/Notes/Chart.cs
https://github.com/Nanook/TheGHOST/blob/27f143205d3698a1fca49f34c0710bd8347e8cb3/TheGHOST/NotesEditor/NotesEditor.cs
https://github.com/Nanook/TheGHOST/blob/master/TheGHOSTCore/Info/FAQ.txt
https://python-soundfile.readthedocs.io/en/latest/_modules/soundfile.html

Testing: M4_9_TEST_RESULTS.txt, Python 3.11.18/Linux/Qt offscreen. New regressions cover Unicode/custom ini/tag preservation, copied Vorbis conflict reporting, safe folder naming, GUI review, no double-flip of natural HOPOs, chord/repeat exclusions, orphan/duplicate/tap rejection, chart marker round trip and 1,000 exact notes with 999 eligible HOPO events. Actual source charts inspected: notes(1), Hard 720 surviving gems: 33.8/42.8% estimated events; Expert 868 gems: 39.3/44.8%. notes(2), Expert 1315 gems: 64.7/72.4%. Ratios are half-/one-beat policies and events, not individual gems or game results. GUI export review rendered and inspected offscreen.

Limitations: actual Windows, TheGHOST and Wii/Dolphin acceptance pending; changing importer HOPO measure changes flip behavior; game timings/meter/tempo transitions may differ from viewer model. Existing Ogg metadata is not rewritten; conflicts reported with authoritative reviewed chart/ini. Extra ini artwork/stem references are metadata only. Source difficulties may retain unsupported source features. MIDI forcing equivalence unverified and gated. No hidden density reduction or batch execution.

Next milestone: one real song acceptance before batch. No Claude execution or quota monitoring occurred. User explained startup-log lock was an older app still running and asked to disregard; startup scripts were not changed in this milestone.
