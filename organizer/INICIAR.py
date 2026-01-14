#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🍄 DescargasOrdenadas v3.0 - Edición Portable
Creado por Champi 🍄

Punto de entrada único para la aplicación de organización automática de archivos.
"""

import sys
import os
from pathlib import Path

# Asegurar que el directorio padre está en el path para importar organizer
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse
import logging
import importlib.util
import subprocess
import time

def instalar_dependencia(package_name):
    """Instala una dependencia automáticamente."""
    try:
        print(f"📦 Instalando {package_name}...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", package_name,
            "--quiet", "--disable-pip-version-check"
        ])
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Error al instalar {package_name}")
        return False

def verificar_dependencias():
    """Verifica e instala dependencias automáticamente."""
    required_packages = [
        ("pillow", "PIL"),
        ("PySide6", "PySide6"),
        ("watchdog", "watchdog")
    ]
    
    if sys.platform == "win32":
        required_packages.append(("pywin32", "win32api"))
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            importlib.import_module(import_name)
        except ImportError:
            missing_packages.append((package_name, import_name))
    
    if missing_packages:
        print("🔧 Instalando dependencias automáticamente...")
        
        for package_name, import_name in missing_packages:
            if package_name == "pywin32" and sys.platform == "win32":
                print("🪟 Instalando pywin32 para Windows...")
                instalar_dependencia(package_name)
            else:
                if not instalar_dependencia(package_name):
                    print(f"❌ Error: No se pudo instalar {package_name}")
                    return False
        
        print("✅ Dependencias instaladas correctamente")
        time.sleep(1)
    
    return True

def verificar_y_crear_acceso_directo():
    """Verifica si existe un acceso directo y lo crea si no existe."""
    if sys.platform != "win32":
        return  # Solo en Windows
    
    try:
        script_dir = Path(__file__).parent.absolute()
        shortcut_path = script_dir / "DescargasOrdenadas.lnk"
        
        # Si ya existe, no hacer nada
        if shortcut_path.exists():
            return
        
        # Intentar crear el acceso directo silenciosamente
        try:
            import win32com.client
            
            bat_file = script_dir / "INICIAR.bat"
            if not bat_file.exists():
                return
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(bat_file)
            shortcut.WorkingDirectory = str(script_dir)
            shortcut.Description = "DescargasOrdenadas v3.0 - Organizador Automático de Archivos"
            
            # Buscar icono
            ico_path = script_dir / "resources" / "favicon.ico"
            if ico_path.exists():
                shortcut.IconLocation = str(ico_path)
            
            shortcut.save()
            print("🔗 Acceso directo creado en la carpeta raíz")
            
        except Exception:
            # Si falla, no hacer nada (silencioso)
            pass
            
    except Exception:
        # Fallos silenciosos para no interrumpir el flujo principal
        pass

def configurar_logger():
    """Configura el sistema de logging."""
    logger = logging.getLogger('DescargasOrdenadas')
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def obtener_carpeta_descargas():
    """Obtiene la carpeta de descargas del sistema."""
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as key:
                return Path(winreg.QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0])
        except:
            pass
    
    downloads_path = Path.home() / "Downloads"
    if not downloads_path.exists():
        downloads_path = Path.home() / "Descargas"
    
    return downloads_path

def main():
    parser = argparse.ArgumentParser(description="Organiza automáticamente los archivos de descargas")
    parser.add_argument("--gui", action="store_true", help="Abrir interfaz gráfica (por defecto)")
    parser.add_argument("--auto", action="store_true", help="Organizar una vez sin GUI")
    parser.add_argument("--autostart", action="store_true", help="Modo autostart del sistema")
    parser.add_argument("--minimizado", action="store_true", help="Iniciar minimizado")
    parser.add_argument("--sin-consola", action="store_true", help="Ocultar ventana de consola")
    parser.add_argument("--dir", type=str, help="Directorio a organizar")
    
    args = parser.parse_args()
    
    # Ocultar consola ANTES de cualquier print si se solicita
    if args.sin_consola or args.autostart or args.minimizado:
        if sys.platform == "win32":
            try:
                import ctypes
                console_window = ctypes.windll.kernel32.GetConsoleWindow()
                if console_window:
                    ctypes.windll.user32.ShowWindow(console_window, 0)  # SW_HIDE
            except:
                pass
    
    # Solo mostrar prints si NO es modo silencioso
    if not (args.sin_consola or args.autostart or args.minimizado):
        print("🍄 DescargasOrdenadas v3.0 - Edición Portable")
        print("=" * 50)
    
    # Solo configurar logger con salida a consola si NO es modo silencioso
    if not (args.sin_consola or args.autostart or args.minimizado):
        logger = configurar_logger()
    else:
        # Configurar logger solo a archivo en modo silencioso
        logger = logging.getLogger('DescargasOrdenadas')
        logger.setLevel(logging.INFO)
        # Sin handler de consola en modo silencioso
    
    # Verificar dependencias
    if not verificar_dependencias():
        if not args.autostart:  # Solo mostrar input si NO es autostart
            input("\n❌ Presiona Enter para cerrar...")
        sys.exit(1)
    
    # Verificar y crear acceso directo automáticamente
    verificar_y_crear_acceso_directo()
    
    try:
        from organizer.file_organizer import OrganizadorArchivos
        try:
            from organizer.gui_avanzada import run_advanced_gui as run_gui
        except ImportError:
            from organizer.gui import run_app as run_gui
    except ImportError as e:
        logger.error(f"Error al importar módulos: {e}")
        if not args.autostart:  # Solo mostrar input si NO es autostart
            input("\n❌ Presiona Enter para cerrar...")
        sys.exit(1)
    
    # Determinar directorio
    if args.dir:
        directorio = Path(args.dir)
        if not directorio.exists():
            logger.error(f"El directorio no existe: {directorio}")
            sys.exit(1)
    else:
        directorio = obtener_carpeta_descargas()
    
    logger.info(f"📁 Directorio: {directorio}")
    
    # Modo de funcionamiento
    if args.auto:
        # Solo organizar una vez
        logger.info("📂 Organizando archivos...")
        organizador = OrganizadorArchivos(carpeta_descargas=str(directorio), usar_subcarpetas=True)
        resultados, errores = organizador.organizar()
        total = sum(len(files) for cat in resultados.values() for files in cat.values())
        logger.info(f"✅ {total} archivos organizados")
        
    elif args.autostart:
        # Modo autostart: organizar + GUI minimizada con auto-organización
        logger.info("🚀 Modo autostart iniciado...")
        organizador = OrganizadorArchivos(carpeta_descargas=str(directorio), usar_subcarpetas=True)
        resultados, errores = organizador.organizar()
        total = sum(len(files) for cat in resultados.values() for files in cat.values())
        logger.info(f"✅ {total} archivos organizados inicialmente")
        
        # Ocultar consola
        if sys.platform == "win32":
            try:
                import ctypes
                console_window = ctypes.windll.kernel32.GetConsoleWindow()
                if console_window:
                    ctypes.windll.user32.ShowWindow(console_window, 0)
            except:
                pass
        
        # Iniciar GUI minimizada
        try:
            run_gui(directorio=directorio, minimizado=True)
        except Exception as e:
            logger.error(f"Error iniciando GUI: {e}")
            
    else:
        # Modo normal: GUI
        logger.info("🖥️  Iniciando interfaz gráfica...")
        try:
            run_gui(directorio=directorio, minimizado=args.minimizado)
        except Exception as e:
            logger.error(f"Error iniciando GUI: {e}")
            # No mostrar input() porque la GUI maneja su propio cierre
            sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Aplicación cerrada por el usuario")
        # Salir silenciosamente en interrupciones de teclado
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        # Solo mostrar input si se ejecuta directamente desde consola
        # Si hay GUI activa, salir silenciosamente
        try:
            # Verificar si hay argumentos que indican modo GUI
            import sys
            if len(sys.argv) == 1 or '--auto' not in sys.argv:
                # Modo GUI o sin argumentos específicos - salir silenciosamente
                sys.exit(1)
            else:
                # Modo consola explícito - mostrar input
                input("Presiona Enter para cerrar...")
                sys.exit(1)
        except:
            # En caso de error, salir silenciosamente
            sys.exit(1) 