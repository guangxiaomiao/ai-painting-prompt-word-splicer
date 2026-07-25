# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('src', 'src')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PySide6.Qt3DAnimation', 'PySide6.Qt3DCore', 'PySide6.Qt3DExtras', 'PySide6.Qt3DInput', 'PySide6.Qt3DLogic', 'PySide6.Qt3DRender', 'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets', 'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.QtCharts', 'PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets', 'PySide6.QtOpenGL', 'PySide6.QtOpenGLWidgets', 'PySide6.QtPdf', 'PySide6.QtPdfWidgets', 'PySide6.QtPrintSupport', 'PySide6.QtSvg', 'PySide6.QtSvgWidgets', 'PySide6.QtTest', 'PySide6.QtUiTools', 'PySide6.QtBluetooth', 'PySide6.QtLocation', 'PySide6.QtPositioning', 'PySide6.QtSensors', 'PySide6.QtSerialPort', 'PySide6.QtNetworkAuth', 'PySide6.QtRemoteObjects', 'PySide6.QtScxml', 'PySide6.QtStateMachine', 'PySide6.QtTextToSpeech', 'PySide6.QtVirtualKeyboard', 'PySide6.QtWebChannel', 'PySide6.QtWebSockets', 'PySide6.QtWebView', 'PySide6.QtXml', 'PySide6.QtDesigner', 'PySide6.QtHelp', 'PySide6.QtHttpServer', 'PySide6.QtLottie', 'PySide6.QtNfc', 'PySide6.QtAxContainer', 'sqlalchemy.testing', 'pygame', 'matplotlib', 'numpy', 'scipy', 'torch', 'tensorflow', 'sklearn', 'pandas', 'PIL', 'cv2', 'pydantic', 'jupyter', 'notebook', 'ipython', 'sphinx', 'tkinter', 'wx', 'PyQt5', 'PyQt6'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AI_Prompt_Generator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AI_Prompt_Generator',
)
