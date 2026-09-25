#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gestión centralizada de la versión de DescargasOrdenadas.

VERSION.txt es la única fuente de verdad de la versión. Todos los módulos
(GUI, actualizaciones, arranque) deben leer la versión desde aquí para evitar
desincronizaciones entre archivos.
"""

from .app_paths import obtener_archivo_version

VERSION_FALLBACK = "7.0.1"


def obtener_version() -> str:
    """Obtiene la versión actual desde VERSION.txt con fallback seguro."""
    try:
        version = obtener_archivo_version().read_text(encoding="utf-8").strip()
        return version or VERSION_FALLBACK
    except Exception:
        return VERSION_FALLBACK
