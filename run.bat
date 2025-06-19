@echo off
title BulletUploader GUI
cd /d "C:\Users\BALAS\Desktop\PROGRAMACION\2_SCRIPTS_FUNCIONALES\github-scripts\AUTO_UPLOADER"

echo Starting BulletUploader GUI...
echo.

if not exist main_gui.py (
    echo ERROR: main_gui.py not found!
    pause
    exit /b 1
)

python main_gui.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Application failed to start. Error code: %ERRORLEVEL%
    echo Make sure Python is installed and all dependencies are available.
)

pause