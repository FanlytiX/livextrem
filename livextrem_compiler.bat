@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM =========================================================
REM  liveXtrem Build Script (Windows) - robust
REM  - auto-detects project root (folder containing "livextrem")
REM  - creates/uses .venv
REM  - installs deps
REM  - builds with PyInstaller (onedir)
REM  - bundles config_local.json if present, otherwise skips and
REM    creates a template.
REM  - IMPORTANT: always run the EXE from dist\livextrem\
REM =========================================================

REM --- start in folder where this .bat is located ---
cd /d "%~dp0"

REM --- Root auto-detect: go up until folder "livextrem" exists (max 6 levels) ---
set "ROOT=%CD%"
for /L %%i in (1,1,6) do (
  if exist "%ROOT%\livextrem\" goto :root_ok
  for %%p in ("%ROOT%\..") do set "ROOT=%%~fp"
)
echo ERROR: Could not find project root containing folder "livextrem".
echo Put this .bat in the project (or a subfolder) and try again.
pause
exit /b 1

:root_ok
cd /d "%ROOT%"

REM ---- CONFIG ----
set "MAIN_SCRIPT=livextrem\login.py"
set "APP_NAME=livextrem"

set "VENV_DIR=.venv"
set "VENV_PY=%CD%\%VENV_DIR%\Scripts\python.exe"

set "DIST_DIR=%CD%\dist"
set "BUILD_DIR=%CD%\build"
set "SPEC_DIR=%CD%\buildspec"

echo.
echo [1/7] Checking virtual environment...
if not exist "%VENV_DIR%\Scripts\python.exe" (
  echo     Creating venv: %VENV_DIR%
  py -3 -m venv "%VENV_DIR%"
  if errorlevel 1 (
    echo ERROR: venv creation failed.
    pause
    exit /b 1
  )
) else (
  echo     Virtual environment already exists: %VENV_DIR%
)

echo.
echo [2/7] Ensuring pip is available...
"%VENV_PY%" -m pip --version >nul 2>&1
if errorlevel 1 (
  echo     pip missing - running ensurepip...
  "%VENV_PY%" -m ensurepip --upgrade
)
"%VENV_PY%" -m pip --version >nul 2>&1
if errorlevel 1 (
  echo ERROR: pip still not available in venv.
  echo Tip: delete "%VENV_DIR%" and rerun.
  pause
  exit /b 1
)

echo.
echo [3/7] Installing / upgrading build tools...
"%VENV_PY%" -m pip install -U pip setuptools wheel
if errorlevel 1 (
  echo ERROR: pip upgrade failed.
  pause
  exit /b 1
)

echo.
echo [4/7] Installing dependencies...
if exist "requirements.txt" (
  echo     Found requirements.txt - installing...
  "%VENV_PY%" -m pip install -r requirements.txt
  if errorlevel 1 (
    echo ERROR: requirements install failed.
    pause
    exit /b 1
  )
) else (
  echo     No requirements.txt found - installing inferred deps...
  "%VENV_PY%" -m pip install customtkinter pillow requests reportlab tkcalendar twitchAPI mysql-connector-python mariadb
  if errorlevel 1 (
    echo ERROR: dependency install failed.
    echo If it fails at mariadb: install VS Build Tools or pin a version that has wheels for your Python.
    pause
    exit /b 1
  )
)

echo.
echo [5/7] Installing PyInstaller...
"%VENV_PY%" -m pip install -U pyinstaller
if errorlevel 1 (
  echo ERROR: PyInstaller install failed.
  pause
  exit /b 1
)

echo.
echo [6/7] Building with PyInstaller (onedir)...
if not exist "%MAIN_SCRIPT%" (
  echo ERROR: MAIN_SCRIPT not found: %MAIN_SCRIPT%
  pause
  exit /b 1
)

REM --- Always remove old build artifacts + spec to avoid stale --add-data paths ---
if exist "%DIST_DIR%\%APP_NAME%\" rmdir /s /q "%DIST_DIR%\%APP_NAME%\" >nul 2>&1
if exist "%BUILD_DIR%\" rmdir /s /q "%BUILD_DIR%\" >nul 2>&1
if exist "%SPEC_DIR%\%APP_NAME%.spec" del /q "%SPEC_DIR%\%APP_NAME%.spec" >nul 2>&1

if not exist "%SPEC_DIR%\" mkdir "%SPEC_DIR%" >nul 2>&1

REM --- Find config_local.json (try common locations) ---
set "CFG="
if exist "config_local.json" set "CFG=%CD%\config_local.json"
if not defined CFG if exist "livextrem\config_local.json" set "CFG=%CD%\livextrem\config_local.json"
if not defined CFG if exist "livextrem\config\config_local.json" set "CFG=%CD%\livextrem\config\config_local.json"

set "ADD_DATA_ARG="
if defined CFG (
  echo     Using config file: "!CFG!"
  REM Bundle into _internal/ so your app can load it there
  set "ADD_DATA_ARG=--add-data ""!CFG!;_internal"""
) else (
  echo     No config_local.json found. Building without bundling config.
  if not exist "livextrem\config_local.template.json" (
    echo     Creating template: livextrem\config_local.template.json
    > "livextrem\config_local.template.json" echo {
    >>"livextrem\config_local.template.json" echo   "LIVEXTREM_DB_HOST": "88.218.227.14",
    >>"livextrem\config_local.template.json" echo   "LIVEXTREM_DB_PORT": "3306",
    >>"livextrem\config_local.template.json" echo   "LIVEXTREM_DB_NAME": "livextrem",
    >>"livextrem\config_local.template.json" echo   "LIVEXTREM_DB_USER": "<db-user>",
    >>"livextrem\config_local.template.json" echo   "LIVEXTREM_DB_PASS": "<db-pass>",
    >>"livextrem\config_local.template.json" echo   "LIVEXTREM_TWITCH_CLIENT_ID": "<client-id>",
    >>"livextrem\config_local.template.json" echo   "LIVEXTREM_TWITCH_CLIENT_SECRET": "<client-secret>",
    >>"livextrem\config_local.template.json" echo   "LIVEXTREM_TWITCH_REDIRECT_URI": "http://localhost:8080"
    >>"livextrem\config_local.template.json" echo }
  )
)


REM --- Bundle logo asset (required for UI) ---
set "LOGO=%CD%\livextrem\images\logo.png"
if exist "%LOGO%" (
  echo     Using logo: "%LOGO%"
  if defined ADD_DATA_ARG (
    set "ADD_DATA_ARG=!ADD_DATA_ARG! --add-data ""%LOGO%;_internal\images"""
    set "ADD_DATA_ARG=!ADD_DATA_ARG! --add-data ""%LOGO%;_internal\livextrem\images"""
  ) else (
    set "ADD_DATA_ARG=--add-data ""%LOGO%;_internal\images"" --add-data ""%LOGO%;_internal\livextrem\images"""
  )
) else (
  echo     WARNING: Logo not found at livextrem\images\logo.png
)
REM --- Bundle CustomTkinter theme (style.json) ---
set "STYLE_JSON=%CD%\livextrem\style.json"
if exist "%STYLE_JSON%" (
  echo     Using theme: "%STYLE_JSON%"
  if defined ADD_DATA_ARG (
    set "ADD_DATA_ARG=!ADD_DATA_ARG! --add-data ""%STYLE_JSON%;_internal"""
    set "ADD_DATA_ARG=!ADD_DATA_ARG! --add-data ""%STYLE_JSON%;_internal\livextrem"""
  ) else (
    set "ADD_DATA_ARG=--add-data ""%STYLE_JSON%;_internal"" --add-data ""%STYLE_JSON%;_internal\livextrem"""
  )
) else (
  echo     WARNING: style.json not found at livextrem\style.json
)

REM --- Build ---
"%VENV_PY%" -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --noconsole ^
  --windowed ^
  --collect-data certifi ^
  --hidden-import certifi ^
  --collect-data mysql.connector ^
  --collect-submodules mysql.connector ^
  --hidden-import mysql.connector.locales.eng ^
  --hidden-import mysql.connector.locales.eng.client_error ^
  --name "%APP_NAME%" ^
  --distpath "%DIST_DIR%" ^
  --workpath "%BUILD_DIR%" ^
  --specpath "%SPEC_DIR%" ^
  !ADD_DATA_ARG! ^
  "%MAIN_SCRIPT%"

if errorlevel 1 (
  echo ERROR: PyInstaller build failed.
  pause
  exit /b 1
)

REM --- Ensure logo exists where the app might expect it (extra safety) ---
if exist "%LOGO%" (
  REM Some builds place login.py at _internal\login.py -> expects _internal\images\logo.png
  if not exist "%DIST_DIR%\%APP_NAME%\_internal\images\" mkdir "%DIST_DIR%\%APP_NAME%\_internal\images" >nul 2>&1
  copy /Y "%LOGO%" "%DIST_DIR%\%APP_NAME%\_internal\images\logo.png" >nul 2>&1
  REM Other builds keep folder -> expects _internal\livextrem\images\logo.png
  if not exist "%DIST_DIR%\%APP_NAME%\_internal\livextrem\images\" mkdir "%DIST_DIR%\%APP_NAME%\_internal\livextrem\images" >nul 2>&1
  copy /Y "%LOGO%" "%DIST_DIR%\%APP_NAME%\_internal\livextrem\images\logo.png" >nul 2>&1
)


REM --- Ensure style.json exists where modules might expect it (extra safety) ---
if exist "%STYLE_JSON%" (
  if not exist "%DIST_DIR%\%APP_NAME%\_internal\" mkdir "%DIST_DIR%\%APP_NAME%\_internal" >nul 2>&1
  copy /Y "%STYLE_JSON%" "%DIST_DIR%\%APP_NAME%\_internal\style.json" >nul 2>&1
  if not exist "%DIST_DIR%\%APP_NAME%\_internal\livextrem\" mkdir "%DIST_DIR%\%APP_NAME%\_internal\livextrem" >nul 2>&1
  copy /Y "%STYLE_JSON%" "%DIST_DIR%\%APP_NAME%\_internal\livextrem\style.json" >nul 2>&1
)

REM --- If config exists but app expects file, copy it too ---
echo.
echo [7/7] Post steps...
if not exist "%DIST_DIR%\%APP_NAME%\_internal\" (
  echo WARNING: dist internal folder not found. Something is off.
) else (
  if defined CFG (
    copy /Y "!CFG!" "%DIST_DIR%\%APP_NAME%\_internal\config_local.json" >nul
    echo     Copied config into dist: dist\%APP_NAME%\_internal\config_local.json
  ) else (
    echo     Config not present. Fill the template and create either:
    echo       - %CD%\config_local.json   OR
    echo       - %CD%\livextrem\config_local.json
    echo     Then rerun this .bat.
  )
)

echo.
echo DONE. Start your app from:
echo   %DIST_DIR%\%APP_NAME%\%APP_NAME%.exe
echo (Do NOT start anything from the build\ folder.)
echo.
explorer "%DIST_DIR%\%APP_NAME%" >nul 2>&1
pause