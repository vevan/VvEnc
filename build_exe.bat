@echo off
chcp 65001 >nul
echo ========================================
echo Batch Video Encoder - Build Script
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

echo [1/5] Checking PyInstaller...
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller --upgrade
    if errorlevel 1 (
        echo [ERROR] PyInstaller installation failed
        pause
        exit /b 1
    )
) else (
    echo PyInstaller is installed
)

echo.
echo [2/5] Processing icon file...
set ICON_PARAM=
if exist icon.ico (
    echo Found icon.ico
    set ICON_PARAM=--icon=icon.ico
) else (
    if exist icon.png (
        echo Found icon.png, converting...
        python convert_icon.py >nul 2>&1
        if exist icon.ico (
            echo Icon converted successfully
            set ICON_PARAM=--icon=icon.ico
        ) else (
            echo [WARNING] Conversion failed, using default icon
        )
    ) else (
        echo No icon file found, using default icon
    )
)

echo.
echo [3/5] Cleaning old files...
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul
if exist *.spec del /q *.spec 2>nul
echo Cleanup complete

echo.
echo [4/5] Building executable...
python -m PyInstaller --name="VideoEncoder" --onefile --windowed %ICON_PARAM% --add-data "core;core" --add-data "gui;gui" --hidden-import=PyQt5.QtCore --hidden-import=PyQt5.QtGui --hidden-import=PyQt5.QtWidgets --collect-all PyQt5 --clean main.py

if errorlevel 1 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)

echo.
echo [5/5] Build complete!
echo.
echo Executable: dist\VideoEncoder.exe
echo.
pause

