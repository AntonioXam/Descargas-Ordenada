#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sistema de actualizaciones — **versión heredada**, solo como último recurso.

La implementación vigente es :mod:`organizer.actualizaciones_mejorado`, que
maneja los límites de la API de GitHub y las descargas sin conexión. Este
módulo se conserva únicamente como respaldo por si el paquete instalado no
incluyera el nuevo, y avisa por el registro cuando se usa. No añadir aquí
funcionalidad nueva: los cambios van en ``actualizaciones_mejorado``.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

from .version import obtener_version
from .app_paths import obtener_directorio_configuracion

logger = logging.getLogger('organizador.actualizaciones')

try:
    import requests
    REQUESTS_DISPONIBLE = True
except ImportError:
    REQUESTS_DISPONIBLE = False

class GestorActualizaciones:
    """Gestor de actualizaciones automáticas."""
    
    VERSION_ACTUAL = obtener_version()
    URL_ACTUALIZACIONES = "https://api.github.com/repos/AntonioXam/Descargas-Ordenada/releases/latest"
    
    def __init__(self):
        self.config_path = self._obtener_ruta_config()
        self.ultima_verificacion = None
        self.nueva_version_disponible = None
        self._cargar_config()
    
    def _obtener_ruta_config(self) -> Path:
        """Obtiene la ruta del archivo de configuración."""
        config_dir = obtener_directorio_configuracion()
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "actualizaciones.json"
    
    def _cargar_config(self):
        """Carga la configuración de actualizaciones."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    fecha_str = config.get('ultima_verificacion')
                    if fecha_str:
                        self.ultima_verificacion = datetime.fromisoformat(fecha_str)
        except Exception as e:
            logger.error(f"Error cargando config actualizaciones: {e}")
    
    def _guardar_config(self):
        """Guarda la configuración de actualizaciones."""
        try:
            config = {
                'ultima_verificacion': self.ultima_verificacion.isoformat() if self.ultima_verificacion else None,
                'nueva_version': self.nueva_version_disponible
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            logger.error(f"Error guardando config actualizaciones: {e}")
    
    def verificar_actualizaciones(self, forzar=False) -> Tuple[bool, Optional[Dict]]:
        """Verifica si hay actualizaciones disponibles."""
        if not REQUESTS_DISPONIBLE:
            return False, None
        
        if not forzar and self.ultima_verificacion:
            if datetime.now() - self.ultima_verificacion < timedelta(hours=24):
                if self.nueva_version_disponible:
                    return True, self.nueva_version_disponible
                return False, None
        
        try:
            response = requests.get(self.URL_ACTUALIZACIONES, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            version_remota = data.get('tag_name', '').lstrip('v')
            
            self.ultima_verificacion = datetime.now()
            
            if self._es_version_nueva(version_remota):
                self.nueva_version_disponible = {
                    'version': version_remota,
                    'nombre': data.get('name', ''),
                    'descripcion': data.get('body', ''),
                    'url': data.get('html_url', ''),
                    'fecha': data.get('published_at', '')
                }
                self._guardar_config()
                return True, self.nueva_version_disponible
            else:
                self.nueva_version_disponible = None
                self._guardar_config()
                return False, None
                
        except Exception as e:
            logger.error(f"Error verificando actualizaciones: {e}")
            return False, None
    
    def _es_version_nueva(self, version_remota: str) -> bool:
        """Compara versiones semánticas rellenando con ceros las partes que falten."""
        try:
            local = tuple(map(int, self.VERSION_ACTUAL.split('.')))
            remota = tuple(map(int, version_remota.split('.')))
            longitud = max(len(local), len(remota))
            local += (0,) * (longitud - len(local))
            remota += (0,) * (longitud - len(remota))
            return remota > local
        except Exception:
            return False
    
    def obtener_version_actual(self) -> str:
        """Obtiene la versión actual."""
        return self.VERSION_ACTUAL
    
    def obtener_info_actualizacion(self) -> Optional[Dict]:
        """Obtiene información de actualización disponible."""
        return self.nueva_version_disponible
    
    def marcar_actualizacion_ignorada(self):
        """Marca la actualización como ignorada."""
        self.nueva_version_disponible = None
        self._guardar_config()
    
    def abrir_pagina_descarga(self):
        """Abre la página de descarga en el navegador."""
        if self.nueva_version_disponible:
            url = self.nueva_version_disponible.get('url')
            if url:
                try:
                    import webbrowser
                    webbrowser.open(url)
                    return True
                except Exception as e:
                    logger.error(f"Error abriendo navegador: {e}")
        return False

# Instancia global
_gestor_actualizaciones_global = None

def obtener_gestor_actualizaciones():
    """Obtiene la instancia global del gestor de actualizaciones."""
    global _gestor_actualizaciones_global
    if _gestor_actualizaciones_global is None:
        _gestor_actualizaciones_global = GestorActualizaciones()
    return _gestor_actualizaciones_global
