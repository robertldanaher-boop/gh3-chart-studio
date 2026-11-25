param([switch]$Unsigned)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\windows_sdk.ps1"
try {
    $root = Split-Path $PSScriptRoot
    $version = [regex]::Match((Get-Content "$root\gh3studio\__init__.py" -Raw), "__version__\s*=\s*'([^']+)'").Groups[1].Value
    if ($version -notmatch '^\d+\.\d+\.\d+$') { throw 'Invalid app version' }
    $compiler = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
        "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
    ) | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if (-not $compiler) { throw 'Install Inno Setup 6.3 or newer' }
    $arguments = @("/DAppVersion=$version")
    $suffix = '-unsigned'
    if ($Unsigned) { $arguments += '/DGH3UnsignedBuild' }
    else {
        $thumb = Assert-SigningThumbprint $env:GH3_SIGNING_THUMBPRINT
        $null = Find-WindowsSdkTool 'signtool'
        $env:GH3_SIGNING_THUMBPRINT = $thumb
        $script = (Join-Path $PSScriptRoot 'sign.ps1').Replace('$','$$')
        $hostExe = (Join-Path $PSHOME 'powershell.exe')
        if (-not (Test-Path $hostExe)) { $hostExe = Join-Path $PSHOME 'pwsh.exe' }
        $hook = '$q' + $hostExe.Replace('$','$$') + '$q -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $q' + $script + '$q -Path $f'
        $arguments += '/DGH3SignedBuild'
        $arguments += ('/Sgh3sign=' + $hook)
        $suffix = ''
    }
    $arguments += (Join-Path $PSScriptRoot 'GH3ChartStudio.iss')
    $file = Join-Path $PSScriptRoot "output\GH3ChartStudio-Setup-$version$suffix.exe"
    if (Test-Path -LiteralPath $file) { Remove-Item -LiteralPath $file -Force }
    & $compiler @arguments
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $file)) { throw 'Installer compile/signing failed' }
    if (-not $Unsigned) {
        & "$PSScriptRoot\sign.ps1" -Path $file -VerifyOnly -ReportPath "$file.signing.json"
        if ($LASTEXITCODE -ne 0) { throw 'Final installer signature verification failed' }
    }
    Write-Host "Built: $file"
} catch { Write-Error $_; exit 1 }
