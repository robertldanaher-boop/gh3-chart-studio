param()
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\windows_sdk.ps1"
$pfx = $null
try {
    $expected = Assert-SigningThumbprint $env:GH3_CODESIGN_THUMBPRINT
    if (-not $env:GH3_CODESIGN_PFX_BASE64 -or -not $env:GH3_CODESIGN_PFX_PASSWORD) {
        throw 'Configure the protected release environment signing secrets; no unsigned release will be uploaded.'
    }
    if (Test-Path "Cert:\CurrentUser\My\$expected") { throw 'Signing certificate already exists; refusing to overwrite a runner identity' }
    $pfx = Join-Path $env:RUNNER_TEMP ('gh3-sign-' + [guid]::NewGuid() + '.pfx')
    [IO.File]::WriteAllBytes($pfx,[Convert]::FromBase64String($env:GH3_CODESIGN_PFX_BASE64))
    $password = ConvertTo-SecureString $env:GH3_CODESIGN_PFX_PASSWORD -AsPlainText -Force
    $certs = @(Import-PfxCertificate -FilePath $pfx -CertStoreLocation Cert:\CurrentUser\My -Password $password)
    $private = @($certs | Where-Object { $_.HasPrivateKey })
    if ($private.Count -ne 1 -or $private[0].Thumbprint -ne $expected) {
        foreach ($cert in $certs) { Remove-Item -LiteralPath ("Cert:\CurrentUser\My\" + $cert.Thumbprint) -Force -ErrorAction SilentlyContinue }
        throw 'Imported private-key identity does not match the pinned signing thumbprint'
    }
    # Only public identifiers cross steps. The password/private key are never logged.
    "GH3_SIGNING_THUMBPRINT=$expected" | Out-File $env:GITHUB_ENV -Append -Encoding UTF8
    "GH3_IMPORTED_CERTIFICATE=$expected" | Out-File $env:GITHUB_ENV -Append -Encoding UTF8
} catch { Write-Error $_; exit 1 }
finally {
    if ($pfx -and (Test-Path -LiteralPath $pfx)) { Remove-Item -LiteralPath $pfx -Force }
    Remove-Item Env:GH3_CODESIGN_PFX_BASE64,Env:GH3_CODESIGN_PFX_PASSWORD -ErrorAction SilentlyContinue
}
