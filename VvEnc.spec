# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'PyQt5.QtMultimedia', 'PyQt5.QtWinExtras']
hiddenimports += collect_submodules('PyQt5.QtCore')
hiddenimports += collect_submodules('PyQt5.QtGui')
hiddenimports += collect_submodules('PyQt5.QtWidgets')
hiddenimports += collect_submodules('PyQt5.QtMultimedia')


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('core', 'core'), ('gui', 'gui'), ('translations', 'translations'), ('icon.ico', '.')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5.QtWebEngine', 'PyQt5.QtWebEngineWidgets', 'PyQt5.QtWebEngineCore', 'PyQt5.QtBluetooth', 'PyQt5.QtNfc', 'PyQt5.QtPositioning', 'PyQt5.QtLocation', 'PyQt5.QtSensors', 'PyQt5.QtSerialPort', 'PyQt5.QtQuick', 'PyQt5.QtQml', 'PyQt5.Qt3D', 'PyQt5.QtDesigner', 'PyQt5.QtHelp', 'PyQt5.QtSql', 'PyQt5.QtTest', 'PyQt5.QtXml', 'PyQt5.QtXmlPatterns', 'matplotlib', 'numpy', 'pandas', 'scipy', 'PIL', 'tkinter'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VvEnc',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
