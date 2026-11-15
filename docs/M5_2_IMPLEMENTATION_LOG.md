# Milestone 5.2 — First-run acknowledgement

November 15, 2026

Files changed: gh3studio/first_run.py (new agreement and persistent choice); gh3studio/gui.py (gated launch and readiness); docs/LICENSE_AND_DISCLAIMER.md (broader target scope and acknowledgement); tests/test_first_run.py (new regression tests); gh3studio/__init__.py and pyproject.toml (0.5.2); README.md, HANDOFF_LATEST.md and milestone guide/results/log.

Features: explicit Agree and continue / Disagree and close; closing rejects; studio created only after acceptance; remembered per-user across updates; full notice and MIT text; readable dialog before startup ready signal; no reading timeout; unavailable document blocks acceptance; persistence errors stay on prompt. Other compatible open-source chart-based games are included in scope without claims of verified compatibility. No changes to chart transformation or audio export.

Tests: 183 passed in 16.86 seconds on Linux/Qt offscreen. Six new tests cover saved acceptance/reloaded preferences, decline/close, missing notice, settings write failure, and main-entry integration for Agree and Disagree. Earlier test run found a missing test fixture; corrected before the complete passing run. Full output in M5_2_TEST_RESULTS.txt.

Limitations: source ZIP has no install wizard; first-launch prompt follows dependency setup and tests. Acceptance is per-user rather than per extracted folder. Native Windows registry/startup, packaged EXE and actual game execution remain unverified. This is not a legal enforceability certification or blanket support for other games.

Windows steps: M5_2_WINDOWS_GUIDE.md. Next milestone: one-song preview, exact four-fret Medium conversion and chosen importer/game acceptance before batch support.
