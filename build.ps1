# build.ps1 — Build script for R6v3
# Produces a single-file executable that bundles ffmpeg.exe automatically.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "==> Building R6v3 with PyInstaller..." -ForegroundColor Cyan
pyinstaller --clean main.spec

Write-Host ""
Write-Host "==> Build complete. Executable is at: dist\R6v3.exe" -ForegroundColor Green

