#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Detección inteligente de tipos de archivo basada en contenido
"""

import os
import mimetypes
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class DetectorInteligente:
    """
    Detector que combina extensión, contenido y heurísticas para 
    clasificar archivos de manera más precisa.
    """
    
    def __init__(self):
        # Firmas de archivos (magic numbers)
        self.firmas_archivos = {
            # Imágenes
            b'\xFF\xD8\xFF': ('Imágenes', 'Fotografía'),  # JPEG
            b'\x89PNG\r\n\x1a\n': ('Imágenes', 'Gráficos'),  # PNG
            b'GIF8': ('Imágenes', 'Gráficos'),  # GIF
            b'RIFF': ('Imágenes', 'Gráficos'),  # WebP (si contiene WEBP)
            
            # Videos
            b'\x00\x00\x00\x18ftypmp4': ('Vídeos', 'Películas'),  # MP4
            b'\x1a\x45\xdf\xa3': ('Vídeos', 'Películas'),  # WebM/MKV
            
            # Audio
            b'ID3': ('Audio', 'Música'),  # MP3 con ID3
            b'\xff\xfb': ('Audio', 'Música'),  # MP3
            b'fLaC': ('Audio', 'Música'),  # FLAC
            
            # Documentos
            b'%PDF': ('PDFs', 'Documentos'),  # PDF
            b'PK\x03\x04': self._detectar_zip_office,  # ZIP/Office
            
            # Ejecutables
            b'MZ': ('Ejecutables', 'Windows'),  # Windows PE
            b'\x7fELF': ('Ejecutables', 'Linux'),  # Linux ELF
            b'\xca\xfe\xba\xbe': ('Ejecutables', 'macOS'),  # macOS Mach-O
            
            # APK (ZIP con estructura específica)
            b'PK\x03\x04': self._detectar_apk,
        }
        
        # Heurísticas por nombre de archivo
        self.heuristicas_nombre = {
            'factura': ('Documentos', 'Facturas'),
            'invoice': ('Documentos', 'Facturas'),
            'receipt': ('Documentos', 'Facturas'),
            'manual': ('PDFs', 'Manuales'),
            'tutorial': ('Vídeos', 'Tutoriales'),
            'screenshot': ('Imágenes', 'Capturas'),
            'captura': ('Imágenes', 'Capturas'),
            'backup': ('Backups', 'Sistema'),
            'instalador': ('Ejecutables', 'Windows'),
            'setup': ('Ejecutables', 'Windows'),
        }
    
    def detectar_tipo_inteligente(self, archivo: Path) -> Tuple[str, Optional[str]]:
        """
        Detecta el tipo de archivo usando múltiples métodos.
        
        Args:
            archivo: Ruta al archivo
            
        Returns:
            Tupla con (categoría, subcategoría)
        """
        if not archivo.exists() or not archivo.is_file():
            return ("Otros", "Desconocidos")
        
        # 1. Intentar por firma de archivo (más confiable)
        categoria_firma = self._detectar_por_firma(archivo)
        if categoria_firma[0] != "Otros":
            logger.debug(f"Detectado por firma: {archivo.name} -> {categoria_firma}")
            return categoria_firma
        
        # 2. Intentar por heurísticas de nombre
        categoria_nombre = self._detectar_por_nombre(archivo)
        if categoria_nombre[0] != "Otros":
            logger.debug(f"Detectado por nombre: {archivo.name} -> {categoria_nombre}")
            return categoria_nombre
        
        # 3. Intentar por MIME type
        categoria_mime = self._detectar_por_mime(archivo)
        if categoria_mime[0] != "Otros":
            logger.debug(f"Detectado por MIME: {archivo.name} -> {categoria_mime}")
            return categoria_mime
        
        # 4. Fallback a detección por extensión (método original)
        return ("Otros", "Desconocidos")
    
    def _detectar_por_firma(self, archivo: Path) -> Tuple[str, Optional[str]]:
        """Detecta tipo por firma binaria del archivo."""
        try:
            with open(archivo, 'rb') as f:
                header = f.read(32)  # Leer primeros 32 bytes
                
            for firma, resultado in self.firmas_archivos.items():
                if header.startswith(firma):
                    if callable(resultado):
                        return resultado(archivo, header)
                    return resultado
                    
        except (IOError, PermissionError):
            pass
        
        return ("Otros", "Desconocidos")
    
    def _detectar_por_nombre(self, archivo: Path) -> Tuple[str, Optional[str]]:
        """Detecta tipo por heurísticas en el nombre del archivo."""
        nombre_lower = archivo.stem.lower()
        
        for patron, categoria in self.heuristicas_nombre.items():
            if patron in nombre_lower:
                return categoria
        
        return ("Otros", "Desconocidos")
    
    def _detectar_por_mime(self, archivo: Path) -> Tuple[str, Optional[str]]:
        """Detecta tipo por MIME type."""
        try:
            mime_type, _ = mimetypes.guess_type(str(archivo))
            if not mime_type:
                return ("Otros", "Desconocidos")
            
            # Mapeo de MIME types a categorías
            mime_mapping = {
                'image/': ('Imágenes', 'Fotografía'),
                'video/': ('Vídeos', 'Películas'),
                'audio/': ('Audio', 'Música'),
                'application/pdf': ('PDFs', 'Documentos'),
                'application/zip': ('Comprimidos', 'Comunes'),
                'text/': ('Documentos', 'Texto'),
            }
            
            for mime_prefix, categoria in mime_mapping.items():
                if mime_type.startswith(mime_prefix):
                    return categoria
                    
        except Exception:
            pass
        
        return ("Otros", "Desconocidos")
    
    def _detectar_zip_office(self, archivo: Path, header: bytes) -> Tuple[str, Optional[str]]:
        """Detecta si un ZIP es un documento de Office o comprimido normal."""
        try:
            import zipfile
            with zipfile.ZipFile(archivo, 'r') as zf:
                archivos_internos = zf.namelist()
                
                # Detectar documentos Office
                if any(nombre.startswith('word/') for nombre in archivos_internos):
                    return ('Documentos', 'Word')
                elif any(nombre.startswith('xl/') for nombre in archivos_internos):
                    return ('Hojas de cálculo', 'Excel')
                elif any(nombre.startswith('ppt/') for nombre in archivos_internos):
                    return ('Presentaciones', 'PowerPoint')
                elif 'AndroidManifest.xml' in archivos_internos:
                    return ('Ejecutables', 'Android')  # Es un APK
                    
        except Exception:
            pass
        
        return ('Comprimidos', 'Comunes')
    
    def _detectar_apk(self, archivo: Path, header: bytes) -> Tuple[str, Optional[str]]:
        """Detecta específicamente APKs."""
        if archivo.suffix.lower() == '.apk':
            return ('Ejecutables', 'Android')
        
        # Si es ZIP, verificar si contiene AndroidManifest.xml
        return self._detectar_zip_office(archivo, header) 