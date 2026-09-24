#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Efectos visuales nativos: transparencia real de cada sistema.

Hace que la ventana se sienta parte del escritorio, como una aplicación nativa:

- **macOS**: *vibrancy* con ``NSVisualEffectView``, el mismo material que usan
  Finder o Ajustes del Sistema.
- **Windows 11**: efecto *Mica*, con las esquinas redondeadas del sistema. En
  Windows 10 se deja el fondo opaco, porque Mica no existe ahí.
- **Linux**: translucidez del compositor, **solo si hay compositor**. Sin él la
  ventana se queda opaca: forzarla daría un fondo negro.

## Lo que estaba mal antes

El efecto estaba **activado y tapado a la vez**. Se creaba el
``NSVisualEffectView`` y se activaba Mica, pero la ventana nunca se declaraba
translúcida, así que Qt pintaba su fondo opaco encima y el material del sistema
no se veía. El resultado era un color plano: ni vibrancy ni Mica. En Linux,
además, se usaba ``setWindowOpacity``, que **no es translucidez**: baja la
opacidad de la ventana entera, texto incluido, y deja la interfaz desvaída.

Aquí se corrigen las tres cosas:

1. La ventana se declara **no opaca** (``WA_TranslucentBackground`` y, en macOS,
   ``setOpaque:NO``), para que Qt deje huecos por los que se vea el material.
2. La capa de efecto se inserta **por debajo** del contenido de Qt, no como
   subvista suya (que quedaría encima y taparía toda la interfaz).
3. Se retiene el objeto nativo, en lugar de guardar solo un booleano.

También se corrigieron los valores de los materiales: el código anterior usaba
``7`` creyendo que era *sidebar*, cuando ``sidebar`` es ``4`` y ``7`` es
*windowBackground*.

Todo degrada con elegancia: si algo no está soportado o falla, la ventana se
queda como estaba y la aplicación sigue funcionando.
"""

from __future__ import annotations

import logging
import os
import sys

logger = logging.getLogger('organizador.efectos')

# Variable de entorno para desactivar la transparencia sin tocar el código.
# Sirve para diagnosticar problemas de renderizado y para quien no la quiera.
VARIABLE_DESACTIVAR = "DESCARGASORDENADAS_SIN_TRANSPARENCIA"


def desactivado_por_entorno() -> bool:
    """Indica si se ha pedido explícitamente no usar transparencia."""
    return os.environ.get(VARIABLE_DESACTIVAR, "").strip() not in ("", "0", "false")


def soportado() -> bool:
    """Indica si el sistema actual admite algún efecto de transparencia."""
    if desactivado_por_entorno():
        return False
    return sys.platform in ("darwin", "win32") or sys.platform.startswith("linux")


def aplicar_efecto_ventana(ventana) -> bool:
    """Aplica el efecto nativo correspondiente a la ventana indicada.

    Args:
        ventana: ``QMainWindow`` ya creada (debe tener un ``winId()`` válido).

    Returns:
        True si el efecto quedó aplicado. Si es False, la ventana conserva su
        aspecto opaco y nada más cambia.
    """
    if desactivado_por_entorno():
        logger.info("Transparencia desactivada por %s", VARIABLE_DESACTIVAR)
        return False

    try:
        if sys.platform == "darwin":
            return _aplicar_macos(ventana)
        if sys.platform == "win32":
            return _aplicar_windows(ventana)
        return _aplicar_linux(ventana)
    except Exception as e:
        logger.debug(f"Sin efecto de ventana: {e}")
        return False


def _hacer_ventana_translucida(ventana) -> None:
    """Deja que Qt no pinte un fondo opaco en la ventana.

    Es el paso que faltaba: sin esto, cualquier material que se ponga detrás
    queda tapado por el propio fondo de Qt. El color lo sigue poniendo la hoja
    de estilo, pero con alfa.
    """
    from PySide6.QtCore import Qt

    ventana.setAttribute(Qt.WA_TranslucentBackground, True)
    ventana.setAutoFillBackground(False)


# --------------------------------------------------------------------------
# macOS: vibrancy con NSVisualEffectView
# --------------------------------------------------------------------------

# Valores de NSVisualEffectMaterial (AppKit). Los del código anterior estaban
# equivocados: usaba 7 como «sidebar», pero sidebar es 4 y 7 es windowBackground.
# Se dejan los tres documentados porque son los que hacen falta para dar
# vibrancy a la barra lateral y al contenido por separado.
_MATERIAL_SIDEBAR = 4            # el de la barra lateral de Finder
_MATERIAL_WINDOW_BACKGROUND = 7  # el del fondo de ventana
_MATERIAL_UNDER_WINDOW = 12      # detrás del contenido (el que se usa aquí)

# NSVisualEffectBlendingMode
_MEZCLA_BEHIND_WINDOW = 0

# NSVisualEffectState: Active = siempre visible, pase lo que pase con el foco.
_ESTADO_ACTIVO = 1

# NSViewWidthSizable | NSViewHeightSizable: la capa acompaña a la ventana.
_MASCARA_ELASTICA = 18

# NSWindowBelow: inserta la capa justo por debajo del contenido de Qt.
_DEBAJO_DEL_CONTENIDO = -1


def _aplicar_macos(ventana) -> bool:
    """Añade una capa de vibrancy nativa por debajo del contenido de la ventana."""
    import ctypes
    import ctypes.util

    objc = ctypes.cdll.LoadLibrary(ctypes.util.find_library("objc"))
    if not objc:
        return False

    c_void_p = ctypes.c_void_p
    c_double = ctypes.c_double

    class NSPoint(ctypes.Structure):
        _fields_ = [("x", c_double), ("y", c_double)]

    class NSSize(ctypes.Structure):
        _fields_ = [("width", c_double), ("height", c_double)]

    class NSRect(ctypes.Structure):
        _fields_ = [("origin", NSPoint), ("size", NSSize)]

    msg = objc.objc_msgSend
    objc.objc_getClass.restype = c_void_p
    objc.objc_getClass.argtypes = [ctypes.c_char_p]
    objc.sel_registerName.restype = c_void_p
    objc.sel_registerName.argtypes = [ctypes.c_char_p]

    def sel(nombre: str) -> c_void_p:
        return objc.sel_registerName(nombre.encode())

    def enviar(objeto, nombre, *args, restype=c_void_p, argtypes=None):
        """Llama a un método Objective-C declarando bien los tipos.

        Los tipos importan: devolver un ``NSRect`` (cuatro dobles) o pasar una
        estructura por valor no funciona si se declara todo como puntero.
        """
        msg.restype = restype
        msg.argtypes = [c_void_p, c_void_p] + (argtypes or [c_void_p] * len(args))
        return msg(objeto, sel(nombre), *args)

    def clase(nombre: bytes) -> c_void_p:
        valor = objc.objc_getClass(nombre)
        return c_void_p(valor) if valor else c_void_p(0)

    vista_contenido = c_void_p(int(ventana.winId()))
    if not vista_contenido.value:
        return False

    ventana_ns = enviar(vista_contenido, "window")
    if not ventana_ns:
        return False

    # 1) Ventana no opaca. Sin esto el material no se ve nunca.
    enviar(
        ventana_ns, "setOpaque:", ctypes.c_bool(False),
        restype=None, argtypes=[ctypes.c_bool],
    )
    color_transparente = enviar(clase(b"NSColor"), "clearColor")
    if color_transparente:
        enviar(ventana_ns, "setBackgroundColor:", color_transparente, restype=None)

    # 2) Qt deja huecos para que se vea el material.
    _hacer_ventana_translucida(ventana)

    # 3) Capa de vibrancy del tamaño del contenido.
    marco = enviar(vista_contenido, "bounds", restype=NSRect, argtypes=[])
    capa = enviar(
        enviar(clase(b"NSVisualEffectView"), "alloc"),
        "initWithFrame:",
        marco,
        argtypes=[NSRect],
    )
    if not capa:
        return False

    enviar(capa, "setMaterial:", c_void_p(_MATERIAL_UNDER_WINDOW), restype=None)
    enviar(capa, "setBlendingMode:", c_void_p(_MEZCLA_BEHIND_WINDOW), restype=None)
    enviar(capa, "setState:", c_void_p(_ESTADO_ACTIVO), restype=None)
    enviar(capa, "setAutoresizingMask:", c_void_p(_MASCARA_ELASTICA), restype=None)

    # 4) Se inserta POR DEBAJO del contenido de Qt. Como subvista suya quedaría
    # encima y taparía toda la interfaz: es el error que hay que evitar.
    contenedor = enviar(vista_contenido, "superview")
    destino = contenedor or enviar(ventana_ns, "contentView")
    if destino:
        enviar(
            destino,
            "addSubview:positioned:relativeTo:",
            capa,
            ctypes.c_long(_DEBAJO_DEL_CONTENIDO),
            vista_contenido,
            restype=None,
            argtypes=[c_void_p, ctypes.c_long, c_void_p],
        )

    # 5) Referencia fuerte al objeto nativo: si no, podría liberarse y dejar la
    # ventana sin material. Antes se guardaba solo un booleano.
    ventana._capa_vibrancy = capa
    ventana.setProperty("_vibrancy_activo", True)
    logger.info("Vibrancy de macOS aplicado")
    return True


# --------------------------------------------------------------------------
# Windows 11: efecto Mica
# --------------------------------------------------------------------------

def _aplicar_windows(ventana) -> bool:
    """Activa Mica y las esquinas redondeadas de Windows 11.

    Mica necesita que el fondo de la ventana sea transparente para poder verse;
    de ahí que se marque la ventana como translúcida. En Windows 10 no existe
    Mica, así que se deja el fondo opaco en lugar de forzar un efecto a medias.
    """
    import ctypes

    if _build_windows() < 22000:
        logger.info("Windows 10: Mica no está disponible, se mantiene el fondo opaco")
        return False

    DWMWA_WINDOW_CORNER_PREFERENCE = 33
    DWMWA_SYSTEMBACKDROP_TYPE = 38
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    DWMSBT_MAINWINDOW = 2   # Mica
    DWMWCP_ROUND = 2        # esquinas redondeadas del sistema

    ident = ctypes.c_void_p(int(ventana.winId()))

    def atributo(codigo: int, valor: int) -> int:
        dato = ctypes.c_int(valor)
        return ctypes.windll.dwmapi.DwmSetWindowAttribute(
            ident, ctypes.c_uint(codigo), ctypes.byref(dato), ctypes.sizeof(dato)
        )

    try:
        # Las esquinas redondeadas funcionan aunque Mica no llegue a aplicarse.
        atributo(DWMWA_WINDOW_CORNER_PREFERENCE, DWMWCP_ROUND)

        # Igual que en macOS: sin translucidez, Mica queda tapado por Qt.
        _hacer_ventana_translucida(ventana)

        if atributo(DWMWA_SYSTEMBACKDROP_TYPE, DWMSBT_MAINWINDOW) != 0:
            logger.debug("Windows no aceptó el efecto Mica")
            return False

        atributo(DWMWA_USE_IMMERSIVE_DARK_MODE, 1)
        logger.info("Efecto Mica y esquinas redondeadas aplicados")
        return True
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

# Procesos de composición conocidos. La comprobación es aproximada, pero basta
# para no activar la translucidez en un escritorio sin compositor, donde el
# resultado sería un fondo negro.
_COMPOSITORES = (
    "picom", "compton", "kwin_x11", "kwin_wayland", "mutter",
    "gnome-shell", "xfwm4", "marco", "muffin", "sway", "hyprland",
    "weston", "kwin",
)


def hay_compositor() -> bool:
    """Indica si el escritorio parece tener composición activa."""
    if os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland":
        # En Wayland el compositor forma parte del servidor gráfico.
        return True

    try:
        import subprocess

        for nombre in _COMPOSITORES:
            resultado = subprocess.run(
                ["pgrep", "-x", nombre], capture_output=True, timeout=3, check=False
            )
            if resultado.returncode == 0:
                return True
    except Exception as e:
        logger.debug(f"No se pudo comprobar el compositor: {e}")
    return False


def _aplicar_linux(ventana) -> bool:
    """Translucidez suave, solo si el escritorio puede componerla."""
    if not hay_compositor():
        logger.info("Sin compositor: la ventana se queda opaca")
        return False

    try:
        _hacer_ventana_translucida(ventana)
        logger.debug("Translucidez de Linux aplicada")
        return True
    except Exception as e:
        logger.debug(f"Sin translucidez en Linux: {e}")
        return False
