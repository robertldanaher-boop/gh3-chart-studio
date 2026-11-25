"""Real Windows SDK signing/MakeAppx tests. Test certs never leave the runner."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import pytest

ROOT=Path(__file__).resolve().parents[1]
PWSH=shutil.which('pwsh') or shutil.which('powershell')
pytestmark=pytest.mark.skipif(os.name!='nt' or not PWSH,reason='Windows SDK and Windows certificate store integration')


@pytest.fixture(autouse=True)
def packaging_tools_available():
    kits=Path(os.environ.get('ProgramFiles(x86)','C:/Program Files (x86)'))/'Windows Kits/10/bin'
    missing=[name for name in ('signtool','makeappx') if not (shutil.which(name) or any(kits.glob('*/x64/'+name+'.exe')))]
    inno=Path(os.environ.get('ProgramFiles(x86)','C:/Program Files (x86)'))/'Inno Setup 6/ISCC.exe'
    if not inno.is_file():missing.append('Inno Setup 6')
    if missing:
        reason='Developer packaging tools not installed: '+', '.join(missing)
        if os.environ.get('GH3_REQUIRE_WINDOWS_PACKAGING_TESTS')=='1':pytest.fail(reason)
        pytest.skip(reason)


def run(script,tmp_path,**env):
    path=tmp_path/'check.ps1';path.write_text(script,encoding='utf-8-sig')
    return subprocess.run([PWSH,'-NoProfile','-NonInteractive','-File',str(path)],env=dict(os.environ,GH3_REPO=str(ROOT),GH3_PYTHON=sys.executable,RUNNER_TEMP=str(tmp_path),**env),text=True,capture_output=True,timeout=120)


def test_missing_signing_identity_stops_without_modifying_file(tmp_path):
    target=tmp_path/'app.exe';shutil.copyfile(sys.executable,target);before=target.read_bytes()
    r=subprocess.run([PWSH,'-NoProfile','-NonInteractive','-File',str(ROOT/'installer/sign.ps1'),'-Path',str(target)],env=dict(os.environ,GH3_SIGNING_THUMBPRINT=''),text=True,capture_output=True,timeout=30)
    assert r.returncode!=0 and target.read_bytes()==before
    assert 'GH3_SIGNING_THUMBPRINT' in r.stderr+r.stdout


def test_real_sign_timestamp_verify_and_tamper_rejection(tmp_path):
    if os.environ.get('GH3_REQUIRE_WINDOWS_PACKAGING_TESTS')!='1' and os.environ.get('GH3_RUN_ISOLATED_SIGNING_TEST')!='1':
        pytest.skip('Trust-store integration is opt-in for an isolated Windows VM/CI only')
    # Build the real installer hook against a minimal source fixture, with spaces in its path.
    source=tmp_path/'installer source';(source/'gh3studio/assets').mkdir(parents=True)
    shutil.copytree(ROOT/'installer',source/'installer',ignore=shutil.ignore_patterns('output'))
    for relative in ['LICENSE','gh3studio/__init__.py','gh3studio/assets/app.ico']:
        shutil.copyfile(ROOT/relative,source/relative)
    # The temporary self-signed identity is trusted ONLY inside this isolated test.
    script=r'''
$ErrorActionPreference='Stop'
. "$env:GH3_REPO\installer\windows_sdk.ps1"
$tool=Find-WindowsSdkTool 'signtool'
$subject='CN=GH3 isolated signing test '+[guid]::NewGuid()
$cert=New-SelfSignedCertificate -Type CodeSigningCert -Subject $subject -KeyExportPolicy Exportable -CertStoreLocation Cert:\CurrentUser\My
$public=Join-Path $env:TEMP ([guid]::NewGuid().ToString()+'.cer')
try {
 Export-Certificate -Cert $cert -FilePath $public | Out-Null
 Import-Certificate -FilePath $public -CertStoreLocation Cert:\LocalMachine\Root | Out-Null
 # Exercise CI PFX import without exposing a password in a command line or a repository file.
 $base=Split-Path $PSCommandPath
 $pfx=Join-Path $base 'temporary-test-key.pfx'
 $secret=[guid]::NewGuid().ToString()
 $secure=ConvertTo-SecureString $secret -AsPlainText -Force
 Export-PfxCertificate -Cert $cert -FilePath $pfx -Password $secure | Out-Null
 Remove-Item "Cert:\CurrentUser\My\$($cert.Thumbprint)" -DeleteKey -Force
 $env:GH3_CODESIGN_PFX_BASE64=[Convert]::ToBase64String([IO.File]::ReadAllBytes($pfx))
 Remove-Item $pfx -Force
 $env:GH3_CODESIGN_PFX_PASSWORD=$secret
 $env:GH3_CODESIGN_THUMBPRINT=$cert.Thumbprint
 $env:GITHUB_ENV=Join-Path $base 'public-signing-environment.txt'
 & "$env:GH3_REPO\installer\import_ci_certificate.ps1"
 if (-not (Test-Path "Cert:\CurrentUser\My\$($cert.Thumbprint)")) {throw 'PFX import did not install the expected key'}
 if ((Get-Content $env:GITHUB_ENV -Raw) -match [regex]::Escape($secret)) {throw 'Private password leaked to environment output'}
 $file=Join-Path (Split-Path $PSCommandPath) 'signed app.exe' 
 Copy-Item -LiteralPath $env:GH3_PYTHON -Destination $file
 $env:GH3_SIGNING_THUMBPRINT=$cert.Thumbprint
 & "$env:GH3_REPO\installer\sign.ps1" -Path $file -ReportPath ($file+'.json')
 if ($LASTEXITCODE -ne 0) {throw 'Real signing/timestamp failed'}
 $info=Get-Content ($file+'.json') -Raw | ConvertFrom-Json
 if ($info.signer_thumbprint -ne $cert.Thumbprint -or $info.signature_status -ne 'Valid') {throw 'Identity verification failed'}
 $base=Split-Path $PSCommandPath
 $app=Join-Path $base 'msix-app';New-Item -ItemType Directory -Path $app | Out-Null
 Copy-Item $env:GH3_PYTHON (Join-Path $app 'GH3ChartStudio.exe')
 & $env:GH3_PYTHON "$env:GH3_REPO\packaging\msix_manifest.py" --app-root $app --version 0.20.0 --publisher $cert.Subject
 if ($LASTEXITCODE -ne 0) {throw 'Manifest generation failed'}
 $make=Find-WindowsSdkTool 'makeappx'
 $packages=Join-Path $base 'signed-bundle-input';New-Item -ItemType Directory -Path $packages | Out-Null
 & $make pack /o /d $app /p (Join-Path $packages 'app.msix')
 if ($LASTEXITCODE -ne 0) {throw 'MSIX pack failed'}
 $bundle=Join-Path $base 'signed.msixbundle'
 & $make bundle /o /d $packages /p $bundle
 if ($LASTEXITCODE -ne 0) {throw 'MSIX bundle failed'}
 & "$env:GH3_REPO\installer\sign.ps1" -Path $bundle -ReportPath ($bundle+'.json')
 if ($LASTEXITCODE -ne 0) {throw 'MSIX signing failed'}
 & "$env:GH3_TEST_INSTALL_SOURCE\installer\build_installer.ps1"
 if ($LASTEXITCODE -ne 0) {throw 'Signed Inno hook build failed'}
 $bytes=[IO.File]::ReadAllBytes($file);$bytes[128]=$bytes[128] -bxor 1;[IO.File]::WriteAllBytes($file,$bytes)
 # Run verification out-of-process: expected failure must not exit this test script.
 & (Get-Process -Id $PID).Path -NoProfile -NonInteractive -File "$env:GH3_REPO\installer\sign.ps1" -Path $file -VerifyOnly
 if ($LASTEXITCODE -eq 0) {throw 'Tampered binary was accepted'}
 Write-Host 'SIGNED_TIMESTAMPED_VERIFIED_AND_TAMPER_REJECTED'
} finally {
 Remove-Item "Cert:\LocalMachine\Root\$($cert.Thumbprint)" -Force -ErrorAction SilentlyContinue
 Remove-Item "Cert:\CurrentUser\My\$($cert.Thumbprint)" -DeleteKey -Force -ErrorAction SilentlyContinue
 Remove-Item $public -Force -ErrorAction SilentlyContinue
}
'''
    r=run(script,tmp_path,GH3_TEST_INSTALL_SOURCE=str(source))
    assert r.returncode==0,r.stdout+r.stderr
    assert 'SIGNED_TIMESTAMPED_VERIFIED_AND_TAMPER_REJECTED' in r.stdout


def test_windows_sdk_can_pack_and_bundle_generated_manifest(tmp_path):
    app=tmp_path/'app';app.mkdir();shutil.copyfile(sys.executable,app/'GH3ChartStudio.exe')
    subprocess.run([sys.executable,str(ROOT/'packaging/msix_manifest.py'),'--app-root',str(app),'--version','0.20.0','--publisher','CN=GH3 test'],check=True)
    script=r'''
$ErrorActionPreference='Stop'
. "$env:GH3_REPO\installer\windows_sdk.ps1"
$tool=Find-WindowsSdkTool 'makeappx'
$base=Split-Path $PSCommandPath
$bundleInput=Join-Path $base 'bundle-input';New-Item -ItemType Directory -Path $bundleInput | Out-Null
& $tool pack /o /d (Join-Path $base 'app') /p (Join-Path $bundleInput 'app.msix')
if ($LASTEXITCODE -ne 0) {throw 'Package validation failed'}
& $tool bundle /o /d $bundleInput /p (Join-Path $base 'app.msixbundle')
if ($LASTEXITCODE -ne 0) {throw 'Bundle validation failed'}
& $tool unbundle /o /p (Join-Path $base 'app.msixbundle') /d (Join-Path $base 'unbundled')
if ($LASTEXITCODE -ne 0) {throw 'Bundle read-back failed'}
if (-not (Test-Path (Join-Path $base 'unbundled\app.msix'))) {throw 'Expected architecture package missing'}
'''
    r=run(script,tmp_path)
    assert r.returncode==0,r.stdout+r.stderr
