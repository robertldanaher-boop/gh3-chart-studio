<#
  GH3 Chart Studio - uninstaller for the script installer (install.ps1).
  Removes the Start menu entries, desktop icon, the Settings > Apps entry and the
  installed program folder (including its private Python environment).
  Your songs, charts and exported song folders are never touched: they live
  outside the program folder.
#>
param([switch]$Quiet)

$ErrorActionPreference = 'Continue'
$AppName = 'GH3 Chart Studio'
$AppId   = '{2E998221-C3C3-4195-9C31-6047FBBDDE0E}_is1'
$Target  = Join-Path $env:LOCALAPPDATA "Programs\$AppName"
$UninstallKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$AppId"
Add-Type -AssemblyName System.Windows.Forms

if (-not $Quiet) {
    $answer = [System.Windows.Forms.MessageBox]::Show("Remove $AppName from this PC?`n`nYour songs and exported folders are not affected.",
        "Uninstall $AppName", 'OKCancel', 'Question')
    if ($answer -ne 'OK') { exit 1 }
}

$running = Get-CimInstance Win32_Process -Filter "Name='pythonw.exe' OR Name='python.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -and $_.CommandLine -like "*$Target*" }
if ($running) {
    if (-not $Quiet) { [void][System.Windows.Forms.MessageBox]::Show("$AppName is running. Close it, then uninstall again.", "Uninstall $AppName", 'OK', 'Warning') }
    exit 1
}

$programs = [Environment]::GetFolderPath('Programs')
$desktop  = [Environment]::GetFolderPath('Desktop')
foreach ($link in @((Join-Path $programs "$AppName.lnk"), (Join-Path $programs "$AppName - Repair.lnk"),
                    (Join-Path $programs "$AppName - Uninstall.lnk"), (Join-Path $desktop "$AppName.lnk"))) {
    Remove-Item -Force $link -ErrorAction SilentlyContinue
}
Remove-Item -Path $UninstallKey -Recurse -Force -ErrorAction SilentlyContinue

# This script lives inside the folder being removed; PowerShell has already read
# it, so the folder can be deleted. Anything still locked is reported.
Set-Location $env:TEMP
Remove-Item -Recurse -Force $Target -ErrorAction SilentlyContinue
if (Test-Path $Target) {
    if (-not $Quiet) { [void][System.Windows.Forms.MessageBox]::Show("Most files were removed. Some were in use; delete this folder later:`n$Target", "Uninstall $AppName", 'OK', 'Warning') }
    exit 2
}
if (-not $Quiet) { [void][System.Windows.Forms.MessageBox]::Show("$AppName was removed.", "Uninstall $AppName", 'OK', 'Information') }
exit 0
