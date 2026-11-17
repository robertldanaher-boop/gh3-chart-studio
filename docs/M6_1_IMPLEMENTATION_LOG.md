# Milestone 6.1 — Windows test failures

November 17, 2026

User report: 2 failed, 203 passed, 1 skipped. Cleaner export test read UTF-8 song.ini with the Windows default encoding; larger-text window test observed width1227 instead of1024.

Changes: tests/test_cleaner.py explicitly reads and writes UTF-8 in all text fixtures/checks. The production exporter already writes UTF-8; no metadata transliteration or stripping was added. gh3studio/cleaner_gui.py shortens fixed-width review/export text with a descriptive tooltip. gh3studio/library_gui.py adds a scroll container so wide hidden controls cannot force the main window wider. gh3studio/gui.py separates header navigation buttons and explicitly enables scrolling tabs. tests/test_gui.py adds a deliberately wide hidden-control regression. Version files, README, handoff and milestone docs updated.

Validation: 207 tests passed in 21.43 seconds on Linux/Qt offscreen; full test output in M6_1_TEST_RESULTS.txt. Existing 1024x700 checks retained, including 18px larger text and expanded advanced settings. New test verifies unusually wide hidden-library control text uses horizontal scrolling without widening the window. Offscreen larger-text Audio Studio and cleaner both measured1024x700; screenshot visually inspected with draft footer visible. Exact Windows1227px failure was not reproduced natively here.

Limits: native Windows, actual audio output and Wii/importer checks remain pending. This fixes identified platform-sensitive code, not a claim of completed Windows acceptance. No gameplay, sustain-placement, cleanup or audio encoding behavior changed. Exact user steps in M6_1_WINDOWS_GUIDE.md. Next milestone: Windows startup acceptance and one-song clean export/import test.
