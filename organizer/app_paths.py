#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rutas de recursos y configuración compatibles con PyInstaller."""

import logging
import os
import sys
import tempfile
from pathlib import Path

logger = logging.getLogger('organizador.app_paths')


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


def crear_directorio(ruta: Path) -> bool:
    """Intenta crear la carpeta indicada sin lanzar excepciones.

    Crear una carpeta puede fallar por permisos, por una ruta de solo lectura o
    por un disco desconectado. Ninguno de esos casos debe terminar en una traza:
    se devuelve ``False`` y quien llama decide qué hacer, que normalmente es
    caer a una ubicación alternativa.

    Returns:
        True si la carpeta existe al terminar (se acabe de crear o no).
    """
    try:
        Path(ruta).mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, ValueError) as e:
        logger.debug(f"No se pudo crear {ruta}: {e}")
        return False


def directorio_temporal_app() -> Path:
    """Carpeta de último recurso dentro del directorio temporal del sistema."""
    ruta = Path(tempfile.gettempdir()) / "DescargasOrdenadas"
    crear_directorio(ruta)
    return ruta


def crear_directorio_con_respaldo(ruta: Path) -> Path:
    """Crea la carpeta pedida y, si no puede, devuelve una alternativa usable.

    Se usa para los directorios de configuración y datos: es preferible que la
    aplicación siga funcionando con la configuración en otro sitio a que se
    caiga al arrancar.
    """
    if crear_directorio(ruta):
        return ruta
    logger.warning(
        f"Sin permisos para crear {ruta}; se usará el directorio temporal"
    )
    return directorio_temporal_app()


def obtener_directorio_configuracion() -> Path:
    """Devuelve la carpeta de configuración según el sistema y el modo de ejecución.

    Si no se puede crear (permisos, volumen de solo lectura), se cae al
    directorio temporal en lugar de fallar.
    """
    if not getattr(sys, "frozen", False):
        return crear_directorio_con_respaldo(obtener_base_recursos() / ".config")

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

    return crear_directorio_con_respaldo(base)
