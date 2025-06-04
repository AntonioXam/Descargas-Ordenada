#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import shutil
import stat
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('organizador')

# Definición de los tipos de archivos y sus extensiones con subcategorías
TIPOS_ARCHIVOS_DETALLADOS = {
    'Imágenes': {
        'Fotografía': ['.jpg', '.jpeg', '.raw', '.cr2', '.nef', '.orf', '.arw', '.dng', '.heic'],
        'Gráficos': ['.png', '.gif', '.bmp', '.tiff', '.webp', '.ico', '.tga'],
        'Edición': ['.psd', '.ai', '.indd', '.xcf', '.cdr', '.eps', '.afphoto', '.kra']
    },
    'Vídeos': {
        'Películas': ['.mp4', '.mkv', '.avi', '.mov', '.m4v'],
        'Clips': ['.webm', '.flv', '.3gp', '.ts', '.ogv'],
        'TV': ['.mp4', '.mkv', '.avi', '.wmv', '.m2ts', '.mts', '.divx', '.vob'],
        'Compresión': ['.h264', '.h265', '.hevc', '.vp9', '.av1']
    },
    'Audio': {
        'Música': ['.mp3', '.m4a', '.flac', '.wav', '.ogg', '.aac', '.opus', '.wma', '.alac', '.ape'],
        'Podcasts': ['.mp3', '.m4a', '.ogg', '.aac'],
        'Sonidos': ['.wav', '.mid', '.midi', '.amr', '.aiff', '.pcm', '.au', '.3ga', '.dsf', '.dff', '.mpc', '.tta'],
        'Efectos': ['.wav', '.mp3', '.ogg', '.ac3', '.dts']
    },
    'Documentos': {
        'Word': ['.doc', '.docx', '.dot', '.dotx', '.rtf'],
        'OpenOffice': ['.odt', '.fodt', '.sxw'],
        'Texto': ['.txt', '.md', '.log', '.tex', '.wpd', '.abw', '.zabw', '.lyx', '.xml', '.pub']
    },
    'Hojas de cálculo': {
        'Excel': ['.xls', '.xlsx', '.xlsm', '.xltx', '.xltm', '.csv', '.tsv'],
        'OpenOffice': ['.ods', '.fods', '.sxc'],
        'Otros': ['.numbers', '.xlr', '.gnumeric', '.dbf']
    },
    'Presentaciones': {
        'PowerPoint': ['.ppt', '.pptx', '.pps', '.ppsx', '.pptm', '.pot', '.potx'],
        'OpenOffice': ['.odp', '.fodp', '.sxi'],
        'Otros': ['.key', '.kpr', '.slk', '.sdd']
    },
    'PDFs': {
        'Documentos': ['.pdf'],
        'Electrónicos': ['.xps', '.oxps', '.djvu', '.eps', '.ps']
    },
    'Ebooks': {
        'EPUB': ['.epub'],
        'Kindle': ['.mobi', '.azw', '.azw3', '.azw4', '.kfx'],
        'Comics': ['.cbr', '.cbz'],
        'Otros': ['.djvu', '.fb2', '.ibooks', '.lit', '.lrf', '.pdb', '.prc', '.tcr', '.tpz', '.opf']
    },
    'Archivos 3D': {
        'Modelos': ['.obj', '.fbx', '.3ds', '.stl', '.ply', '.gltf', '.glb', '.x3d', '.vrml', '.3mf', '.wrl'],
        'Escenas': ['.blend', '.dae', '.max', '.c4d', '.ma', '.mb', '.xsi', '.usd', '.usda', '.usdc'],
        'Animación': ['.abc', '.bvh', '.mdd', '.fbx'],
        'Game Assets': ['.unitypackage', '.prefab', '.babylon', '.lwo', '.lxo']
    },
    'CAD': {
        'AutoCAD': ['.dwg', '.dxf', '.dwt', '.dxb'],
        'SolidWorks': ['.sldprt', '.sldasm', '.slddrw'],
        'CATIA': ['.catpart', '.catproduct'],
        'Otros': ['.step', '.stp', '.iges', '.igs', '.prt', '.asm', '.ipt', '.iam', '.solidworks', '.sat', '.scad', '.ldr', '.idw', '.ipn', '.3dm', '.skb', '.dgn', '.jt', '.x_t', '.x_b', '.3mf', '.ifc', '.skp']
    },
    'Ejecutables': {
        'Windows': ['.exe', '.msi', '.bat', '.com', '.vb', '.vbs', '.msc', '.appxbundle', '.scr'],
        'Linux': ['.sh', '.appimage', '.deb', '.rpm', '.run'],
        'macOS': ['.app', '.pkg', '.dmg'],
        'Scripts': ['.ps1', '.cmd', '.wsf', '.ahk', '.action'],
        'Java': ['.jar']
    },
    'Comprimidos': {
        'Comunes': ['.zip', '.rar', '.7z'],
        'Unix': ['.tar', '.gz', '.bz2', '.xz', '.tgz', '.txz', '.tlz', '.tbz2'],
        'Especiales': ['.iso', '.cab', '.lzh', '.lha', '.arj', '.z', '.lz', '.br', '.zst', '.lz4', '.lzma', '.ace', '.arc', '.sit', '.sitx', '.zoo', '.wim', '.zpaq']
    },
    'Código Fuente': {
        'Web': ['.html', '.htm', '.css', '.js', '.jsx', '.ts', '.tsx', '.php', '.asp', '.aspx', '.jsp'],
        'Scripts': ['.py', '.rb', '.pl', '.sh', '.ps1', '.lua', '.tcl', '.groovy', '.r'],
        'Compilados': ['.c', '.cpp', '.h', '.java', '.cs', '.swift', '.kt', '.go', '.rs', '.m', '.vb', '.f', '.f90', '.d'],
        'Datos': ['.json', '.xml', '.yaml', '.yml', '.csv', '.toml', '.ini'],
        'Otros': ['.scala', '.dart', '.jl', '.elm', '.erl', '.ex', '.exs', '.clj', '.hs', '.lisp', '.pas', '.sol', '.v', '.mq4', '.mq5', '.nim', '.zig', '.ml', '.rkt', '.kts', '.cob', '.cobol', '.pro', '.cson', '.razor']
    },
    'Web': {
        'Marcado': ['.html', '.htm', '.xhtml', '.xml', '.svg', '.xht', '.mdx', '.cshtml', '.phtml'],
        'Estilos': ['.css', '.scss', '.sass', '.less'],
        'Scripts': ['.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.wasm'],
        'Frameworks': ['.vue', '.svelte', '.astro', '.jsx', '.tsx'],
        'Datos': ['.json', '.graphql', '.gql', '.webmanifest'],
        'Config': ['.htaccess']
    },
    'Datos': {
        'Texto': ['.json', '.xml', '.yaml', '.yml', '.csv', '.tsv', '.toml', '.ini', '.conf', '.cfg', '.properties', '.env', '.ndjson', '.jsonl'],
        'Bases de datos': ['.sql', '.db', '.sqlite', '.sqlite3', '.mdb', '.accdb'],
        'Científicos': ['.parquet', '.avro', '.hdf5', '.h5', '.sav', '.biom', '.rdf', '.bson', '.onnx', '.pbtxt', '.safetensors'],
        'Configuración': ['.dat', '.proto', '.graphql']
    },
    'Imágenes de Disco': {
        'Virtuales': ['.iso', '.vhd', '.vmdk', '.vdi', '.qcow2', '.hdd', '.vhdx', '.vmx', '.vpc'],
        'Físicas': ['.img', '.bin', '.dsk', '.dmg', '.toast', '.wim', '.nrg', '.cdr', '.hfs', '.vcd', '.daa', '.udf'],
        'CD/DVD': ['.iso', '.bin', '.img', '.mdf', '.mds', '.ccd', '.cue', '.ecm']
    },
    'Fuentes': {
        'Web': ['.ttf', '.otf', '.woff', '.woff2', '.eot'],
        'Sistema': ['.ttf', '.otf', '.fnt', '.fon', '.bdf', '.pcf', '.snf', '.t42', '.suit', '.dfont', '.ttc'],
        'Edición': ['.pfb', '.afm', '.pfa', '.pfm', '.glyphs', '.sfd', '.vfb', '.vf', '.mf', '.pk']
    },
    'Configuración': {
        'Sistema': ['.ini', '.cfg', '.conf', '.config', '.reg', '.plist'],
        'Desarrollo': ['.gitconfig', '.editorconfig', '.vimrc', '.eslintrc', '.dockerignore', '.gitignore', '.npmrc', '.prettierrc'],
        'Datos': ['.json', '.xml', '.yaml', '.yml', '.properties', '.prop', '.env', '.toml'],
        'Windows': ['.inf']
    },
    'Vectoriales': {
        'Ilustración': ['.svg', '.ai', '.eps', '.cdr', '.afdesign', '.sketch', '.xd', '.figma', '.pdf'],
        'CAD': ['.dxf', '.dwg', '.dwt', '.dxb'],
        'Otros': ['.vsdx', '.emf', '.wmf', '.odg', '.ps', '.xaml', '.afpub', '.afphoto', '.cvs', '.drw', '.slddrt', '.psd', '.gdoc']
    },
    'Subtítulos': {
        'Estándar': ['.srt', '.sub', '.sbv', '.vtt', '.ass', '.ssa'],
        'Avanzados': ['.ttml', '.dfxp', '.cap', '.smi', '.rt', '.scc', '.sami', '.stl', '.itt'],
        'Especiales': ['.qt', '.jss', '.pjs', '.psb', '.usf', '.rtf', '.sup', '.idx', '.ttxt', '.srv3', '.mks']
    },
    'Backups': {
        'Editores': ['.bak', '.old', '.tmp', '.temp', '.backup', '.save', '.swp', '.swo', '.~', '.orig', '.back', '.bk', '.autosave'],
        'Sistema': ['.bkp', '.gho', '.gbk', '.tib', '.ibk', '.abk', '.gbp', '.win', '.vbk', '.arc', '.paq'],
        'Secuencias': ['.001', '.002', '.003', '.r00', '.r01', '.r02']
    },
    'Videojuegos': {
        'Guardados': ['.sav', '.save', '.dat'],
        'Recursos': ['.pak', '.bsa', '.esm', '.esp', '.mpq', '.bsp', '.upk', '.uasset', '.umap', '.unity3d', '.udk', '.wad'],
        'Mods': ['.mod', '.esm', '.esp', '.bsa', '.fomod'],
        'ROMs': ['.gba', '.nes', '.rom', '.n64', '.gb', '.z64', '.srm', '.lss']
    },
    'Diseño Técnico': {
        'PCB': ['.gerber', '.gbr', '.gbl', '.gbs', '.gbo', '.gbp', '.gtp', '.gts', '.gto', '.cam', '.brd'],
        'Esquemáticos': ['.sch', '.lbr', '.easyeda', '.kicad_pcb', '.kicad_pro', '.kicad_sch', '.lib', '.dsn'],
        'Producción': ['.alt', '.pcb', '.cmp', '.bot', '.fab', '.top']
    },
    'Malla / Geometría': {
        'Mallas': ['.msh', '.mesh', '.mdl', '.gmsh', '.off', '.ply'],
        'Ingeniería': ['.geo', '.cgr', '.cgf', '.veg', '.grp', '.ifc'],
        'Escaneo 3D': ['.e57', '.alembic', '.ptc', '.las', '.pts', '.pcd', '.pcl']
    },
    'Descargas P2P': {
        'Torrents': ['.torrent', '.magnet'],
        'Enlaces': ['.url', '.webloc', '.desktop', '.link'],
        'Metadatos': ['.nfo', '.diz', '.sfv', '.md5', '.sha1', '.crc', '.par2', '.rev']
    }
}

# Versión plana para compatibilidad
TIPOS_ARCHIVOS = {}
for categoria, subcategorias in TIPOS_ARCHIVOS_DETALLADOS.items():
    TIPOS_ARCHIVOS[categoria] = []
    for _, extensiones in subcategorias.items():
        TIPOS_ARCHIVOS[categoria].extend(extensiones)
    # Eliminar duplicados
    TIPOS_ARCHIVOS[categoria] = list(set(TIPOS_ARCHIVOS[categoria]))

class OrganizadorArchivos:
    """Clase principal para organizar archivos de la carpeta de descargas."""
    
    def __init__(self, carpeta_descargas: Optional[str] = None, usar_subcarpetas: bool = True):
        """
        Inicializa el organizador de archivos.
        
        Args:
            carpeta_descargas: Ruta a la carpeta de descargas. Si es None, se detectará automáticamente.
            usar_subcarpetas: Si es True, organiza los archivos en subcarpetas según su tipo.
        """
        self.carpeta_descargas = self._detectar_carpeta_descargas() if carpeta_descargas is None else Path(carpeta_descargas)
        self.archivo_huella = self.carpeta_descargas / '.organized.json'
        self.archivos_procesados: Dict[str, str] = {}
        self.usar_subcarpetas = usar_subcarpetas
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
        """Guarda el archivo de huella con los archivos procesados y lo oculta."""
        try:
            with open(self.archivo_huella, 'w', encoding='utf-8') as f:
                json.dump(self.archivos_procesados, f, ensure_ascii=False, indent=2)
            
            # Verificar que el archivo existe antes de intentar ocultarlo
            if self.archivo_huella.exists():
                # Ocultar el archivo en Windows
                if sys.platform == 'win32':
                    try:
                        # Usar attrib para ocultar el archivo
                        subprocess.run(["attrib", "+H", str(self.archivo_huella)], check=False)
                        logger.info(f"Archivo de huella ocultado correctamente.")
                    except Exception as e:
                        logger.warning(f"No se pudo ocultar el archivo de huella: {e}")
                # En Unix/Linux/macOS, archivos que empiezan con . ya son ocultos
            else:
                logger.warning(f"No se pudo ocultar el archivo de huella porque no existe.")
            
            logger.info(f"Archivo de huella guardado: {len(self.archivos_procesados)} archivos procesados.")
        except Exception as e:
            logger.error(f"Error al guardar archivo de huella: {e}")
    
    def _obtener_tipo_archivo(self, archivo: Path) -> Tuple[str, Optional[str]]:
        """
        Determina el tipo de archivo basado en su extensión.
        
        Args:
            archivo: Ruta al archivo a verificar.
            
        Returns:
            Tupla con (categoría, subcategoría) a la que pertenece el archivo.
            Si no usa subcarpetas, la subcategoría será None.
        """
        extension = archivo.suffix.lower()
        
        # Si estamos usando subcarpetas
        if self.usar_subcarpetas:
            for categoria, subcategorias in TIPOS_ARCHIVOS_DETALLADOS.items():
                for subcategoria, extensiones in subcategorias.items():
                    if extension in extensiones:
                        return categoria, subcategoria
            return "Otros", None
        
        # Si no usamos subcarpetas (comportamiento original)
        for categoria, extensiones in TIPOS_ARCHIVOS.items():
            if extension in extensiones:
                return categoria, None
        
        return "Otros", None
    
    def organizar(self, callback=None, organizar_subcarpetas: bool = False) -> Tuple[Dict[str, Dict[str, List[str]]], List[str]]:
        """
        Organiza los archivos de la carpeta de descargas.
        
        Args:
            callback: Función opcional a llamar por cada archivo procesado.
                     Recibe (nombre_archivo, carpeta_destino, subcarpeta_destino) como parámetros.
            organizar_subcarpetas: Si es True, organiza también archivos dentro de subcarpetas.
        
        Returns:
            Tupla con un diccionario de archivos movidos por categoría/subcategoría y una lista de errores.
        """
        if not self.carpeta_descargas.exists():
            logger.error(f"La carpeta de descargas no existe: {self.carpeta_descargas}")
            return {}, [f"La carpeta de descargas no existe: {self.carpeta_descargas}"]
        
        # Diccionario para almacenar los resultados
        archivos_movidos: Dict[str, Dict[str, List[str]]] = {}
        errores: List[str] = []
        
        # Crear la carpeta especial para otras carpetas
        carpeta_carpetas = self.carpeta_descargas / "Carpetas"
        
        # Obtener la lista de categorías para no procesarlas recursivamente
        categorias = list(TIPOS_ARCHIVOS_DETALLADOS.keys()) + ["Otros", "Carpetas"]
        
        # Función recursiva para procesar directorios
        def procesar_directorio(directorio: Path, es_raiz: bool = False):
            # Listar todos los items en el directorio
            try:
                items = list(directorio.iterdir())
            except PermissionError:
                errores.append(f"Sin permiso para acceder a {directorio}")
                return
            
            # Primero procesar directorios
            for item in [i for i in items if i.is_dir()]:
                # Si estamos en la raíz y la carpeta es una categoría, la saltamos
                if es_raiz and item.name in categorias:
                    continue
                
                # Si estamos en la raíz y la carpeta empieza con punto, la saltamos
                if es_raiz and item.name.startswith('.'):
                    continue
                
                # Si estamos organizando subcarpetas, procesamos recursivamente
                if organizar_subcarpetas and not es_raiz:
                    procesar_directorio(item)
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
                        archivos_movidos["Carpetas"] = {}
                    
                    if "General" not in archivos_movidos["Carpetas"]:
                        archivos_movidos["Carpetas"]["General"] = []
                    
                    archivos_movidos["Carpetas"]["General"].append(item.name)
                    
                    # Actualizar huella
                    ruta_relativa = os.path.join("Carpetas", destino.name)
                    self.archivos_procesados[item.name] = ruta_relativa
                    
                    if callback:
                        callback(item.name, "Carpetas", "General")
                        
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
                
                # Calcular ruta relativa desde la carpeta de descargas
                try:
                    ruta_relativa = item.relative_to(self.carpeta_descargas)
                    nombre_relativo = str(ruta_relativa)
                except ValueError:
                    # Si no se puede calcular la ruta relativa, usamos solo el nombre
                    nombre_relativo = item.name
                
                # Verificar si el archivo ya fue procesado
                if nombre_relativo in self.archivos_procesados:
                    logger.debug(f"Archivo ya procesado anteriormente: {nombre_relativo}")
                    continue
                
                # Determinar la categoría y subcategoría del archivo
                categoria, subcategoria = self._obtener_tipo_archivo(item)
                subcategoria = subcategoria or "General"
                
                try:
                    # Crear la carpeta de destino si no existe
                    carpeta_destino = self.carpeta_descargas / categoria
                    carpeta_destino.mkdir(exist_ok=True)
                    
                    # Si usamos subcarpetas, crear la subcarpeta
                    if self.usar_subcarpetas and subcategoria != "General":
                        subcarpeta_destino = carpeta_destino / subcategoria
                        subcarpeta_destino.mkdir(exist_ok=True)
                        carpeta_destino = subcarpeta_destino
                    
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
                        archivos_movidos[categoria] = {}
                    
                    if subcategoria not in archivos_movidos[categoria]:
                        archivos_movidos[categoria][subcategoria] = []
                    
                    archivos_movidos[categoria][subcategoria].append(nombre_relativo)
                    
                    # Actualizar huella
                    if self.usar_subcarpetas and subcategoria != "General":
                        ruta_relativa = os.path.join(categoria, subcategoria, destino.name)
                    else:
                        ruta_relativa = os.path.join(categoria, destino.name)
                        
                    self.archivos_procesados[nombre_relativo] = ruta_relativa
                    
                    if callback:
                        callback(nombre_relativo, categoria, subcategoria)
                    
                    logger.info(f"Archivo movido: {nombre_relativo} -> {ruta_relativa}")
                except Exception as e:
                    error_msg = f"Error al mover archivo {nombre_relativo}: {e}"
                    logger.error(error_msg)
                    errores.append(error_msg)
        
        # Iniciar procesamiento desde la raíz
        procesar_directorio(self.carpeta_descargas, es_raiz=True)
        
        # Guardar el archivo de huella
        self._guardar_huella()
        
        return archivos_movidos, errores 