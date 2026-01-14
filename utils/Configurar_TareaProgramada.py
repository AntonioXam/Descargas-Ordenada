#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DescargasOrdenadas v3.0 - Configurador Universal de Tareas Programadas
======================================================================
Configurador que detecta automáticamente el sistema operativo
y configura las tareas programadas correspondientes.

Creado por Champi 🍄
"""

import sys
import os
import platform
import subprocess
from pathlib import Path

def detectar_sistema():
    """Detecta el sistema operativo actual."""
    sistema = platform.system().lower()
    if sistema == "windows":
        return "windows"
    elif sistema == "darwin":
        return "macos"
    elif sistema == "linux":
        return "linux"
    else:
        return "desconocido"

def obtener_script_configuracion(sistema):
    """Obtiene el script de configuración correcto según el sistema operativo."""
    script_dir = Path(__file__).parent / "scripts"
    
    scripts = {
        "windows": script_dir / "tarea_windows.bat",
        "macos": script_dir / "tarea_macos.sh",
        "linux": script_dir / "tarea_linux.sh"
    }
    
    return scripts.get(sistema)

def hacer_ejecutable(archivo):
    """Hace un archivo ejecutable en sistemas Unix."""
    try:
        os.chmod(archivo, 0o755)
    except:
        pass

def mostrar_banner():
    """Muestra el banner de la aplicación."""
    print()
    print("🍄 DescargasOrdenadas v3.0 - Configurador Universal de Tareas")
    print("============================================================")
    print()

def mostrar_info_sistema(sistema):
    """Muestra información específica del sistema."""
    info = {
        "windows": {
            "emoji": "🪟",
            "nombre": "Windows",
            "descripcion": "Configurará tareas con Programador de Tareas de Windows"
        },
        "macos": {
            "emoji": "🍎",
            "nombre": "macOS",
            "descripcion": "Configurará LaunchAgents/LaunchDaemons y tareas cron"
        },
        "linux": {
            "emoji": "🐧",
            "nombre": "Linux",
            "descripcion": "Configurará servicios systemd, autostart y tareas cron"
        }
    }
    
    if sistema in info:
        data = info[sistema]
        print(f"{data['emoji']} Sistema: {data['nombre']}")
        print(f"📋 {data['descripcion']}")
        print()

def main():
    mostrar_banner()
    
    # Detectar sistema operativo
    sistema = detectar_sistema()
    
    if sistema == "desconocido":
        print("❌ Sistema operativo no soportado")
        print("💡 Este configurador soporta Windows, macOS y Linux")
        input("\nPresiona Enter para cerrar...")
        sys.exit(1)
    
    mostrar_info_sistema(sistema)
    
    # Obtener script correcto
    script = obtener_script_configuracion(sistema)
    
    if not script or not script.exists():
        print(f"❌ No se encontró el script de configuración para {sistema}")
        print(f"💡 Busque el archivo: {script}")
        input("\nPresiona Enter para cerrar...")
        sys.exit(1)
    
    print(f"🔧 Usando configurador: {script.name}")
    print()
    
    # Hacer ejecutable en sistemas Unix
    if sistema in ["macos", "linux"]:
        hacer_ejecutable(script)
    
    print("🚀 Iniciando configurador...")
    print("=" * 50)
    print()
    
    try:
        if sistema == "windows":
            # En Windows, ejecutar el .bat
            proceso = subprocess.run([str(script)], shell=True)
        else:
            # En Unix, ejecutar con bash
            proceso = subprocess.run(["bash", str(script)])
        
        print()
        print("=" * 50)
        if proceso.returncode == 0:
            print("✅ Configuración completada exitosamente")
        else:
            print("⚠️  Configuración completada con advertencias")
        
        # Propagar el código de salida
        sys.exit(proceso.returncode)
        
    except FileNotFoundError:
        print(f"❌ No se pudo ejecutar {script}")
        print("💡 Verifica que el archivo existe y tiene permisos")
        input("\nPresiona Enter para cerrar...")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Configuración interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        input("\nPresiona Enter para cerrar...")
        sys.exit(1)

if __name__ == "__main__":
    main() 