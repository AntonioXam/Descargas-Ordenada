#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sistema de actualizaciones automáticas para DescargasOrdenadas v3.1"""

import logging
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger('organizador.actualizaciones')

try:
    import requests
    REQUESTS_DISPONIBLE = True
except ImportError:
    REQUESTS_DISPONIBLE = False

class GestorActualizaciones:
    """Gestor de actualizaciones automáticas."""
    
    VERSION_ACTUAL = "3.1.0"
    URL_ACTUALIZACIONES = "https://api.github.com/repos/usuario/descargasordenadas/releases/latest"
    
    def __init__(self):
        self.config_path = self._obtener_ruta_config()
        self.ultima_verificacion = None
        self.nueva_version_disponible = None
        self._cargar_config()
    
    def _obtener_ruta_config(self) -> Path:
        """Obtiene la ruta del archivo de configuración."""
        import sys
        if getattr(sys, 'frozen', False):
            base_dir = Path(sys.executable).parent
        else:
            base_dir = Path(__file__).parent.parent
        
        config_dir = base_dir / ".config"
        config_dir.mkdir(exist_ok=True)
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
        """Compara versiones."""
        try:
            local = tuple(map(int, self.VERSION_ACTUAL.split('.')))
            remota = tuple(map(int, version_remota.split('.')))
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
