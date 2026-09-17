#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gestión centralizada de la versión de DescargasOrdenadas.

VERSION.txt es la única fuente de verdad de la versión. Todos los módulos
(GUI, actualizaciones, arranque) deben leer la versión desde aquí para evitar
desincronizaciones entre archivos.
"""

from pathlib import Path

VERSION_FALLBACK = "3.4.0"


def obtener_version() -> str:
    """Obtiene la versión actual desde VERSION.txt con fallback seguro."""
    try:
        version_path = Path(__file__).parent.parent / "VERSION.txt"
        version = version_path.read_text(encoding="utf-8").strip()
        return version or VERSION_FALLBACK
    except Exception:
        return VERSION_FALLBACK
