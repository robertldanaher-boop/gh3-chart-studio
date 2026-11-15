# Milestone 5 / v0.5.0 — guided desktop studio

## Install and startup

Close older running copies first. Extract GH3_Chart_Studio_v0_5_0.zip into a new folder and double-click START_WINDOWS.cmd. The startup window keeps setup → full tests → launch, estimated percent/ETA, elapsed counter, live log and failure handling. It now has a dark studio theme, four-color animated equalizer, Pause/Resume animation and Credits. The animation is decorative, not an indication of measured progress. No new dependency is needed. The startup window still requires Python 3.11 x64 with Tcl/Tk.

## Existing chart → four-fret Medium

1. On Start, click **Open an existing chart** under “Keep the challenge. Lose Orange.”
2. Select the chart. The app opens the existing-chart workspace automatically. Follow the highlighted NEXT message.
3. Choose **Hard or Expert** in Display / copy source, then click **Remove Orange → Medium**. Verify the output provenance label and compare source/Medium.
4. Choose/check the matching recording and click Play preview audio. Listen and adjust timing before export; scroll down for timing controls on a smaller screen.
5. Click **4. Export song folder**. Review metadata, any explicit Medium-only cleanup and optional experimental HOPO settings. The prior 2.95 TheGHOST HOPO requirement remains unchanged.
6. After success, the banner says EXPORT COMPLETE and **Open exported song folder** opens the result. Import notes.chart + song.ogg in TheGHOST and test the song in-game. No new compatibility claim is implied by the new presentation.

## Audio only → chart draft

1. On Start, click **Choose a recording** under “Start with the recording.” No chart or pattern library is required. This route clears any previous chart template after you select a new file; cancelling the picker leaves your current work intact.
2. Analysis opens in Audio Studio. Review the waveform and attack table, unchecking sounds that should not become notes. The detector does not isolate guitar or distinguish all instruments.
3. If the tempo could not be estimated, the NEXT message points to Optional settings → BPM → Reanalyze. A chart tempo map/local patterns remain optional advanced inputs.
4. Click **Create draft from selected attacks → Listen**. The app takes you to playback, then follow Listen → Export as above.

## Other controls

- **Start / choose a goal** returns to the Start screen without discarding current work. Continue current song resumes the current workspace.
- **Advanced chart conversion / variations** opens the existing converter workflow. These functions and the Pattern Library remain accessible as tabs; they are not forced steps for Orange removal or audio-only drafting.
- Dropping a chart/audio file on Start chooses the corresponding guided route. Chart folders still route to Pattern Library scanning, not batch conversion.
- **About / credits** includes Nanook and TeamGHOST, format documentation contributors, libraries and license pointers. Credits distinguish compatibility references from software actually used.
- At smaller sizes the converter/playback sections scroll; export-review buttons remain reachable. The app was rendered/inspected at 1024×700 logical pixels locally. Windows DPI/font scaling still needs manual acceptance.

## Acceptance checklist

Test both Start cards, cancel a picker without losing work, choose Hard/Expert, compare source and Medium, preview audio, review metadata/HOPOs, export Ogg, and open the result folder. Verify the startup animation remains responsive while setup/tests run and Pause animation does not stop the timer/log. Verify Credits opens. Check 100%/125%/150% Windows display scaling if used.

Local automated workflow tests and offscreen Qt layout inspection passed; native Windows/Tk animation, audio hardware, Explorer launch and TheGHOST/Wii acceptance remain pending. The prior locked-log behavior is unchanged: close older copies before startup. Single-song correctness remains the priority; batch support is not added.
