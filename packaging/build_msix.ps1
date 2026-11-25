param(
    [switch]$Unsigned,
    [string]$Python = '',
    [string]$Publisher = '',
    [switch]$Release
)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot
. "$root\installer\windows_sdk.ps1"
try {
    if (-not $Python) { $Python = Join-Path $root '.venv\Scripts\python.exe' }
    if (-not (Test-Path -LiteralPath $Python)) { throw 'Set -Python to Windows x64 Python 3.11 with requirements-dev.txt installed' }
    if ($Release -and ($Unsigned -or $env:GH3_BINARY_REDISTRIBUTION_REVIEWED -ne 'true')) {
        throw 'Release requires signing and a completed matching-source/native-license redistribution review (GH3_BINARY_REDISTRIBUTION_REVIEWED=true).'
    }
    $makeappx = Find-WindowsSdkTool 'makeappx'
    $version = [regex]::Match((Get-Content "$root\gh3studio\__init__.py" -Raw), "__version__\s*=\s*'([^']+)'").Groups[1].Value
    $suffix = '.unsigned'
    if (-not $Unsigned) {
        $thumb = Assert-SigningThumbprint $env:GH3_SIGNING_THUMBPRINT
        $cert = Get-Item -LiteralPath "Cert:\CurrentUser\My\$thumb"
        if ($Publisher -and $Publisher -cne $cert.Subject) { throw 'MSIX Publisher must exactly match the certificate Subject' }
        $Publisher = $cert.Subject
        $suffix = ''
    } elseif (-not $Publisher) { $Publisher = 'CN=GH3 Chart Studio Development' }
    $work = Join-Path $PSScriptRoot 'work'
    $output = Join-Path $PSScriptRoot 'output'
    if (Test-Path -LiteralPath $work) { Remove-Item -LiteralPath $work -Recurse -Force }
    $null = New-Item -ItemType Directory -Force -Path $work,$output
    & $Python "$root\tools\freeze_app.py" --distpath "$work\dist" --workpath "$work\pyinstaller"
    if ($LASTEXITCODE -ne 0) { throw 'Frozen app build failed' }
    $app = Join-Path $work 'dist\GH3ChartStudio'
    & $Python "$PSScriptRoot\msix_manifest.py" --app-root $app --version $version --publisher $Publisher
    if ($LASTEXITCODE -ne 0) { throw 'MSIX manifest/icon creation failed' }
    $exe = Join-Path $app 'GH3ChartStudio.exe'
    if (-not $Unsigned) {
        & "$root\installer\sign.ps1" -Path $exe -ReportPath "$output\app-signature.json"
        if ($LASTEXITCODE -ne 0) { throw 'App executable signing failed' }
    }
    # Exercise the actual frozen program, including Qt, codecs and paired chart/MIDI export.
    $smoke = Join-Path $output 'frozen-app-check.json'
    if (Test-Path $smoke) { Remove-Item $smoke -Force }
    $process = Start-Process -FilePath $exe -ArgumentList @('--package-self-test',('"' + $smoke + '"')) -PassThru
    if (-not $process.WaitForExit(120000)) { $process.Kill(); throw 'Frozen app check timed out' }
    if ($process.ExitCode -ne 0 -or -not (Test-Path $smoke)) { throw 'Frozen app functional checks failed' }
    $packages = Join-Path $work 'bundle-input';$null = New-Item -ItemType Directory -Path $packages
    $package = Join-Path $packages "GH3ChartStudio-$version-x64.msix"
    $bundle = Join-Path $output "GH3ChartStudio-$version-x64$suffix.msixbundle"
    if (Test-Path $bundle) { Remove-Item $bundle -Force }
    # Full MakeAppx validation stays enabled: deliberately no /nv switch.
    & $makeappx pack /o /d $app /p $package
    if ($LASTEXITCODE -ne 0) { throw 'MSIX package validation failed' }
    & $makeappx bundle /o /d $packages /p $bundle
    if ($LASTEXITCODE -ne 0) { throw 'MSIX bundle validation failed' }
    if (-not $Unsigned) {
        & "$root\installer\sign.ps1" -Path $bundle -ReportPath "$bundle.signing.json"
        if ($LASTEXITCODE -ne 0) { throw 'MSIX bundle signature verification failed' }
    }
    $inventory = @(Get-ChildItem $app -Recurse -File | Where-Object { $_.Extension -in @('.exe','.dll','.pyd') } | ForEach-Object {
        @{ file=$_.FullName.Substring($app.Length+1); sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash }
    })
    $inventory | ConvertTo-Json -Depth 4 | Set-Content "$output\binary-inventory.json" -Encoding UTF8
    @{ version=$version+'.0'; architecture='x64'; publisher=$Publisher; signed=(-not $Unsigned)
       makeappx_validation='passed'; frozen_checks=(Get-Content $smoke -Raw | ConvertFrom-Json)
       bundle_sha256=(Get-FileHash -LiteralPath $bundle -Algorithm SHA256).Hash
       installation_tested=$false; game_compatibility_tested=$false
    } | ConvertTo-Json -Depth 5 | Set-Content "$output\msix-validation.json" -Encoding UTF8
    Write-Host "MSIX bundle built and validated: $bundle"
} catch { Write-Error $_; exit 1 }
