#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gestor de configuración portable para DescargasOrdenadas v3.1"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger('organizador.portable_config')

class ConfigPortable:
    """Gestor de configuración portable."""
    
    def __init__(self, nombre_app="DescargasOrdenadas"):
        self.nombre_app = nombre_app
        self._config = {}
        self._config_path = self._obtener_ruta_config()
        self._cargar_config()
    
    def _obtener_ruta_config(self) -> Path:
        """Obtiene la ruta del archivo de configuración."""
        if getattr(sys, 'frozen', False):
            base_dir = Path(sys.executable).parent
        else:
            base_dir = Path(__file__).parent.parent
        
        config_dir = base_dir / ".config"
        config_dir.mkdir(exist_ok=True)
        return config_dir / f"{self.nombre_app.lower()}_config.json"
    
    def _cargar_config(self):
        """Carga la configuración desde el archivo."""
        try:
            if self._config_path.exists():
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                self._config = self._obtener_config_por_defecto()
                self._guardar_config()
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            self._config = self._obtener_config_por_defecto()
    
    def _guardar_config(self):
        """Guarda la configuración en el archivo."""
        try:
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
    
    def _obtener_config_por_defecto(self) -> Dict[str, Any]:
        """Obtiene la configuración por defecto."""
        return {
            "tema": "azul_oscuro",
            "notificaciones_habilitadas": True,
            "auto_organizacion": False,
            "usar_subcarpetas": True,
            "organizar_recursivo": False,
            "patron_fechas": "YYYY/MM-Mes",
            "organizacion_fechas_activa": False,
            "ultima_carpeta_usada": None,
            "ventana": {"ancho": 1000, "alto": 700, "maximizada": False},
            "ai": {"nivel_confianza": 60}
        }
    
    def obtener(self, clave: str, valor_por_defecto: Any = None) -> Any:
        """Obtiene un valor de configuración."""
        try:
            if '.' in clave:
                partes = clave.split('.')
                valor = self._config
                for parte in partes:
                    valor = valor.get(parte, {})
                return valor if valor != {} else valor_por_defecto
            else:
                return self._config.get(clave, valor_por_defecto)
        except Exception:
            return valor_por_defecto
    
    def establecer(self, clave: str, valor: Any):
        """Establece un valor de configuración."""
        try:
            if '.' in clave:
                partes = clave.split('.')
                config_actual = self._config
                for parte in partes[:-1]:
                    if parte not in config_actual:
                        config_actual[parte] = {}
                    config_actual = config_actual[parte]
                config_actual[partes[-1]] = valor
            else:
                self._config[clave] = valor
            
            self._guardar_config()
        except Exception as e:
            logger.error(f"Error estableciendo configuración {clave}: {e}")
    
    def obtener_todas(self) -> Dict[str, Any]:
        """Obtiene toda la configuración."""
        return self._config.copy()
    
    def restablecer(self):
        """Restablece la configuración."""
        self._config = self._obtener_config_por_defecto()
        self._guardar_config()

# Instancia global
_config_global = None

def obtener_config() -> ConfigPortable:
    """Obtiene la instancia global de configuración."""
    global _config_global
    if _config_global is None:
        _config_global = ConfigPortable()
    return _config_global
