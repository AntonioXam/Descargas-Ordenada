#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rutas de recursos y configuración compatibles con PyInstaller."""

import os
import sys
from pathlib import Path


def obtener_base_recursos() -> Path:
    """Devuelve la carpeta donde están VERSION.txt y resources."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def obtener_recurso(nombre: str) -> Path:
    """Devuelve la ruta absoluta a un recurso incluido en el paquete."""
    return obtener_base_recursos() / "resources" / nombre


def obtener_archivo_version() -> Path:
    """Devuelve la ruta del archivo VERSION.txt."""
    return obtener_base_recursos() / "VERSION.txt"


def obtener_directorio_configuracion() -> Path:
    """Devuelve la carpeta de configuración según el sistema y el modo de ejecución."""
    if not getattr(sys, "frozen", False):
        return obtener_base_recursos() / ".config"

    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / "DescargasOrdenadas"
    elif sys.platform == "win32":
        appdata = os.getenv("APPDATA")
        base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
        base = base / "DescargasOrdenadas"
    else:
        xdg_config = os.getenv("XDG_CONFIG_HOME")
        base = Path(xdg_config) if xdg_config else Path.home() / ".config"
        base = base / "DescargasOrdenadas"

    base.mkdir(parents=True, exist_ok=True)
    return base
