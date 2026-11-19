# 0.11.2 — Prevent clipped collection help

- Move collection source settings into the scroll area; wrapped explanation cannot shrink below its requested height.
- Keep output controls fixed and retain all layout assertions.

# 0.11.1 — Large-text startup layout fix

- Wrap collection source-difficulty help text so hidden/active pages fit small windows.
- Regression coverage checks long help text, both collection and single-song views, and visible export controls.
- Keep startup tests enabled; no dependency or chart/audio processing changes.

# 0.11.0 — Embedded bulk workflow and reusable exports

- Removed bulk popup; main Four-fret workspace switches between single-song and collection views.
- Stable output directories; validated replacement with normal-error rollback, preserved extras and append-only run log.
- Recognize source identities to update correct folders without overwriting unrelated same-title songs.

# 0.10.0 — Three-fret Easy and complete difficulty slots

- Single/bulk four-fret conversion now produces Easy G/R/Y and Medium G/R/Y/B.
- Retains existing Hard/Expert; fills missing slots with selected source.
- Preserves source rhythm in all-removed fallback and rejects empty converted slots before export.

# 0.9.1 — Song identity folder names

- All song-folder exports use Artist - Song Title; no numbered prefix or timestamp.
- Case-insensitive collision suffixes protect existing files; metadata remains intact.

# 0.9.0 — Bulk four-fret Medium

- Recursive collections, Expert/Hard source policy and optional sustain transfer.
- Shared queue selection, metadata/audio repair, worker progress, cancellation and per-song logs.
- Medium-only conversion/repairs; source files unchanged and other tracks retained with shared sync translation.

# 0.8.1 — Automatic song.ini delay

- Clean Songs normalizes stored delay automatically, without per-song synchronization confirmation.
- Chart Offset is ignored by this user-selected policy; missing delay is zero. Source files unchanged.
- Optional manual timing tool and adjustment logs retained; eight new regression cases.

# 0.8.0 — Interactive chart editing

- Transactional preview editor, note/sustain drags, star power, HOPO/strum and pattern actions.
- Undo/redo, audio navigation, full-song export preserving source files and four-fret Medium.
- User reports 0.7.3 playing in Dolphin; new editor acceptance pending.

# Changelog

## 0.7.3 — November 18, 2026

Built-in strict FFmpeg fallback for source audio decoding failures, verified header
frame/rate/channel preservation, atomic Ogg export and clearer stage/file errors.
Automatic setup of pinned imageio-ffmpeg; recovery shown in results and logs.
263 tests passed, plus the supplied original Opus recovered through the cleaner
with a synthetic chart. Native Windows/game acceptance pending.

## 0.7.2 — November 18, 2026

Per-song synchronization review in Clean songs; normalize an explicitly selected
shift with exact chart translation and audio padding, zero exported delay and
logged changes. Safely remove matching editor anchors; conflicting timestamps
require explicit retention of the existing BPM map. Thirty-two new tests; 257 passed
on Linux/offscreen. Native Windows/game acceptance pending. See
docs/M7_2_IMPLEMENTATION_LOG.md.

## 0.7.1 — November 18, 2026

Fix shared-header minimum width after Windows startup reported five small-window
failures. Stack/wrap branding and split the Medium footer actions into two rows.
Keep the existing size limits and startup test gate. Add wide-font regressions
and detailed layout reports on assertion failure. 225 tests passed on Linux with
Qt offscreen; native Windows acceptance remains pending. See
docs/M7_1_IMPLEMENTATION_LOG.md and docs/M7_1_WINDOWS_GUIDE.md.

## 0.3.0 — November 14, 2026

Local audio decoding, spectral/energy attack analysis, tempo/beat estimates, manual
BPM and draft shift, waveform preview, onset-aligned four-fret drafts, authored
tempo preservation, learned-pattern transfer and offset/drift diagnostics.
Unicode title handling and Qt disposal fixes. See docs/M3_IMPLEMENTATION_LOG.md.

## 0.2.0 — November 14, 2026

Local pattern library: recursive scans, SQLite storage, deduplication/resume,
feature and repeated-motif extraction, similarity search, pattern preferences,
three seeded variation modes and a dedicated GUI workspace. 74 tests passed,
with additional GUI stress and independent export checks. Windows/gameplay
acceptance remains pending. See docs/M2_IMPLEMENTATION_LOG.md.

## 0.1.0 — November 13, 2026

Initial Milestone 1 source release: authored-chart conversion, four-fret Medium,
PySide6 GUI, paired chart/MIDI export, compatibility validation, 53 automated tests,
independent format checks, Windows scripts and pinned dependency lock.
Windows executable and in-game acceptance remain pending.
