#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sistema de iconos propio de DescargasOrdenadas.

Sustituye a los iconos genéricos de Qt (``QStyle.standardIcon``), que no son el
lenguaje visual de ningún sistema y hacían que la interfaz pareciera improvisada.

Los iconos son **SVG escritos a mano**, embebidos como texto: no hay archivos
que empaquetar, no hay dependencias externas y no hay licencias de terceros que
respetar. Se dibujan sobre una rejilla de 24×24 con trazo redondeado, que es la
convención de los sets de iconos actuales (Lucide, SF Symbols, Fluent), y se
pintan en el color del tema para que encajen tanto en claro como en oscuro.

El renderizado se hace con ``QSvgRenderer`` al tamaño exacto que pide la
pantalla, incluido su factor de escala, para que los iconos queden nítidos en
pantallas de alta densidad. Si QtSvg no estuviera disponible, se devuelve un
icono vacío y la interfaz sigue funcionando sin iconos.
"""

from __future__ import annotations

import logging

logger = logging.getLogger('organizador.iconos')

try:
    from PySide6.QtCore import QByteArray, QRectF, Qt
    from PySide6.QtGui import QIcon, QPainter, QPixmap
    from PySide6.QtSvg import QSvgRenderer

    SVG_DISPONIBLE = True
except ImportError:
    SVG_DISPONIBLE = False

from . import estilos


# --------------------------------------------------------------------------
# Trazos de los iconos (rejilla 24x24, solo el contenido interior)
# --------------------------------------------------------------------------

_TRAZOS: dict[str, str] = {
    # --- navegación -------------------------------------------------------
    "inicio": (
        '<path d="M3 10.5 12 3.2l9 7.3"/>'
        '<path d="M5.6 9.6V20h12.8V9.6"/>'
        '<path d="M9.8 20v-5.6h4.4V20"/>'
    ),
    "historial": (
        '<path d="M3.6 12a8.4 8.4 0 1 0 2.5-5.9"/>'
        '<path d="M3.2 4.6V9.2h4.6"/>'
        '<path d="M12 7.6V12l3 1.9"/>'
    ),
    "actividad": '<path d="M3 12h3.4l2.1-6.4 3.6 12.8 2.5-8.3 1.7 1.9H21"/>',
    "ajustes": (
        '<path d="M4 7.5h9.2"/><path d="M17.6 7.5H20"/>'
        '<circle cx="15.4" cy="7.5" r="2.2"/>'
        '<path d="M4 16.5h2.4"/><path d="M10.8 16.5H20"/>'
        '<circle cx="8.6" cy="16.5" r="2.2"/>'
    ),
    "avanzado": (
        '<path d="M12 3.2 3.2 7.6 12 12l8.8-4.4z"/>'
        '<path d="m3.2 12.4 8.8 4.4 8.8-4.4"/>'
        '<path d="m3.2 16.8 8.8 4.4 8.8-4.4"/>'
    ),

    # --- archivos y acciones ---------------------------------------------
    "carpeta": (
        '<path d="M3 7.4a2 2 0 0 1 2-2h3.6l2.1 2.6H19a2 2 0 0 1 2 2v7.6'
        'a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
    ),
    "organizar": (
        '<path d="M10.5 3.4 12.2 8.6 17.4 10.3 12.2 12 10.5 17.2 8.8 12 3.6 10.3 8.8 8.6z"/>'
        '<path d="M18.6 3.4v3.2"/><path d="M17 5h3.2"/>'
    ),
    "deshacer": (
        '<path d="M4 8.8h9.8a5.6 5.6 0 0 1 0 11.2H8.2"/>'
        '<path d="M7.6 5.2 4 8.8l3.6 3.6"/>'
    ),
    "refrescar": (
        '<path d="M20.4 12a8.4 8.4 0 1 1-2.5-5.9"/>'
        '<path d="M20.8 4.6V9.2h-4.6"/>'
    ),
    "descargar": (
        '<path d="M12 3.4v11.2"/><path d="m7.4 10.2 4.6 4.6 4.6-4.6"/>'
        '<path d="M4 18.6h16"/>'
    ),
    "buscar": '<circle cx="10.6" cy="10.6" r="6.4"/><path d="m20 20-4.9-4.9"/>',
    "duplicados": (
        '<rect x="3.4" y="3.4" width="11.6" height="11.6" rx="2.2"/>'
        '<rect x="9" y="9" width="11.6" height="11.6" rx="2.2"/>'
    ),
    "disco": (
        '<rect x="3" y="4.2" width="18" height="6.8" rx="2"/>'
        '<rect x="3" y="13" width="18" height="6.8" rx="2"/>'
        '<path d="M7.2 7.6h.01"/><path d="M7.2 16.4h.01"/>'
    ),
    "fechas": (
        '<rect x="3.4" y="5" width="17.2" height="16" rx="2.2"/>'
        '<path d="M3.4 10h17.2"/><path d="M8.2 3v3.6"/><path d="M15.8 3v3.6"/>'
    ),
    "estadisticas": (
        '<path d="M3.6 20.4h16.8"/>'
        '<path d="M7 20.4v-9.2"/><path d="M12 20.4V4.6"/><path d="M17 20.4v-6.2"/>'
    ),
    "cerrar": '<path d="M6 6 18 18"/><path d="M18 6 6 18"/>',

    # --- estados y permisos ----------------------------------------------
    "escudo": (
        '<path d="M12 3.2 19.8 6v5.4c0 4.4-3.2 7.9-7.8 9.4-4.6-1.5-7.8-5-7.8-9.4V6z"/>'
    ),
    "info": '<circle cx="12" cy="12" r="8.8"/><path d="M12 11.2v5"/><path d="M12 8h.01"/>',
    "exito": (
        '<circle cx="12" cy="12" r="8.8"/><path d="m8.2 12.4 2.7 2.7L16 9.4"/>'
    ),
    "error": (
        '<path d="M12 3.6 21.4 20H2.6z"/><path d="M12 10v4.2"/><path d="M12 17.2h.01"/>'
    ),
    "campana": (
        '<path d="M6.6 10.2a5.4 5.4 0 0 1 10.8 0c0 3.9 1.6 5.4 1.6 5.4H5'
        's1.6-1.5 1.6-5.4"/>'
        '<path d="M10.1 18.6a2 2 0 0 0 3.8 0"/>'
    ),
    "red": (
        '<circle cx="12" cy="12" r="8.8"/><path d="M3.2 12h17.6"/>'
        '<path d="M12 3.2c2.6 2.6 3.9 5.6 3.9 8.8s-1.3 6.2-3.9 8.8'
        'c-2.6-2.6-3.9-5.6-3.9-8.8S9.4 5.8 12 3.2"/>'
    ),
    "rayo": '<path d="M13.2 3 4.8 13.6h6L10.8 21l8.4-10.6h-6z"/>',
}

# Nombre que se usa cuando se pide uno que no existe.
_POR_DEFECTO = "info"

_PLANTILLA = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
    'fill="none" stroke="{color}" stroke-width="{grosor}" '
    'stroke-linecap="round" stroke-linejoin="round">{cuerpo}</svg>'
)

# Caché de iconos ya renderizados: (nombre, tamano, color, dpr) -> QIcon
_cache: dict = {}


# --------------------------------------------------------------------------
# Colores
# --------------------------------------------------------------------------

def color_texto(tema: str = "auto") -> str:
    """Color del texto normal del tema indicado."""
    return estilos.paleta(_resolver(tema))["texto"]


def color_tenue(tema: str = "auto") -> str:
    """Color secundario, para iconos discretos."""
    return estilos.paleta(_resolver(tema))["texto_sec"]


def color_acento(tema: str = "auto") -> str:
    return estilos.paleta(_resolver(tema))["acento"]


def _resolver(tema: str) -> str:
    if tema == "auto":
        return estilos.tema_del_sistema()
    return "oscuro" if tema == "oscuro" else "claro"


# --------------------------------------------------------------------------
# Renderizado
# --------------------------------------------------------------------------

def _renderizar(nombre: str, tamano: int, color: str, dpr: float) -> QPixmap:
    """Dibuja el icono en un QPixmap del tamaño físico que toca."""
    cuerpo = _TRAZOS.get(nombre, _TRAZOS[_POR_DEFECTO])
    # El grosor se ajusta al tamaño para que el trazo no se vea desproporcionado
    # cuando el icono es pequeño.
    grosor = 2.0 if tamano >= 20 else 2.2
    svg = _PLANTILLA.format(color=color, grosor=grosor, cuerpo=cuerpo)

    lado = max(1, int(round(tamano * dpr)))
    pixmap = QPixmap(lado, lado)
    pixmap.fill(Qt.transparent)

    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    if not renderer.isValid():
        logger.debug(f"El SVG del icono «{nombre}» no es válido")
        return pixmap

    pintor = QPainter(pixmap)
    pintor.setRenderHint(QPainter.Antialiasing, True)
    pintor.setRenderHint(QPainter.SmoothPixmapTransform, True)
    try:
        renderer.render(pintor, QRectF(0, 0, lado, lado))
    finally:
        pintor.end()

    pixmap.setDevicePixelRatio(dpr)
    return pixmap


def pixmap(nombre: str, tamano: int = 20, color: str | None = None,
           tema: str = "auto") -> QPixmap:
    """Devuelve el icono como QPixmap en el color indicado."""
    if not SVG_DISPONIBLE:
        return QPixmap()

    color = color or color_texto(tema)
    dpr = _factor_escala()
    return _renderizar(nombre, tamano, color, dpr)


def icono(nombre: str, tamano: int = 20, color: str | None = None,
          tema: str = "auto", color_seleccionado: str | None = None) -> QIcon:
    """Devuelve el icono listo para usar en cualquier widget.

    Args:
        nombre: identificador del icono (ver ``disponibles()``).
        tamano: lado en píxeles lógicos.
        color: color del trazo. Si es ``None`` se usa el del tema.
        tema: ``"claro"``, ``"oscuro"`` o ``"auto"``.
        color_seleccionado: color cuando el elemento está seleccionado. Se usa
            en la barra lateral, donde el fondo pasa a ser el color de acento y
            el icono necesita contrastar.
    """
    if not SVG_DISPONIBLE:
        return QIcon()

    color = color or color_texto(tema)
    clave = (nombre, tamano, color, color_seleccionado, _factor_escala())
    if clave in _cache:
        return _cache[clave]

    resultado = QIcon()
    resultado.addPixmap(_renderizar(nombre, tamano, color, _factor_escala()), QIcon.Normal)

    if color_seleccionado:
        resultado.addPixmap(
            _renderizar(nombre, tamano, color_seleccionado, _factor_escala()),
            QIcon.Selected,
        )
        resultado.addPixmap(
            _renderizar(nombre, tamano, color_seleccionado, _factor_escala()),
            QIcon.Active,
        )

    _cache[clave] = resultado
    return resultado


def icono_lateral(nombre: str, tamano: int = 18, tema: str = "auto") -> QIcon:
    """Icono del raíl lateral.

    El elemento activo **no** lleva fondo relleno (el raíl lo marca con una
    barra carmesí a su izquierda), así que el icono activo va en carmesí sobre
    el papel en vez de en blanco sobre un color.
    """
    return icono(nombre, tamano, tema=tema, color_seleccionado=color_acento(tema))


def _factor_escala() -> float:
    """Factor de escala de la pantalla, para que el icono no salga borroso."""
    try:
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is not None:
            pantalla = app.primaryScreen()
            if pantalla is not None:
                return float(pantalla.devicePixelRatio() or 1.0)
    except Exception:
        pass
    return 1.0


def limpiar_cache() -> None:
    """Vacía la caché. Necesario al cambiar de tema o de pantalla."""
    _cache.clear()


def disponibles() -> list:
    """Nombres de los iconos que existen."""
    return sorted(_TRAZOS)
