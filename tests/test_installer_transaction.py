"""Run actual rollback logic in PowerShell, without installing software or UI.
Windows CI exercises Windows PowerShell 5.1. Other hosts use pwsh if available.
"""
import os
from pathlib import Path
import shutil
import subprocess

import pytest

SHELL = shutil.which('powershell.exe') if os.name == 'nt' else shutil.which('pwsh')
pytestmark = pytest.mark.skipif(not SHELL, reason='PowerShell required for installer transaction integration')


@pytest.mark.parametrize('previous', [False, True])
@pytest.mark.parametrize('fail', [False, True])
def test_install_transaction_restores_complete_previous_version(tmp_path, previous, fail):
    target, stage = tmp_path / 'installed app', tmp_path / 'staged app'
    stage.mkdir()
    (stage / 'program.txt').write_text('new')
    if previous:
        (target / '.venv').mkdir(parents=True)
        (target / 'program.txt').write_text('old')
        (target / '.venv' / 'installed.json').write_text('old dependency environment')
        (target / 'user data.txt').write_text('keep me')
    helper = Path(__file__).resolve().parents[1] / 'installer' / 'transaction.ps1'
    script = tmp_path / 'exercise.ps1'
    # Pass paths as arguments, never interpolate paths into PowerShell source.
    script.write_text('''param($Helper, $Stage, $Target, $Fail)
$ErrorActionPreference = 'Stop'
. $Helper
try {
    Install-StagedProgram -Stage $Stage -Target $Target -Validate {
        param($Root)
        New-Item -ItemType Directory -Path (Join-Path $Root '.venv') | Out-Null
        Set-Content -LiteralPath (Join-Path $Root '.venv/installed.json') -Value 'new dependencies'
        Set-Content -LiteralPath (Join-Path $Root 'start_windows.log') -Value 'setup diagnostics'
        if ($Fail -eq 'yes') { throw 'injected setup failure' }
    }
    exit 0
} catch { Write-Output $_; exit 9 }
''', encoding='utf-8')
    run = subprocess.run([SHELL, '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
                          '-File', str(script), str(helper), str(stage), str(target),
                          'yes' if fail else 'no'], capture_output=True, text=True, timeout=30)
    assert run.returncode == (9 if fail else 0), run.stdout + run.stderr
    if fail:
        assert 'injected setup failure' in run.stdout
        if previous:
            assert (target / 'program.txt').read_text() == 'old'
            assert (target / '.venv' / 'installed.json').read_text() == 'old dependency environment'
            assert (target / 'user data.txt').read_text() == 'keep me'
        else:
            assert not target.exists()
        failed = list(tmp_path.glob('installed app.failed-*'))
        assert len(failed) == 1 and (failed[0] / 'start_windows.log').exists()
        assert not list(tmp_path.glob('installed app.previous-*'))
    else:
        assert (target / 'program.txt').read_text() == 'new'
        backups = list(tmp_path.glob('installed app.previous-*'))
        assert len(backups) == int(previous)
        if previous:
            assert (backups[0] / '.venv' / 'installed.json').read_text() == 'old dependency environment'
    assert not stage.exists()


def test_powershell_installer_entry_points_parse(tmp_path):
    root = Path(__file__).resolve().parents[1]
    script = tmp_path / 'parse.ps1'
    script.write_text('''param($Root)
$ErrorActionPreference = 'Stop'
foreach ($file in @('install.ps1', 'transaction.ps1')) {
    $tokens = $null; $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile((Join-Path $Root $file), [ref]$tokens, [ref]$errors) > $null
    if ($errors) { $errors | Out-String | Write-Output; exit 1 }
}
''', encoding='utf-8')
    run = subprocess.run([SHELL, '-NoProfile', '-NonInteractive', '-File', str(script),
                          str(root / 'installer')], capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stdout + run.stderr
