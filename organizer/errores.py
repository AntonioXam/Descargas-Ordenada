#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manejo centralizado de errores para DescargasOrdenadas.

Objetivo: que **ningún fallo termine en una traza ilegible**. Todo error acaba
de una de estas dos formas:

- En una ventana legible, si hay interfaz gráfica disponible, con el detalle
  técnico plegado para quien lo quiera ver.
- En un mensaje de consola claro, si se está ejecutando desde la terminal o
  desde un menú contextual.

En ambos casos se guarda el rastro completo en ``errores.log`` dentro de la
carpeta de configuración, para poder diagnosticar después sin depender de que
el usuario copie nada.

Este módulo lo usan tanto el punto de entrada como la interfaz, así que no
depende de PySide6 a nivel de importación: se comprueba en tiempo de ejecución.
"""

from __future__ import annotations

import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path

logger = logging.getLogger('organizador.errores')

# Evita que un fallo dentro del propio manejador dispare una recursión infinita.
_manejando_error = False


def ruta_registro_errores() -> Path:
    """Devuelve la ruta del registro de errores, sin fallar si no se puede."""
    try:
        from .app_paths import crear_directorio, obtener_directorio_configuracion

        carpeta = obtener_directorio_configuracion()
        crear_directorio(carpeta)
        return carpeta / "errores.log"
    except Exception:
        import tempfile

        return Path(tempfile.gettempdir()) / "descargasordenadas_errores.log"


def guardar_rastro(rastro: str) -> None:
    """Añade un rastro al registro de errores. Nunca lanza excepción."""
    try:
        with open(ruta_registro_errores(), "a", encoding="utf-8") as f:
            f.write(f"\n{'=' * 70}\n{datetime.now().isoformat()}\n{rastro}\n")
    except Exception:
        # Si ni siquiera se puede escribir el registro, no hay nada más que
        # hacer: no queremos que el propio registro provoque otro fallo.
        pass


def hay_interfaz_grafica():
    """Devuelve la QApplication activa, o None si no hay interfaz."""
    try:
        from PySide6.QtWidgets import QApplication

        return QApplication.instance()
    except Exception:
        return None


def _podemos_abrir_ventanas() -> bool:
    """Indica si es seguro crear widgets ahora mismo.

    Crear o mostrar widgets fuera del hilo principal de Qt no está permitido y
    termina en un bloqueo o en un cierre abrupto. Un error puede llegar desde un
    hilo de trabajo, así que hay que comprobarlo antes de intentar mostrar nada.
    """
    if hay_interfaz_grafica() is None:
        return False
    try:
        import threading

        return threading.current_thread() is threading.main_thread()
    except Exception:
        return False


def _ventana_activa():
    """Devuelve la ventana principal si existe, para usarla como padre."""
    try:
        app = hay_interfaz_grafica()
        if app is None:
            return None
        ventanas = [w for w in app.topLevelWidgets() if w.isVisible()]
        return ventanas[0] if ventanas else None
    except Exception:
        return None


def mostrar_error(
    titulo: str,
    mensaje: str,
    detalle: str | None = None,
    sugerencia: str | None = None,
) -> None:
    """Muestra un error de forma legible, por ventana o por consola.

    Args:
        titulo: Encabezado corto, por ejemplo "No se pudo organizar".
        mensaje: Qué ha pasado, en una frase, sin tecnicismos.
        detalle: Información técnica (traza). Se muestra plegada.
        sugerencia: Qué puede hacer el usuario para resolverlo.
    """
    texto = mensaje
    if sugerencia:
        texto = f"{mensaje}\n\n{sugerencia}"

    if _podemos_abrir_ventanas():
        try:
            from PySide6.QtWidgets import QMessageBox

            caja = QMessageBox(_ventana_activa())
            caja.setIcon(QMessageBox.Warning)
            caja.setWindowTitle("DescargasOrdenadas")
            caja.setText(titulo)
            caja.setInformativeText(texto)
            if detalle:
                caja.setDetailedText(detalle)
            caja.setStandardButtons(QMessageBox.Ok)
            caja.exec()
            return
        except Exception:
            # Si el diálogo falla, caemos a la consola más abajo.
            pass

    print(f"\n⚠️  {titulo}\n{texto}", file=sys.stderr)
    if detalle:
        print(f"\nDetalle técnico:\n{detalle}", file=sys.stderr)


def _manejador_excepciones(tipo, valor, rastro) -> None:
    """Reemplazo de ``sys.excepthook``: registra y muestra el error."""
    global _manejando_error
    if _manejando_error:
        # Un error dentro del manejador: dejamos que Python haga lo de siempre.
        sys.__excepthook__(tipo, valor, rastro)
        return

    _manejando_error = True
    try:
        detalle = "".join(traceback.format_exception(tipo, valor, rastro))
        guardar_rastro(detalle)
        logger.error(f"Error no controlado: {valor}")

        mostrar_error(
            "Ha ocurrido un error inesperado",
            f"{tipo.__name__}: {valor}",
            detalle=detalle,
            sugerencia=(
                "La aplicación seguirá funcionando. Si el problema se repite, "
                f"el detalle completo está en:\n{ruta_registro_errores()}"
            ),
        )
    except Exception:
        sys.__excepthook__(tipo, valor, rastro)
    finally:
        _manejando_error = False


def instalar_manejador_global() -> None:
    """Instala el manejador de excepciones no controladas.

    Se llama lo antes posible al arrancar, tanto en modo gráfico como en modo
    consola. Es idempotente: llamarlo dos veces no tiene efecto.
    """
    if getattr(sys, "_descargasordenadas_manejador", False):
        return
    sys.excepthook = _manejador_excepciones
    sys._descargasordenadas_manejador = True

    # En hilos secundarios, Python no usa sys.excepthook: hay que cubrirlo
    # aparte o los fallos de un hilo morirían en silencio.
    try:
        import threading

        def _manejador_hilo(args):
            _manejador_excepciones(args.exc_type, args.exc_value, args.exc_traceback)

        threading.excepthook = _manejador_hilo
    except (AttributeError, ImportError):
        # Python 3.7 y anteriores no tienen threading.excepthook.
        pass
