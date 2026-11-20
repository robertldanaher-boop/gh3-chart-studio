# Filesystem-only transaction, also exercised by tests/test_installer_transaction.py.
# Stage must be complete before calling. Validate runs at the FINAL path because
# Python virtual environments contain absolute paths and must not be relocated.
function Install-StagedProgram {
    param([string]$Stage, [string]$Target, [scriptblock]$Validate)
    $ErrorActionPreference = 'Stop'
    if (-not (Test-Path -LiteralPath $Stage -PathType Container)) { throw 'Missing staged program.' }
    $suffix = [Guid]::NewGuid().ToString('N')
    $backup = "$Target.previous-$suffix"
    $failed = "$Target.failed-$suffix"
    $hadPrevious = Test-Path -LiteralPath $Target
    $movedPrevious = $false
    $activated = $false
    try {
        if ($hadPrevious) {
            Move-Item -LiteralPath $Target -Destination $backup
            $movedPrevious = $true
        }
        Move-Item -LiteralPath $Stage -Destination $Target
        $activated = $true
        & $Validate $Target | Out-Null
    }
    catch {
        $cause = $_.Exception.Message
        try {
            if ($activated -and (Test-Path -LiteralPath $Target)) {
                # Keep logs and failed files for diagnosis; never delete user data.
                Move-Item -LiteralPath $Target -Destination $failed
            }
            if ($movedPrevious) { Move-Item -LiteralPath $backup -Destination $Target }
        }
        catch {
            throw "Setup failed: $cause`nRecovery also failed: $($_.Exception.Message)`nPrevious installation: $backup`nFailed installation: $failed"
        }
        $restored = if ($movedPrevious) { 'The previous installation was restored.' } else { 'No previous installation was changed.' }
        throw "Setup failed: $cause`n$restored`nDiagnostic files (if setup started): $failed"
    }
    # Retain the backup after success too, including user files and the old venv.
    # Do not run its venv in-place; restore the whole folder to Target if needed.
    return $(if ($hadPrevious) { $backup } else { '' })
}
