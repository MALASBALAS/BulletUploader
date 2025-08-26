@echo off
title BulletUploader GUI - Admin Mode

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
    goto :run_app
) else (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:run_app
cd /d "C:\Users\BALAS\Desktop\PROGRAMACION\2_SCRIPTS_FUNCIONALES\github-scripts\AUTO_UPLOADER"

echo Starting BulletUploader GUI with admin privileges...
echo.

if not exist main_gui.py (
    echo ERROR: main_gui.py not found!
    pause
    exit /b 1
)

REM Prefer local virtual environment if available
set "VENV_PY=%CD%\.venv\Scripts\python.exe"
if exist "%VENV_PY%" (
    echo Using virtual environment Python...
    "%VENV_PY%" main_gui.py
) else (
    python main_gui.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Application failed to start. Error code: %ERRORLEVEL%
    echo Make sure Python is installed and all dependencies are available.
)

pause