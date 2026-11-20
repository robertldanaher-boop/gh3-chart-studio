; GH3 Chart Studio — Windows 10/11 installer (Inno Setup 6.3 or newer).
;
; Per-user install (no administrator prompt) to %LOCALAPPDATA%\Programs\GH3 Chart Studio.
; During installation START_WINDOWS.cmd --install finds or installs Python 3.11 x64,
; creates the private .venv, installs the hash-pinned dependencies and runs the full
; automated test suite ONCE. Start menu / desktop shortcuts then launch the studio
; directly with no setup or tests. "GH3 Chart Studio - Repair" repeats the setup.
;
; Build: installer\build_installer.cmd (local) or the GitHub Actions workflow.
; Version comes from gh3studio\__init__.py via /DAppVersion=x.y.z.

#ifndef AppVersion
  #define AppVersion "0.0.0"
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
OutputBaseFilename=GH3ChartStudio-Setup-{#AppVersion}
Compression=lzma2/max
SolidCompression=yes
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Shortcuts:"

[InstallDelete]
; Remove the previous version's code first so deleted modules/tests never linger.
; The .venv is kept: unchanged dependencies are reused instead of downloaded again.
Type: filesandordirs; Name: "{app}\gh3studio"
Type: filesandordirs; Name: "{app}\tests"
Type: filesandordirs; Name: "{app}\tools"
Type: filesandordirs; Name: "{app}\docs"
Type: filesandordirs; Name: "{app}\examples"
Type: filesandordirs; Name: "{app}\licenses"
Type: filesandordirs; Name: "{app}\presets"
Type: files; Name: "{app}\.venv\installed.json"

[Files]
Source: "..\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; \
  Excludes: ".git,.github,.venv,installer,dist,build,__pycache__,*.pyc,.pytest_cache,*.log,startup_timings.json,repository.bundle,*.zip,.startup-ready-*"

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\.venv\Scripts\pythonw.exe"; \
  Parameters: """{app}\run_app.py"""; WorkingDir: "{app}"; \
  IconFilename: "{app}\gh3studio\assets\app.ico"; AppUserModelID: "{#AppUserModelID}"; \
  Comment: "Clean charts and build four-fret Medium for Guitar Hero III Wii"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\.venv\Scripts\pythonw.exe"; \
  Parameters: """{app}\run_app.py"""; WorkingDir: "{app}"; \
  IconFilename: "{app}\gh3studio\assets\app.ico"; AppUserModelID: "{#AppUserModelID}"; Tasks: desktopicon
Name: "{autoprograms}\{#AppName} - Repair"; Filename: "{app}\START_WINDOWS.cmd"; \
  Parameters: "--install"; WorkingDir: "{app}"; IconFilename: "{app}\gh3studio\assets\app.ico"; \
  Comment: "Re-run setup and the automated tests"

[Run]
Filename: "{app}\.venv\Scripts\pythonw.exe"; Parameters: """{app}\run_app.py"""; WorkingDir: "{app}"; \
  Description: "Open {#AppName} now"; Flags: postinstall nowait skipifsilent; Check: SetupSucceeded

[UninstallDelete]
Type: filesandordirs; Name: "{app}\.venv"
Type: filesandordirs; Name: "{app}\gh3studio"
Type: filesandordirs; Name: "{app}\tests"
Type: filesandordirs; Name: "{app}\tools"
Type: filesandordirs; Name: "{app}\.pytest_cache"
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\startup_timings.json"
Type: dirifempty; Name: "{app}"

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
    WizardForm.StatusLabel.Caption := 'Setting up Python, dependencies and running the automated tests (several minutes on first install)...';
    Command := '/c ""' + ExpandConstant('{app}\START_WINDOWS.cmd') + '" --install"';
    if Exec(ExpandConstant('{cmd}'), Command, ExpandConstant('{app}'), SW_HIDE, ewWaitUntilTerminated, ResultCode) then
      SetupOk := (ResultCode = 0);
    if not SetupOk then
      MsgBox('The program files were installed, but setup or the automated tests did not finish.' + #13#10#13#10 +
        'Logs are in:' + #13#10 + ExpandConstant('{app}') + #13#10 +
        '(start_windows.log and startup_bootstrap.log)' + #13#10#13#10 +
        'Fix the cause (for example the internet connection) and run "GH3 Chart Studio - Repair" from the Start menu.',
        mbError, MB_OK);
  end;
end;
