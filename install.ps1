# FokusBar für Windows – 1-Klick Installer (Windows 10 & 11)
# Lädt FokusBar-Windows.exe (oder installiert aus dem Repo), legt Desktop- & Startmenü-Verknüpfungen an und startet FokusBar sofort.

$ErrorActionPreference = "Stop"

Write-Host "🚀 FokusBar für Windows wird installiert ..." -ForegroundColor Cyan

$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\FokusBar"
$SoundsDir  = Join-Path $InstallDir "Resources\Sounds"
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
New-Item -ItemType Directory -Force -Path $SoundsDir  | Out-Null

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Lade die fertige FokusBar-Windows.exe vom offiziellen GitHub-Release
$ReleaseExeUrl = "https://github.com/Jusaain/fokus-bar-windows/releases/latest/download/FokusBar-Windows.exe"
$TargetExe     = Join-Path $InstallDir "FokusBar.exe"
$DownloadedExe = $false

try {
    Write-Host "📥 Lade FokusBar-Windows.exe ..." -ForegroundColor Gray
    Invoke-WebRequest -Uri $ReleaseExeUrl -OutFile $TargetExe -UseBasicParsing -TimeoutSec 30
    if ((Test-Path $TargetExe) -and ((Get-Item $TargetExe).Length -gt 1000000)) {
        $DownloadedExe = $true
        Write-Host "✅ Standalone FokusBar.exe erfolgreich geladen." -ForegroundColor Green
    }
} catch {
    $DownloadedExe = $false
}

# 2. Lokale Dateien kopieren (Sounds + Python-App als Fallback)
if (Test-Path (Join-Path $ScriptRoot "fokusbar_win.py")) {
    Copy-Item -Force (Join-Path $ScriptRoot "fokusbar_win.py") (Join-Path $InstallDir "fokusbar_win.pyw")
}
if (Test-Path (Join-Path $ScriptRoot "Resources\Sounds")) {
    Copy-Item -Force (Join-Path $ScriptRoot "Resources\Sounds\*.m4a") $SoundsDir
}

# 3. Falls keine fertige .exe geladen wurde, Python 3 sicherstellen
if (-not $DownloadedExe) {
    $PythonCmd = Get-Command pythonw -ErrorAction SilentlyContinue
    if (-not $PythonCmd) {
        Write-Host "📦 Installiere Python 3 über winget ..." -ForegroundColor Yellow
        winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }
}

# 4. Desktop- & Startmenü-Verknüpfung erstellen
$WshShell = New-Object -ComObject WScript.Shell
$DesktopShortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) "FokusBar.lnk"
$StartMenuShortcut = Join-Path ([Environment]::GetFolderPath("Programs")) "FokusBar.lnk"

foreach ($ShortcutPath in @($DesktopShortcut, $StartMenuShortcut)) {
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    if ($DownloadedExe) {
        $Shortcut.TargetPath = $TargetExe
    } else {
        $PyW = (Get-Command pythonw).Source
        $Shortcut.TargetPath = $PyW
        $Shortcut.Arguments = "`"$(Join-Path $InstallDir 'fokusbar_win.pyw')`""
    }
    $Shortcut.WorkingDirectory = $InstallDir
    $Shortcut.Description = "FokusBar – Deep Work, Fokus-Musik & App/Website-Blocker"
    $Shortcut.Save()
}

Write-Host "✅ FokusBar installiert unter: $InstallDir" -ForegroundColor Green
Write-Host "🚀 FokusBar wird gestartet ..." -ForegroundColor Cyan

if ($DownloadedExe) {
    Start-Process -FilePath $TargetExe
} else {
    Start-Process -FilePath "pythonw" -ArgumentList "`"$(Join-Path $InstallDir 'fokusbar_win.pyw')`""
}
