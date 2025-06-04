#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('organizador')

# Definición de los tipos de archivos y sus extensiones
TIPOS_ARCHIVOS = {
    'Imágenes': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico', '.heic', '.raw', '.psd', '.ai', '.indd', '.xcf', '.cdr', '.eps'],
    'Vídeos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.3gp', '.ts', '.vob', '.ogv', '.m2ts', '.mts'],
    'Audio': ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.wma', '.m4a', '.opus', '.mid', '.midi', '.amr', '.aiff', '.alac', '.ape', '.ac3', '.dts'],
    'Documentos': ['.doc', '.docx', '.odt', '.rtf', '.txt', '.md', '.wpd', '.pages', '.log', '.tex', '.wps'],
    'Hojas de cálculo': ['.xls', '.xlsx', '.ods', '.csv', '.tsv', '.numbers', '.xlsm', '.xltx', '.xltm'],
    'Presentaciones': ['.ppt', '.pptx', '.odp', '.key', '.pps', '.ppsx', '.pptm', '.pot', '.potx'],
    'PDFs': ['.pdf'],
    'Ebooks': ['.epub', '.mobi', '.azw', '.azw3', '.azw4', '.cbr', '.cbz', '.djvu', '.fb2', '.ibooks'],
    'Archivos 3D': ['.obj', '.fbx', '.3ds', '.blend', '.dae', '.stl', '.ply', '.gltf', '.glb', '.x3d', '.vrml', '.max', '.c4d', '.ma', '.mb', '.skp', '.usd', '.usda', '.usdc'],
    'CAD': ['.dwg', '.dxf', '.step', '.iges', '.sldprt', '.sldasm', '.catpart', '.catproduct', '.prt', '.asm', '.ipt', '.iam', '.solidworks'],
    'Ejecutables': ['.exe', '.msi', '.app', '.appimage', '.dmg', '.pkg', '.deb', '.rpm', '.apk', '.bat', '.sh', '.com', '.gadget', '.vb', '.vbs', '.msc', '.appxbundle'],
    'Comprimidos': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.tgz', '.iso', '.cab', '.lzh', '.lha', '.arj', '.z', '.lz', '.txz', '.tlz', '.tbz2'],
    'Código Fuente': ['.py', '.js', '.html', '.css', '.java', '.c', '.cpp', '.h', '.php', '.rb', '.go', '.rs', '.ts', '.cs', '.swift', '.kt', '.m', '.vb', '.pl', '.lua', '.scala', '.dart', '.r', '.f', '.f90', '.d', '.jl', '.elm', '.erl', '.ex', '.exs', '.clj', '.hs', '.lisp', '.pas', '.sol', '.groovy', '.v', '.mq4', '.mq5'],
    'Web': ['.html', '.htm', '.css', '.js', '.jsx', '.ts', '.tsx', '.php', '.asp', '.aspx', '.jsp', '.json', '.xml', '.xhtml', '.wasm', '.vue', '.svelte', '.less', '.sass', '.scss', '.htaccess', '.webmanifest'],
    'Datos': ['.json', '.xml', '.yaml', '.yml', '.csv', '.tsv', '.sql', '.db', '.sqlite', '.sqlite3', '.mdb', '.accdb', '.toml', '.ini', '.conf', '.cfg', '.properties', '.env', '.dat', '.parquet', '.avro', '.hdf5', '.h5', '.proto', '.graphql'],
    'Imágenes de Disco': ['.iso', '.img', '.vhd', '.vmdk', '.vdi', '.qcow2', '.hdd', '.wim', '.dmg', '.toast', '.vhdx', '.dsk'],
    'Fuentes': ['.ttf', '.otf', '.woff', '.woff2', '.eot', '.fnt', '.fon', '.bdf', '.pfb', '.afm', '.pfa', '.pcf', '.snf'],
    'Configuración': ['.ini', '.cfg', '.conf', '.config', '.json', '.xml', '.yaml', '.yml', '.properties', '.prop', '.env', '.inf', '.reg', '.plist'],
    'Vectoriales': ['.svg', '.ai', '.eps', '.cdr', '.afdesign', '.sketch', '.xd', '.figma', '.vsdx', '.emf', '.wmf', '.dxf'],
    'Subtítulos': ['.srt', '.sub', '.sbv', '.ass', '.ssa', '.vtt', '.ttml', '.dfxp', '.cap', '.smi'],
    'Backups': ['.bak', '.old', '.tmp', '.temp', '.backup', '.save', '.swp', '.swo', '.~', '.orig']
}

class OrganizadorArchivos:
    """Clase principal para organizar archivos de la carpeta de descargas."""
    
    def __init__(self, carpeta_descargas: Optional[str] = None):
        """
        Inicializa el organizador de archivos.
        
        Args:
            carpeta_descargas: Ruta a la carpeta de descargas. Si es None, se detectará automáticamente.
        """
        self.carpeta_descargas = self._detectar_carpeta_descargas() if carpeta_descargas is None else Path(carpeta_descargas)
        self.archivo_huella = self.carpeta_descargas / '.organized.json'
        self.archivos_procesados: Dict[str, str] = {}
        self._cargar_huella()
        
    def _detectar_carpeta_descargas(self) -> Path:
        """Detecta automáticamente la carpeta de descargas según el sistema operativo."""
        if sys.platform == 'win32':
            # Windows
            return Path(os.path.expanduser('~')) / 'Downloads'
        elif sys.platform == 'darwin':
            # macOS
            return Path(os.path.expanduser('~')) / 'Downloads'
        else:
            # Linux y otros sistemas Unix
            # Intentamos primero la carpeta estándar, luego la traducida
            descargas = Path(os.path.expanduser('~')) / 'Downloads'
            if not descargas.exists():
                descargas = Path(os.path.expanduser('~')) / 'Descargas'
            return descargas
    
    def _cargar_huella(self) -> None:
        """Carga el archivo de huella si existe."""
        if self.archivo_huella.exists():
            try:
                with open(self.archivo_huella, 'r', encoding='utf-8') as f:
                    self.archivos_procesados = json.load(f)
                logger.info(f"Archivo de huella cargado: {len(self.archivos_procesados)} archivos ya procesados.")
            except Exception as e:
                logger.error(f"Error al cargar archivo de huella: {e}")
                self.archivos_procesados = {}
    
    def _guardar_huella(self) -> None:
        """Guarda el archivo de huella con los archivos procesados."""
        try:
            with open(self.archivo_huella, 'w', encoding='utf-8') as f:
                json.dump(self.archivos_procesados, f, ensure_ascii=False, indent=2)
            logger.info(f"Archivo de huella guardado: {len(self.archivos_procesados)} archivos procesados.")
        except Exception as e:
            logger.error(f"Error al guardar archivo de huella: {e}")
    
    def _obtener_tipo_archivo(self, archivo: Path) -> str:
        """
        Determina el tipo de archivo basado en su extensión.
        
        Args:
            archivo: Ruta al archivo a verificar.
            
        Returns:
            Nombre de la categoría a la que pertenece el archivo.
        """
        extension = archivo.suffix.lower()
        
        for tipo, extensiones in TIPOS_ARCHIVOS.items():
            if extension in extensiones:
                return tipo
        
        return "Otros"
    
    def organizar(self, callback=None) -> Tuple[Dict[str, List[str]], List[str]]:
        """
        Organiza los archivos de la carpeta de descargas.
        
        Args:
            callback: Función opcional a llamar por cada archivo procesado.
                     Recibe (nombre_archivo, carpeta_destino) como parámetros.
        
        Returns:
            Tupla con un diccionario de archivos movidos por categoría y una lista de errores.
        """
        if not self.carpeta_descargas.exists():
            logger.error(f"La carpeta de descargas no existe: {self.carpeta_descargas}")
            return {}, [f"La carpeta de descargas no existe: {self.carpeta_descargas}"]
        
        # Diccionario para almacenar los resultados
        archivos_movidos: Dict[str, List[str]] = {}
        errores: List[str] = []
        
        # Crear la carpeta especial para otras carpetas
        carpeta_carpetas = self.carpeta_descargas / "Carpetas"
        
        # Listar todos los archivos en la carpeta de descargas
        items = list(self.carpeta_descargas.iterdir())
        
        # Primero procesar directorios
        for item in [i for i in items if i.is_dir()]:
            # Ignorar carpetas de categorías y la carpeta de carpetas
            if item.name in list(TIPOS_ARCHIVOS.keys()) + ["Otros", "Carpetas"] or item.name.startswith('.'):
                continue
            
            # Mover directorio a la carpeta de carpetas
            try:
                carpeta_carpetas.mkdir(exist_ok=True)
                destino = carpeta_carpetas / item.name
                
                # Evitar sobreescribir carpetas existentes
                if destino.exists():
                    indice = 1
                    while True:
                        nuevo_destino = carpeta_carpetas / f"{item.name}_{indice}"
                        if not nuevo_destino.exists():
                            destino = nuevo_destino
                            break
                        indice += 1
                
                shutil.move(str(item), str(destino))
                
                # Registrar movimiento
                if "Carpetas" not in archivos_movidos:
                    archivos_movidos["Carpetas"] = []
                archivos_movidos["Carpetas"].append(item.name)
                
                # Actualizar huella
                self.archivos_procesados[item.name] = f"Carpetas/{destino.name}"
                
                if callback:
                    callback(item.name, "Carpetas")
                    
                logger.info(f"Carpeta movida: {item.name} -> Carpetas/{destino.name}")
            except Exception as e:
                error_msg = f"Error al mover carpeta {item.name}: {e}"
                logger.error(error_msg)
                errores.append(error_msg)
        
        # Luego procesar archivos
        for item in [i for i in items if i.is_file()]:
            # Ignorar el archivo de huella y archivos ocultos
            if item.name == '.organized.json' or item.name.startswith('.'):
                continue
            
            # Verificar si el archivo ya fue procesado
            if item.name in self.archivos_procesados:
                logger.debug(f"Archivo ya procesado anteriormente: {item.name}")
                continue
            
            # Determinar la categoría del archivo
            categoria = self._obtener_tipo_archivo(item)
            
            try:
                # Crear la carpeta de destino si no existe
                carpeta_destino = self.carpeta_descargas / categoria
                carpeta_destino.mkdir(exist_ok=True)
                
                # Ruta de destino
                destino = carpeta_destino / item.name
                
                # Evitar sobreescribir archivos existentes
                if destino.exists():
                    indice = 1
                    nombre_base = item.stem
                    extension = item.suffix
                    while True:
                        nuevo_nombre = f"{nombre_base}_{indice}{extension}"
                        destino = carpeta_destino / nuevo_nombre
                        if not destino.exists():
                            break
                        indice += 1
                
                # Mover el archivo
                shutil.move(str(item), str(destino))
                
                # Registrar movimiento
                if categoria not in archivos_movidos:
                    archivos_movidos[categoria] = []
                archivos_movidos[categoria].append(item.name)
                
                # Actualizar huella
                self.archivos_procesados[item.name] = f"{categoria}/{destino.name}"
                
                if callback:
                    callback(item.name, categoria)
                
                logger.info(f"Archivo movido: {item.name} -> {categoria}/{destino.name}")
            except Exception as e:
                error_msg = f"Error al mover archivo {item.name}: {e}"
                logger.error(error_msg)
                errores.append(error_msg)
        
        # Guardar el archivo de huella
        self._guardar_huella()
        
        return archivos_movidos, errores 