param(
    [Parameter(Mandatory=$true)][string]$Path,
    [string]$Thumbprint = $env:GH3_SIGNING_THUMBPRINT,
    [string]$TimestampUrl = 'http://timestamp.digicert.com',
    [switch]$VerifyOnly,
    [string]$ReportPath
)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\windows_sdk.ps1"
try {
    $thumb = Assert-SigningThumbprint $Thumbprint
    $file = (Resolve-Path -LiteralPath $Path).Path
    $signingExtension = [IO.Path]::GetExtension($file)
    # Inno signs its uninstaller before renaming the temporary PE file.
    if ($file -match '\.(e32|e64)\.tmp$') { $signingExtension = '.e32' }
    if ($signingExtension -notin @('.exe','.dll','.e32','.e64','.msix','.msixbundle')) { throw 'Unsupported signing file type' }
    $tool = Find-WindowsSdkTool 'signtool'
    if (-not $VerifyOnly) {
        $uri = [uri]$TimestampUrl
        if (-not $uri.IsAbsoluteUri -or $uri.Scheme -notin @('http','https')) { throw 'Use an absolute RFC3161 timestamp URL' }
        $cert = Get-Item -LiteralPath "Cert:\CurrentUser\My\$thumb" -ErrorAction Stop
        if (-not $cert.HasPrivateKey) { throw 'The selected signing identity has no accessible private key' }
        if ($cert.NotAfter -le (Get-Date) -or $cert.NotBefore -gt (Get-Date)) { throw 'The signing certificate is not currently valid' }
        $eku = @($cert.Extensions | Where-Object { $_.Oid.Value -eq '2.5.29.37' } |
            ForEach-Object { $_.EnhancedKeyUsages } | ForEach-Object { $_.Value })
        if ('1.3.6.1.5.5.7.3.3' -notin $eku) { throw 'Certificate must explicitly permit code signing' }
        # No PFX password on a process command line; select the installed private-key provider.
        & $tool sign /fd SHA256 /td SHA256 /tr $TimestampUrl /sha1 $thumb /s My /d 'GH3 Chart Studio' $file
        if ($LASTEXITCODE -ne 0) { throw "SignTool signing/timestamp failed ($LASTEXITCODE)" }
    }
    & $tool verify /pa /all /tw $file
    if ($LASTEXITCODE -ne 0) { throw "SignTool Authenticode verification failed ($LASTEXITCODE)" }
    $signature = Get-AuthenticodeSignature -LiteralPath $file
    if ($signature.Status -ne 'Valid' -or -not $signature.SignerCertificate) { throw 'Signature is not valid and trusted on this build machine' }
    if ($signature.SignerCertificate.Thumbprint -ne $thumb) { throw 'Signer does not match the expected publisher certificate' }
    if (-not $signature.TimeStamperCertificate) { throw 'A verified timestamp is required' }
    $report = [ordered]@{
        file = [IO.Path]::GetFileName($file); sha256 = (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash
        signer_subject = $signature.SignerCertificate.Subject; signer_thumbprint = $thumb
        timestamp_subject = $signature.TimeStamperCertificate.Subject; signature_status = 'Valid'
        checked_at_utc = [DateTime]::UtcNow.ToString('o')
    }
    if ($ReportPath) { $report | ConvertTo-Json | Set-Content -LiteralPath $ReportPath -Encoding UTF8 }
    Write-Host ('Verified signed file: ' + $report.file)
} catch {
    Write-Error $_
    exit 1
}
