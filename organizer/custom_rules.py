#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de reglas personalizables para categorización de archivos
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ReglaPersonalizada:
    """
    Representa una regla personalizada para categorizar archivos.
    """
    
    def __init__(self, nombre: str, categoria: str, subcategoria: str = "General"):
        self.nombre = nombre
        self.categoria = categoria
        self.subcategoria = subcategoria
        self.patrones_extension: List[str] = []
        self.patrones_nombre: List[str] = []
        self.patrones_regex: List[str] = []
        self.tamaño_min: Optional[int] = None
        self.tamaño_max: Optional[int] = None
        self.fecha_min: Optional[datetime] = None
        self.fecha_max: Optional[datetime] = None
        self.prioridad: int = 1000  # Prioridad alta por defecto para reglas usuario
        self.activa: bool = True
    
    def añadir_extension(self, extension: str):
        """Añade una extensión a la regla."""
        if not extension.startswith('.'):
            extension = '.' + extension
        extension = extension.lower()
        if extension not in self.patrones_extension:
            self.patrones_extension.append(extension)
    
    def añadir_patron_nombre(self, patron: str):
        """Añade un patrón de nombre a la regla."""
        if patron not in self.patrones_nombre:
            self.patrones_nombre.append(patron.lower())
    
    def añadir_patron_regex(self, patron: str):
        """Añade un patrón regex a la regla."""
        try:
            re.compile(patron)  # Validar regex
            if patron not in self.patrones_regex:
                self.patrones_regex.append(patron)
        except re.error as e:
            logger.error(f"Patrón regex inválido '{patron}': {e}")
    
    def establecer_rango_tamaño(self, min_bytes: Optional[int], max_bytes: Optional[int]):
        """Establece rango de tamaño para la regla."""
        self.tamaño_min = min_bytes
        self.tamaño_max = max_bytes
    
    def establecer_rango_fecha(self, fecha_min: Optional[datetime], fecha_max: Optional[datetime]):
        """Establece rango de fechas para la regla."""
        self.fecha_min = fecha_min
        self.fecha_max = fecha_max
    
    def coincide(self, archivo: Path) -> bool:
        """
        Verifica si un archivo coincide con esta regla.
        
        Args:
            archivo: Archivo a verificar
            
        Returns:
            True si el archivo coincide con la regla
        """
        if not self.activa:
            return False
        
        # Verificar extensión
        if self.patrones_extension:
            extension = archivo.suffix.lower()
            if extension not in self.patrones_extension:
                return False
        
        # Verificar patrones de nombre
        if self.patrones_nombre:
            nombre_lower = archivo.stem.lower()
            if not any(patron in nombre_lower for patron in self.patrones_nombre):
                return False
        
        # Verificar patrones regex
        if self.patrones_regex:
            nombre_completo = archivo.name
            if not any(re.search(patron, nombre_completo, re.IGNORECASE) 
                      for patron in self.patrones_regex):
                return False
        
        # Verificar tamaño
        if self.tamaño_min is not None or self.tamaño_max is not None:
            try:
                tamaño = archivo.stat().st_size
                if self.tamaño_min is not None and tamaño < self.tamaño_min:
                    return False
                if self.tamaño_max is not None and tamaño > self.tamaño_max:
                    return False
            except (OSError, IOError):
                return False
        
        # Verificar fecha
        if self.fecha_min is not None or self.fecha_max is not None:
            try:
                fecha_mod = datetime.fromtimestamp(archivo.stat().st_mtime)
                if self.fecha_min is not None and fecha_mod < self.fecha_min:
                    return False
                if self.fecha_max is not None and fecha_mod > self.fecha_max:
                    return False
            except (OSError, IOError):
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la regla a diccionario para serialización."""
        return {
            'nombre': self.nombre,
            'categoria': self.categoria,
            'subcategoria': self.subcategoria,
            'patrones_extension': self.patrones_extension,
            'patrones_nombre': self.patrones_nombre,
            'patrones_regex': self.patrones_regex,
            'tamaño_min': self.tamaño_min,
            'tamaño_max': self.tamaño_max,
            'fecha_min': self.fecha_min.isoformat() if self.fecha_min else None,
            'fecha_max': self.fecha_max.isoformat() if self.fecha_max else None,
            'prioridad': self.prioridad,
            'activa': self.activa
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReglaPersonalizada':
        """Crea una regla desde un diccionario."""
        regla = cls(data['nombre'], data['categoria'], data.get('subcategoria', 'General'))
        regla.patrones_extension = data.get('patrones_extension', [])
        regla.patrones_nombre = data.get('patrones_nombre', [])
        regla.patrones_regex = data.get('patrones_regex', [])
        regla.tamaño_min = data.get('tamaño_min')
        regla.tamaño_max = data.get('tamaño_max')
        regla.prioridad = data.get('prioridad', 1000)
        regla.activa = data.get('activa', True)
        
        # Convertir fechas
        if data.get('fecha_min'):
            regla.fecha_min = datetime.fromisoformat(data['fecha_min'])
        if data.get('fecha_max'):
            regla.fecha_max = datetime.fromisoformat(data['fecha_max'])
        
        return regla

class GestorReglasPersonalizadas:
    """
    Gestiona las reglas personalizadas del usuario.
    """
    
    def __init__(self, carpeta_descargas: Path):
        self.carpeta_descargas = carpeta_descargas
        self.carpeta_config = carpeta_descargas / ".config"
        self.carpeta_config.mkdir(exist_ok=True)
        self.archivo_reglas = self.carpeta_config / "reglas_personalizadas.json"
        self.reglas: List[ReglaPersonalizada] = []
        self._cargar_reglas()
        self._crear_reglas_ejemplo()
    
    def _cargar_reglas(self):
        """Carga las reglas desde el archivo de configuración."""
        if not self.archivo_reglas.exists():
            return
        
        try:
            with open(self.archivo_reglas, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.reglas = []
            for regla_data in data.get('reglas', []):
                try:
                    regla = ReglaPersonalizada.from_dict(regla_data)
                    self.reglas.append(regla)
                except Exception as e:
                    logger.error(f"Error cargando regla: {e}")
            
            logger.info(f"✅ Cargadas {len(self.reglas)} reglas personalizadas")
            
        except Exception as e:
            logger.error(f"Error cargando reglas personalizadas: {e}")
    
    def _guardar_reglas(self):
        """Guarda las reglas en el archivo de configuración."""
        try:
            data = {
                'version': '1.0',
                'ultima_actualizacion': datetime.now().isoformat(),
                'reglas': [regla.to_dict() for regla in self.reglas]
            }
            
            with open(self.archivo_reglas, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 Guardadas {len(self.reglas)} reglas personalizadas")
            
        except Exception as e:
            logger.error(f"Error guardando reglas personalizadas: {e}")
    
    def _crear_reglas_ejemplo(self):
        """Crea reglas de ejemplo si no existen."""
        if self.reglas:
            return  # Ya hay reglas
        
        ejemplos = [
            {
                'nombre': 'Proyectos de Diseño',
                'categoria': 'Proyectos',
                'subcategoria': 'Diseño',
                'extensiones': ['.psd', '.ai', '.sketch', '.figma', '.xd'],
                'descripcion': 'Archivos de proyectos de diseño gráfico'
            },
            {
                'nombre': 'Documentos de Trabajo',
                'categoria': 'Trabajo',
                'subcategoria': 'Documentos',
                'patrones_nombre': ['informe', 'reporte', 'presentacion', 'propuesta'],
                'descripcion': 'Documentos relacionados con el trabajo'
            },
            {
                'nombre': 'Archivos de Curso',
                'categoria': 'Educación',
                'subcategoria': 'Cursos',
                'patrones_nombre': ['curso', 'clase', 'leccion', 'tutorial'],
                'descripcion': 'Material educativo y de cursos'
            },
            {
                'nombre': 'Screenshots',
                'categoria': 'Imágenes',
                'subcategoria': 'Capturas',
                'patrones_nombre': ['screenshot', 'captura', 'screen'],
                'extensiones': ['.png', '.jpg'],
                'descripcion': 'Capturas de pantalla'
            }
        ]
        
        for ejemplo in ejemplos:
            regla = ReglaPersonalizada(
                ejemplo['nombre'],
                ejemplo['categoria'],
                ejemplo['subcategoria']
            )
            
            # Añadir extensiones si las hay
            for ext in ejemplo.get('extensiones', []):
                regla.añadir_extension(ext)
            
            # Añadir patrones de nombre si los hay
            for patron in ejemplo.get('patrones_nombre', []):
                regla.añadir_patron_nombre(patron)
            
            self.reglas.append(regla)
        
        self._guardar_reglas()
        logger.info("📝 Creadas reglas de ejemplo")
    
    def añadir_regla(self, regla: ReglaPersonalizada) -> bool:
        """
        Añade una nueva regla personalizada.
        
        Args:
            regla: Regla a añadir
            
        Returns:
            True si se añadió correctamente
        """
        # Verificar que no existe una regla con el mismo nombre
        if any(r.nombre == regla.nombre for r in self.reglas):
            logger.error(f"Ya existe una regla con el nombre '{regla.nombre}'")
            return False
        
        self.reglas.append(regla)
        self.reglas.sort(key=lambda r: r.prioridad, reverse=True)
        self._guardar_reglas()
        
        logger.info(f"✅ Regla añadida: {regla.nombre}")
        return True
    
    def eliminar_regla(self, nombre: str) -> bool:
        """
        Elimina una regla por nombre.
        
        Args:
            nombre: Nombre de la regla a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        reglas_antes = len(self.reglas)
        self.reglas = [r for r in self.reglas if r.nombre != nombre]
        
        if len(self.reglas) < reglas_antes:
            self._guardar_reglas()
            logger.info(f"🗑️ Regla eliminada: {nombre}")
            return True
        else:
            logger.warning(f"No se encontró regla con nombre: {nombre}")
            return False
    
    def activar_regla(self, nombre: str, activa: bool = True):
        """Activa o desactiva una regla."""
        for regla in self.reglas:
            if regla.nombre == nombre:
                regla.activa = activa
                self._guardar_reglas()
                estado = "activada" if activa else "desactivada"
                logger.info(f"⚡ Regla {estado}: {nombre}")
                return True
        
        logger.warning(f"No se encontró regla: {nombre}")
        return False
    
    def obtener_categoria(self, archivo: Path) -> Optional[Tuple[str, str]]:
        """
        Obtiene la categoría de un archivo según las reglas personalizadas.
        
        Args:
            archivo: Archivo a categorizar
            
        Returns:
            Tupla con (categoria, subcategoria) si coincide, None si no
        """
        for regla in self.reglas:
            if regla.coincide(archivo):
                logger.debug(f"Archivo {archivo.name} coincide con regla: {regla.nombre}")
                return (regla.categoria, regla.subcategoria)
        
        return None
    
    def listar_reglas(self) -> List[Dict[str, Any]]:
        """Retorna información de todas las reglas."""
        return [
            {
                'nombre': regla.nombre,
                'categoria': regla.categoria,
                'subcategoria': regla.subcategoria,
                'activa': regla.activa,
                'prioridad': regla.prioridad,
                'extensiones': regla.patrones_extension,
                'patrones': regla.patrones_nombre,
                'regex': regla.patrones_regex
            }
            for regla in self.reglas
        ]
    
    def crear_regla_rapida(self, nombre: str, categoria: str, subcategoria: str = "General",
                          extensiones: List[str] = None, patrones: List[str] = None) -> bool:
        """
        Crea una regla rápida con parámetros básicos.
        
        Args:
            nombre: Nombre de la regla
            categoria: Categoría destino
            subcategoria: Subcategoría destino
            extensiones: Lista de extensiones
            patrones: Lista de patrones de nombre
            
        Returns:
            True si se creó correctamente
        """
        regla = ReglaPersonalizada(nombre, categoria, subcategoria)
        
        if extensiones:
            for ext in extensiones:
                regla.añadir_extension(ext)
        
        if patrones:
            for patron in patrones:
                regla.añadir_patron_nombre(patron)
        
        return self.añadir_regla(regla) 