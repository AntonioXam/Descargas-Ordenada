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

# Importar nuevos módulos
try:
    from .smart_detection import DetectorInteligente
    SMART_DETECTION_AVAILABLE = True
except ImportError:
    SMART_DETECTION_AVAILABLE = False

try:
    from .custom_rules import GestorReglasPersonalizadas
    CUSTOM_RULES_AVAILABLE = True
except ImportError:
    CUSTOM_RULES_AVAILABLE = False

try:
    from .duplicate_detector import DetectorDuplicados
    DUPLICATE_DETECTOR_AVAILABLE = True
except ImportError:
    DUPLICATE_DETECTOR_AVAILABLE = False

try:
    from .notifications import notificador
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

try:
    from .ai_categorizer import CategorizadorIA
    AI_CATEGORIZER_AVAILABLE = True
except ImportError:
    AI_CATEGORIZER_AVAILABLE = False

try:
    from .real_time_monitor import MonitorTiempoReal
    REAL_TIME_MONITOR_AVAILABLE = True
except ImportError:
    REAL_TIME_MONITOR_AVAILABLE = False

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
        'Edición': ['.psd', '.ai', '.indd', '.xcf', '.cdr', '.eps', '.afphoto', '.kra'],
        'Capturas': ['.png', '.jpg', '.jpeg', '.webp', '.screenshot'],
        'Iconos': ['.ico', '.icns', '.icon'],
        'Cómics': ['.cbr', '.cbz', '.cbt'],
        'Transparentes': ['.png', '.tga', '.webp', '.gif'],
        'Memes': ['.jpg', '.jpeg', '.png', '.webp', '.gif'],
        'Wallpapers': ['.jpg', '.jpeg', '.png', '.webp']
    },
    'Vídeos': {
        'Películas': ['.mp4', '.mkv', '.avi', '.mov', '.m4v'],
        'Clips': ['.webm', '.flv', '.3gp', '.ts', '.ogv'],
        'TV': ['.mp4', '.mkv', '.avi', '.wmv', '.m2ts', '.mts', '.divx', '.vob'],
        'Compresión': ['.h264', '.h265', '.hevc', '.vp9', '.av1'],
        'Grabaciones': ['.mp4', '.mkv', '.mov', '.avi'],
        'Tutoriales': ['.mp4', '.mkv', '.mov', '.webm'],
        'Animación': ['.mp4', '.mkv', '.mov', '.avi', '.webm'],
        'Webcam': ['.mp4', '.webm', '.mov', '.avi']
    },
    'Audio': {
        'Música': ['.mp3', '.m4a', '.flac', '.wav', '.ogg', '.aac', '.opus', '.wma', '.alac', '.ape'],
        'Podcasts': ['.mp3', '.m4a', '.ogg', '.aac'],
        'Sonidos': ['.wav', '.mid', '.midi', '.amr', '.aiff', '.pcm', '.au', '.3ga', '.dsf', '.dff', '.mpc', '.tta'],
        'Efectos': ['.wav', '.mp3', '.ogg', '.ac3', '.dts'],
        'Grabaciones': ['.mp3', '.wav', '.ogg', '.m4a', '.aac'],
        'Audiolibros': ['.mp3', '.m4a', '.m4b', '.aac', '.flac', '.ogg'],
        'Instrumentales': ['.mp3', '.wav', '.flac', '.midi']
    },
    'Documentos': {
        'Word': ['.doc', '.docx', '.dot', '.dotx', '.rtf'],
        'OpenOffice': ['.odt', '.fodt', '.sxw'],
        'Texto': ['.txt', '.md', '.log', '.tex', '.wpd', '.abw', '.zabw', '.lyx', '.pub'],
        'Facturas': ['.docx', '.xlsx', '.odt', '.csv'],  # Quitamos PDF de aquí
        'Informes': ['.docx', '.odt', '.md', '.txt'],     # Quitamos PDF de aquí
        'Académicos': ['.docx', '.tex', '.md', '.txt'],   # Quitamos PDF de aquí  
        'Manuales': ['.docx', '.txt', '.md', '.odt'],     # Quitamos PDF de aquí
        'Contratos': ['.docx', '.doc', '.odt'],           # Quitamos PDF de aquí
        'Certificados': ['.cer', '.crt', '.pem', '.p12', '.pfx', '.key']  # Quitamos PDF de aquí
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
        'Electrónicos': ['.xps', '.oxps', '.djvu', '.eps', '.ps'],
        'Formularios': ['.pdf'],
        'Escaneados': ['.pdf'],
        'Manuales': ['.pdf'],
        'Libros': ['.pdf']
    },
    'Ebooks': {
        'EPUB': ['.epub'],
        'Kindle': ['.mobi', '.azw', '.azw3', '.azw4', '.kfx'],
        'Comics': ['.cbr', '.cbz'],
        'Otros': ['.djvu', '.fb2', '.ibooks', '.lit', '.lrf', '.pdb', '.prc', '.tcr', '.tpz', '.opf']
    },
    'Archivos 3D': {
        'Modelos': ['.obj', '.fbx', '.3ds', '.stl', '.ply', '.gltf', '.glb', '.x3d', '.vrml', '.3mf', '.wrl', '.step', '.stp', '.iges', '.dae'],
        'Escenas': ['.blend', '.dae', '.max', '.c4d', '.ma', '.mb', '.xsi', '.usd', '.usda', '.usdc'],
        'Animación': ['.abc', '.bvh', '.mdd', '.fbx'],
        'Game Assets': ['.unitypackage', '.prefab', '.babylon', '.lwo', '.lxo'],
        'Impresión 3D': ['.3mf', '.stl', '.obj', '.amf', '.x3d', '.gcode']
    },
    'CAD': {
        'AutoCAD': ['.dwg', '.dxf', '.dwt', '.dxb'],
        'SolidWorks': ['.sldprt', '.sldasm', '.slddrw'],
        'CATIA': ['.catpart', '.catproduct'],
        'Otros': ['.step', '.stp', '.iges', '.igs', '.prt', '.asm', '.ipt', '.iam', '.solidworks', '.sat', '.scad', '.ldr', '.idw', '.ipn', '.3dm', '.skb', '.dgn', '.jt', '.x_t', '.x_b', '.3mf', '.ifc', '.skp']
    },
    'Ejecutables': {
        'Windows': ['.exe', '.msi', '.bat', '.com', '.vb', '.vbs', '.msc', '.appxbundle', '.scr', '.cmd', '.reg'],
        'Linux': ['.sh', '.appimage', '.deb', '.rpm', '.run', '.snap', '.flatpak', '.bin'],
        'macOS': ['.app', '.pkg', '.dmg', '.mpkg'],
        'Android': ['.apk', '.xapk', '.aab', '.apks'],  # AÑADIMOS APKs AQUÍ
        'iOS': ['.ipa', '.deb'],
        'Scripts': ['.ps1', '.cmd', '.wsf', '.ahk', '.action', '.vbs', '.js', '.py'],
        'Java': ['.jar', '.jnlp'],
        'Otros': ['.air', '.crx', '.xpi', '.vsix', '.nupkg']
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
        'Proyectos': ['.sln', '.csproj', '.vcxproj', '.pbxproj', '.xcodeproj', '.suo', '.sdf', '.iml', '.pyproj'],
        'IDE': ['.idea', '.vscode', '.vs', '.sublime-project', '.sublime-workspace'],
        'Bibliotecas': ['.jar', '.dll', '.so', '.a', '.lib', '.pyd', '.dylib'],
        'Markdown': ['.md', '.markdown', '.mdown', '.mkd'],
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
        'Diagramas': ['.drawio', '.vsdx', '.dia', '.diag', '.erd'],
        'Otros': ['.emf', '.wmf', '.odg', '.ps', '.xaml', '.afpub', '.afphoto', '.cvs', '.drw', '.slddrt', '.psd', '.gdoc']
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
        'Guardados': ['.sav', '.save', '.dat', '.gam', '.sg', '.mcr', '.vms', '.mem', '.srm'],
        'Recursos': ['.pak', '.bsa', '.esm', '.esp', '.mpq', '.bsp', '.upk', '.uasset', '.umap', '.unity3d', '.udk', '.wad', '.vpk', '.gcf', '.ncf', '.pk3', '.pk4'],
        'Mods': ['.mod', '.esm', '.esp', '.bsa', '.fomod', '.mcpack', '.mcworld', '.mctemplate'],
        'ROMs': ['.gba', '.nes', '.rom', '.n64', '.gb', '.gbc', '.z64', '.v64', '.srm', '.lss', '.nds', '.3ds', '.cia', '.nsp', '.xci', '.wbfs', '.gcm', '.iso', '.cso', '.pbp', '.psp', '.vb', '.ngp', '.ngc', '.lnx', '.ws', '.wsc', '.pce', '.sgx'],
        'Switch': ['.nsp', '.nsz', '.xci', '.xcz'],
        'PlayStation': ['.iso', '.cso', '.pbp', '.bin', '.img', '.cue', '.pkg'],
        'Xbox': ['.iso', '.xiso', '.gdf', '.xbe', '.xex', '.xcp'],
        'Steam': ['.vpk', '.gcf', '.ncf', '.acf'],
        'Configuración': ['.ini', '.cfg', '.config', '.properties']
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
    },
    'Móviles': {
        'Android': ['.apk', '.xapk', '.aab', '.apks', '.dex', '.odex', '.vdex'],
        'iOS': ['.ipa', '.deb', '.plist', '.mobileprovision'],
        'Recursos': ['.asar', '.unity3d', '.obb', '.zip'],
        'Configuración': ['.xml', '.json', '.plist', '.properties']
    },
    'Criptomonedas': {
        'Wallets': ['.wallet', '.dat', '.keys'],
        'Blockchain': ['.blk', '.blockchain', '.block'],
        'Configuración': ['.conf', '.config', '.json']
    },
    'Machine Learning': {
        'Modelos': ['.pkl', '.pickle', '.h5', '.hdf5', '.pb', '.onnx', '.pt', '.pth', '.safetensors'],
        'Datos': ['.csv', '.parquet', '.tfrecord', '.npy', '.npz'],
        'Notebooks': ['.ipynb', '.rmd']
    },
    'Virtualización': {
        'Docker': ['.dockerfile', '.docker', '.dockerignore'],
        'VMs': ['.vmdk', '.vdi', '.vhd', '.vhdx', '.qcow2', '.ova', '.ovf'],
        'Vagrant': ['.vagrantfile']
    },
    'Otros': {
        'Desconocidos': ['.*'],
        'Sin_Clasificar': [],
        'Binarios': ['.bin', '.dat', '.blob', '.dump', '.raw'],
        'Temporales': ['.tmp', '.temp', '.bak', '.old', '.cache', '.crdownload', '.part'],
        'Metadatos': ['.meta', '.metadata', '.info', '.nfo', '.diz', '.sfv'],
        'Sistemas': ['.sys', '.dll', '.so', '.dylib', '.pdb'],
        'Logs': ['.log', '.out', '.err', '.trace']
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
        # Cambiar la ubicación del archivo de huella a una carpeta oculta dentro de Descargas
        self.carpeta_config = self.carpeta_descargas / ".config"
        self.carpeta_config.mkdir(exist_ok=True)
        self.archivo_huella = self.carpeta_config / 'organized.json'
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
            # Asegurar que la carpeta de configuración existe
            self.carpeta_config.mkdir(exist_ok=True)
            
            with open(self.archivo_huella, 'w', encoding='utf-8') as f:
                json.dump(self.archivos_procesados, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Archivo de huella guardado: {len(self.archivos_procesados)} archivos procesados.")
        except Exception as e:
            logger.error(f"Error al guardar archivo de huella: {e}")
    
    def _obtener_tipo_archivo(self, archivo: Path) -> Tuple[str, Optional[str]]:
        """
        Determina el tipo de archivo basado en su extensión con lógica de priorización.
        
        Args:
            archivo: Ruta al archivo a verificar.
            
        Returns:
            Tupla con (categoría, subcategoría) a la que pertenece el archivo.
            Si no usa subcarpetas, la subcategoría será None.
        """
        extension = archivo.suffix.lower()
        
        # Priorización especial para extensiones que aparecen en múltiples categorías
        prioridades_especificas = {
            '.pdf': ('PDFs', 'Documentos'),
            '.apk': ('Ejecutables', 'Android'),
            '.ipa': ('Ejecutables', 'iOS'),
            '.iso': ('Imágenes de Disco', 'CD/DVD'),
            '.bin': ('Imágenes de Disco', 'Físicas'),
            '.img': ('Imágenes de Disco', 'Físicas'),
            '.json': ('Código Fuente', 'Datos'),
            '.xml': ('Código Fuente', 'Datos'),
            '.ini': ('Configuración', 'Sistema'),  # Priorizar .ini como Configuración
            '.cfg': ('Configuración', 'Sistema'),  # Archivos de configuración
            '.conf': ('Configuración', 'Sistema'),
            '.py': ('Código Fuente', 'Scripts'),  # Priorizar Python como Código Fuente
            '.js': ('Código Fuente', 'Web'),      # Priorizar JavaScript como Código Fuente
            '.nsp': ('Videojuegos', 'Switch'),
            '.xci': ('Videojuegos', 'Switch'),
            '.dat': ('Videojuegos', 'Guardados'),
            '.sav': ('Videojuegos', 'Guardados'),
            '.torrent': ('Descargas P2P', 'Torrents')
        }
        
        # Si la extensión tiene prioridad específica, usarla
        if extension in prioridades_especificas:
            categoria_prioritaria, subcategoria_prioritaria = prioridades_especificas[extension]
            return categoria_prioritaria, subcategoria_prioritaria if self.usar_subcarpetas else None
        
        # Si estamos usando subcarpetas
        if self.usar_subcarpetas:
            # Buscar en el orden definido, pero evitar duplicados por priorización
            for categoria, subcategorias in TIPOS_ARCHIVOS_DETALLADOS.items():
                for subcategoria, extensiones in subcategorias.items():
                    if extension in extensiones:
                        return categoria, subcategoria
            
            # Si no se encontró una categoría específica, añadir a "Otros/Desconocidos"
            return "Otros", "Desconocidos"
        
        # Si no usamos subcarpetas (comportamiento original)
        # Aplicar priorización también aquí
        categorias_priorizadas = {
            '.pdf': 'PDFs',
            '.apk': 'Ejecutables',
            '.iso': 'Imágenes de Disco',
            '.torrent': 'Descargas P2P'
        }
        
        if extension in categorias_priorizadas:
            return categorias_priorizadas[extension], None
        
        for categoria, extensiones in TIPOS_ARCHIVOS.items():
            if extension in extensiones:
                return categoria, None
        
        # Si no se encontró una categoría, añadir a "Otros"
        return "Otros", None
    
    def reorganizar_completamente(self, callback=None) -> Tuple[Dict[str, Dict[str, List[str]]], List[str]]:
        """
        Reorganiza TODOS los archivos de forma recursiva, incluso los ya organizados.
        Útil para reorganizar archivos que pueden haber cambiado de lugar o categoría.
        
        Args:
            callback: Función opcional a llamar por cada archivo procesado.
        
        Returns:
            Tupla con un diccionario de archivos movidos por categoría/subcategoría y una lista de errores.
        """
        if not self.carpeta_descargas.exists():
            logger.error(f"La carpeta de descargas no existe: {self.carpeta_descargas}")
            return {}, [f"La carpeta de descargas no existe: {self.carpeta_descargas}"]
        
        logger.info("🔄 Iniciando reorganización completa de todos los archivos...")
        
        # Diccionario para almacenar los resultados
        archivos_movidos: Dict[str, Dict[str, List[str]]] = {}
        errores: List[str] = []
        
        # Obtener la lista de categorías para reconocerlas
        categorias = list(TIPOS_ARCHIVOS_DETALLADOS.keys()) + ["Otros", "Carpetas"]
        
        # Lista para almacenar todos los archivos encontrados
        todos_los_archivos: List[Path] = []
        
        # Función recursiva para encontrar TODOS los archivos
        def encontrar_archivos_recursivamente(directorio: Path):
            try:
                for item in directorio.iterdir():
                    if item.is_file():
                        # Ignorar archivos del sistema y configuración
                        if not item.name.startswith('.') and item.name not in ['desktop.ini', 'Thumbs.db']:
                            todos_los_archivos.append(item)
                    elif item.is_dir():
                        # No procesar carpetas del sistema o configuración
                        if not item.name.startswith('.') and item.name not in ['$RECYCLE.BIN', 'System Volume Information']:
                            encontrar_archivos_recursivamente(item)
            except PermissionError:
                errores.append(f"Sin permiso para acceder a {directorio}")
        
        # Encontrar todos los archivos recursivamente
        logger.info("📁 Escaneando todos los archivos...")
        encontrar_archivos_recursivamente(self.carpeta_descargas)
        
        logger.info(f"📋 Se encontraron {len(todos_los_archivos)} archivos para reorganizar")
        
        # Procesar cada archivo
        archivos_procesados = 0
        for archivo in todos_los_archivos:
            try:
                # Calcular ruta relativa desde la carpeta de descargas
                try:
                    ruta_relativa = archivo.relative_to(self.carpeta_descargas)
                    nombre_relativo = str(ruta_relativa)
                except ValueError:
                    nombre_relativo = archivo.name
                
                # Determinar la categoría y subcategoría correcta del archivo
                categoria, subcategoria = self._obtener_tipo_archivo(archivo)
                subcategoria = subcategoria or "General"
                
                # Determinar dónde DEBERÍA estar el archivo
                carpeta_destino_correcta = self.carpeta_descargas / categoria
                if self.usar_subcarpetas and subcategoria != "General":
                    carpeta_destino_correcta = carpeta_destino_correcta / subcategoria
                
                destino_correcto = carpeta_destino_correcta / archivo.name
                
                # Verificar si el archivo ya está en el lugar correcto
                if archivo.parent == carpeta_destino_correcta and archivo.exists():
                    logger.debug(f"✅ Archivo ya está correctamente ubicado: {nombre_relativo}")
                    continue
                
                # El archivo necesita ser movido
                logger.info(f"🔄 Reorganizando: {nombre_relativo} -> {categoria}/{subcategoria}")
                
                # Crear la carpeta de destino si no existe
                carpeta_destino_correcta.mkdir(parents=True, exist_ok=True)
                
                # Evitar sobreescribir archivos existentes
                if destino_correcto.exists() and destino_correcto != archivo:
                    indice = 1
                    nombre_base = archivo.stem
                    extension = archivo.suffix
                    while True:
                        nuevo_nombre = f"{nombre_base}_{indice}{extension}"
                        destino_correcto = carpeta_destino_correcta / nuevo_nombre
                        if not destino_correcto.exists():
                            break
                        indice += 1
                
                # Mover el archivo
                shutil.move(str(archivo), str(destino_correcto))
                
                # Registrar movimiento
                if categoria not in archivos_movidos:
                    archivos_movidos[categoria] = {}
                
                if subcategoria not in archivos_movidos[categoria]:
                    archivos_movidos[categoria][subcategoria] = []
                
                archivos_movidos[categoria][subcategoria].append(nombre_relativo)
                
                # Actualizar huella
                if self.usar_subcarpetas and subcategoria != "General":
                    ruta_relativa_final = os.path.join(categoria, subcategoria, destino_correcto.name)
                else:
                    ruta_relativa_final = os.path.join(categoria, destino_correcto.name)
                    
                self.archivos_procesados[nombre_relativo] = ruta_relativa_final
                
                if callback:
                    callback(nombre_relativo, categoria, subcategoria)
                
                archivos_procesados += 1
                
            except Exception as e:
                error_msg = f"Error al reorganizar archivo {archivo.name}: {e}"
                logger.error(error_msg)
                errores.append(error_msg)
        
        # Limpiar carpetas vacías
        self._limpiar_carpetas_vacias()
        
        # Guardar el archivo de huella
        self._guardar_huella()
        
        logger.info(f"✅ Reorganización completa finalizada. {archivos_procesados} archivos reorganizados.")
        
        return archivos_movidos, errores
    
    def _limpiar_carpetas_vacias(self):
        """Elimina carpetas vacías después de la reorganización"""
        try:
            # Obtener la lista de categorías para no eliminarlas
            categorias = list(TIPOS_ARCHIVOS_DETALLADOS.keys()) + ["Otros", "Carpetas"]
            
            def eliminar_si_vacia(directorio: Path):
                if not directorio.exists() or not directorio.is_dir():
                    return
                
                try:
                    # Primero, procesar subdirectorios recursivamente
                    for subdir in [d for d in directorio.iterdir() if d.is_dir()]:
                        eliminar_si_vacia(subdir)
                    
                    # Verificar si el directorio está vacío (solo considera archivos visibles)
                    contenido = [item for item in directorio.iterdir() 
                                if not item.name.startswith('.') 
                                and item.name not in ['desktop.ini', 'Thumbs.db']]
                    
                    # Si está vacío y no es una carpeta de categoría principal, eliminarla
                    if not contenido and directorio.name not in categorias:
                        # No eliminar si es una subcarpeta directa de la raíz
                        if directorio.parent != self.carpeta_descargas:
                            directorio.rmdir()
                            logger.info(f"🗑️ Carpeta vacía eliminada: {directorio.name}")
                
                except (OSError, PermissionError) as e:
                    logger.debug(f"No se pudo eliminar carpeta {directorio}: {e}")
            
            # Empezar desde la carpeta de descargas
            for item in self.carpeta_descargas.iterdir():
                if item.is_dir() and item.name not in categorias and not item.name.startswith('.'):
                    eliminar_si_vacia(item)
                    
        except Exception as e:
            logger.error(f"Error al limpiar carpetas vacías: {e}")

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
        
        # Lista para hacer seguimiento de archivos no procesados
        archivos_no_procesados: List[Path] = []
        
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
                if item.name.startswith('.') or (self.carpeta_config in item.parents and self.carpeta_config is not None):
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
                    archivos_no_procesados.append(item)
        
        # Iniciar procesamiento desde la raíz
        procesar_directorio(self.carpeta_descargas, es_raiz=True)
        
        # Verificar si quedaron archivos sin procesar y realizar un segundo intento
        if archivos_no_procesados:
            logger.warning(f"Se encontraron {len(archivos_no_procesados)} archivos que no pudieron ser procesados. Realizando un segundo intento...")
            
            for archivo in archivos_no_procesados:
                if not archivo.exists():
                    continue
                    
                try:
                    # Determinar la categoría del archivo
                    categoria = "Otros"
                    subcategoria = "Sin_Clasificar"
                    
                    # Crear la carpeta de destino si no existe
                    carpeta_destino = self.carpeta_descargas / categoria
                    carpeta_destino.mkdir(exist_ok=True)
                    
                    # Si usamos subcarpetas, crear la subcarpeta
                    if self.usar_subcarpetas:
                        subcarpeta_destino = carpeta_destino / subcategoria
                        subcarpeta_destino.mkdir(exist_ok=True)
                        carpeta_destino = subcarpeta_destino
                    
                    # Ruta de destino
                    destino = carpeta_destino / archivo.name
                    
                    # Evitar sobreescribir archivos existentes
                    if destino.exists():
                        indice = 1
                        nombre_base = archivo.stem
                        extension = archivo.suffix
                        while True:
                            nuevo_nombre = f"{nombre_base}_{indice}{extension}"
                            destino = carpeta_destino / nuevo_nombre
                            if not destino.exists():
                                break
                            indice += 1
                    
                    # Mover el archivo
                    shutil.move(str(archivo), str(destino))
                    
                    # Registrar movimiento
                    if categoria not in archivos_movidos:
                        archivos_movidos[categoria] = {}
                    
                    if subcategoria not in archivos_movidos[categoria]:
                        archivos_movidos[categoria][subcategoria] = []
                    
                    try:
                        nombre_relativo = str(archivo.relative_to(self.carpeta_descargas))
                    except ValueError:
                        nombre_relativo = archivo.name
                        
                    archivos_movidos[categoria][subcategoria].append(nombre_relativo)
                    
                    # Actualizar huella
                    if self.usar_subcarpetas:
                        ruta_relativa = os.path.join(categoria, subcategoria, destino.name)
                    else:
                        ruta_relativa = os.path.join(categoria, destino.name)
                        
                    self.archivos_procesados[nombre_relativo] = ruta_relativa
                    
                    if callback:
                        callback(nombre_relativo, categoria, subcategoria)
                    
                    logger.info(f"Archivo movido en segundo intento: {nombre_relativo} -> {ruta_relativa}")
                except Exception as e:
                    error_msg = f"Error al mover archivo en segundo intento {archivo.name}: {e}"
                    logger.error(error_msg)
                    errores.append(error_msg)
        
        # Guardar el archivo de huella
        self._guardar_huella()
        
        # Notificar si está disponible
        archivos_movidos_count = sum(sum(len(sub) for sub in cat.values()) for cat in archivos_movidos.values())
        if NOTIFICATIONS_AVAILABLE and archivos_movidos_count > 0:
            try:
                categorias_usadas = len(archivos_movidos)
                notificador.notificar_organizacion(archivos_movidos_count, categorias_usadas)
            except Exception as e:
                logger.debug(f"Error enviando notificación: {e}")
        
        return archivos_movidos, errores
    
    # ===== NUEVAS FUNCIONALIDADES AVANZADAS =====
    
    def inicializar_modulos_avanzados(self):
        """Inicializa todos los módulos avanzados disponibles."""
        # Inicializar nuevos módulos
        self.detector_inteligente = None
        self.gestor_reglas = None
        self.detector_duplicados = None
        self.categorizador_ia = None
        self.monitor_tiempo_real = None
        
        # Inicializar módulos disponibles
        if SMART_DETECTION_AVAILABLE:
            try:
                from .smart_detection import DetectorInteligente
                self.detector_inteligente = DetectorInteligente()
                logger.info("🧠 Detección inteligente activada")
            except Exception as e:
                logger.warning(f"Error inicializando detección inteligente: {e}")
        
        if CUSTOM_RULES_AVAILABLE:
            try:
                from .custom_rules import GestorReglasPersonalizadas
                self.gestor_reglas = GestorReglasPersonalizadas(self.carpeta_descargas)
                logger.info("🎨 Reglas personalizadas activadas")
            except Exception as e:
                logger.warning(f"Error inicializando reglas personalizadas: {e}")
        
        if DUPLICATE_DETECTOR_AVAILABLE:
            try:
                from .duplicate_detector import DetectorDuplicados
                self.detector_duplicados = DetectorDuplicados(self.carpeta_descargas)
                logger.info("🔍 Detector de duplicados activado")
            except Exception as e:
                logger.warning(f"Error inicializando detector de duplicados: {e}")
        
        if AI_CATEGORIZER_AVAILABLE:
            try:
                from .ai_categorizer import CategorizadorIA
                self.categorizador_ia = CategorizadorIA(self.carpeta_descargas)
                logger.info("🤖 Categorizador IA activado")
            except Exception as e:
                logger.warning(f"Error inicializando categorizador IA: {e}")
        
        if REAL_TIME_MONITOR_AVAILABLE:
            try:
                from .real_time_monitor import MonitorTiempoReal
                self.monitor_tiempo_real = MonitorTiempoReal(
                    self.carpeta_descargas,
                    self._organizar_archivo_individual
                )
                logger.info("🔄 Monitor tiempo real disponible")
            except Exception as e:
                logger.warning(f"Error inicializando monitor tiempo real: {e}")
        
        # Configurar notificaciones
        if NOTIFICATIONS_AVAILABLE:
            try:
                logger.info("🔔 Notificaciones activadas")
            except Exception as e:
                logger.warning(f"Error configurando notificaciones: {e}")
    
    def _organizar_archivo_individual(self, archivo: Path):
        """
        Organiza un archivo individual usando todas las técnicas disponibles.
        Usado por el monitor en tiempo real.
        """
        try:
            categoria, subcategoria = self._obtener_tipo_archivo_avanzado(archivo)
            
            # Determinar carpeta destino
            carpeta_destino = self.carpeta_descargas / categoria
            if self.usar_subcarpetas and subcategoria and subcategoria != "General":
                carpeta_destino = carpeta_destino / subcategoria
            
            # Crear carpeta si no existe
            carpeta_destino.mkdir(parents=True, exist_ok=True)
            
            # Mover archivo
            destino_final = carpeta_destino / archivo.name
            if not destino_final.exists():
                shutil.move(str(archivo), str(destino_final))
                logger.info(f"📂 Archivo organizado automáticamente: {archivo.name} → {categoria}")
                
                # Notificar archivo individual
                if NOTIFICATIONS_AVAILABLE:
                    try:
                        notificador.notificar_archivo_nuevo(archivo.name, categoria)
                    except Exception as e:
                        logger.debug(f"Error notificando archivo: {e}")
        
        except Exception as e:
            logger.error(f"Error organizando archivo {archivo}: {e}")
    
    def _obtener_tipo_archivo_avanzado(self, archivo: Path) -> Tuple[str, Optional[str]]:
        """
        Determina el tipo de archivo usando todos los métodos disponibles:
        1. Reglas personalizadas (prioridad máxima)
        2. IA categorización
        3. Detección inteligente por contenido
        4. Método original por extensión
        """
        # 1. Verificar reglas personalizadas primero
        if self.gestor_reglas:
            try:
                resultado_reglas = self.gestor_reglas.obtener_categoria(archivo)
                if resultado_reglas:
                    categoria, subcategoria = resultado_reglas
                    logger.debug(f"Categorizado por regla personalizada: {archivo.name} → {categoria}/{subcategoria}")
                    return categoria, subcategoria
            except Exception as e:
                logger.debug(f"Error en reglas personalizadas: {e}")
        
        # 2. Intentar IA categorización
        if self.categorizador_ia:
            try:
                resultado_ia = self.categorizador_ia.analizar_nombre_archivo(archivo)
                if resultado_ia:
                    categoria, confianza = resultado_ia
                    # Buscar subcategoría apropiada en los tipos detallados
                    subcategoria = "General"
                    if categoria in TIPOS_ARCHIVOS_DETALLADOS:
                        extension = archivo.suffix.lower()
                        for sub, extensiones in TIPOS_ARCHIVOS_DETALLADOS[categoria].items():
                            if extension in extensiones:
                                subcategoria = sub
                                break
                    
                    logger.debug(f"Categorizado por IA: {archivo.name} → {categoria} (confianza: {confianza:.2f})")
                    
                    # Entrenar la IA con esta decisión
                    self.categorizador_ia.entrenar_con_decision(archivo, categoria, subcategoria, True)
                    
                    return categoria, subcategoria
            except Exception as e:
                logger.debug(f"Error en IA categorización: {e}")
        
        # 3. Intentar detección inteligente por contenido
        if self.detector_inteligente:
            try:
                resultado_inteligente = self.detector_inteligente.detectar_tipo_inteligente(archivo)
                if resultado_inteligente[0] != "Otros":
                    categoria, subcategoria = resultado_inteligente
                    logger.debug(f"Categorizado por detección inteligente: {archivo.name} → {categoria}/{subcategoria}")
                    return categoria, subcategoria
            except Exception as e:
                logger.debug(f"Error en detección inteligente: {e}")
        
        # 4. Fallback al método original
        return self._obtener_tipo_archivo(archivo)
    
    def iniciar_monitor_tiempo_real(self, delay_segundos: int = 3) -> bool:
        """
        Inicia el monitor en tiempo real para organización automática.
        
        Args:
            delay_segundos: Segundos a esperar antes de organizar un archivo
            
        Returns:
            True si se inició correctamente
        """
        if not hasattr(self, 'monitor_tiempo_real') or not self.monitor_tiempo_real:
            self.inicializar_modulos_avanzados()
        
        if not self.monitor_tiempo_real:
            logger.error("Monitor en tiempo real no disponible")
            return False
        
        exito = self.monitor_tiempo_real.iniciar(delay_segundos)
        
        if exito and NOTIFICATIONS_AVAILABLE:
            try:
                notificador.notificar_monitor_iniciado(str(self.carpeta_descargas))
            except Exception as e:
                logger.debug(f"Error notificando inicio de monitor: {e}")
        
        return exito
    
    def detener_monitor_tiempo_real(self):
        """Detiene el monitor en tiempo real."""
        if hasattr(self, 'monitor_tiempo_real') and self.monitor_tiempo_real:
            self.monitor_tiempo_real.detener()
    
    def esta_monitor_activo(self) -> bool:
        """Verifica si el monitor en tiempo real está activo."""
        if hasattr(self, 'monitor_tiempo_real') and self.monitor_tiempo_real:
            return self.monitor_tiempo_real.esta_activo()
        return False
    
    def escanear_duplicados(self, incluir_subcarpetas: bool = True) -> Dict[str, Any]:
        """
        Escanea archivos duplicados en la carpeta.
        
        Args:
            incluir_subcarpetas: Si incluir subcarpetas en el escaneo
            
        Returns:
            Diccionario con resultados del escaneo
        """
        if not hasattr(self, 'detector_duplicados') or not self.detector_duplicados:
            self.inicializar_modulos_avanzados()
        
        if not self.detector_duplicados:
            return {'error': 'Detector de duplicados no disponible'}
        
        return self.detector_duplicados.escanear_duplicados(incluir_subcarpetas)
    
    def eliminar_duplicados(self, estrategia: str = 'mas_nuevo', confirmar: bool = False) -> Dict[str, Any]:
        """
        Elimina archivos duplicados según una estrategia.
        
        Args:
            estrategia: 'mas_nuevo', 'mas_viejo', 'carpeta_principal'
            confirmar: Si ejecutar la eliminación o solo simular
            
        Returns:
            Diccionario con resultados de la eliminación
        """
        if not hasattr(self, 'detector_duplicados') or not self.detector_duplicados:
            return {'error': 'Detector de duplicados no disponible'}
        
        resultado = self.detector_duplicados.eliminar_duplicados(estrategia, confirmar)
        
        # Notificar si hay duplicados eliminados
        if confirmar and resultado.get('archivos_eliminados', 0) > 0 and NOTIFICATIONS_AVAILABLE:
            try:
                notificador.notificar_duplicados(
                    resultado['archivos_eliminados'],
                    resultado['espacio_liberado_legible']
                )
            except Exception as e:
                logger.debug(f"Error notificando duplicados: {e}")
        
        return resultado
    
    def obtener_estado_modulos(self) -> Dict[str, bool]:
        """Obtiene el estado de todos los módulos avanzados."""
        return {
            'deteccion_inteligente': SMART_DETECTION_AVAILABLE and hasattr(self, 'detector_inteligente') and self.detector_inteligente is not None,
            'reglas_personalizadas': CUSTOM_RULES_AVAILABLE and hasattr(self, 'gestor_reglas') and self.gestor_reglas is not None,
            'detector_duplicados': DUPLICATE_DETECTOR_AVAILABLE and hasattr(self, 'detector_duplicados') and self.detector_duplicados is not None,
            'notificaciones': NOTIFICATIONS_AVAILABLE,
            'ia_categorizacion': AI_CATEGORIZER_AVAILABLE and hasattr(self, 'categorizador_ia') and self.categorizador_ia is not None,
            'monitor_tiempo_real': REAL_TIME_MONITOR_AVAILABLE and hasattr(self, 'monitor_tiempo_real') and self.monitor_tiempo_real is not None,
            'monitor_activo': self.esta_monitor_activo()
        } 