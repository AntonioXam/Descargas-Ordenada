#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Análisis de uso de disco para DescargasOrdenadas.

Responde a la pregunta «¿qué está ocupando mi carpeta?» sin mover nada:

- Tamaño por categoría (lo que ya está organizado).
- Archivos más grandes.
- Carpetas más pesadas.
- Oportunidades de limpieza (temporales, duplicados evidentes, descargas
  antiguas que nadie ha usado).
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger('organizador.analisis_disco')


def formatear_bytes(cantidad: float) -> str:
    """Convierte bytes a una unidad legible (KB, MB, GB…)."""
    valor = float(cantidad or 0)
    for unidad in ("B", "KB", "MB", "GB", "TB"):
        if valor < 1024:
            return f"{valor:.1f} {unidad}"
        valor /= 1024
    return f"{valor:.1f} PB"


class AnalizadorDisco:
    """Calcula el uso de disco de una carpeta y sugiere limpieza."""

    # Archivos que no suelen aportar nada y se pueden revisar
    PATRONES_TEMPORALES = (
        ".tmp", ".temp", ".crdownload", ".part", ".bak", ".old",
        ".dmp", ".cache", ".download",
    )

    def __init__(self, carpeta: Path | str):
        self.carpeta = Path(carpeta)

    # ------------------------------------------------------------- análisis

    def analizar(self, limite_archivos: int = 10) -> Dict[str, Any]:
        """Recorre la carpeta y devuelve un informe de uso.

        Args:
            limite_archivos: cuántos archivos y carpetas grandes se listan.

        Returns:
            Diccionario con totales, reparto por categoría, archivos grandes,
            carpetas pesadas y sugerencias de limpieza.
        """
        if not self.carpeta.exists() or not self.carpeta.is_dir():
            return {
                "error": f"La carpeta no existe: {self.carpeta}",
                "total": 0, "archivos": 0, "categorias": {},
                "mas_grandes": [], "carpetas": [], "sugerencias": [],
            }

        total = 0
        archivos = 0
        por_categoria: Dict[str, Dict[str, int]] = {}
        mas_grandes: List[Dict[str, Any]] = []
        tamanos_carpetas: Dict[str, int] = {}
        sugerencias: List[Dict[str, Any]] = []
        ahora = time.time()

        try:
            elementos = list(self.carpeta.rglob("*"))
        except PermissionError as e:
            return {
                "error": f"Sin permisos para leer la carpeta: {e}",
                "total": 0, "archivos": 0, "categorias": {},
                "mas_grandes": [], "carpetas": [], "sugerencias": [],
            }

        for elemento in elementos:
            if elemento.is_dir():
                continue
            if any(parte.startswith(".") for parte in elemento.relative_to(self.carpeta).parts[:-1]):
                continue
            if elemento.name.startswith("."):
                continue

            try:
                tamano = elemento.stat().st_size
                modificado = elemento.stat().st_mtime
            except OSError:
                continue

            total += tamano
            archivos += 1

            # Reparto por categoría (carpeta de primer nivel)
            try:
                relativo = elemento.relative_to(self.carpeta)
                categoria = relativo.parts[0] if len(relativo.parts) > 1 else "(sin organizar)"
            except ValueError:
                categoria = "(sin organizar)"

            datos = por_categoria.setdefault(categoria, {"archivos": 0, "tamaño": 0})
            datos["archivos"] += 1
            datos["tamaño"] += tamano
            tamanos_carpetas[categoria] = tamanos_carpetas.get(categoria, 0) + tamano

            mas_grandes.append({
                "nombre": elemento.name,
                "ruta": str(elemento),
                "tamaño": tamano,
                "categoria": categoria,
            })

            # Sugerencias de limpieza
            if elemento.suffix.lower() in self.PATRONES_TEMPORALES:
                sugerencias.append({
                    "tipo": "temporal",
                    "archivo": elemento.name,
                    "ruta": str(elemento),
                    "tamaño": tamano,
                    "motivo": "Archivo temporal o de descarga incompleta",
                })
            elif ahora - modificado > 365 * 24 * 3600:
                sugerencias.append({
                    "tipo": "antiguo",
                    "archivo": elemento.name,
                    "ruta": str(elemento),
                    "tamaño": tamano,
                    "motivo": "Sin modificarse desde hace más de un año",
                })

        mas_grandes.sort(key=lambda a: -a["tamaño"])
        carpetas = [
            {"nombre": nombre, "tamaño": tamano}
            for nombre, tamano in sorted(tamanos_carpetas.items(), key=lambda x: -x[1])
        ]
        # Las sugerencias más útiles primero: por tamaño
        sugerencias.sort(key=lambda s: -s["tamaño"])

        return {
            "total": total,
            "archivos": archivos,
            "categorias": por_categoria,
            "mas_grandes": mas_grandes[:limite_archivos],
            "carpetas": carpetas[:limite_archivos],
            "sugerencias": sugerencias[:limite_archivos],
            "espacio_recuperable": sum(s["tamaño"] for s in sugerencias),
        }

    # ---------------------------------------------------------------- texto

    def informe(self, limite_archivos: int = 10) -> str:
        """Genera el informe en texto para mostrarlo en la interfaz."""
        datos = self.analizar(limite_archivos)
        if datos.get("error"):
            return datos["error"]

        lineas = [
            f"Carpeta: {self.carpeta}",
            f"Total: {formatear_bytes(datos['total'])} en {datos['archivos']} archivos",
            "",
            "Reparto por categoría:",
        ]

        for nombre, info in sorted(
            datos["categorias"].items(), key=lambda x: -x[1]["tamaño"]
        )[:10]:
            lineas.append(
                f"  {nombre}: {formatear_bytes(info['tamaño'])} ({info['archivos']} archivos)"
            )
        if not datos["categorias"]:
            lineas.append("  (no hay archivos)")

        lineas.append("")
        lineas.append("Archivos más grandes:")
        for archivo in datos["mas_grandes"][:8]:
            lineas.append(f"  {formatear_bytes(archivo['tamaño'])}  {archivo['nombre']}")
        if not datos["mas_grandes"]:
            lineas.append("  (ninguno)")

        lineas.append("")
        lineas.append("Sugerencias de limpieza:")
        if datos["sugerencias"]:
            for sugerencia in datos["sugerencias"][:8]:
                lineas.append(
                    f"  {formatear_bytes(sugerencia['tamaño'])}  {sugerencia['archivo']}"
                    f"  ({sugerencia['motivo']})"
                )
            lineas.append("")
            lineas.append(
                f"Espacio potencialmente recuperable: "
                f"{formatear_bytes(datos.get('espacio_recuperable', 0))}"
            )
        else:
            lineas.append("  Nada evidente que eliminar. La carpeta está sana.")

        return "\n".join(lineas)
