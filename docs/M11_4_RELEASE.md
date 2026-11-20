# 0.11.4 — Windows open fully on screen

## Problem (Bob, Windows, 0.11.3)
The main window opened too high: the title bar was above the top of the screen, so
the window could not be dragged, and the resize corner could not be reached.

## Cause
`Window` always opened at a fixed 1180x840 client size with no screen check. On a
display whose usable height is below roughly 890px (for example 1366x768, or
1920x1080 at 125–150% scaling) Windows had to place part of the frame off-screen.
The startup progress window had the same fixed-size pattern (860x700).

## Change
- New `gh3studio/window_fit.py`:
  - `fit_geometry()` — pure arithmetic: shrink preferred size to the available
    area, never below the layout minimum, centre the frame, and always keep the
    frame's top-left (title bar) inside the available area.
  - `place_on_screen()` — applies it to the main window using the screen's
    `availableGeometry()`; called before show and once more after show when real
    frame margins are known.
  - `fit_size()` — clamps dialog sizes; Qt still centres dialogs on their parent.
- `gui.main()` uses `place_on_screen`; six dialogs use `fit_size` instead of
  fixed `resize()`.
- `tools/startup_windows.py`: Tk progress window clamps to screen size and centres.
- No layout, workflow, chart or audio behaviour changes. The window was always
  resizable; it is now reachable.

## Known limit
The layouts still need about 1024x700 of client area (existing tested limit). On a
screen with less usable height than that, the window opens at the top edge with the
title bar visible but the bottom may extend past the screen. Workaround: maximize
(double-click the title bar or Win+Up).

## Windows acceptance
1. Run START_WINDOWS.cmd. The progress window should be fully visible.
2. The studio should open centred with its title bar visible.
3. Drag the title bar; drag the bottom-right corner to shrink/grow.
4. Open About and an export review; each should fit on screen.
