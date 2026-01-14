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
        self.tema_actual = "azul_oscuro"
    
    def _cargar_temas_predefinidos(self):
        """Carga los temas predefinidos."""
        
        # Tema Azul Oscuro
        self.temas["azul_oscuro"] = Tema("Azul Oscuro", {
            'fondo_1': '#1a1a2e', 'fondo_2': '#16213e', 'fondo_panel': '#16213e',
            'fondo_oscuro': '#0a1929', 'borde': '#0f3460',
            'tab_inactivo_1': '#0f3460', 'tab_inactivo_2': '#0a2647',
            'acento_1': '#00d4ff', 'acento_2': '#0084ff',
            'acento_hover': '#00e1ff', 'acento_pressed': '#0066cc',
            'hover_1': '#16537e', 'hover_2': '#113f67',
            'texto': '#e0e0e0', 'texto_secundario': '#b0b0c0',
            'texto_deshabilitado': '#666677',
            'deshabilitado_1': '#2a2a3e', 'deshabilitado_2': '#1a1a2e'
        })
        
        # Tema Verde Oscuro
        self.temas["verde_oscuro"] = Tema("Verde Oscuro", {
            'fondo_1': '#1a2e1a', 'fondo_2': '#16213e', 'fondo_panel': '#1e2e1e',
            'fondo_oscuro': '#0a190a', 'borde': '#0f6034',
            'tab_inactivo_1': '#0f4034', 'tab_inactivo_2': '#0a2720',
            'acento_1': '#4CAF50', 'acento_2': '#45a049',
            'acento_hover': '#66BB6A', 'acento_pressed': '#2e7d32',
            'hover_1': '#16537e', 'hover_2': '#113f67',
            'texto': '#e0e0e0', 'texto_secundario': '#b0c0b0',
            'texto_deshabilitado': '#666677',
            'deshabilitado_1': '#2a3e2a', 'deshabilitado_2': '#1a2e1a'
        })
        
        # Tema Púrpura
        self.temas["purpura"] = Tema("Púrpura", {
            'fondo_1': '#2e1a2e', 'fondo_2': '#21163e', 'fondo_panel': '#2e1e2e',
            'fondo_oscuro': '#190a19', 'borde': '#60347e',
            'tab_inactivo_1': '#40347e', 'tab_inactivo_2': '#272047',
            'acento_1': '#9C27B0', 'acento_2': '#7B1FA2',
            'acento_hover': '#AB47BC', 'acento_pressed': '#6A1B9A',
            'hover_1': '#537e7e', 'hover_2': '#3f6767',
            'texto': '#e0e0e0', 'texto_secundario': '#c0b0c0',
            'texto_deshabilitado': '#776677',
            'deshabilitado_1': '#3e2a3e', 'deshabilitado_2': '#2e1a2e'
        })
        
        # Tema Naranja
        self.temas["naranja"] = Tema("Naranja", {
            'fondo_1': '#2e1f1a', 'fondo_2': '#3e2116', 'fondo_panel': '#2e2116',
            'fondo_oscuro': '#19100a', 'borde': '#7e4034',
            'tab_inactivo_1': '#603420', 'tab_inactivo_2': '#472720',
            'acento_1': '#FF9800', 'acento_2': '#F57C00',
            'acento_hover': '#FFB74D', 'acento_pressed': '#EF6C00',
            'hover_1': '#7e5316', 'hover_2': '#673f11',
            'texto': '#e0e0e0', 'texto_secundario': '#c0b0a0',
            'texto_deshabilitado': '#776666',
            'deshabilitado_1': '#3e2e2a', 'deshabilitado_2': '#2e1f1a'
        })
        
        # Tema Gris
        self.temas["gris"] = Tema("Gris", {
            'fondo_1': '#2b2b2b', 'fondo_2': '#1e1e1e', 'fondo_panel': '#2d2d2d',
            'fondo_oscuro': '#1a1a1a', 'borde': '#505050',
            'tab_inactivo_1': '#404040', 'tab_inactivo_2': '#353535',
            'acento_1': '#757575', 'acento_2': '#616161',
            'acento_hover': '#9E9E9E', 'acento_pressed': '#424242',
            'hover_1': '#505050', 'hover_2': '#454545',
            'texto': '#ffffff', 'texto_secundario': '#cccccc',
            'texto_deshabilitado': '#999999',
            'deshabilitado_1': '#555555', 'deshabilitado_2': '#2b2b2b'
        })
    
    def obtener_tema(self, nombre: str):
        """Obtiene un tema por nombre."""
        return self.temas.get(nombre, self.temas["azul_oscuro"])
    
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
