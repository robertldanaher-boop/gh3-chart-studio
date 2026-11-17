# Version 0.6.0 — Clean charts for GH3

## Start and scan

1. Close older copies, extract this complete ZIP into a new writable folder, and run START_WINDOWS.cmd. Automatic runtime/dependency setup from 0.5.6 is retained.
2. On Start, choose **03 Clean charts for GH3 — one folder or a collection**. Select a single song directory or a parent containing many song folders. Alternatively drop a directory onto Start or Clean charts. Folder drops onto Pattern Library still scan patterns.
3. Scan is recursive, with up to 2,000 song folders. One chart is selected per folder: notes.chart first, then a unique .chart, then notes.mid/notes.midi or a unique MIDI. Alternative files are reported; ambiguous folders need Select chart. Other instrument sections are omitted, not merged into guitar.

## Review and correct

4. Select each row. The detail area lists errors, planned marker removals/sustain repairs, metadata, audio and warnings. Ready rows are checked for export; uncheck any you do not want.
5. Use **Edit selected metadata** to verify Name/Artist and optional album, year, genre, charter, track number, album artist and copyright. Title/artist are required; missing optional fields are flagged. Values are taken from the chart/song.ini and missing values may be filled from audio tags. No web lookup or guessed names. You must verify factual accuracy.
6. If audio is missing/ambiguous, use **Select matching audio**. Auto-selection uses a valid MusicStream, unique song.* or a single non-stem candidate. Stems and preview audio are not automatically substituted. Explicitly selected audio is your responsibility to match.
7. This conservative profile cleans ALL included guitar difficulties. It removes forced-HOPO/tap/open-note and other modifier events, including supported forced overrides; natural HOPOs may change. It shortens incompatible overlapping/unequal chord sustains and reports every change. It preserves onset ticks and tempo maps. Orange in Medium is removed; Orange sustains first transfer to seeded G/R/Y/B positions, then undergo the same listed sustain compatibility repair. Expert/Hard Orange stays. Missing difficulties are not generated.
8. Unsupported anchors, nonzero Offset/song.ini delay, non-/4 meter, malformed charts, duplicate gems and invalid/overlapping phrases remain blocked for manual correction. Do not call a blocked chart game-ready. MIDI uses the existing modern phrase interpretation (116 Star Power); legacy MIDI may need separate review/conversion.

## Export and test

9. Tick **I reviewed changes and verified the metadata and matching audio**. Click **Export checked songs** and select an output parent OUTSIDE the scanned source directory. The app creates a new timestamped collection directory with uniquely numbered Artist - Title song folders.
10. Each successful song contains notes.chart, song.ogg (Vorbis), song.ini, validation.json and IMPORT_README.txt. The collection has cleanup_summary.json with successes, failures and unprocessed songs. No source files are overwritten. Changed sources require a rescan. Cancelling stops between songs; a current encode may need to finish first.
11. Existing Vorbis is copied only if embedded tags agree with reviewed metadata. Conflicting tags cause re-encoding; this is lossy but retains sample rate/frame count and adds no timing shift. Other supported audio is converted to Vorbis. No guitar/bass stems or artwork are copied or fabricated.
12. Open the output folder. Reopen notes.chart and check metadata and difficulties, compare source/output onset timing, listen with the actual recording, then import through TheGHOST or the target tool. Check one song in-game before trusting a large collection. These are import folders, not Wii game archives.

## Windows acceptance cases

- One authored Expert/Hard chart, full-mix WAV and song.ini: review, export and compare.
- Parent with two valid songs and a malformed chart: only selected ready rows export; failures are visible.
- Missing artist/audio: export remains blocked until corrected.
- Already-Vorbis audio with matching vs conflicting tags: verify copy vs encode in validation.json.
- Cancel a collection and inspect cleanup_summary.json; original files must stay untouched.

Tests here use Linux/Qt offscreen and synthetic audio. Native Windows, actual recording synchronization and TheGHOST/Wii acceptance remain pending. This profile cannot certify every GH3 mechanic. Next milestone: one real song plus a small mixed collection tested on Windows and in the intended importer/game.
