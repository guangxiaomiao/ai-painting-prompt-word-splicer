import sys
import os

block_cipher = None

EXCLUDES = [
    'PySide6.Qt3D*', 'PySide6.QtWebEngine*', 'PySide6.QtBluetooth',
    'PySide6.QtCharts', 'PySide6.QtDataVisualization', 'PySide6.QtDesigner',
    'PySide6.QtGraphs', 'PySide6.QtHelp', 'PySide6.QtHttpServer',
    'PySide6.QtLocation', 'PySide6.QtLottie', 'PySide6.QtMultimedia*',
    'PySide6.QtNetworkAuth', 'PySide6.QtNfc', 'PySide6.QtOpenGL*',
    'PySide6.QtPdf*', 'PySide6.QtPositioning', 'PySide6.QtPrintSupport',
    'PySide6.QtQml', 'PySide6.QtQuick*', 'PySide6.QtRemoteObjects',
    'PySide6.QtScxml', 'PySide6.QtSensors', 'PySide6.QtSerial*',
    'PySide6.QtSpatialAudio', 'PySide6.QtSql', 'PySide6.QtStateMachine',
    'PySide6.QtSvg*', 'PySide6.QtTest', 'PySide6.QtTextToSpeech',
    'PySide6.QtUiTools', 'PySide6.QtVirtualKeyboard', 'PySide6.QtWebChannel',
    'PySide6.QtWebSockets', 'PySide6.QtWebView', 'PySide6.QtXml',
    'sqlalchemy.testing', 'sqlalchemy.test',
    'matplotlib', 'numpy', 'scipy', 'torch', 'tensorflow',
    'sklearn', 'pandas', 'PIL', 'cv2', 'pydantic',
    'jupyter', 'notebook', 'ipython', 'sphinx',
    'tkinter', 'wx', 'PyQt5', 'PyQt6',
    'test', 'tests',
]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('src', 'src'),
    ],
    hiddenimports=[
        'PySide6.QtWidgets',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtNetwork',
        'shiboken6',
        'sqlalchemy',
        'sqlalchemy.engine',
        'sqlalchemy.sql',
        'sqlalchemy.orm',
        'sqlalchemy.schema',
        'sqlalchemy.types',
        'sqlalchemy.ext.declarative',
        'sqlalchemy.sql.default_comparator',
        'sqlalchemy.dialects.sqlite',
        'requests',
        'certifi',
        'charset_normalizer',
        'urllib3',
        'urllib3.poolmanager',
        'idna',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=EXCLUDES,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x86_64',
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AI_Prompt_Generator',
)
