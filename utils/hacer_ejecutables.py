#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DescargasOrdenadas v3.0 - Configurador de Permisos Portable
===========================================================
Script para hacer ejecutables todos los archivos necesarios
en sistemas Unix (macOS y Linux).

Creado por Champi 🍄
"""

import os
import platform
import stat
from pathlib import Path

def detectar_sistema():
    """Detecta si es un sistema Unix que necesita permisos ejecutables."""
    sistema = platform.system().lower()
    return sistema in ["darwin", "linux"]

def hacer_ejecutable(archivo):
    """Hace un archivo ejecutable."""
    try:
        # Obtener permisos actuales
        permisos_actuales = os.stat(archivo).st_mode
        
        # Agregar permisos de ejecución para propietario, grupo y otros
        nuevos_permisos = permisos_actuales | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
        
        # Aplicar nuevos permisos
        os.chmod(archivo, nuevos_permisos)
        return True
    except Exception as e:
        print(f"❌ Error al hacer ejecutable {archivo}: {e}")
        return False

def main():
    print()
    print("🍄 DescargasOrdenadas v3.0 - Configurador de Permisos")
    print("===================================================")
    print()
    
    # Verificar si es un sistema Unix
    if not detectar_sistema():
        print("ℹ️  Este script solo es necesario en macOS y Linux")
        print("🪟 En Windows los archivos .bat ya son ejecutables")
        return
    
    sistema = platform.system()
    print(f"🖥️  Sistema detectado: {sistema}")
    print("🔧 Configurando permisos ejecutables...")
    print()
    
    # Directorio base del proyecto
    base_dir = Path(__file__).parent
    
    # Archivos que deben ser ejecutables
    archivos_ejecutables = [
        # Scripts principales
        "DescargasOrdenadas.sh",
        "DescargasOrdenadas.command",
        
        # Scripts de configuración
        "scripts/tarea_macos.sh",
        "scripts/tarea_linux.sh",
        "scripts/instalar_dependencias.sh",
        
        # Launchers Python
        "Ejecutar_DescargasOrdenadas.py",
        "Configurar_TareaProgramada.py",
        "main.py",
    ]
    
    exitos = 0
    errores = 0
    
    for archivo_rel in archivos_ejecutables:
        archivo_path = base_dir / archivo_rel
        
        if archivo_path.exists():
            print(f"🔧 Configurando: {archivo_rel}")
            if hacer_ejecutable(archivo_path):
                print(f"✅ {archivo_rel} - Permisos configurados")
                exitos += 1
            else:
                print(f"❌ {archivo_rel} - Error al configurar")
                errores += 1
        else:
            print(f"⚠️  {archivo_rel} - Archivo no encontrado")
            errores += 1
        
        print()
    
    # Resumen
    print("=" * 50)
    print("📊 Resumen de configuración:")
    print(f"✅ Archivos configurados exitosamente: {exitos}")
    print(f"❌ Errores encontrados: {errores}")
    
    if errores == 0:
        print()
        print("🎉 ¡Todos los permisos configurados correctamente!")
        print("🚀 El proyecto está listo para ser portable")
    else:
        print()
        print("⚠️  Algunos archivos no se pudieron configurar")
        print("💡 Verifica que tengas permisos suficientes")
    
    print()
    print("💡 Ahora puedes comprimir la carpeta y compartir en cualquier sistema")
    print()

if __name__ == "__main__":
    main() 