#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DescargasOrdenadas - Aplicación portable para organizar automáticamente los archivos.
Versión 3.0 - Edición Portable
Creado por Champi 🍄
"""

import sys
import os
import argparse
import logging
import importlib.util
import subprocess
import time
from pathlib import Path

def instalar_dependencia(package_name, import_name=None):
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

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas e instala las faltantes automáticamente."""
    required_packages = [
        ("pillow", "PIL"),
        ("PySide6", "PySide6")
    ]
    
    # Solo agregar pywin32 en Windows
    if sys.platform == "win32":
        required_packages.append(("pywin32", "win32api"))
    
    missing_packages = []
    
    # Primera verificación
    for package_name, import_name in required_packages:
        try:
            importlib.import_module(import_name)
        except ImportError:
            missing_packages.append((package_name, import_name))
    
    # Si hay dependencias faltantes, intentar instalarlas automáticamente
    if missing_packages:
        print("🔧 Instalando dependencias faltantes automáticamente...")
        print("⏳ Este proceso puede tardar unos minutos...")
        
        # Separar pywin32 de otras dependencias
        pywin32_needed = False
        other_packages = []
        
        for package_name, import_name in missing_packages:
            if package_name == "pywin32":
                pywin32_needed = True
            else:
                other_packages.append((package_name, import_name))
        
        # Instalar dependencias normales primero
        failed_installs = []
        for package_name, import_name in other_packages:
            if not instalar_dependencia(package_name):
                failed_installs.append((package_name, import_name))
        
        # Manejar pywin32 especialmente en Windows
        if pywin32_needed and sys.platform == "win32":
            print("🪟 Instalando pywin32 para Windows...")
            if instalar_dependencia("pywin32"):
                print("✅ pywin32 instalado correctamente")
                print("⚠️  NOTA: Es posible que necesites reiniciar la aplicación")
                print("   para que pywin32 funcione correctamente.")
                
                # Intentar importar inmediatamente
                try:
                    importlib.import_module("win32api")
                    print("✅ pywin32 funciona correctamente")
                except ImportError:
                    print("⚠️  pywin32 instalado pero necesita reinicio de la aplicación")
                    print("🔄 Reinicia la aplicación para aplicar los cambios")
                    # No considerar esto como un error fatal
            else:
                print("❌ Error instalando pywin32")
                print("💡 Intenta instalar manualmente: pip install pywin32")
                # pywin32 no es crítico para la funcionalidad básica
        
        # Verificar de nuevo después de la instalación (excepto pywin32)
        still_missing = []
        for package_name, import_name in other_packages:
            try:
                importlib.import_module(import_name)
                print(f"✅ {package_name} instalado correctamente")
            except ImportError:
                still_missing.append(package_name)
        
        if still_missing:
            print(f"❌ Error: No se pudieron instalar algunas dependencias críticas: {', '.join(still_missing)}")
            print("💡 Instálalas manualmente con:")
            print(f"   pip install {' '.join(still_missing)}")
            print("📁 Esta es una versión portable que requiere Python y dependencias.")
            return False
        else:
            if other_packages:
                print("✅ Dependencias críticas instaladas correctamente")
            time.sleep(1)  # Pequeña pausa para que el usuario vea el mensaje
    
    return True

def ocultar_consola_gradual():
    """Oculta la consola gradualmente después de mostrar mensajes importantes."""
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            user32 = ctypes.windll.user32
            
            console_window = kernel32.GetConsoleWindow()
            if console_window:
                # Mostrar mensaje de que se ocultará la consola
                print("🖥️  Iniciando interfaz gráfica...")
                print("⏳ La consola se ocultará en 3 segundos...")
                time.sleep(3)
                user32.ShowWindow(console_window, 0)  # SW_HIDE
        except:
            pass

def configurar_logger():
    """Configura el sistema de logging."""
    logger = logging.getLogger('DescargasOrdenadas')
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
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
    parser = argparse.ArgumentParser(description="DescargasOrdenadas v3.0 - Portable | Organiza automáticamente los archivos.")
    parser.add_argument("--auto-organizar", action="store_true", help="Organiza automáticamente sin mostrar la interfaz gráfica.")
    parser.add_argument("--reorganizar", action="store_true", help="Reorganiza TODOS los archivos, incluso los ya organizados")
    parser.add_argument("--dir", type=str, help="Directorio a organizar (por defecto: carpeta de descargas).")
    parser.add_argument("--minimizado", action="store_true", help="Iniciar la aplicación minimizada en la bandeja del sistema")
    parser.add_argument("--sin-subcarpetas", action="store_true", help="No usar subcarpetas para organizar (modo simple)")
    parser.add_argument("--tarea-programada", action="store_true", help="Modo para ejecución como tarea programada")
    parser.add_argument("--inicio-sistema", action="store_true", help="Organización automática al inicio del sistema")
    
    args = parser.parse_args()
    
    logger = configurar_logger()
    logger.info("🍄 DescargasOrdenadas v3.0 - Edición Portable por Champi")
    
    # Verificar e instalar dependencias automáticamente
    if not check_dependencies():
        input("\n❌ Presiona Enter para cerrar...")
        sys.exit(1)
    
    try:
        from organizer.file_organizer import OrganizadorArchivos
        # Intentar importar la GUI avanzada primero
        try:
            from organizer.gui_avanzada import run_advanced_gui as run_app
            GUI_TIPO = "avanzada"
        except ImportError:
            from organizer.gui import run_app
            GUI_TIPO = "básica"
    except ImportError as e:
        logger.error(f"Error al importar módulos de la aplicación: {e}")
        logger.info("💡 Asegúrate de que todos los archivos estén en su lugar y las dependencias instaladas.")
        input("\n❌ Presiona Enter para cerrar...")
        sys.exit(1)
    
    if args.dir:
        directorio = Path(args.dir)
        if not directorio.exists():
            logger.error(f"El directorio especificado no existe: {directorio}")
            input("\n❌ Presiona Enter para cerrar...")
            sys.exit(1)
    else:
        directorio = obtener_carpeta_descargas()
    
    logger.info(f"📁 Directorio a organizar: {directorio}")
    
    usar_subcarpetas = not args.sin_subcarpetas
    
    if args.auto_organizar or args.reorganizar or args.tarea_programada or args.inicio_sistema:
        try:
            if args.reorganizar:
                logger.info("🔄 Reorganización completa iniciada...")
            elif args.tarea_programada:
                logger.info("⏰ Ejecutando organización automática programada...")
            elif args.inicio_sistema:
                logger.info("🚀 Ejecutando organización automática al inicio del sistema...")
            else:
                logger.info("📂 Organización automática iniciada...")
                
            organizador = OrganizadorArchivos(carpeta_descargas=str(directorio), usar_subcarpetas=usar_subcarpetas)
            
            if args.reorganizar:
                resultados, errores = organizador.reorganizar_completamente()
            else:
                resultados, errores = organizador.organizar(organizar_subcarpetas=True)
            
            total_archivos = sum(len(files) for cat in resultados.values() for files in cat.values())
            logger.info(f"✅ Organización completada. {total_archivos} archivos organizados.")
            
            if errores:
                logger.warning(f"⚠️  {len(errores)} errores encontrados durante la organización.")
            
            if resultados and not (args.tarea_programada or args.inicio_sistema):
                logger.info("📊 Resumen de organización:")
                for categoria, subcategorias in resultados.items():
                    total_cat = sum(len(files) for files in subcategorias.values())
                    if total_cat > 0:
                        logger.info(f"  📂 {categoria}: {total_cat} archivos")
            
            # Para tareas programadas y de inicio, no mantener la consola abierta
            if args.tarea_programada or args.inicio_sistema:
                time.sleep(2)  # Pequeña pausa para ver los resultados
                        
        except Exception as e:
            logger.error(f"❌ Error durante la organización: {e}")
            if not (args.tarea_programada or args.inicio_sistema):
                input("\n❌ Presiona Enter para cerrar...")
            sys.exit(1)
    else:
        try:
            if GUI_TIPO == "avanzada":
                logger.info("🍄 Iniciando interfaz avanzada con IA, fechas, duplicados y estadísticas...")
            else:
                logger.info("🖥️  Iniciando interfaz gráfica básica...")
            
            # Ocultar consola gradualmente después de mostrar el mensaje inicial
            if not args.minimizado:
                ocultar_consola_gradual()
            
            run_app(directorio=directorio, minimizado=args.minimizado)
        except Exception as e:
            logger.error(f"❌ Error al iniciar la interfaz gráfica: {e}")
            
            try:
                import tkinter as tk
                from tkinter import messagebox
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("Error - DescargasOrdenadas v3.0", 
                                   f"Error al iniciar la aplicación:\n\n{e}\n\n🍄 Creado por Champi")
                root.destroy()
            except:
                pass
            
            input("\n❌ Presiona Enter para cerrar...")
            sys.exit(1)

if __name__ == "__main__":
    main() 