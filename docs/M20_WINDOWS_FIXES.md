# Native Windows packaging fixes

Initial MSIX/signing CI run:
https://github.com/robertldanaher-boop/gh3-chart-studio/actions/runs/45654117403
421 tests passed; the signing integration test failed before signing because
Import-Certificate into CurrentUser/Root requested an interactive confirmation
(`UI is not allowed in this operation`). The build stopped; no MSIX build/pass
was claimed from that run.

The isolated CI trust-store fixture now uses the ephemeral runner's LocalMachine
Root store and removes the test certificate/key in finally. Outside CI the trust
fixture requires an explicit isolated-VM opt-in; ordinary source installs do not
modify root trust. Production signing/import does not add root certificates and
continues requiring valid signer trust, matching thumbprint and a timestamp.

Read the latest PR Windows result for the corrected execution, including subsequent
real SDK, frozen runtime and MSIX validation. Tests/verification were not disabled
or replaced by stubs to obtain a passing production-signature claim.

The next native run verified real RFC3161 signatures on PE and MSIX bundle. Inno then exposed its `uninst.e32.tmp` naming convention. The signing extension guard now permits only the specific Inno `.e32.tmp`/`.e64.tmp` suffixes, retaining SDK signature verification.

Final corrected code commit `6e0c203` passed the complete Windows job: 422 tests, frozen app smoke, actual MSIX pack/bundle and unsigned fallback installer. See M20_RELEASE.md for the run and evidence.
