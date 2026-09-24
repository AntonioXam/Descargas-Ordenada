#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Historial de organizaciones para DescargasOrdenadas.

Guarda cada operación realizada (qué archivos se movieron y a dónde) para
poder consultarla después y deshacerla. Se conserva un máximo de operaciones
y se guarda en la carpeta de configuración de la aplicación.

El historial permite:

- Ver las últimas organizaciones con su fecha, modo y número de archivos.
- Deshacer una operación concreta devolviendo cada archivo a su origen, sin
  tocar el resto de organizaciones.
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .app_paths import (
    crear_directorio,
    directorio_temporal_app,
    obtener_directorio_configuracion,
)

logger = logging.getLogger('organizador.historial')

MAXIMO_OPERACIONES = 30


class HistorialOperaciones:
    """Historial persistente de organizaciones, con deshacer."""

    def __init__(self, nombre_app: str = "DescargasOrdenadas"):
        self.nombre_app = nombre_app
        self._ruta = self._obtener_ruta()
        self._operaciones: List[Dict] = []
        self._cargar()

    def _obtener_ruta(self) -> Path:
        try:
            carpeta = obtener_directorio_configuracion()
            crear_directorio(carpeta)
            return carpeta / "historial.json"
        except Exception:
            # Último recurso: el directorio temporal del sistema, que siempre
            # es escribible. ``Path.cwd()`` puede no serlo.
            return directorio_temporal_app() / "historial.json"

    # ------------------------------------------------------------- lectura

    def _cargar(self):
        """Carga el historial desde el disco."""
        try:
            if self._ruta.exists():
                datos = json.loads(self._ruta.read_text(encoding="utf-8"))
                self._operaciones = datos.get("operaciones", []) or []
        except Exception as e:
            logger.debug(f"No se pudo cargar el historial: {e}")
            self._operaciones = []

    def _guardar(self):
        """Guarda el historial en el disco."""
        try:
            self._ruta.write_text(
                json.dumps({"operaciones": self._operaciones}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            logger.debug(f"No se pudo guardar el historial: {e}")

    # ------------------------------------------------------------ registro

    def registrar(self, resultados: Dict[str, Dict[str, List[str]]],
                  carpeta: Path, modo: str = "basico") -> Optional[Dict]:
        """Añade una operación al historial.

        Args:
            resultados: mismo diccionario que devuelve el organizador.
            carpeta: carpeta organizada.
            modo: 'basico' o 'detallado'.

        Returns:
            La operación registrada (con su desplazamiento y movimientos).
        """
        # Reconstruir los movimientos a partir del resultado del organizador
        movimientos = []
        for categoria, subcategorias in (resultados or {}).items():
            for subcategoria, archivos in (subcategorias or {}).items():
                for nombre in archivos:
                    origen = Path(carpeta) / nombre
                    if subcategoria and subcategoria != "General":
                        destino = Path(carpeta) / categoria / subcategoria / Path(nombre).name
                    else:
                        destino = Path(carpeta) / categoria / Path(nombre).name
                    movimientos.append({
                        "origen": str(origen),
                        "destino": str(destino),
                        "categoria": categoria,
                        "subcategoria": subcategoria,
                    })

        if not movimientos:
            return None

        operacion = {
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "carpeta": str(carpeta),
            "modo": modo,
            "total": len(movimientos),
            "movimientos": movimientos,
        }
        self._operaciones.insert(0, operacion)
        # Conservar solo las últimas operaciones
        self._operaciones = self._operaciones[:MAXIMO_OPERACIONES]
        self._guardar()
        logger.info(f"Operación registrada: {len(movimientos)} movimientos")
        return operacion

    # -------------------------------------------------------------- consulta

    def operaciones(self) -> List[Dict]:
        """Devuelve las operaciones guardadas, de la más reciente a la más vieja."""
        return list(self._operaciones)

    def ultima(self) -> Optional[Dict]:
        """Devuelve la última operación o None."""
        return self._operaciones[0] if self._operaciones else None

    def descripcion(self, operacion: Dict) -> str:
        """Texto legible de una operación para mostrar en una lista."""
        try:
            fecha = datetime.fromisoformat(operacion.get("fecha", ""))
            cuando = fecha.strftime("%d/%m %H:%M")
        except Exception:
            cuando = "?"
        modo = "Detallado" if operacion.get("modo") == "detallado" else "Básico"
        total = operacion.get("total", 0)
        carpeta = Path(operacion.get("carpeta", "")).name or "?"
        return f"{cuando} · {total} archivos · {modo} · {carpeta}"

    # ------------------------------------------------------------- deshacer

    def deshacer(self, operacion: Dict) -> Dict:
        """Devuelve los archivos de una operación a su sitio original.

        No toca los archivos que se hayan movido después ni los que ya no
        estén donde se dejaron: solo actúa sobre los que siguen en el destino
        que registró el historial.

        Returns:
            Diccionario con ``devueltos``, ``omitidos`` y ``errores``.
        """
        devueltos = 0
        omitidos = 0
        errores: List[str] = []

        for movimiento in reversed(operacion.get("movimientos", [])):
            destino = Path(movimiento.get("destino", ""))
            origen = Path(movimiento.get("origen", ""))

            if not destino.exists():
                omitidos += 1
                continue

            try:
                origen.parent.mkdir(parents=True, exist_ok=True)
                destino_final = origen
                if origen.exists():
                    # No pisar nada: se añade un sufijo
                    base = origen.stem
                    extension = origen.suffix
                    indice = 1
                    while destino_final.exists():
                        destino_final = origen.parent / f"{base}_restaurado_{indice}{extension}"
                        indice += 1
                shutil.move(str(destino), str(destino_final))
                devueltos += 1
            except Exception as e:
                errores.append(f"{destino.name}: {e}")

        # Quitar del historial la operación deshecha
        try:
            self._operaciones = [
                op for op in self._operaciones if op is not operacion
            ]
            self._guardar()
        except Exception:
            pass

        logger.info(
            f"Deshacer: {devueltos} devueltos, {omitidos} omitidos, {len(errores)} errores"
        )
        return {"devueltos": devueltos, "omitidos": omitidos, "errores": errores}

    def limpiar(self):
        """Vacía el historial."""
        self._operaciones = []
        self._guardar()


# Instancia global
_historial_global: Optional[HistorialOperaciones] = None


def obtener_historial() -> HistorialOperaciones:
    """Obtiene la instancia global del historial."""
    global _historial_global
    if _historial_global is None:
        _historial_global = HistorialOperaciones()
    return _historial_global
