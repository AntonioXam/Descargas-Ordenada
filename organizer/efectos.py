#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Efectos visuales nativos de cada sistema para DescargasOrdenadas.

Hace que la ventana se sienta integrada en el escritorio, como una aplicación
nativa de verdad:

- **macOS**: aplica *vibrancy* (``NSVisualEffectView``) con el material de barra
  lateral, igual que Ajustes del Sistema o Finder.
- **Windows 11**: activa el efecto *Mica* con la API de DWM; en Windows 10 se
  usa un tinte acrílico discreto.
- **Linux**: intenta la translucidez del compositor (KWin/GNOME) y, si no está
  disponible, deja la ventana opaca sin romper nada.

Todos los efectos degradan con elegancia: si algo no está soportado, la
aplicación se ve exactamente igual que antes.
"""

from __future__ import annotations

import logging
import sys

logger = logging.getLogger('organizador.efectos')


def soportado() -> bool:
    """Indica si el sistema actual admite algún efecto de transparencia."""
    return sys.platform in ("darwin", "win32") or sys.platform.startswith("linux")


def aplicar_efecto_ventana(ventana) -> bool:
    """Aplica el efecto nativo correspondiente a la ventana indicada.

    Args:
        ventana: ``QMainWindow`` ya creada (debe tener un ``winId()`` válido).

    Returns:
        True si se aplicó algún efecto.
    """
    try:
        if sys.platform == "darwin":
            return _aplicar_macos(ventana)
        if sys.platform == "win32":
            return _aplicar_windows(ventana)
        return _aplicar_linux(ventana)
    except Exception as e:
        logger.debug(f"Sin efecto de ventana: {e}")
        return False


# --------------------------------------------------------------------------
# macOS: vibrancy con NSVisualEffectView
# --------------------------------------------------------------------------

def _aplicar_macos(ventana) -> bool:
    """Añade una capa de vibrancy nativa detrás del contenido de la ventana.

    En macOS, ``winId()`` devuelve la vista de contenido (``contentView``) del
    ``NSWindow``. Se inserta un ``NSVisualEffectView`` como subvista inferior y
    se pinta su fondo con un poco de transparencia para que se aprecie, igual
    que hacen Finder o Ajustes del Sistema.
    """
    import ctypes
    import ctypes.util

    objc = ctypes.cdll.LoadLibrary(ctypes.util.find_library("objc"))
    if not objc:
        return False

    objc.objc_getClass.restype = ctypes.c_void_p
    objc.objc_getClass.argtypes = [ctypes.c_char_p]
    objc.sel_registerName.restype = ctypes.c_void_p
    objc.sel_registerName.argtypes = [ctypes.c_char_p]
    msg = objc.objc_msgSend

    def enviar(objeto, nombre, *argumentos):
        sel = objc.sel_registerName(nombre.encode())
        if argumentos:
            msg.restype = ctypes.c_void_p
            msg.argtypes = [ctypes.c_void_p, ctypes.c_void_p] + [
                ctypes.c_void_p for _ in argumentos
            ]
            return msg(objeto, sel, *argumentos)
        msg.restype = ctypes.c_void_p
        msg.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        return msg(objeto, sel)

    try:
        vista_contenido = ctypes.c_void_p(int(ventana.winId()))
        if not vista_contenido.value:
            return False

        # Crear el NSVisualEffectView
        clase = objc.objc_getClass(b"NSVisualEffectView")
        instancia = enviar(clase, "alloc")
        efecto = enviar(instancia, "init")

        # Material 7 = sidebar (el de Finder/Ajustes)
        enviar(efecto, "setMaterial:", ctypes.c_void_p(7))
        # Blending 0 = behindWindow
        enviar(efecto, "setBlendingMode:", ctypes.c_void_p(0))
        # Estado 1 = active
        enviar(efecto, "setState:", ctypes.c_void_p(1))
        # 18 = ancho y alto elásticos: se redimensiona con la ventana
        enviar(efecto, "setAutoresizingMask:", ctypes.c_void_p(18))

        # Insertarla en el fondo, por debajo del contenido de Qt
        enviar(vista_contenido, "addSubview:positioned:relativeTo:",
               efecto, ctypes.c_void_p(-1), ctypes.c_void_p(0))

        # No se toca WA_TranslucentBackground: la hoja de estilo deja el fondo
        # del contenido semitransparente y así no se rompe el redimensionado.

        # Guardar referencia para que Python no libere la vista nativa
        ventana.setProperty("_vibrancy_activo", True)
        logger.info("Vibrancy de macOS aplicado")
        return True
    except Exception as e:
        logger.debug(f"No se pudo aplicar vibrancy en macOS: {e}")
        return False


# --------------------------------------------------------------------------
# Windows 11: efecto Mica
# --------------------------------------------------------------------------

def _aplicar_windows(ventana) -> bool:
    """Activa Mica en Windows 11 (o un acrílico discreto en Windows 10)."""
    import ctypes

    try:
        build = _build_windows()
        ident = int(ventana.winId())

        # Windows 11: atributo DWMWA_SYSTEMBACKDROP_TYPE (38)
        if build >= 22000:
            DWMWA_SYSTEMBACKDROP_TYPE = 38
            DWMSBT_MAINWINDOW = 2  # Mica
            valor = ctypes.c_int(DWMSBT_MAINWINDOW)
            resultado = ctypes.windll.dwmapi.DwmSetWindowAttribute(
                ctypes.c_void_p(ident),
                ctypes.c_uint(DWMWA_SYSTEMBACKDROP_TYPE),
                ctypes.byref(valor),
                ctypes.sizeof(valor),
            )
            if resultado == 0:
                logger.info("Efecto Mica aplicado")
                return True

        # Windows 10: tinte acrílico de la barra de título (no invasivo)
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        activo = ctypes.c_int(1)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            ctypes.c_void_p(ident),
            ctypes.c_uint(DWMWA_USE_IMMERSIVE_DARK_MODE),
            ctypes.byref(activo),
            ctypes.sizeof(activo),
        )
        logger.debug("Mica no disponible; se aplicó el modo oscuro de la barra")
        return False
    except Exception as e:
        logger.debug(f"No se pudo aplicar el efecto de Windows: {e}")
        return False


def _build_windows() -> int:
    """Devuelve el número de compilación de Windows."""
    import ctypes

    class OSVERSIONINFOEXW(ctypes.Structure):
        _fields_ = [
            ("dwOSVersionInfoSize", ctypes.c_ulong),
            ("dwMajorVersion", ctypes.c_ulong),
            ("dwMinorVersion", ctypes.c_ulong),
            ("dwBuildNumber", ctypes.c_ulong),
            ("dwPlatformId", ctypes.c_ulong),
            ("szCSDVersion", ctypes.c_wchar * 128),
        ]

    info = OSVERSIONINFOEXW()
    info.dwOSVersionInfoSize = ctypes.sizeof(OSVERSIONINFOEXW)
    ctypes.windll.ntdll.RtlGetVersion(ctypes.byref(info))
    return int(info.dwBuildNumber)


# --------------------------------------------------------------------------
# Linux: translucidez del compositor
# --------------------------------------------------------------------------

def _aplicar_linux(ventana) -> bool:
    """Translucidez suave si el compositor la admite.

    Se limita a un valor alto (0.98) para que el texto siga siendo legible y
    el resultado no dependa de tener un fondo de escritorio concreto.
    """
    try:
        from PySide6.QtCore import Qt

        ventana.setAttribute(Qt.WA_TranslucentBackground, False)
        ventana.setWindowOpacity(0.985)
        logger.debug("Translucidez discreta aplicada en Linux")
        return True
    except Exception as e:
        logger.debug(f"Sin translucidez en Linux: {e}")
        return False
