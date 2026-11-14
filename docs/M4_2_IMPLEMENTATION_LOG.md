# Version 0.4.2 — consolidated Windows startup package

Included START_WINDOWS.cmd. Removed setup_windows.cmd, test_windows.cmd and
launch_windows.cmd as requested. Retained build_windows.cmd: it builds the optional
Windows executable and is not replaced by the normal startup workflow.
Updated version metadata, README, current testing/feature guides and Claude handoff.
Historical milestone logs may name the scripts that existed at those milestones.

Functional behavior: setup -> pytest -> launch, stop on failure, one diagnostic log,
no intermediate success pauses. No chart-conversion or GUI logic changed in 0.4.2.

Verification: static launcher review from the startup change; package CRC/required
file/removed-file checks completed during packaging. Last Python regression evidence
is 129 passing tests from 0.4.1; not rerun for packaging/documentation-only changes.
Windows CMD execution and audible/in-game compatibility remain unverified here.

Windows test: extract into a NEW folder, double-click START_WINDOWS.cmd, wait for
setup and tests, then confirm title 0.4.2. Failure must stop and leave a diagnostic
window; details are in start_windows.log. Reusing/merging an old folder would leave
obsolete scripts on disk, so use a new folder.

Next milestone: user Windows acceptance, then instrument-focused chart refinement.
