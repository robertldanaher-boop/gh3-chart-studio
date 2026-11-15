# Milestone 4.7 — preview playback recovery

November 14, 2026. User reported preview audio not working.

Observed defect: opening a chart clears the recording; the previous Play action called QMediaPlayer.play with an empty source, providing no prompt or visible explanation. This does not establish every cause of the user's audible playback failure.

Files/features:
- preview_audio.py: safe local MusicStream lookup and unambiguous song.* fallback; no stem guessing or outside-directory metadata paths.
- playback.py: Play opens a file picker if empty; returns success/failure for file loading; missing file clears stale audio; pending playback starts on load; Play/Pause text follows actual state. Output-device selector and refresh on device changes, explicit output selection on play. Visible media errors/no-device warnings and detailed application diagnostic log entries.
- gui.py: clear stale audio and load matching recording after chart import.
- audio_gui.py: audition restores the original mix when no source exists and uses the shared playback entry point.
- tests/test_preview_audio.py and test_gui.py: safe/ambiguous/stem lookup, chart autoload, missing file behavior, cancelled picker, actual decode/clock from prompted play. Existing pause/seek test retained.
- Version metadata, README, handoff, Windows guide and test evidence updated. No dependencies or third-party code added.

See M4_7_TEST_RESULTS.txt for full-suite results on Python 3.11.18/Linux/Qt offscreen. Actual audio device output, native Windows routing and the user's recording have not been tested. Device selection APIs are exercised without a physical device. Existing chart accuracy/export tests remain part of the suite.

Next: user tests audible Windows preview; request saved application diagnostic log if unresolved. Do not claim a Windows audio fix is verified merely from a moving player clock.

During regression work, an initial full run stalled in the native playback pause/seek test. The playback change was revised to avoid resetting an unchanged output device and to wait for LoadingMedia completion before issuing Play, rather than issuing it twice. The focused real-player tests then passed. Final full-suite evidence is separate; the transient stall is not proof of the user's exact Windows failure.
