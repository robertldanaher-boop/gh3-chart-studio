# 0.13.1 — Combined release: 0.13.0 plus window fit

0.13.0 (ChatGPT) and 0.11.4 (Claude) were both built from 0.11.3. This release is
0.13.0 with the 0.11.4 window fix carried over; see docs/M11_4_RELEASE.md for the
fix itself. No workflow or processing changes.

## Windows acceptance
1. Extract GH3_Chart_Studio_v0_13_1.zip to a new folder; run START_WINDOWS.cmd.
2. Startup progress window is fully visible.
3. Studio opens centred, title bar visible; drag the title bar and the
   bottom-right corner.
4. Home shows Prepare my songs and Clean only; run one song through Prepare.
5. Open About and the export review; each fits on screen.

## Evidence
Linux/Python 3.13 without PySide6: test_window_fit + test_minimal 11 passed,
1 skipped (Qt). Full suite not run here.
