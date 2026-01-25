@echo off
setlocal ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

set "PACK_DIR=%~dp0"
set "REQ_FILE=%PACK_DIR%requirements.txt"
set "WHEELS_DIR=%PACK_DIR%wheels"
set "VENDOR_DIR=%PACK_DIR%vendor"
if "%VENV_DIR%"=="" set "VENV_DIR=%PACK_DIR%.venv"
if "%PY_DEST%"=="" set "PY_DEST=%PACK_DIR%.python"
set "PY_SRC=%PACK_DIR%python"

set "ARCHIVE="
if exist "%PY_SRC%" (
  for /f "delims=" %%A in (
    'dir /b /o:n "%PY_SRC%\*.tar.gz" 2^>nul'
  ) do (
    set "ARCHIVE=%PY_SRC%\%%A"
    goto :archive_found
  )
)
:archive_found

set "HAS_ARCHIVE=0"
if not "%ARCHIVE%"=="" set "HAS_ARCHIVE=1"

set "BUNDLED_PY="

if "%HAS_ARCHIVE%"=="1" (
  if not exist "%PY_DEST%" mkdir "%PY_DEST%"

  for /f "delims=" %%P in (
    'dir /s /b /o:n "%PY_DEST%\python.exe" 2^>nul'
  ) do (
    set "BUNDLED_PY=%%P"
    goto :found
  )

  tar -C "%PY_DEST%" -xzf "%ARCHIVE%"
  echo ✔ Extracted python

  for /f "delims=" %%P in (
    'dir /s /b /o:n "%PY_DEST%\python.exe" 2^>nul'
  ) do (
    set "BUNDLED_PY=%%P"
    goto :found
  )
)

:found
if not "%BUNDLED_PY%"=="" set "BASE_PY=%BUNDLED_PY%"

if "%BASE_PY%"=="" (
  if "%HAS_ARCHIVE%"=="0" (
    echo ERROR: BASE_PY must be set when no python archive is provided
  ) else (
    echo ERROR: Bundled python not found after extracting archive
  )
  exit /b 1
)

if not exist "%BASE_PY%" (
  echo ERROR: BASE_PY not found: %BASE_PY%
  exit /b 1
)

echo Using base interpreter: %BASE_PY%
"%BASE_PY%" -m venv "%VENV_DIR%"

set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
if not exist "%VENV_PY%" (
  echo ERROR: Venv python missing
  exit /b 1
)

set "PIP_NO_INDEX=1"
set "PIP_DISABLE_PIP_VERSION_CHECK=1"

"%VENV_PY%" -m ensurepip --upgrade --default-pip >nul 2>nul

"%VENV_PY%" -m pip install ^
  --find-links "%WHEELS_DIR%" ^
  --find-links "%VENDOR_DIR%" ^
  -r "%REQ_FILE%"

echo Done.
echo Activate with:
echo   %VENV_DIR%\Scripts\activate.bat
endlocal
