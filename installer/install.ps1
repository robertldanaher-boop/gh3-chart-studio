<#
  GH3 Chart Studio - script installer for Windows 10/11 (Windows PowerShell 5.1+).

  Does what a normal per-user Windows installer does, without needing a compiled
  setup .exe:
    * copies the program to %LOCALAPPDATA%\Programs\GH3 Chart Studio
    * runs setup and the full automated test suite once (START_WINDOWS.cmd --install)
    * creates Start menu entries (GH3 Chart Studio, GH3 Chart Studio - Repair,
      GH3 Chart Studio - Uninstall)
      and a desktop icon
    * registers the program in Settings > Apps > Installed apps with an Uninstall
      button (same registry entry the Inno Setup installer uses, so the two never
      show up twice)
  No administrator rights are needed. Run it with "Install GH3 Chart Studio.cmd".
#>
param([switch]$NoDesktopIcon, [switch]$NoLaunch, [switch]$SkipConfirmation)

$ErrorActionPreference = 'Stop'
$AppName   = 'GH3 Chart Studio'
$AppId     = '{2E998221-C3C3-4195-9C31-6047FBBDDE0E}_is1'
$Releases  = 'https://github.com/robertldanaher-boop/gh3-chart-studio/releases'
$Source    = Split-Path -Parent $PSScriptRoot
$Target    = Join-Path $env:LOCALAPPDATA "Programs\$AppName"
$UninstallKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$AppId"

Add-Type -AssemblyName System.Windows.Forms
. (Join-Path $PSScriptRoot 'transaction.ps1')
$installLock = $null
$stage = $null
function Show-Message([string]$text, [string]$icon = 'Information') {
    [void][System.Windows.Forms.MessageBox]::Show($text, "$AppName setup", 'OK', $icon)
}

function Get-AppVersion([string]$root) {
    $line = Select-String -Path (Join-Path $root 'gh3studio\__init__.py') -Pattern "__version__\s*=\s*'([^']+)'" | Select-Object -First 1
    if ($line) { return $line.Matches[0].Groups[1].Value }
    return '0.0.0'
}

try {
    if (-not (Test-Path (Join-Path $Source 'START_WINDOWS.cmd')) -or -not (Test-Path (Join-Path $Source 'gh3studio\__init__.py'))) {
        throw "Extract the whole ZIP first, then run 'Install GH3 Chart Studio.cmd' from the extracted folder."
    }
    if ([Environment]::Is64BitOperatingSystem -eq $false) { throw 'GH3 Chart Studio needs 64-bit Windows.' }
    $version = Get-AppVersion $Source

    if (-not $SkipConfirmation) {
    $answer = [System.Windows.Forms.MessageBox]::Show(
        "Install $AppName $version for your Windows account?`n`n" +
        "Location: $Target`n`n" +
        "Setup will install Python 3.11 if needed, download the program's libraries and run the automated tests once. " +
        "This needs an internet connection and can take several minutes the first time.",
        "$AppName setup", 'OKCancel', 'Question')
    if ($answer -ne 'OK') { exit 1 }
    }

    # When started by the app's "Download and install", the app is still closing: wait up to 30 s.
    $deadline = (Get-Date).AddSeconds(30)
    do {
        $running = Get-CimInstance Win32_Process -Filter "Name='pythonw.exe' OR Name='python.exe'" -ErrorAction SilentlyContinue |
            Where-Object { $_.CommandLine -and $_.CommandLine -like "*$Target*" }
        if ($running) { Start-Sleep -Milliseconds 500 }
    } while ($running -and (Get-Date) -lt $deadline)
    if ($running) { throw "$AppName is running. Close it, then run the installer again." }

    # Serialize installers. An abandoned process releases the exclusive handle.
    $parent = Split-Path -Parent $Target
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    $lockPath = Join-Path $parent 'GH3 Chart Studio.install.lock'
    $installLock = [System.IO.File]::Open($lockPath, 'OpenOrCreate', 'ReadWrite', 'None')

    # Stage BEFORE moving any installed files; this also supports repair from
    # inside Target. A fresh venv is built at Target, never moved after setup.
    $stage = "$Target.staging-$([Guid]::NewGuid().ToString('N'))"
    New-Item -ItemType Directory -Path $stage | Out-Null
    $null = & robocopy $Source $stage /E /NFL /NDL /NJH /NJS /NP /R:1 /W:1 `
        /XD .git .github .venv __pycache__ .pytest_cache output dist build `
        /XF *.log *.pyc startup_timings.json repository.bundle *.zip
    if ($LASTEXITCODE -ge 8) { throw "Copying the program files failed (robocopy exit $LASTEXITCODE). The installed version was not changed." }
    $backup = Install-StagedProgram -Stage $stage -Target $Target -Validate {
        param($installedRoot)
        $setup = Start-Process -FilePath (Join-Path $env:SystemRoot 'System32\cmd.exe') `
            -ArgumentList '/c', "`"`"$installedRoot\START_WINDOWS.cmd`" --install`"" `
            -WorkingDirectory $installedRoot -WindowStyle Hidden -Wait -PassThru
        if ($setup.ExitCode -ne 0 -or -not (Test-Path (Join-Path $installedRoot '.venv\installed.json'))) {
            throw "Setup or automated tests failed (exit $($setup.ExitCode))."
        }
    }
    $stage = $null

    # Publish shortcuts and registration only after successful setup and tests.
    $shell   = New-Object -ComObject WScript.Shell
    $icon    = Join-Path $Target 'gh3studio\assets\app.ico'
    $pythonw = Join-Path $Target '.venv\Scripts\pythonw.exe'
    $runApp  = Join-Path $Target 'run_app.py'
    function New-Shortcut([string]$path, [string]$exe, [string]$arguments, [string]$description) {
        $link = $shell.CreateShortcut($path)
        $link.TargetPath = $exe
        $link.Arguments = $arguments
        $link.WorkingDirectory = $Target
        $link.IconLocation = "$icon,0"
        $link.Description = $description
        $link.Save()
    }
    $programs = [Environment]::GetFolderPath('Programs')
    $desktop  = [Environment]::GetFolderPath('Desktop')
    New-Shortcut (Join-Path $programs "$AppName.lnk") $pythonw "`"$runApp`"" 'Clean charts and build four-fret Medium for Guitar Hero III Wii'
    New-Shortcut (Join-Path $programs "$AppName - Repair.lnk") (Join-Path $Target 'START_WINDOWS.cmd') '--install' 'Re-run setup and the automated tests'
    $uninstallScript = Join-Path $Target 'installer\uninstall.ps1'
    New-Shortcut (Join-Path $programs "$AppName - Uninstall.lnk") (Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe') `
        "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$uninstallScript`"" "Remove $AppName from this PC"
    if (-not $NoDesktopIcon) {
        New-Shortcut (Join-Path $desktop "$AppName.lnk") $pythonw "`"$runApp`"" 'GH3 Chart Studio'
    }

    # Settings > Apps entry with Uninstall.
    $sizeKb = [int]((Get-ChildItem $Target -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum / 1KB)
    New-Item -Path $UninstallKey -Force | Out-Null
    $values = @{
        DisplayName     = $AppName
        DisplayVersion  = $version
        Publisher       = 'Bob Danaher'
        DisplayIcon     = $icon
        InstallLocation = $Target
        URLInfoAbout    = $Releases
        URLUpdateInfo   = $Releases
        UninstallString = "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$uninstallScript`""
        QuietUninstallString = "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$uninstallScript`" -Quiet"
        InstallDate     = (Get-Date -Format 'yyyyMMdd')
    }
    foreach ($name in $values.Keys) { Set-ItemProperty -Path $UninstallKey -Name $name -Value $values[$name] }
    Set-ItemProperty -Path $UninstallKey -Name NoModify -Value 1 -Type DWord
    Set-ItemProperty -Path $UninstallKey -Name NoRepair -Value 1 -Type DWord
    Set-ItemProperty -Path $UninstallKey -Name EstimatedSize -Value $sizeKb -Type DWord

    $backupNote = if ($backup) { "`n`nPrevious installation retained at:`n$backup" } else { '' }
    Show-Message "$AppName $version is installed.`n`nOpen it from the Start menu or desktop icon.$backupNote"
    if (-not $NoLaunch) { Start-Process -FilePath $pythonw -ArgumentList "`"$runApp`"" -WorkingDirectory $Target }
    exit 0
}
catch {
    Show-Message ("Installation stopped:`n`n" + $_.Exception.Message) 'Error'
    exit 1
}
finally {
    if ($stage -and (Test-Path -LiteralPath $stage)) { Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue }
    if ($installLock) { $installLock.Dispose() }
}
