; GH3 Chart Studio — Windows 10/11 installer (Inno Setup 6.3 or newer).
;
; Per-user install (no administrator prompt) to %LOCALAPPDATA%\Programs\GH3 Chart Studio.
; The compiled installer stages its payload in a temporary folder and calls the
; same transactional PowerShell installer used by app updates. That installer
; runs START_WINDOWS.cmd --install to find or install Python 3.11 x64,
; creates the private .venv, installs the hash-pinned dependencies and runs the full
; automated test suite ONCE. Start menu / desktop shortcuts then launch the studio
; directly with no setup or tests. "GH3 Chart Studio - Repair" repeats the setup.
;
; Build: installer\build_installer.cmd (local) or the GitHub Actions workflow.
; Version comes from gh3studio\__init__.py via /DAppVersion=x.y.z.

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif
#ifndef GH3SignedBuild
  #ifndef GH3UnsignedBuild
    #error Use build_installer.ps1: signed builds require a signing identity; development builds must explicitly select -Unsigned.
  #endif
#endif
#define AppName "GH3 Chart Studio"
#define AppUserModelID "GH3ChartStudio.Studio"
#define ReleasesURL "https://github.com/robertldanaher-boop/gh3-chart-studio/releases"

[Setup]
; Never change AppId: it is how Windows recognises upgrades of the same program.
AppId={{2E998221-C3C3-4195-9C31-6047FBBDDE0E}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher=Bob Danaher
AppPublisherURL={#ReleasesURL}
AppSupportURL={#ReleasesURL}
AppUpdatesURL={#ReleasesURL}
VersionInfoVersion={#AppVersion}
DefaultDirName={localappdata}\Programs\{#AppName}
DisableProgramGroupPage=yes
DisableDirPage=yes
CreateAppDir=no
Uninstallable=no
#ifdef GH3SignedBuild
SignTool=gh3sign
SignedUninstaller=yes
#else
SignedUninstaller=no
#endif
UsePreviousAppDir=no
; install.ps1 owns shortcuts and the per-user uninstall registry entry.
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; Windows 10 1809 or newer, including all Windows 11 versions.
MinVersion=10.0.17763
LicenseFile=..\LICENSE
SetupIconFile=..\gh3studio\assets\app.ico
UninstallDisplayIcon={app}\gh3studio\assets\app.ico
UninstallDisplayName={#AppName}
WizardStyle=modern
WizardImageFile=wizard_large.bmp,wizard_large_200.bmp
WizardSmallImageFile=wizard_small.bmp,wizard_small_200.bmp
OutputDir=output
#ifdef GH3SignedBuild
OutputBaseFilename=GH3ChartStudio-Setup-{#AppVersion}
#else
OutputBaseFilename=GH3ChartStudio-Setup-{#AppVersion}-unsigned
#endif
Compression=lzma2/max
SolidCompression=yes
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Shortcuts:"

[Files]
; Never overwrite the live app from Inno Setup. The shared script stages,
; validates at the final path, and restores the previous app on setup failure.
Source: "..\*"; DestDir: "{tmp}\gh3-payload"; Flags: ignoreversion recursesubdirs createallsubdirs; \
  Excludes: ".git,.github,.venv,dist,build,__pycache__,*.pyc,.pytest_cache,*.log,startup_timings.json,repository.bundle,*.zip,.startup-ready-*,installer\output,packaging\work,packaging\output,*.pfx,*.p12,*.key,*.pem,*.e32,*.e64"

[Run]
Filename: "{localappdata}\Programs\GH3 Chart Studio\.venv\Scripts\pythonw.exe"; \
  Parameters: """{localappdata}\Programs\GH3 Chart Studio\run_app.py"""; \
  WorkingDir: "{localappdata}\Programs\GH3 Chart Studio"; \
  Description: "Open {#AppName} now"; Flags: postinstall nowait skipifsilent; Check: SetupSucceeded

[Code]
var
  SetupOk: Boolean;

function SetupSucceeded: Boolean;
begin
  Result := SetupOk;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
  Command: String;
begin
  if CurStep = ssPostInstall then
  begin
    SetupOk := False;
    WizardForm.StatusLabel.Caption := 'Installing and testing the update; the previous version is retained...';
    Command := '-NoProfile -ExecutionPolicy Bypass -File "' +
      ExpandConstant('{tmp}\gh3-payload\installer\install.ps1') + '" -NoLaunch -SkipConfirmation';
    if not WizardIsTaskSelected('desktopicon') then
      Command := Command + ' -NoDesktopIcon';
    if Exec(ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe'), Command,
      ExpandConstant('{tmp}'), SW_HIDE, ewWaitUntilTerminated, ResultCode) then
      SetupOk := (ResultCode = 0);
    if not SetupOk then
      RaiseException('Installation did not complete. See the installer error for recovery status and diagnostic file location.');
  end;
end;
