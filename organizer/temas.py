#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sistema de temas personalizables para DescargasOrdenadas v3.1"""

import logging

logger = logging.getLogger('organizador.temas')

class Tema:
    """Clase que representa un tema visual."""
    
    def __init__(self, nombre: str, colores: dict):
        self.nombre = nombre
        self.colores = colores
    
    def obtener_stylesheet(self) -> str:
        """Genera el stylesheet CSS para este tema."""
        c = self.colores
        
        return f"""
            QMainWindow {{ 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {c['fondo_1']}, stop:1 {c['fondo_2']});
                color: {c['texto']};
            }}
            QTabWidget::pane {{
                border: 2px solid {c['borde']};
                background-color: {c['fondo_panel']};
                border-radius: 10px;
                margin-top: 8px;
                padding: 5px;
            }}
            QTabBar::tab {{
                padding: 14px 24px;
                margin-right: 4px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {c['tab_inactivo_1']}, stop:1 {c['tab_inactivo_2']});
                border: 1px solid {c['fondo_1']};
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-weight: bold;
                color: {c['texto_secundario']};
                font-size: 13px;
                min-width: 100px;
            }}
            QTabBar::tab:selected {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {c['acento_1']}, stop:1 {c['acento_2']});
                color: {c['texto']};
                border-bottom: 3px solid {c['acento_1']};
                padding-bottom: 11px;
            }}
            QTabBar::tab:hover:!selected {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {c['hover_1']}, stop:1 {c['hover_2']});
                color: {c['texto']};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {c['borde']};
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {c['fondo_1']}, stop:1 {c['fondo_panel']});
                color: {c['texto']};
                font-size: 14px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px 0 10px;
                color: {c['acento_1']};
                background-color: transparent;
                font-weight: bold;
            }}
            QCheckBox {{
                spacing: 10px;
                color: {c['texto']};
                font-size: 13px;
                padding: 5px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 5px;
                border: 2px solid {c['borde']};
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {c['fondo_panel']}, stop:1 {c['tab_inactivo_2']});
            }}
            QCheckBox::indicator:checked {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {c['acento_1']}, stop:1 {c['acento_2']});
                border-color: {c['acento_1']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {c['acento_1']};
            }}
            QLabel {{
                color: {c['texto']};
                font-size: 13px;
            }}
            QListWidget {{
                border: 2px solid {c['borde']};
                border-radius: 8px;
                background-color: {c['fondo_oscuro']};
                color: {c['texto']};
                padding: 5px;
                selection-background-color: {c['acento_1']};
                selection-color: #000000;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
                margin: 2px 0;
            }}
            QListWidget::item:hover {{
                background-color: {c['fondo_panel']};
            }}
            QTextEdit, QPlainTextEdit {{
                border: 2px solid {c['borde']};
                border-radius: 8px;
                background-color: {c['fondo_oscuro']};
                color: {c['texto']};
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }}
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {c['acento_1']}, stop:1 {c['acento_2']});
                color: white;
                border: none;
                padding: 14px 24px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 13px;
                min-height: 18px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {c['acento_hover']}, stop:1 {c['acento_1']});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {c['acento_2']}, stop:1 {c['acento_pressed']});
            }}
            QPushButton:disabled {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {c['deshabilitado_1']}, stop:1 {c['deshabilitado_2']});
                color: {c['texto_deshabilitado']};
            }}
            QComboBox {{
                border: 2px solid {c['borde']};
                border-radius: 6px;
                padding: 8px 12px;
                background-color: {c['fondo_oscuro']};
                color: {c['texto']};
                font-size: 13px;
            }}
            QComboBox:hover {{
                border-color: {c['acento_1']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {c['fondo_oscuro']};
                color: {c['texto']};
                selection-background-color: {c['acento_1']};
            }}
            QProgressBar {{
                border: 2px solid {c['borde']};
                border-radius: 8px;
                background-color: {c['fondo_oscuro']};
                color: {c['texto']};
                height: 24px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {c['acento_1']}, stop:1 {c['acento_hover']});
                border-radius: 6px;
            }}
        """

class GestorTemas:
    """Gestor de temas visuales."""
    
    def __init__(self):
        self.temas = {}
        self._cargar_temas_predefinidos()
        self.tema_actual = "minimal_oscuro"
    
    def _cargar_temas_predefinidos(self):
        """Carga los temas predefinidos (solo paleta minimalista)."""

        # Tema Minimal Claro (estilo Apple)
        self.temas["minimal_claro"] = Tema("Minimal Claro", {
            'fondo_1': '#F5F5F7', 'fondo_2': '#F5F5F7', 'fondo_panel': '#FFFFFF',
            'fondo_oscuro': '#FFFFFF', 'borde': '#D2D2D7',
            'tab_inactivo_1': '#E8E8ED', 'tab_inactivo_2': '#E8E8ED',
            'acento_1': '#0071E3', 'acento_2': '#0071E3',
            'acento_hover': '#0077ED', 'acento_pressed': '#0068D6',
            'hover_1': '#EBEBED', 'hover_2': '#EBEBED',
            'texto': '#1D1D1F', 'texto_secundario': '#6E6E73',
            'texto_deshabilitado': '#AEAEB2',
            'deshabilitado_1': '#E8E8ED', 'deshabilitado_2': '#E8E8ED'
        })

        # Tema Minimal Oscuro (estilo Apple)
        self.temas["minimal_oscuro"] = Tema("Minimal Oscuro", {
            'fondo_1': '#1C1C1E', 'fondo_2': '#1C1C1E', 'fondo_panel': '#2C2C2E',
            'fondo_oscuro': '#2C2C2E', 'borde': '#38383D',
            'tab_inactivo_1': '#2C2C2E', 'tab_inactivo_2': '#2C2C2E',
            'acento_1': '#0A84FF', 'acento_2': '#0A84FF',
            'acento_hover': '#409CFF', 'acento_pressed': '#0060DF',
            'hover_1': '#3A3A3C', 'hover_2': '#3A3A3C',
            'texto': '#F5F5F7', 'texto_secundario': '#98989D',
            'texto_deshabilitado': '#636366',
            'deshabilitado_1': '#2C2C2E', 'deshabilitado_2': '#2C2C2E'
        })

    def obtener_tema(self, nombre: str):
        """Obtiene un tema por nombre."""
        return self.temas.get(nombre, self.temas["minimal_oscuro"])
    
    def obtener_nombres_temas(self) -> list:
        """Obtiene lista de nombres de temas."""
        return list(self.temas.keys())
    
    def establecer_tema_actual(self, nombre: str):
        """Establece el tema actual."""
        if nombre in self.temas:
            self.tema_actual = nombre
    
    def obtener_tema_actual(self):
        """Obtiene el tema actual."""
        return self.obtener_tema(self.tema_actual)

# Instancia global
_gestor_temas_global = None

def obtener_gestor_temas():
    """Obtiene la instancia global del gestor de temas."""
    global _gestor_temas_global
    if _gestor_temas_global is None:
        _gestor_temas_global = GestorTemas()
    return _gestor_temas_global
