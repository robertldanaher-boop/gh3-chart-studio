Set-StrictMode -Version Latest

function Find-WindowsSdkTool([string]$Name) {
    $override = [Environment]::GetEnvironmentVariable('GH3_' + $Name.ToUpper() + '_PATH')
    if ($override) {
        if (-not (Test-Path -LiteralPath $override -PathType Leaf)) { throw "$Name override does not exist" }
        return (Resolve-Path -LiteralPath $override).Path
    }
    $command = Get-Command ($Name + '.exe') -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }
    $root = Join-Path ${env:ProgramFiles(x86)} 'Windows Kits\10\bin'
    $versions = @(Get-ChildItem -LiteralPath $root -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '^\d+\.\d+\.\d+\.\d+$' } |
        Sort-Object { [version]$_.Name } -Descending)
    foreach ($version in $versions) {
        $candidate = Join-Path $version.FullName ('x64\' + $Name + '.exe')
        if (Test-Path -LiteralPath $candidate) { return $candidate }
    }
    throw "Install the Windows 10/11 SDK (Signing Tools): $Name.exe was not found."
}

function Assert-SigningThumbprint([string]$Value) {
    $value = $Value -replace '\s', ''
    if ($value -notmatch '^[a-fA-F0-9]{40}$') {
        throw 'Set GH3_SIGNING_THUMBPRINT to the exact code-signing certificate thumbprint in CurrentUser\My. No unsigned fallback is permitted.'
    }
    return $value.ToUpperInvariant()
}
