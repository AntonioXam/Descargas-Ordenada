#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import subprocess
from pathlib import Path
import argparse
import platform
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('build')

def compilar_recursos():
    """Compila los recursos QRC a Python."""
    logger.info("Compilando recursos QRC...")
    
    # Comprobar si existe el directorio de recursos
    if not Path("resources").exists() or not Path("resources/resources.qrc").exists():
        logger.error("No se encontró el archivo resources.qrc en el directorio resources")
        return False
    
    # Crear directorio de salida si no existe
    Path("organizer/resources").mkdir(exist_ok=True)
    
    # Comando de compilación según plataforma
    if sys.platform == 'win32':
        cmd = ["pyside6-rcc", "-o", "organizer/resources.py", "resources/resources.qrc"]
    else:
        cmd = ["pyside6-rcc", "-o", "organizer/resources.py", "resources/resources.qrc"]
    
    try:
        subprocess.check_call(cmd)
        logger.info("Recursos compilados correctamente")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al compilar recursos: {e}")
        return False
    except FileNotFoundError:
        logger.error("No se encontró pyside6-rcc. Asegúrese de tener PySide6 instalado.")
        return False

def limpiar_build():
    """Limpia directorios de compilación anteriores."""
    logger.info("Limpiando directorios de build anteriores...")
    
    # Directorios a limpiar
    dirs_to_clean = ["build", "dist", "__pycache__"]
    dirs_to_clean.extend([p for p in Path(".").glob("**/__pycache__")])
    
    # Archivos a limpiar
    files_to_clean = [p for p in Path(".").glob("**/*.pyc")]
    files_to_clean.extend([p for p in Path(".").glob("**/*.pyo")])
    
    # Limpiar directorios
    for dir_path in dirs_to_clean:
        try:
            dir_path = Path(dir_path)
            if dir_path.exists():
                if dir_path.is_dir():
                    shutil.rmtree(dir_path)
                else:
                    dir_path.unlink()
        except Exception as e:
            logger.warning(f"No se pudo eliminar {dir_path}: {e}")
    
    # Limpiar archivos
    for file_path in files_to_clean:
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            logger.warning(f"No se pudo eliminar {file_path}: {e}")
    
    logger.info("Limpieza completada")
    return True

def construir_spec():
    """Construye el archivo .spec para PyInstaller."""
    logger.info("Creando archivo .spec...")
    
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DescargasOrdenadas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/app_icon.ico',
)
"""
    
    # Crear archivo spec
    with open("DescargasOrdenadas.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    logger.info("Archivo .spec creado correctamente")
    return True

def build_pyinstaller():
    """Construye la aplicación con PyInstaller."""
    logger.info("Construyendo con PyInstaller...")
    
    try:
        # Crear archivo .spec si no existe
        if not Path("DescargasOrdenadas.spec").exists():
            construir_spec()
        
        # Buscar pyinstaller.exe o usar el módulo de Python
        pyinstaller_cmd = "pyinstaller"
        # Intentar encontrar pyinstaller.exe en el PATH o en sitios comunes
        if sys.platform == 'win32':
            python_scripts = Path(sys.executable).parent / "Scripts"
            pyinstaller_exe = python_scripts / "pyinstaller.exe"
            
            if pyinstaller_exe.exists():
                pyinstaller_cmd = str(pyinstaller_exe)
            else:
                # Comprobar si está instalado como módulo
                try:
                    import PyInstaller
                    pyinstaller_cmd = [sys.executable, "-m", "PyInstaller"]
                except ImportError:
                    pass
        
        # Comando de construcción
        if isinstance(pyinstaller_cmd, list):
            cmd = pyinstaller_cmd + ["--clean", "--onefile", "--windowed", "--noconsole", "--name", "DescargasOrdenadas"]
        else:
            cmd = [pyinstaller_cmd, "--clean", "--onefile", "--windowed", "--noconsole", "--name", "DescargasOrdenadas"]
        
        # Añadir ícono según plataforma
        if sys.platform == 'win32':
            cmd.extend(["--icon", "resources/app_icon.ico"])
            # Añadir archivo de manifiesto para permisos de administrador en Windows
            manifest_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <!-- Windows 10 and 11 -->
      <supportedOS Id="{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}"/>
    </application>
  </compatibility>
</assembly>"""
            manifest_file = Path("win_manifest.xml")
            with open(manifest_file, "w", encoding="utf-8") as f:
                f.write(manifest_content)
            cmd.extend(["--manifest", "win_manifest.xml"])
        elif sys.platform == 'darwin':
            cmd.extend(["--icon", "resources/app_icon.icns"])
            # Añadir permisos para acceso a archivos en macOS
            cmd.extend(["--osx-bundle-identifier", "com.descargasordenadas"])
        else:
            cmd.extend(["--icon", "resources/app_icon.png"])
        
        # Añadir main.py
        cmd.append("main.py")
        
        # Ejecutar comando
        subprocess.check_call(cmd)
        
        # Crear atajos para Windows
        if sys.platform == 'win32' and Path("dist/DescargasOrdenadas.exe").exists():
            try:
                import pythoncom
                from win32com.client import Dispatch
                
                # Crear acceso directo en el escritorio
                desktop = Path(os.path.expanduser("~/Desktop"))
                if desktop.exists():
                    shortcut_path = desktop / "DescargasOrdenadas.lnk"
                    target_path = Path("dist/DescargasOrdenadas.exe").resolve()
                    
                    shell = Dispatch("WScript.Shell")
                    shortcut = shell.CreateShortCut(str(shortcut_path))
                    shortcut.Targetpath = str(target_path)
                    shortcut.WorkingDirectory = str(target_path.parent)
                    shortcut.IconLocation = str(target_path)
                    shortcut.save()
                    logger.info(f"Acceso directo creado en: {shortcut_path}")
            except Exception as e:
                logger.warning(f"No se pudo crear el acceso directo: {e}")
        
        logger.info("Construcción con PyInstaller completada")
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Error durante la construcción con PyInstaller: {e}")
        return False
    
    except FileNotFoundError:
        logger.error("No se encontró PyInstaller. Instálelo con 'pip install pyinstaller'")
        return False

def build_inno_setup_installer():
    """Construye un instalador para Windows usando Inno Setup."""
    logger.info("Construyendo instalador con Inno Setup...")
    
    try:
        # Verificar que Inno Setup está instalado
        inno_compiler = None
        possible_paths = [
            "C:/Program Files (x86)/Inno Setup 6/ISCC.exe",
            "C:/Program Files/Inno Setup 6/ISCC.exe",
            # Para versiones anteriores
            "C:/Program Files (x86)/Inno Setup 5/ISCC.exe",
            "C:/Program Files/Inno Setup 5/ISCC.exe"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                inno_compiler = path
                break
        
        if not inno_compiler:
            logger.error("No se encontró el compilador de Inno Setup (ISCC.exe). Instale Inno Setup desde https://jrsoftware.org/isdl.php")
            return False
        
        # Verificar que existe el ejecutable de PyInstaller
        if not Path("dist/DescargasOrdenadas.exe").exists():
            logger.warning("No se encontró el ejecutable en dist/. Primero se compilará con PyInstaller.")
            if not build_pyinstaller():
                return False
        
        # Verificar que existe el script de Inno Setup
        iss_file = Path("DescargasOrdenadas.iss")
        if not iss_file.exists():
            logger.error("No se encontró el archivo de script DescargasOrdenadas.iss para Inno Setup.")
            return False
        
        # Crear directorio de salida para el instalador si no existe
        Path("installer").mkdir(exist_ok=True)
        
        # Compilar con Inno Setup
        cmd = [inno_compiler, str(iss_file)]
        subprocess.check_call(cmd)
        
        if Path("installer/DescargasOrdenadas_Installer.exe").exists():
            logger.info("Instalador creado correctamente en: installer/DescargasOrdenadas_Installer.exe")
            return True
        else:
            logger.error("No se pudo generar el instalador.")
            return False
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Error durante la compilación del instalador: {e}")
        return False
    
    except Exception as e:
        logger.error(f"Error inesperado al construir el instalador: {e}")
        return False

def build_mac_app():
    """Construye la aplicación para macOS usando py2app."""
    logger.info("Construyendo para macOS con py2app...")
    
    # Crear setup.py para py2app
    setup_content = """
from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'resources/app_icon.icns',
    'plist': {
        'CFBundleName': 'DescargasOrdenadas',
        'CFBundleDisplayName': 'DescargasOrdenadas',
        'CFBundleIdentifier': 'com.descargasordenadas',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2024',
    },
    'packages': ['organizer'],
    'includes': ['PySide6', 'requests'],
}

setup(
    app=APP,
    name='DescargasOrdenadas',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
"""
    
    try:
        # Crear setup.py
        with open("setup.py", "w", encoding="utf-8") as f:
            f.write(setup_content)
        
        # Limpiar builds anteriores
        subprocess.check_call([sys.executable, "setup.py", "py2app", "--clean"])
        
        # Construir app
        subprocess.check_call([sys.executable, "setup.py", "py2app"])
        
        logger.info("Construcción con py2app completada")
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Error durante la construcción con py2app: {e}")
        return False
    
    except FileNotFoundError:
        logger.error("Error al ejecutar py2app. Instálelo con 'pip install py2app'")
        return False

def build_linux_appimage():
    """Construye la aplicación para Linux usando AppImage."""
    logger.info("Construyendo para Linux con AppImage...")
    
    try:
        # 1. Construir con PyInstaller
        if not build_pyinstaller():
            return False
        
        # 2. Crear estructura AppDir
        appdir = Path("AppDir")
        if appdir.exists():
            shutil.rmtree(appdir)
        
        appdir.mkdir()
        (appdir / "usr").mkdir()
        (appdir / "usr/bin").mkdir(parents=True)
        (appdir / "usr/share").mkdir(parents=True)
        (appdir / "usr/share/applications").mkdir(parents=True)
        (appdir / "usr/share/icons").mkdir(parents=True)
        (appdir / "usr/share/icons/hicolor").mkdir(parents=True)
        (appdir / "usr/share/icons/hicolor/256x256").mkdir(parents=True)
        (appdir / "usr/share/icons/hicolor/256x256/apps").mkdir(parents=True)
        
        # 3. Copiar el ejecutable
        shutil.copy("dist/DescargasOrdenadas", appdir / "usr/bin")
        
        # 4. Crear .desktop
        desktop_content = """[Desktop Entry]
Name=DescargasOrdenadas
Comment=Organizador de la carpeta de descargas
Exec=DescargasOrdenadas
Icon=descargasordenadas
Type=Application
Categories=Utility;
"""
        
        with open(appdir / "usr/share/applications/descargasordenadas.desktop", "w") as f:
            f.write(desktop_content)
        
        # Copiar también a la raíz de AppDir (requerido por AppImage)
        shutil.copy(appdir / "usr/share/applications/descargasordenadas.desktop", appdir)
        
        # 5. Copiar icono
        shutil.copy("resources/app_icon.png", 
                   appdir / "usr/share/icons/hicolor/256x256/apps/descargasordenadas.png")
        
        # 6. Crear AppRun
        with open(appdir / "AppRun", "w") as f:
            f.write("""#!/bin/sh
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/DescargasOrdenadas" "$@"
""")
        
        # Hacer ejecutable AppRun
        os.chmod(appdir / "AppRun", 0o755)
        
        # 7. Construir AppImage
        subprocess.check_call(["appimagetool", "AppDir", "DescargasOrdenadas.AppImage"])
        
        logger.info("Construcción de AppImage completada")
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Error durante la construcción de AppImage: {e}")
        return False
    
    except FileNotFoundError:
        logger.error("No se encontró appimagetool. Descárguelo desde https://github.com/AppImage/AppImageKit/releases")
        return False

def main():
    """Función principal."""
    # Crear parser de argumentos
    parser = argparse.ArgumentParser(description="Script de construcción para DescargasOrdenadas")
    
    # Argumentos
    parser.add_argument("--platform", choices=["win", "mac", "linux", "all"], default="auto",
                       help="Plataforma para la que construir (por defecto: detectar automáticamente)")
    parser.add_argument("--clean", action="store_true", help="Limpiar archivos de build anteriores")
    parser.add_argument("--skip-resources", action="store_true", help="Saltar la compilación de recursos QRC")
    parser.add_argument("--installer", action="store_true", help="Crear un instalador para la aplicación (sólo Windows)")
    
    args = parser.parse_args()
    
    # Detectar plataforma si es automático
    if args.platform == "auto":
        if sys.platform == "win32":
            args.platform = "win"
        elif sys.platform == "darwin":
            args.platform = "mac"
        else:
            args.platform = "linux"
    
    # Limpiar si se solicita
    if args.clean:
        limpiar_build()
    
    # Compilar recursos (saltable)
    if not args.skip_resources:
        if not compilar_recursos():
            logger.warning("Saltando la compilación de recursos y continuando con la construcción.")
            # Crear el directorio de recursos si no existe
            Path("organizer/resources").mkdir(exist_ok=True)
            # Crear un archivo resources.py vacío
            with open("organizer/resources.py", "w", encoding="utf-8") as f:
                f.write("# Archivo de recursos generado\n")
    
    # Construir según la plataforma
    if args.platform == "win" or args.platform == "all":
        logger.info("Construyendo para Windows...")
        if not build_pyinstaller():
            logger.error("Error al construir para Windows.")
            if args.platform != "all":
                return 1
        
        # Crear instalador si se solicita
        if args.installer:
            if sys.platform == "win32":
                logger.info("Creando instalador para Windows...")
                if not build_inno_setup_installer():
                    logger.error("Error al crear el instalador para Windows.")
                    return 1
            else:
                logger.error("La creación de instaladores solo está disponible en Windows.")
                return 1
    
    if args.platform == "mac" or args.platform == "all":
        logger.info("Construyendo para macOS...")
        if not build_mac_app():
            logger.error("Error al construir para macOS.")
            if args.platform != "all":
                return 1
    
    if args.platform == "linux" or args.platform == "all":
        logger.info("Construyendo para Linux...")
        if not build_linux_appimage():
            logger.error("Error al construir para Linux.")
            if args.platform != "all":
                return 1
    
    logger.info("Construcción completada.")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 