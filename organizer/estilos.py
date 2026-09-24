#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sistema de estilos de DescargasOrdenadas.

Un único punto de verdad para la apariencia de la aplicación.

## La identidad: «mesa de clasificación»

La aplicación ordena archivos, así que se parece a una mesa donde las cosas se
colocan. De ahí las decisiones, que no son de adorno sino de estructura:

- **Sin cajas.** El material nativo de un organizador de archivos es una lista
  alineada, no una pila de tarjetas. La jerarquía la llevan el espacio y una
  línea fina, nunca un contenedor redondeado alrededor de cada bloque.
- **Etiqueta a la izquierda, valor a la derecha**, en columna. Es como se lee
  una lista de archivos con sus tamaños y fechas.
- **El carmesí es un sello, no un fondo.** Sale del propio icono de la
  aplicación (una seta roja) y aparece en dos sitios: el marcador de la sección
  activa y la acción principal. Nunca como relleno decorativo.
- **Los números se alinean.** Todo valor que puede cambiar —recuentos, tamaños,
  intervalos, rutas— va en monoespaciada con cifras tabulares, porque ahí la
  alineación significa algo.
- **Cálido, no clínico.** El papel y la tinta llevan una traza del rojo de la
  seta, para que la aplicación tenga temperatura en vez de ser gris de sistema.

Cualquier widget puede marcar su rol con ``setProperty("rol", "...")`` para
recibir el estilo adecuado (titulo, dato, primario, banda...).
"""

from __future__ import annotations

import sys


# --------------------------------------------------------------------------
# Tokens de diseño
# --------------------------------------------------------------------------
# Una sola escala para toda la aplicación. Los componentes se describen en
# términos de estos valores y no de números sueltos.

TOKENS = {
    # Escala de espaciado (múltiplos de 4). Generosa en vertical: la estructura
    # se apoya en el aire, no en cajas.
    "esp_xs": 4,
    "esp_s": 8,
    "esp_m": 12,
    "esp_l": 16,
    "esp_xl": 28,
    "esp_xxl": 40,

    # Radios. Contenidos a propósito: las cajas redondeadas de tarjeta
    # desaparecen, así que el radio queda para controles, campos y menús.
    "radio_control": 6,
    "radio_campo": 7,
    "radio_boton": 7,
    "radio_menu": 10,
    "radio_item": 6,
    "radio_panel": 12,

    # Alturas y grosores
    "alto_control": 22,
    "grosor_borde": 1,
    "grosor_barra": 3,       # la barra de progreso es un filamento, no un bloque
    "grosor_scroll": 10,
    "grosor_marcador": 3,    # barra carmesí del elemento activo

    # Tipografía (se suman al tamaño base del sistema)
    "tipo_titulo": 11,       # la voz de la aplicación
    "tipo_seccion": 3,
    "tipo_subtitulo": 1,
    "tipo_pequeno": 1,
    "tipo_discreto": 2,

    # Ancho de lectura: una utilidad se lee en columna, no a todo lo ancho.
    "ancho_lectura": 760,

    # Movimiento (milisegundos)
    "mov_micro": 80,
    "mov_transicion": 140,
}


# --------------------------------------------------------------------------
# Paletas
# --------------------------------------------------------------------------

PALETA_CLARA = {
    "nombre": "claro",
    # Papel: off-white cálido, no el gris clínico de sistema.
    "fondo": "#F7F5F3",
    "fondo_barra": "#F2EEEB",
    "fondo_lateral": "#EFEAE6",   # el raíl, un escalón por detrás del papel
    "panel": "#FFFFFF",
    "panel_alt": "#F2EDE9",
    "panel_hover": "#EAE2DD",
    "seleccion": "#F7E4E8",
    # Líneas: el único recurso estructural que queda.
    "borde": "#DCD1CA",
    "borde_suave": "#E9E1DB",
    # Tinta: negro cálido, con una traza del rojo de la seta.
    "texto": "#241C1B",
    "texto_sec": "#6E615D",
    "texto_disc": "#A3988F",
    # Carmesí del sombrero de la seta. Un sello, no un relleno.
    "acento": "#C4123C",
    "acento_hover": "#A90E32",
    "acento_pulsado": "#8E0A29",
    "acento_suave": "#FBE8EC",
    "acento_texto": "#FFFFFF",
    "exito": "#3F7D4E",
    "aviso": "#A26400",
    # El rojo de error es más cálido y más oscuro que el carmesí de marca
    # (#C4123C). Si fueran del mismo tono, «Reiniciar modelo» parecería la
    # acción principal en lugar de una acción que hay que pensar.
    "error": "#9A2B24",
    "sombra": "rgba(36, 28, 27, 0.10)",
    "mono": "'SF Mono', 'Menlo', 'Consolas', 'DejaVu Sans Mono', monospace",
}

PALETA_OSCURA = {
    "nombre": "oscuro",
    "fondo": "#171314",
    "fondo_barra": "#1D1819",
    "fondo_lateral": "#131011",
    "panel": "#201B1C",
    "panel_alt": "#262021",
    "panel_hover": "#2E2728",
    "seleccion": "#3B1C26",
    "borde": "#372E2F",
    "borde_suave": "#2A2324",
    "texto": "#F4EFEC",
    "texto_sec": "#A79A96",
    "texto_disc": "#6F6461",
    "acento": "#E0355C",
    "acento_hover": "#F04A6E",
    "acento_pulsado": "#C42A4E",
    "acento_suave": "#3B1C26",
    "acento_texto": "#FFFFFF",
    "exito": "#5FAF72",
    "aviso": "#E0A03A",
    # Más cálido que el carmesí de marca, por el mismo motivo que en claro.
    "error": "#D9584C",
    "sombra": "rgba(0, 0, 0, 0.50)",
    "mono": "'SF Mono', 'Menlo', 'Consolas', 'DejaVu Sans Mono', monospace",
}


# --------------------------------------------------------------------------
# Tipografía
# --------------------------------------------------------------------------

def familias_sistema() -> str:
    """Devuelve la lista de familias tipográficas nativas del sistema.

    Es una elección, no una dejadez: una utilidad de escritorio que se ejecuta
    en tres sistemas debe leer el texto con la fuente del sistema, porque es la
    que el usuario tiene calibrada. El carácter no lo pone aquí una tipografía
    exótica, lo ponen el color, la estructura y los números.
    """
    if sys.platform == "darwin":
        familias = ["SF Pro Text", "SF Pro Display", "Helvetica Neue"]
    elif sys.platform == "win32":
        familias = ["Segoe UI Variable Text", "Segoe UI", "Inter"]
    else:
        familias = ["Inter", "Ubuntu", "Cantarell", "Noto Sans", "DejaVu Sans"]
    familias.append("sans-serif")
    return ", ".join(f"'{f}'" for f in familias)


def tamano_fuente_base() -> int:
    """Tamaño de fuente base por sistema (los mac suelen ir algo más pequeños)."""
    if sys.platform == "darwin":
        return 13
    if sys.platform == "win32":
        return 10
    return 11


# --------------------------------------------------------------------------
# Detección del tema del sistema
# --------------------------------------------------------------------------

def tema_del_sistema() -> str:
    """Devuelve 'oscuro' o 'claro' según la preferencia del sistema operativo.

    Es una comprobación ligera y con múltiples fallbacks: si algo falla se
    asume claro, que es el valor menos agresivo visualmente.
    """
    try:
        if sys.platform == "darwin":
            return _tema_macos()
        if sys.platform == "win32":
            return _tema_windows()
        return _tema_linux()
    except Exception:
        return "claro"


def _tema_macos() -> str:
    import subprocess

    resultado = subprocess.run(
        ["defaults", "read", "-g", "AppleInterfaceStyle"],
        capture_output=True, text=True, timeout=3, check=False,
    )
    return "oscuro" if "dark" in (resultado.stdout or "").lower() else "claro"


def _tema_windows() -> str:
    import winreg

    clave = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
    )
    try:
        AppsUseLightTheme, _ = winreg.QueryValueEx(clave, "AppsUseLightTheme")
    finally:
        winreg.CloseKey(clave)
    return "claro" if int(AppsUseLightTheme) == 1 else "oscuro"


def _tema_linux() -> str:
    import subprocess

    comandos = [
        ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
        ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
    ]
    for comando in comandos:
        try:
            resultado = subprocess.run(
                comando, capture_output=True, text=True, timeout=3, check=False
            )
            salida = (resultado.stdout or "").lower()
            if "dark" in salida or "oscuro" in salida:
                return "oscuro"
            if salida.strip():
                return "claro"
        except Exception:
            continue
    return "claro"


# --------------------------------------------------------------------------
# Hojas de estilo
# --------------------------------------------------------------------------

def paleta(nombre: str) -> dict:
    """Devuelve la paleta indicada ('claro' u 'oscuro')."""
    return PALETA_OSCURA if nombre == "oscuro" else PALETA_CLARA


def colores_translucidos(nombre: str, opacidad: float = 0.70) -> dict:
    """Convierte los colores base a versiones con alfa (rgba).

    Se usa cuando hay un material nativo detrás (vibrancy en macOS, Mica en
    Windows): el fondo del contenido se vuelve semitransparente para dejar ver
    el material, mientras que las superficies se mantienen bastante opacas para
    que el texto se lea sin esfuerzo.

    Nota: desde la 6.0.2 la transparencia está **apagada por defecto** (ver
    ``efectos.py``), porque en un Mac real la ventana translúcida dejaba restos
    entre fotogramas. Esta función se conserva para cuando se active.

    Args:
        nombre: 'claro' u 'oscuro'.
        opacidad: opacidad del fondo del contenido (1.0 = opaco).
    """
    c = dict(paleta(nombre))
    alpha = max(0.0, min(1.0, opacidad))

    def rgba(color_hex: str, alfa: float) -> str:
        color_hex = color_hex.lstrip("#")
        if len(color_hex) == 3:
            color_hex = "".join(ch * 2 for ch in color_hex)
        r = int(color_hex[0:2], 16)
        g = int(color_hex[2:4], 16)
        b = int(color_hex[4:6], 16)
        return f"rgba({r}, {g}, {b}, {alfa:.3f})"

    c["fondo"] = rgba(c["fondo"], alpha)
    c["fondo_barra"] = rgba(c["fondo_barra"], min(1.0, alpha + 0.10))
    c["fondo_lateral"] = rgba(c["fondo_lateral"], min(1.0, alpha + 0.08))
    c["panel"] = rgba(c["panel"], min(1.0, alpha + 0.26))
    c["panel_alt"] = rgba(c["panel_alt"], min(1.0, alpha + 0.22))
    c["panel_hover"] = rgba(c["panel_hover"], min(1.0, alpha + 0.22))
    return c


def hoja_estilo(nombre: str = "auto", opacidad: float = 1.0) -> str:
    """Genera la hoja de estilo Qt completa para la paleta indicada.

    Args:
        nombre: 'claro', 'oscuro' o 'auto' (usar el tema del sistema).
        opacidad: opacidad del fondo (menor que 1.0 activa el efecto
            translúcido, pensado para cuando hay un material nativo detrás).
    """
    if nombre == "auto":
        nombre = tema_del_sistema()
    if opacidad < 1.0:
        c = colores_translucidos(nombre, opacidad)
    else:
        c = paleta(nombre)
    c = dict(c)
    c.setdefault("nombre", "oscuro" if nombre == "oscuro" else "claro")
    fuente = familias_sistema()
    base = tamano_fuente_base()
    tk = TOKENS

    return f"""
/* ================================================================= base */
* {{
    font-family: {fuente};
    font-size: {base}px;
    outline: 0;
}}
QWidget {{
    color: {c['texto']};
    background-color: transparent;
}}
QMainWindow, QDialog {{
    background-color: {c['fondo']};
}}
QToolTip {{
    background-color: {c['fondo_barra']};
    color: {c['texto']};
    border: {tk['grosor_borde']}px solid {c['borde']};
    border-radius: {tk['radio_control']}px;
    padding: {tk['esp_xs'] + 2}px {tk['esp_s']}px;
    font-size: {base - tk['tipo_pequeno']}px;
}}

/* ============================================================ tipografía */
/* La jerarquía la lleva el tamaño y el peso, no las cajas que la envuelven. */
QLabel[rol="titulo"] {{
    font-size: {base + tk['tipo_titulo']}px;
    font-weight: 600;
    color: {c['texto']};
    letter-spacing: -0.4px;
}}
/* El estado de la aplicación es un titular, pero un escalón por debajo del
   título de la sección: antes los dos iban al mismo tamaño y no había
   jerarquía ninguna. */
QLabel[rol="estado"] {{
    font-size: {base + 5}px;
    font-weight: 600;
    color: {c['texto']};
    letter-spacing: -0.2px;
}}
QLabel[rol="seccion"] {{
    font-size: {base + tk['tipo_seccion']}px;
    font-weight: 600;
    color: {c['texto']};
    letter-spacing: -0.1px;
    padding: 0 0 {tk['esp_s']}px 0;
}}
QLabel[rol="subtitulo"] {{
    font-size: {base + tk['tipo_subtitulo']}px;
    color: {c['texto_sec']};
}}
QLabel[rol="etiqueta"] {{
    font-size: {base}px;
    color: {c['texto']};
}}
QLabel[rol="secundaria"] {{
    font-size: {base - tk['tipo_pequeno']}px;
    color: {c['texto_sec']};
}}
QLabel[rol="discreta"] {{
    font-size: {base - tk['tipo_discreto']}px;
    color: {c['texto_disc']};
    letter-spacing: 0.2px;
}}

/* Los valores que cambian van en monoespaciada y se alinean entre sí. Es lo
   que hace legible una lista de archivos con sus tamaños y sus fechas. */
QLabel[rol="dato"] {{
    font-family: {c['mono']};
    font-size: {base}px;
    color: {c['texto']};
}}
QLabel[rol="dato_grande"] {{
    font-family: {c['mono']};
    font-size: {base + 7}px;
    font-weight: 600;
    color: {c['texto']};
    letter-spacing: -0.5px;
}}
QLabel[rol="ruta"] {{
    font-family: {c['mono']};
    font-size: {base - tk['tipo_pequeno']}px;
    color: {c['texto_sec']};
}}
QLabel[rol="exito"] {{ color: {c['exito']}; font-weight: 600; }}
QLabel[rol="aviso"] {{ color: {c['aviso']}; font-weight: 600; }}
QLabel[rol="error"] {{ color: {c['error']}; font-weight: 600; }}

/* ============================================================== estructura */
/* Aquí no hay tarjetas: los bloques se separan con aire y con una línea fina.
   Las reglas de «tarjeta» se conservan solo para que el código antiguo que las
   usa no se rompa, y las aplana. */
QFrame[rol="tarjeta"], QFrame[rol="banda"] {{
    background-color: transparent;
    border: none;
    border-radius: 0;
}}
/* La única marca de la casa: un bloque destacado se señala con el sello. */
QFrame[rol="tarjeta_destacada"] {{
    background-color: transparent;
    border: none;
    border-left: {tk['grosor_marcador']}px solid {c['acento']};
    padding-left: {tk['esp_l']}px;
}}
QFrame[rol="separador"] {{
    background-color: {c['borde_suave']};
    border: none;
    max-height: 1px;
    min-height: 1px;
}}
/* Filas de una lista: se separan con una línea, como una lista de archivos.
   Sin ella, varios bloques planos seguidos se leen como un solo párrafo. */
QFrame[rol="fila"] {{
    background-color: transparent;
    border: none;
    border-bottom: {tk['grosor_borde']}px solid {c['borde_suave']};
}}
QFrame[rol="fila"][ultima="si"] {{
    border-bottom: none;
}}

/* Grupo = sección: una línea arriba y aire. Nunca una caja. */
QGroupBox {{
    background-color: transparent;
    border: none;
    border-top: {tk['grosor_borde']}px solid {c['borde_suave']};
    margin-top: {tk['esp_xl']}px;
    padding: {tk['esp_l']}px 0 0 0;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 0;
    top: {tk['esp_s']}px;
    padding: 0;
    /* En tinta, no en gris: antes los títulos de sección se leían como
       etiquetas secundarias y no se veía dónde empieza cada bloque. */
    color: {c['texto']};
    font-size: {base + tk['tipo_subtitulo']}px;
    font-weight: 600;
    letter-spacing: 0;
}}

/* Chips: contorno fino, sin relleno. Informan sin competir. */
QLabel[rol="chip"] {{
    background-color: transparent;
    color: {c['texto_sec']};
    border: {tk['grosor_borde']}px solid {c['borde']};
    border-radius: {tk['radio_control']}px;
    padding: {tk['esp_xs'] - 1}px {tk['esp_s']}px;
    font-size: {base - tk['tipo_discreto']}px;
}}
QLabel[rol="punto"] {{
    font-size: {base + 10}px;
    color: {c['texto_disc']};
}}
QLabel[rol="punto"][estado="activo"] {{ color: {c['exito']}; }}
QLabel[rol="punto"][estado="inactivo"] {{ color: {c['texto_disc']}; }}
QLabel[rol="punto"][estado="aviso"] {{ color: {c['aviso']}; }}
QLabel[rol="punto"][estado="error"] {{ color: {c['error']}; }}

/* =============================================================== controles */
QPushButton {{
    background-color: {c['panel']};
    color: {c['texto']};
    border: {tk['grosor_borde']}px solid {c['borde']};
    border-radius: {tk['radio_boton']}px;
    padding: {tk['esp_s']}px {tk['esp_l']}px;
    min-height: {tk['alto_control']}px;
    font-size: {base}px;
}}
QPushButton:hover {{
    background-color: {c['panel_hover']};
    border-color: {c['texto_disc']};
}}
QPushButton:pressed {{
    background-color: {c['seleccion']};
}}
QPushButton:disabled {{
    color: {c['texto_disc']};
    background-color: transparent;
    border-color: {c['borde_suave']};
}}
/* El sello. Una sola acción por pantalla lleva el carmesí. */
QPushButton[rol="primario"] {{
    background-color: {c['acento']};
    color: {c['acento_texto']};
    border: none;
    font-weight: 600;
}}
QPushButton[rol="primario"]:hover {{ background-color: {c['acento_hover']}; }}
QPushButton[rol="primario"]:pressed {{ background-color: {c['acento_pulsado']}; }}
QPushButton[rol="primario"]:disabled {{
    background-color: {c['panel_alt']};
    color: {c['texto_disc']};
}}
QPushButton[rol="peligro"] {{
    background-color: transparent;
    color: {c['error']};
    border-color: {c['borde']};
}}
QPushButton[rol="peligro"]:hover {{
    background-color: {c['error']};
    color: #FFFFFF;
    border-color: {c['error']};
}}
QPushButton[rol="plano"] {{
    background-color: transparent;
    border: none;
    color: {c['acento']};
    padding: {tk['esp_xs']}px {tk['esp_s']}px;
    font-weight: 500;
}}
QPushButton[rol="plano"]:hover {{
    color: {c['acento_hover']};
    background-color: {c['acento_suave']};
    border-radius: {tk['radio_control']}px;
}}

/* Campos: hundidos en el papel, sin caja. Se reconocen por su tono. */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit {{
    background-color: {c['fondo_barra']};
    border: {tk['grosor_borde']}px solid {c['borde_suave']};
    border-radius: {tk['radio_campo']}px;
    padding: {tk['esp_s'] - 1}px {tk['esp_m'] - 2}px;
    min-height: {tk['alto_control']}px;
    color: {c['texto']};
    selection-background-color: {c['acento']};
    selection-color: #FFFFFF;
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QDateEdit:focus, QTimeEdit:focus {{
    border-color: {c['acento']};
}}
QLineEdit[rol="dato"], QComboBox[rol="dato"] {{
    font-family: {c['mono']};
}}
QComboBox::drop-down {{ border: none; width: {tk['esp_xl']}px; }}
QComboBox QAbstractItemView {{
    background-color: {c['panel']};
    color: {c['texto']};
    border: {tk['grosor_borde']}px solid {c['borde']};
    border-radius: {tk['radio_menu']}px;
    padding: {tk['esp_xs']}px;
    selection-background-color: {c['acento']};
    selection-color: #FFFFFF;
    outline: 0;
}}
QComboBox QAbstractItemView::item {{
    border-radius: {tk['radio_item']}px;
    padding: {tk['esp_xs'] + 1}px {tk['esp_s']}px;
    min-height: {tk['alto_control']}px;
}}

QCheckBox, QRadioButton {{
    spacing: {tk['esp_s']}px;
    color: {c['texto']};
}}
QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 1.5px solid {c['borde']};
    background-color: {c['fondo_barra']};
}}
QCheckBox::indicator {{ border-radius: {tk['radio_control'] - 3}px; }}
QRadioButton::indicator {{ border-radius: 8px; }}
QCheckBox::indicator:hover, QRadioButton::indicator:hover {{ border-color: {c['acento']}; }}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background-color: {c['acento']};
    border-color: {c['acento']};
}}
QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {{
    border-color: {c['borde_suave']};
    background-color: transparent;
}}

/* ================================================================== listas */
QListWidget, QTreeWidget, QTableWidget, QListView, QTreeView, QTableView {{
    background-color: transparent;
    border: none;
    border-radius: 0;
    padding: 0;
    color: {c['texto']};
    outline: 0;
}}
QListWidget::item, QTreeWidget::item, QListView::item, QTreeView::item {{
    border-radius: {tk['radio_item']}px;
    padding: {tk['esp_s']}px {tk['esp_m'] - 2}px;
    margin: 1px 0;
}}
QListWidget::item:hover, QTreeView::item:hover, QListView::item:hover {{
    background-color: {c['panel_hover']};
}}
QListWidget::item:selected, QTreeWidget::item:selected, QListView::item:selected,
QTreeView::item:selected, QListWidget::item:selected:active,
QTreeView::item:selected:active {{
    background-color: {c['seleccion']};
    color: {c['texto']};
}}
QHeaderView::section {{
    background-color: transparent;
    border: none;
    border-bottom: {tk['grosor_borde']}px solid {c['borde_suave']};
    padding: {tk['esp_s']}px {tk['esp_s']}px;
    color: {c['texto_sec']};
    font-weight: 600;
}}
QHeaderView::section:last {{ border-bottom-color: {c['borde_suave']}; }}

QPlainTextEdit, QTextEdit {{
    background-color: {c['fondo_barra']};
    border: {tk['grosor_borde']}px solid {c['borde_suave']};
    border-radius: {tk['radio_menu']}px;
    padding: {tk['esp_s']}px;
    color: {c['texto']};
    font-family: {c['mono']};
    font-size: {base - tk['tipo_pequeno']}px;
    selection-background-color: {c['acento']};
    selection-color: #FFFFFF;
}}

/* ============================================================== indicadores */
QProgressBar {{
    background-color: {c['borde_suave']};
    border: none;
    border-radius: 0;
    height: {tk['grosor_barra']}px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background-color: {c['acento']};
    border-radius: 0;
}}

QSlider::groove:horizontal {{
    height: {tk['esp_xs']}px;
    background: {c['borde_suave']};
    border-radius: 0;
}}
QSlider::sub-page:horizontal {{ background: {c['acento']}; border-radius: 0; }}
QSlider::handle:horizontal {{
    width: 14px;
    height: 14px;
    margin: -6px 0;
    border-radius: 7px;
    background: {c['panel']};
    border: 1px solid {c['borde']};
}}
QSlider::handle:horizontal:hover {{ border-color: {c['acento']}; }}

/* ============================================================ desplazamiento */
QScrollBar:vertical {{
    background: transparent;
    width: {tk['grosor_scroll']}px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {c['borde']};
    border-radius: {tk['grosor_scroll'] // 2}px;
    min-height: {tk['esp_xxl']}px;
}}
QScrollBar::handle:vertical:hover {{ background: {c['texto_disc']}; }}
QScrollBar:horizontal {{
    background: transparent;
    height: {tk['grosor_scroll']}px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {c['borde']};
    border-radius: {tk['grosor_scroll'] // 2}px;
    min-width: {tk['esp_xxl']}px;
}}
QScrollBar::handle:horizontal:hover {{ background: {c['texto_disc']}; }}
QScrollBar::add-line, QScrollBar::sub-line,
QScrollBar::add-page, QScrollBar::sub-page {{
    background: none;
    border: none;
    height: 0;
    width: 0;
}}

/* =================================================================== raíl */
/* La barra lateral es el raíl: un escalón por detrás del papel, con el sello
   carmesí marcando dónde estás. Sin píldoras de color, sin iconos blancos. */
QWidget#panelLateral {{
    background-color: {c['fondo_lateral']};
    border-right: {tk['grosor_borde']}px solid {c['borde_suave']};
}}
QListWidget[rol="lateral"] {{
    background-color: transparent;
    border: none;
    border-radius: 0;
    padding: {tk['esp_l']}px 0;
}}
QListWidget[rol="lateral"]::item {{
    border-radius: 0;
    border-left: {tk['grosor_marcador']}px solid transparent;
    padding: {tk['esp_s'] + 1}px {tk['esp_m']}px {tk['esp_s'] + 1}px {tk['esp_l']}px;
    margin: 0;
    color: {c['texto_sec']};
    font-weight: 500;
}}
QListWidget[rol="lateral"]::item:hover {{
    color: {c['texto']};
    background-color: {c['panel_hover']};
}}
QListWidget[rol="lateral"]::item:selected {{
    background-color: transparent;
    color: {c['texto']};
    font-weight: 600;
    border-left: {tk['grosor_marcador']}px solid {c['acento']};
}}

/* ================================================================= lengüetas */
/* Subrayado, no píldora: más cerca de una herramienta que de una tarjeta. */
QTabWidget::pane {{
    border: none;
    background: transparent;
}}
QTabBar {{ qproperty-drawBase: 0; }}
QTabBar::tab {{
    background: transparent;
    color: {c['texto_sec']};
    padding: {tk['esp_s']}px 0;
    margin-right: {tk['esp_xl']}px;
    border: none;
    border-bottom: 2px solid transparent;
    border-radius: 0;
    font-size: {base}px;
}}
QTabBar::tab:selected {{
    color: {c['texto']};
    font-weight: 600;
    border-bottom: 2px solid {c['acento']};
}}
QTabBar::tab:hover:!selected {{
    color: {c['texto']};
    border-bottom-color: {c['borde']};
}}

/* ========================================================= barra de estado */
QStatusBar {{
    background: transparent;
    color: {c['texto_sec']};
    border-top: {tk['grosor_borde']}px solid {c['borde_suave']};
    font-size: {base - tk['tipo_pequeno']}px;
}}
QStatusBar::item {{ border: none; }}

/* =================================================================== menús */
QMenu {{
    background-color: {c['panel']};
    border: {tk['grosor_borde']}px solid {c['borde']};
    border-radius: {tk['radio_menu']}px;
    padding: {tk['esp_xs']}px;
}}
QMenu::item {{
    border-radius: {tk['radio_item']}px;
    padding: {tk['esp_s'] - 2}px {tk['esp_xl']}px {tk['esp_s'] - 2}px {tk['esp_s']}px;
}}
QMenu::item:selected {{
    background-color: {c['acento_suave']};
    color: {c['texto']};
}}
QMenu::separator {{
    height: 1px;
    background: {c['borde_suave']};
    margin: {tk['esp_xs']}px {tk['esp_s']}px;
}}
QMenuBar {{ background: transparent; }}
QMenuBar::item {{
    background: transparent;
    padding: {tk['esp_xs'] + 1}px {tk['esp_s']}px;
    border-radius: {tk['radio_control'] - 2}px;
}}
QMenuBar::item:selected {{ background: {c['panel_hover']}; }}

/* ================================================================ diálogos */
QMessageBox {{ background-color: {c['fondo']}; }}
QMessageBox QLabel {{ color: {c['texto']}; font-size: {base}px; }}
QMessageBox QPushButton {{ min-width: 84px; }}
QProgressDialog {{ background-color: {c['fondo']}; }}
QProgressDialog QLabel {{ color: {c['texto']}; }}
QScrollArea {{ background: transparent; border: none; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}
QSplitter::handle {{ background: {c['borde_suave']}; }}
QToolBar {{ background: transparent; border: none; spacing: {tk['esp_s']}px; }}

/* Velo que cubre el contenido cuando el raíl flota encima, en ventanas
   estrechas. Al pulsarlo se cierra el menú. */
QWidget#veloLateral {{
    background-color: rgba(36, 28, 27, 0.32);
}}
"""


def hoja_estilo_switch(nombre: str = "auto") -> dict:
    """Colores que necesita el interruptor dibujado a mano (clase Switch)."""
    c = paleta(_resolver_tema(nombre))
    return {
        "on": c["acento"],
        "off": "#4A4042" if c["nombre"] == "oscuro" else "#CFC5BF",
        "on_disabled": "#3B2A2E" if c["nombre"] == "oscuro" else "#EBD9DD",
        "off_disabled": "#302A2B" if c["nombre"] == "oscuro" else "#E4DCD6",
        "thumb": "#FFFFFF",
        "texto": c["texto"],
        "texto_disabled": c["texto_disc"],
    }


def _resolver_tema(nombre: str) -> str:
    """Traduce 'auto' al tema real del sistema."""
    if nombre == "auto":
        return tema_del_sistema()
    return "oscuro" if nombre == "oscuro" else "claro"
