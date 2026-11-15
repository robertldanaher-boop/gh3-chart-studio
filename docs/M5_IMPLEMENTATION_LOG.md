# Milestone 5 / 0.5.0 — November 15, 2026

Request: more appealing GUI, guidance based on audio-only versus Orange-removal intent, more engaging startup/animation, credit to open-source projects including Nanook.

Files/features:
- appearance.py: shared dark navy/teal visual language, accessible contrast, selected/focused/disabled controls, primary actions, consistent tables/forms/tabs. No third-party artwork/template dependency.
- welcome.py: goal-based Start cards, four-fret visual motif, advanced/pattern entry points, resume action, About / credits. Reference projects separated from included software.
- gui.py: persistent brand/header navigation, Start tab, explicit guided routing after choosing input, cancelling a picker leaves current work intact, audio-only start discards previous chart template only after file selection. Main converter scrolls at small sizes. Idle operation bars hidden so a completed task's 100% cannot be mistaken for whole-workflow completion. Home drag/drop routes by input type. Successful song export has a completion state and folder action.
- audio_gui.py: context-specific step labels and NEXT guidance, no audio-analysis detour for Orange removal, tempo-unknown guidance, export-complete state and explicit Open exported song folder action. Source operation semantics unchanged.
- playback.py: scrollable controls, less redundant chart-open UI in guided paths, descriptive hints. Applying timing edits clears stale export-complete UI state.
- tools/startup_windows.py: dark Tk theme, animated four-color equalizer, pause/resume motion, scrollable live log, short credits and Credits dialog. Animation is decorative; setup/tests/ready-handshake, progress, ETA, cancellation and logs remain separate and unchanged in behavior.
- tests/test_gui.py: guided chart/audio/advanced paths, cancelled selection, clearing old template, exact Hard-minus-Orange copy, export completion invalidation and 1024×700 layout regression. Existing tests remain.
- docs/CREDITS.md, Windows guide, this log, test evidence, version metadata, README and handoff updated. No dependency additions or gameplay/export algorithm changes.

Testing: docs/M5_TEST_RESULTS.txt. Python 3.11.18/Linux/Qt offscreen. Rendered/inspected Start and existing-chart workspace at desktop and 1024×700 sizes; scrolling introduced after detecting a 825px forced minimum height. Legacy audio-review assertion updated for heading capitalization; test still checks review step and attack count. Guided routes use real worker operations and source data, not just navigation mocks. Existing metadata, four-fret, HOPO, Ogg, MIDI and startup workflow tests retained.

Native Tk rendering/animation cannot be visually exercised in this environment (no display/X server). Tk module compiles/imports as part of startup tests; native Windows startup animation, OS folder launch, device audio and DPI scaling require user acceptance. No Windows build or in-game compatibility claim. Source folder/export formats remain exactly as v0.4.9.

Credits: TheGHOST/Nanook/TeamGHOST and GuitarGame_ChartFormats are behavioral/documentation references, not incorporated source code. Libraries and existing bundled license notices are identified separately. No claimed Claude participation. User's earlier locked-log issue was explained as an older app still open and marked disregard; log rotation behavior is unchanged.

Next milestone: user acceptance of both guided paths on Windows with one actual song, including original metadata, Ogg audio timing and TheGHOST/game HOPO behavior. Batch remains deferred.
