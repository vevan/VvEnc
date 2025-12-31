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
set ADD_DATA_PARAM=--add-data "core;core" --add-data "gui;gui" --add-data "translations;translations" --add-data "version;."
if exist icon.ico (
    set ADD_DATA_PARAM=%ADD_DATA_PARAM% --add-data "icon.ico;."
)
python -m PyInstaller --name="VvEnc" --onefile --windowed %ICON_PARAM% %ADD_DATA_PARAM% ^
  --hidden-import=PyQt5.QtCore --hidden-import=PyQt5.QtGui --hidden-import=PyQt5.QtWidgets --hidden-import=PyQt5.QtMultimedia --hidden-import=PyQt5.QtWinExtras ^
  --collect-submodules=PyQt5.QtCore --collect-submodules=PyQt5.QtGui --collect-submodules=PyQt5.QtWidgets --collect-submodules=PyQt5.QtMultimedia ^
  --exclude-module=PyQt5.QtWebEngine --exclude-module=PyQt5.QtWebEngineWidgets --exclude-module=PyQt5.QtWebEngineCore ^
  --exclude-module=PyQt5.QtBluetooth --exclude-module=PyQt5.QtNfc --exclude-module=PyQt5.QtPositioning --exclude-module=PyQt5.QtLocation --exclude-module=PyQt5.QtSensors --exclude-module=PyQt5.QtSerialPort ^
  --exclude-module=PyQt5.QtQuick --exclude-module=PyQt5.QtQml --exclude-module=PyQt5.Qt3D --exclude-module=PyQt5.QtDesigner --exclude-module=PyQt5.QtHelp --exclude-module=PyQt5.QtSql --exclude-module=PyQt5.QtTest --exclude-module=PyQt5.QtXml --exclude-module=PyQt5.QtXmlPatterns ^
  --exclude-module=matplotlib --exclude-module=numpy --exclude-module=pandas --exclude-module=scipy --exclude-module=PIL --exclude-module=tkinter ^
  --clean main.py

if errorlevel 1 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)

echo.
echo [5/5] Copying additional files...
if exist ringtone.mp3 (
    copy /Y ringtone.mp3 dist\ >nul 2>&1
    echo Copied ringtone.mp3
) else (
    echo [WARNING] ringtone.mp3 not found, skipping
)
if exist config.json (
    copy /Y config.json dist\ >nul 2>&1
    echo Copied config.json
) else (
    echo [WARNING] config.json not found, skipping
)
echo.
echo Build complete!
echo.
echo Executable: dist\VvEnc.exe
echo.
pause

