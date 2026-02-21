@echo off
setlocal EnableDelayedExpansion

:: ============================================================
::  Arc Booster — Windows build script
::  Produces a single-file executable: dist\ArcBooster.exe
:: ============================================================

echo.
echo  ============================================================
echo   Arc Booster Build Script
echo  ============================================================
echo.

:: ── 1. Check Python ──────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found on PATH.
    echo.
    echo  Please install Python 3.8+ from https://python.org/downloads
    echo  and make sure "Add Python to PATH" is checked during install.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo  Found: %%v

:: ── 2. Install / upgrade PyInstaller ─────────────────────────
echo.
echo  [1/3] Installing build tools ...
echo.
python -m pip install --upgrade --quiet pyinstaller
if errorlevel 1 (
    echo  [ERROR] Failed to install PyInstaller.
    echo  Try running this script as Administrator or check your pip configuration.
    pause
    exit /b 1
)
echo  PyInstaller ready.

:: ── 3. Build the executable ──────────────────────────────────
echo.
echo  [2/3] Building ArcBooster.exe ...
echo.

:: Remove previous build artefacts to ensure a clean build
if exist build  rmdir /s /q build
if exist dist   rmdir /s /q dist

:: PyInstaller flags:
::   --onefile          bundle everything into a single .exe
::   --windowed         no console window (GUI application)
::   --name             output executable name
::   --icon             application icon (skipped if file absent)
::   --clean            purge cached build data before building

set ICON_FLAG=
if exist arc_booster.ico set ICON_FLAG=--icon arc_booster.ico

python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name ArcBooster ^
    --clean ^
    %ICON_FLAG% ^
    arc_booster.py

if errorlevel 1 (
    echo.
    echo  [ERROR] Build failed — see output above for details.
    pause
    exit /b 1
)

:: ── 4. Done ──────────────────────────────────────────────────
echo.
echo  [3/3] Build complete!
echo.
echo  Output: dist\ArcBooster.exe
echo.
echo  ============================================================
echo   To use:
echo     1. Open dist\ArcBooster.exe
echo     2. Right-click ^> "Run as administrator" for full effect
echo  ============================================================
echo.

:: Open the output folder in Explorer for convenience
explorer dist

pause
