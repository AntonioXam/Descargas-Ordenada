#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Programación de organización automática a una hora concreta.

Permite que la aplicación organice la carpeta a una hora determinada del día
(por ejemplo, a las 22:00) en vez de solo cada cierto intervalo. Es útil para
quien prefiere que el ordenado ocurra fuera del horario de trabajo.

La preferencia se guarda en la configuración y se aplica al abrir la app.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger('organizador.programacion')

HORA_POR_DEFECTO = "22:00"


def parsear_hora(texto: str) -> Optional[tuple[int, int]]:
    """Convierte 'HH:MM' en (hora, minuto). Devuelve None si no es válido."""
    try:
        partes = str(texto).strip().split(":")
        if len(partes) != 2:
            return None
        hora, minuto = int(partes[0]), int(partes[1])
        if 0 <= hora <= 23 and 0 <= minuto <= 59:
            return hora, minuto
    except (TypeError, ValueError):
        pass
    return None


def segundos_hasta_la_hora(texto_hora: str, ahora: Optional[datetime] = None) -> Optional[int]:
    """Calcula cuántos segundos faltan para la próxima vez que sea esa hora.

    Si la hora ya ha pasado hoy, apunta a mañana. Devuelve None si el formato
    no es válido.
    """
    partes = parsear_hora(texto_hora)
    if partes is None:
        return None
    hora, minuto = partes
    ahora = ahora or datetime.now()

    objetivo = ahora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
    if objetivo <= ahora:
        objetivo += timedelta(days=1)
    return int((objetivo - ahora).total_seconds())


def descripcion(texto_hora: str) -> str:
    """Texto legible de la programación para la interfaz."""
    partes = parsear_hora(texto_hora)
    if partes is None:
        return "Sin hora programada"
    hora, minuto = partes
    restante = segundos_hasta_la_hora(texto_hora)
    if restante is None:
        return f"Cada día a las {hora:02d}:{minuto:02d}"
    horas = restante // 3600
    minutos = (restante % 3600) // 60
    if horas:
        cuando = f"en {horas} h {minutos} min"
    else:
        cuando = f"en {minutos} min"
    return f"Cada día a las {hora:02d}:{minuto:02d} (próxima {cuando})"
