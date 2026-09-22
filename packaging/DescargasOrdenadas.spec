# -*- mode: python ; coding: utf-8 -*-
"""Spec de PyInstaller para DescargasOrdenadas en Windows, macOS y Linux."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(SPECPATH).resolve().parent
VERSION = (PROJECT_ROOT / "VERSION.txt").read_text(encoding="utf-8").strip()

icono = None
if sys.platform == "win32":
    icono = str(PROJECT_ROOT / "resources" / "icon.ico")
elif sys.platform == "darwin":
    icono = str(PROJECT_ROOT / "resources" / "icon.icns")
else:
    icono = str(PROJECT_ROOT / "resources" / "icon.png")

a = Analysis(
    [str(PROJECT_ROOT / "organizer" / "INICIAR.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=[
        (str(PROJECT_ROOT / "resources" / "*"), "resources"),
        (str(PROJECT_ROOT / "VERSION.txt"), "."),
    ],
    hiddenimports=[
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "PySide6.QtNetwork",
        "organizer.single_instance",
        "PIL",
        "PIL.Image",
        "watchdog",
        "plyer",
        "requests",
        "organizer.gui_avanzada",
        "organizer.gui",
        "organizer.native_notifications",
        "organizer.notifications",
        "organizer.autostart",
        "organizer.context_menu",
        "organizer.portable_config",
        "organizer.version",
        "organizer.app_paths",
        "organizer.actualizaciones",
        "organizer.actualizaciones_mejorado",
        "organizer.file_organizer",
        "organizer.estilos",
        "organizer.duplicate_detector",
        "organizer.statistics",
        "organizer.temas",
        "organizer.real_time_monitor",
        "organizer.smart_detection",
        "organizer.custom_rules",
        "organizer.ai_categorizer",
        "organizer.date_organizer",
        "organizer.resources",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DescargasOrdenadas",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=icono,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="DescargasOrdenadas",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="DescargasOrdenadas.app",
        icon=str(PROJECT_ROOT / "resources" / "icon.icns"),
        bundle_identifier="com.antonioxam.DescargasOrdenadas",
        version=VERSION,
        info_plist={
            "CFBundleName": "DescargasOrdenadas",
            "CFBundleDisplayName": "Descargas Ordenadas",
            "CFBundleShortVersionString": VERSION,
            "CFBundleVersion": VERSION,
            "LSMinimumSystemVersion": "10.15",
            "NSHighResolutionCapable": True,
        },
    )
