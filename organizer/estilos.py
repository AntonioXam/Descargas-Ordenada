#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sistema de estilos tipo Apple para DescargasOrdenadas.

Un único punto de verdad para la apariencia de la aplicación:

- Paleta clara y oscura inspirada en macOS (System Colors).
- Tipografía nativa de cada sistema (San Francisco, Segoe UI Variable, Inter...).
- Componentes con esquinas redondeadas, tarjetas, separadores finos y estados
  de hover/pressed discretos.
- Adaptación automática al tema del sistema si no hay preferencia guardada.

Cualquier widget puede marcar su rol con ``setProperty("rol", "...")`` para
recibir el estilo adecuado (tarjeta, titulo, subtitulo, primario...).
"""

from __future__ import annotations

import sys


# --------------------------------------------------------------------------
# Paletas
# --------------------------------------------------------------------------

PALETA_CLARA = {
    "nombre": "claro",
    "fondo": "#F2F2F7",
    "fondo_barra": "#ECECEF",
    "fondo_lateral": "#E7E7EB",
    "panel": "#FFFFFF",
    "panel_alt": "#F7F7F9",
    "panel_hover": "#EFEFF4",
    "seleccion": "#E4EBF8",
    "borde": "#D6D6DC",
    "borde_suave": "#E4E4EA",
    "texto": "#1D1D1F",
    "texto_sec": "#6E6E73",
    "texto_disc": "#A9A9B0",
    "acento": "#0071E3",
    "acento_hover": "#0077ED",
    "acento_pulsado": "#0062C4",
    "acento_suave": "#E1EEFB",
    "acento_texto": "#FFFFFF",
    "exito": "#248A3D",
    "aviso": "#B25000",
    "error": "#D70015",
    "sombra": "rgba(0, 0, 0, 0.10)",
    "mono": "'SF Mono', 'Menlo', 'Consolas', 'DejaVu Sans Mono', monospace",
}

PALETA_OSCURA = {
    "nombre": "oscuro",
    "fondo": "#161618",
    "fondo_barra": "#1C1C1E",
    "fondo_lateral": "#1A1A1C",
    "panel": "#242426",
    "panel_alt": "#2C2C2E",
    "panel_hover": "#333336",
    "seleccion": "#2C3B52",
    "borde": "#3A3A3D",
    "borde_suave": "#2E2E31",
    "texto": "#F5F5F7",
    "texto_sec": "#A1A1A6",
    "texto_disc": "#66666C",
    "acento": "#0A84FF",
    "acento_hover": "#3D9BFF",
    "acento_pulsado": "#0060DF",
    "acento_suave": "#1D344E",
    "acento_texto": "#FFFFFF",
    "exito": "#30D158",
    "aviso": "#FF9F0A",
    "error": "#FF453A",
    "sombra": "rgba(0, 0, 0, 0.45)",
    "mono": "'SF Mono', 'Menlo', 'Consolas', 'DejaVu Sans Mono', monospace",
}


# --------------------------------------------------------------------------
# Tipografía
# --------------------------------------------------------------------------

def familias_sistema() -> str:
    """Devuelve la lista de familias tipográficas nativas del sistema."""
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


def colores_translucidos(nombre: str, transparencia: float = 0.82) -> dict:
    """Convierte los colores base a versiones con alfa (rgba).

    Se usa cuando la ventana tiene un efecto nativo detrás (vibrancy en macOS,
    Mica en Windows): el fondo del contenido se vuelve semitransparente para
    dejar ver el material del sistema, manteniendo los paneles legibles.

    Args:
        nombre: 'claro' u 'oscuro'.
        transparencia: opacidad de los fondos (1.0 = opaco).
    """
    c = dict(paleta(nombre))
    alpha = max(0.0, min(1.0, transparencia))

    def rgba(color_hex: str, alfa: float) -> str:
        color_hex = color_hex.lstrip("#")
        if len(color_hex) == 3:
            color_hex = "".join(ch * 2 for ch in color_hex)
        r = int(color_hex[0:2], 16)
        g = int(color_hex[2:4], 16)
        b = int(color_hex[4:6], 16)
        return f"rgba({r}, {g}, {b}, {alfa:.3f})"

    # Fondos con el alfa indicado; los paneles un poco más opacos para que el
    # texto siempre se lea bien.
    c["fondo"] = rgba(c["fondo"], alpha)
    c["fondo_lateral"] = rgba(c["fondo_lateral"], min(1.0, alpha + 0.08))
    c["panel"] = rgba(c["panel"], min(1.0, alpha + 0.12))
    c["panel_alt"] = rgba(c["panel_alt"], min(1.0, alpha + 0.10))
    c["panel_hover"] = rgba(c["panel_hover"], min(1.0, alpha + 0.10))
    return c


def hoja_estilo(nombre: str = "auto", transparencia: float = 1.0) -> str:
    """Genera la hoja de estilo Qt completa para la paleta indicada.

    Args:
        nombre: 'claro', 'oscuro' o 'auto' (usar el tema del sistema).
        transparencia: opacidad de los fondos (menor que 1.0 activa el efecto
            translúcido, pensado para cuando hay un material nativo detrás).
    """
    if nombre == "auto":
        nombre = tema_del_sistema()
    if transparencia < 1.0:
        c = colores_translucidos(nombre, transparencia)
    else:
        c = paleta(nombre)
    c = dict(c)
    # Propagar el tema a los elementos que lo necesitan
    c.setdefault("nombre", "oscuro" if nombre == "oscuro" else "claro")
    fuente = familias_sistema()
    base = tamano_fuente_base()

    return f"""
/* ---------------------------------------------------------------- base */
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
    background-color: {c['panel']};
    color: {c['texto']};
    border: 1px solid {c['borde']};
    border-radius: 8px;
    padding: 6px 9px;
    font-size: {base - 1}px;
}}

/* ---------------------------------------------------------- tipografía */
QLabel[rol="titulo"] {{
    font-size: {base + 9}px;
    font-weight: 700;
    color: {c['texto']};
    letter-spacing: -0.2px;
}}
QLabel[rol="subtitulo"] {{
    font-size: {base + 1}px;
    color: {c['texto_sec']};
}}
QLabel[rol="seccion"] {{
    font-size: {base}px;
    font-weight: 600;
    color: {c['texto_sec']};
    letter-spacing: 0.2px;
    padding: 2px 0;
}}
QLabel[rol="etiqueta"] {{
    font-size: {base}px;
    color: {c['texto']};
}}
QLabel[rol="secundaria"] {{
    font-size: {base - 1}px;
    color: {c['texto_sec']};
}}
QLabel[rol="discreta"] {{
    font-size: {base - 2}px;
    color: {c['texto_disc']};
}}
QLabel[rol="exito"] {{ color: {c['exito']}; font-weight: 600; }}
QLabel[rol="aviso"] {{ color: {c['aviso']}; font-weight: 600; }}
QLabel[rol="error"] {{ color: {c['error']}; font-weight: 600; }}

/* ------------------------------------------------------------- tarjetas */
QFrame[rol="tarjeta"] {{
    background-color: {c['panel']};
    border: 1px solid {c['borde_suave']};
    border-radius: 16px;
}}
QFrame[rol="tarjeta_destacada"] {{
    background-color: {c['panel']};
    border: 1px solid {c['acento']};
    border-radius: 16px;
}}
QLabel[rol="punto"] {{
    font-size: {base + 10}px;
    color: {c['texto_disc']};
}}
QLabel[rol="punto"][estado="activo"] {{
    color: {c['exito']};
}}
QLabel[rol="punto"][estado="inactivo"] {{
    color: {c['texto_disc']};
}}
QLabel[rol="punto"][estado="aviso"] {{
    color: {c['aviso']};
}}
QLabel[rol="punto"][estado="error"] {{
    color: {c['error']};
}}
QLabel[rol="chip"] {{
    background-color: {c['panel_alt']};
    color: {c['texto_sec']};
    border: 1px solid {c['borde_suave']};
    border-radius: 10px;
    padding: 4px 10px;
    font-size: {base - 1}px;
}}
QFrame[rol="separador"] {{
    background-color: {c['borde_suave']};
    border: none;
    max-height: 1px;
    min-height: 1px;
}}
QGroupBox {{
    background-color: {c['panel']};
    border: 1px solid {c['borde_suave']};
    border-radius: 16px;
    margin-top: 14px;
    padding: 22px 16px 14px 16px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 16px;
    top: 4px;
    padding: 0 4px;
    color: {c['texto_sec']};
    font-size: {base - 1}px;
    font-weight: 600;
}}

/* ------------------------------------------------------------- botones */
QPushButton {{
    background-color: {c['panel']};
    color: {c['texto']};
    border: 1px solid {c['borde']};
    border-radius: 10px;
    padding: 8px 16px;
    min-height: 20px;
    font-size: {base}px;
}}
QPushButton:hover {{
    background-color: {c['panel_hover']};
    border-color: {c['acento']};
}}
QPushButton:pressed {{
    background-color: {c['seleccion']};
}}
QPushButton:disabled {{
    color: {c['texto_disc']};
    background-color: {c['panel_alt']};
    border-color: {c['borde_suave']};
}}
QPushButton[rol="primario"] {{
    background-color: {c['acento']};
    color: {c['acento_texto']};
    border: none;
    font-weight: 600;
    padding: 9px 18px;
}}
QPushButton[rol="primario"]:hover {{ background-color: {c['acento_hover']}; }}
QPushButton[rol="primario"]:pressed {{ background-color: {c['acento_pulsado']}; }}
QPushButton[rol="primario"]:disabled {{
    background-color: {c['panel_alt']};
    color: {c['texto_disc']};
}}
QPushButton[rol="peligro"] {{
    color: {c['error']};
    border-color: {c['borde']};
}}
QPushButton[rol="peligro"]:hover {{
    background-color: {c['error']};
    color: #FFFFFF;
    border-color: {c['error']};
}}
QPushButton[rol="plano"] {{
    background: transparent;
    border: none;
    color: {c['acento']};
    padding: 6px 10px;
}}
QPushButton[rol="plano"]:hover {{ color: {c['acento_hover']}; }}

/* --------------------------------------------------------------- campos */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit {{
    background-color: {c['panel']};
    border: 1px solid {c['borde']};
    border-radius: 10px;
    padding: 7px 12px;
    min-height: 20px;
    selection-background-color: {c['acento']};
    selection-color: #FFFFFF;
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QDateEdit:focus, QTimeEdit:focus {{
    border: 1px solid {c['acento']};
}}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background-color: {c['panel']};
    color: {c['texto']};
    border: 1px solid {c['borde']};
    border-radius: 10px;
    padding: 4px;
    selection-background-color: {c['acento']};
    selection-color: #FFFFFF;
    outline: 0;
}}
QComboBox QAbstractItemView::item {{
    border-radius: 6px;
    padding: 5px 8px;
    min-height: 20px;
}}

/* ------------------------------------------------------ checks y radios */
QCheckBox, QRadioButton {{
    spacing: 9px;
    color: {c['texto']};
}}
QCheckBox::indicator, QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border: 1.5px solid {c['borde']};
    background-color: {c['panel']};
}}
QCheckBox::indicator {{ border-radius: 5px; }}
QRadioButton::indicator {{ border-radius: 10px; }}
QCheckBox::indicator:hover, QRadioButton::indicator:hover {{ border-color: {c['acento']}; }}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background-color: {c['acento']};
    border-color: {c['acento']};
}}
QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {{
    border-color: {c['borde_suave']};
    background-color: {c['panel_alt']};
}}

/* ------------------------------------------------------------ listas */
QListWidget, QTreeWidget, QTableWidget, QListView, QTreeView, QTableView {{
    background-color: {c['panel']};
    border: 1px solid {c['borde_suave']};
    border-radius: 12px;
    padding: 4px;
    color: {c['texto']};
    outline: 0;
}}
QListWidget::item, QTreeWidget::item, QListView::item, QTreeView::item {{
    border-radius: 7px;
    padding: 6px 8px;
    margin: 1px 2px;
}}
QListWidget::item:hover, QTreeView::item:hover, QListView::item:hover {{
    background-color: {c['panel_hover']};
}}
QListWidget::item:selected, QTreeWidget::item:selected, QListView::item:selected, QTreeView::item:selected,
QListWidget::item:selected:active, QTreeView::item:selected:active {{
    background-color: {c['acento']};
    color: #FFFFFF;
}}
QHeaderView::section {{
    background-color: transparent;
    border: none;
    border-bottom: 1px solid {c['borde_suave']};
    padding: 6px 8px;
    color: {c['texto_sec']};
    font-weight: 600;
}}

/* ------------------------------------------------------------ texto */
QPlainTextEdit, QTextEdit {{
    background-color: {c['fondo']};
    border: 1px solid {c['borde_suave']};
    border-radius: 12px;
    padding: 9px;
    color: {c['texto']};
    font-family: {c['mono']};
    font-size: {base - 1}px;
    selection-background-color: {c['acento']};
    selection-color: #FFFFFF;
}}

/* --------------------------------------------------------- progreso */
QProgressBar {{
    background-color: {c['panel_alt']};
    border: none;
    border-radius: 3px;
    height: 6px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background-color: {c['acento']};
    border-radius: 3px;
}}

/* ------------------------------------------------------------- slider */
QSlider::groove:horizontal {{
    height: 4px;
    background: {c['panel_alt']};
    border-radius: 2px;
}}
QSlider::sub-page:horizontal {{ background: {c['acento']}; border-radius: 2px; }}
QSlider::handle:horizontal {{
    width: 18px;
    height: 18px;
    margin: -7px 0;
    border-radius: 9px;
    background: #FFFFFF;
    border: 0.5px solid {c['borde']};
}}
QSlider::handle:horizontal:hover {{ background: {c['panel']}; }}

/* --------------------------------------------------------- scrollbars */
QScrollBar:vertical {{
    background: transparent;
    width: 11px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: {c['borde']};
    border-radius: 5px;
    min-height: 32px;
}}
QScrollBar::handle:vertical:hover {{ background: {c['texto_disc']}; }}
QScrollBar:horizontal {{
    background: transparent;
    height: 11px;
    margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background: {c['borde']};
    border-radius: 5px;
    min-width: 32px;
}}
QScrollBar::handle:horizontal:hover {{ background: {c['texto_disc']}; }}
QScrollBar::add-line, QScrollBar::sub-line,
QScrollBar::add-page, QScrollBar::sub-page {{
    background: none;
    border: none;
    height: 0;
    width: 0;
}}

/* ------------------------------------------------------ barra lateral */
QWidget#panelLateral {{
    background-color: {c['fondo_lateral']};
    border-right: 1px solid {c['borde_suave']};
}}
QListWidget[rol="lateral"] {{
    background-color: transparent;
    border: none;
    border-radius: 0;
    padding: 12px 8px;
}}
QListWidget[rol="lateral"]::item {{
    border-radius: 9px;
    padding: 9px 12px;
    margin: 2px 4px;
    color: {c['texto']};
    font-weight: 500;
}}
QListWidget[rol="lateral"]::item:hover {{
    background-color: rgba(120, 120, 128, 0.14);
}}
QListWidget[rol="lateral"]::item:selected {{
    background-color: {c['acento']};
    color: #FFFFFF;
    font-weight: 600;
}}

/* -------------------------------------------------------- barra tabs */
QTabWidget::pane {{
    border: none;
    background: transparent;
}}
QTabBar {{ qproperty-drawBase: 0; }}
QTabBar::tab {{
    background: transparent;
    color: {c['texto_sec']};
    padding: 6px 12px;
    margin-right: 4px;
    border-radius: 8px;
    font-size: {base - 1}px;
}}
QTabBar::tab:selected {{
    background: {c['acento']};
    color: #FFFFFF;
    font-weight: 600;
}}
QTabBar::tab:hover:!selected {{
    color: {c['texto']};
    background: {c['panel_hover']};
}}

/* -------------------------------------------------------- status y menú */
QStatusBar {{
    background: transparent;
    color: {c['texto_sec']};
    border-top: 1px solid {c['borde_suave']};
}}
QStatusBar::item {{ border: none; }}
QMenu {{
    background-color: {c['panel']};
    border: 1px solid {c['borde']};
    border-radius: 10px;
    padding: 5px;
}}
QMenu::item {{
    border-radius: 7px;
    padding: 6px 22px 6px 12px;
}}
QMenu::item:selected {{
    background-color: {c['acento']};
    color: #FFFFFF;
}}
QMenu::separator {{
    height: 1px;
    background: {c['borde_suave']};
    margin: 4px 8px;
}}
QMenuBar {{ background: transparent; }}
QMenuBar::item {{
    background: transparent;
    padding: 5px 10px;
    border-radius: 6px;
}}
QMenuBar::item:selected {{ background: {c['panel_hover']}; }}

/* ---------------------------------------------------- diálogos y misc */
QMessageBox {{ background-color: {c['fondo']}; }}
QMessageBox QLabel {{ color: {c['texto']}; font-size: {base}px; }}
QMessageBox QPushButton {{ min-width: 84px; }}
QProgressDialog {{ background-color: {c['fondo']}; }}
QProgressDialog QLabel {{ color: {c['texto']}; }}
QScrollArea {{ background: transparent; border: none; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}
QSplitter::handle {{ background: {c['borde_suave']}; }}
QToolBar {{ background: transparent; border: none; spacing: 6px; }}
"""


def hoja_estilo_switch(nombre: str = "auto") -> dict:
    """Colores que necesita el interruptor dibujado a mano (clase Switch)."""
    c = paleta("oscuro" if nombre == "auto" and tema_del_sistema() == "oscuro" else ("oscuro" if nombre == "oscuro" else "claro"))
    return {
        "on": c["acento"],
        "off": "#48484A" if c["nombre"] == "oscuro" else "#D1D1D6",
        "on_disabled": "#3A3A3C" if c["nombre"] == "oscuro" else "#E4E4EA",
        "off_disabled": "#2E2E31" if c["nombre"] == "oscuro" else "#EDEDF2",
        "thumb": "#FFFFFF",
        "texto": c["texto"],
        "texto_disabled": c["texto_disc"],
    }
