# Milestone 5.5 — Layout regression fix

November 16, 2026

User evidence: Windows startup tests reported 1 failed, 192 passed, 1 skipped. test_guided_footer_visible_at_small_window requested width 1024 but received 1282. Python setup succeeded; pytest failure correctly prevented launch.

Files changed: gh3studio/audio_gui.py (two-by-two workflow actions, separate draft footer, concise button labels and wrapped title), gh3studio/library_gui.py (split scan/filter/action and rating/report rows), gh3studio/gui.py (wrapping header labels), tests/test_gui.py (normal and 18px large-text layout coverage), gh3studio/__init__.py and pyproject.toml (0.5.5), README.md, HANDOFF_LATEST.md and milestone guide/log/results.

Investigation: with enlarged text on Linux, the hidden Pattern Library tab imposed a 1046-pixel minimum window width even while Audio Studio was selected. Splitting its control rows removed that constraint. Audio action/footer rows were also reduced to avoid long combined minimum widths. This reproduces the class of failure, not the exact user's Windows font/DPI environment.

Verification: 195 tests passed in 18.14 seconds on Linux/Qt offscreen. Existing compact-window assertion retained. Added larger-text variant also checks advanced-settings/footer visibility. Default-font test also passed with QT_FONT_DPI=144. Rendered larger-text screenshot visually inspected at exactly 1024x700, with draft footer visible. Git whitespace and ZIP integrity checks completed during packaging. No tests bypassed; no chart/audio algorithms changed.

Limits: native Windows reproduction and corrected Windows run remain pending. No audio-device/Wii/importer validation established. Exact retest instructions: M5_5_WINDOWS_GUIDE.md. Next milestone: user's Windows startup acceptance, then one-song gameplay acceptance.
