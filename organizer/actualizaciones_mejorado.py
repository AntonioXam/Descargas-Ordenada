#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de actualizaciones automáticas con descarga desde GitHub
DescargasOrdenadas v3.1
"""

import sys
import logging
import json
import zipfile
import shutil
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger('organizador.actualizaciones')

try:
    import requests
    REQUESTS_DISPONIBLE = True
except ImportError:
    REQUESTS_DISPONIBLE = False
    logger.warning("requests no disponible - actualizaciones deshabilitadas")

class GestorActualizacionesMejorado:
    """Gestor de actualizaciones con descarga automática desde GitHub."""
    
    VERSION_ACTUAL = "3.1.0"
    GITHUB_USER = "tu-usuario"  # Cambiar por tu usuario de GitHub
    GITHUB_REPO = "Descargas-Ordenada"  # Cambiar por tu repositorio
    API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
    
    def __init__(self):
        self.config_path = self._obtener_ruta_config()
        self.ultima_verificacion = None
        self.nueva_version_disponible = None
        self._cargar_config()
    
    def _obtener_ruta_config(self) -> Path:
        """Obtiene la ruta del archivo de configuración."""
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
                'nueva_version': self.nueva_version_disponible,
                'version_actual': self.VERSION_ACTUAL
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            logger.error(f"Error guardando config actualizaciones: {e}")
    
    def verificar_actualizaciones(self, forzar=False) -> Tuple[bool, Optional[Dict]]:
        """Verifica si hay actualizaciones disponibles."""
        if not REQUESTS_DISPONIBLE:
            return False, None
        
        # Verificar frecuencia (24 horas)
        if not forzar and self.ultima_verificacion:
            if datetime.now() - self.ultima_verificacion < timedelta(hours=24):
                if self.nueva_version_disponible:
                    return True, self.nueva_version_disponible
                return False, None
        
        try:
            logger.info(f"Verificando actualizaciones desde: {self.API_URL}")
            
            headers = {'Accept': 'application/vnd.github.v3+json'}
            response = requests.get(self.API_URL, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            version_remota = data.get('tag_name', '').lstrip('vV')
            
            self.ultima_verificacion = datetime.now()
            
            if self._es_version_nueva(version_remota):
                # Buscar el asset .zip en la release
                assets = data.get('assets', [])
                zip_url = None
                
                for asset in assets:
                    if asset.get('name', '').endswith('.zip'):
                        zip_url = asset.get('browser_download_url')
                        break
                
                # Si no hay zip en assets, usar zipball_url
                if not zip_url:
                    zip_url = data.get('zipball_url')
                
                self.nueva_version_disponible = {
                    'version': version_remota,
                    'nombre': data.get('name', ''),
                    'descripcion': data.get('body', ''),
                    'url': data.get('html_url', ''),
                    'download_url': zip_url,
                    'fecha': data.get('published_at', '')
                }
                self._guardar_config()
                logger.info(f"✨ Nueva versión disponible: {version_remota}")
                return True, self.nueva_version_disponible
            else:
                self.nueva_version_disponible = None
                self._guardar_config()
                logger.info("✅ Ya tienes la última versión")
                return False, None
                
        except Exception as e:
            logger.error(f"Error verificando actualizaciones: {e}")
            return False, None
    
    def _es_version_nueva(self, version_remota: str) -> bool:
        """Compara versiones usando versionado semántico."""
        try:
            local = tuple(map(int, self.VERSION_ACTUAL.split('.')))
            remota = tuple(map(int, version_remota.split('.')))
            return remota > local
        except Exception:
            return False
    
    def descargar_actualizacion(self, info: Dict, callback_progreso=None) -> Tuple[bool, str]:
        """
        Descarga la actualización desde GitHub.
        
        Args:
            info: Diccionario con información de la actualización
            callback_progreso: Función para reportar progreso (porcentaje)
        
        Returns:
            (exito, mensaje/ruta_archivo)
        """
        if not REQUESTS_DISPONIBLE:
            return False, "requests no disponible"
        
        download_url = info.get('download_url')
        if not download_url:
            return False, "URL de descarga no disponible"
        
        try:
            # Crear carpeta temporal
            if getattr(sys, 'frozen', False):
                base_dir = Path(sys.executable).parent
            else:
                base_dir = Path(__file__).parent.parent
            
            temp_dir = base_dir / ".temp_update"
            temp_dir.mkdir(exist_ok=True)
            
            # Nombre del archivo
            version = info.get('version', 'latest')
            zip_path = temp_dir / f"DescargasOrdenadas_v{version}.zip"
            
            logger.info(f"Descargando desde: {download_url}")
            
            # Descargar con progreso
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if callback_progreso and total_size > 0:
                            porcentaje = int((downloaded / total_size) * 100)
                            callback_progreso(porcentaje)
            
            logger.info(f"✅ Descarga completada: {zip_path}")
            return True, str(zip_path)
            
        except Exception as e:
            logger.error(f"Error descargando actualización: {e}")
            return False, f"Error: {e}"
    
    def instalar_actualizacion(self, zip_path: str) -> Tuple[bool, str]:
        """
        Descomprime e instala la actualización.
        
        Args:
            zip_path: Ruta al archivo .zip descargado
        
        Returns:
            (exito, mensaje)
        """
        try:
            zip_path = Path(zip_path)
            
            if not zip_path.exists():
                return False, f"Archivo no encontrado: {zip_path}"
            
            # Obtener directorio base
            if getattr(sys, 'frozen', False):
                base_dir = Path(sys.executable).parent
            else:
                base_dir = Path(__file__).parent.parent
            
            # Crear backup del proyecto actual
            backup_dir = base_dir.parent / f"DescargasOrdenadas_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"Creando backup en: {backup_dir}")
            
            try:
                shutil.copytree(base_dir, backup_dir, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git'))
            except Exception as e:
                logger.warning(f"Error creando backup: {e}")
            
            # Descomprimir actualización
            temp_extract = base_dir / ".temp_extract"
            temp_extract.mkdir(exist_ok=True)
            
            logger.info(f"Descomprimiendo: {zip_path}")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract)
            
            # Buscar la carpeta del proyecto dentro del zip
            # (GitHub zipball crea una carpeta con el nombre del repo)
            extracted_folders = [f for f in temp_extract.iterdir() if f.is_dir()]
            
            if not extracted_folders:
                return False, "No se encontró contenido en el archivo ZIP"
            
            source_folder = extracted_folders[0]
            
            # Copiar archivos al proyecto actual (excluyendo .config)
            logger.info(f"Copiando archivos desde: {source_folder}")
            
            archivos_copiados = 0
            for item in source_folder.rglob('*'):
                if item.is_file():
                    # Excluir ciertos archivos/carpetas
                    relative_path = item.relative_to(source_folder)
                    
                    if any(part.startswith('.') for part in relative_path.parts):
                        continue  # Skip archivos/carpetas ocultas
                    
                    if '.config' in relative_path.parts:
                        continue  # Preservar configuración
                    
                    # Copiar archivo
                    dest_path = base_dir / relative_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    shutil.copy2(item, dest_path)
                    archivos_copiados += 1
            
            # Limpiar archivos temporales
            shutil.rmtree(temp_extract, ignore_errors=True)
            zip_path.unlink(missing_ok=True)
            
            logger.info(f"✅ Actualización instalada: {archivos_copiados} archivos")
            
            return True, f"Actualización instalada correctamente\n\n" \
                        f"📁 Archivos actualizados: {archivos_copiados}\n" \
                        f"💾 Backup creado en: {backup_dir.name}\n\n" \
                        f"⚠️ IMPORTANTE: Reinicia la aplicación para aplicar los cambios"
            
        except Exception as e:
            logger.error(f"Error instalando actualización: {e}")
            return False, f"Error durante la instalación: {e}"
    
    def obtener_version_actual(self) -> str:
        """Obtiene la versión actual."""
        return self.VERSION_ACTUAL
    
    def obtener_info_actualizacion(self) -> Optional[Dict]:
        """Obtiene información de actualización disponible."""
        return self.nueva_version_disponible
    
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
        _gestor_actualizaciones_global = GestorActualizacionesMejorado()
    return _gestor_actualizaciones_global
