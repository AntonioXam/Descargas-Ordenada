#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===================================================================
🍄 DescargasOrdenadas v3.0 - Launcher Principal Universal
===================================================================

¡LAUNCHER PRINCIPAL! - Ejecuta este archivo desde cualquier sistema
- Detecta automáticamente Windows, macOS o Linux
- Ejecuta el launcher correspondiente de cada sistema
- No requiere Python preinstalado en el sistema de destino

Creado por Champi 🍄
Versión: 3.0
"""

import os
import sys
import platform
import subprocess

def detectar_sistema():
    """Detecta el sistema operativo actual"""
    sistema = platform.system().lower()
    
    if sistema == "windows":
        return "windows"
    elif sistema == "darwin":
        return "macos"
    elif sistema == "linux":
        return "linux"
    else:
        return "desconocido"

def ejecutar_launcher(sistema):
    """Ejecuta el launcher específico del sistema"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    if sistema == "windows":
        launcher = os.path.join(script_dir, "windows", "INICIAR.bat")
        if os.path.exists(launcher):
            print(f"🪟 Ejecutando launcher de Windows: {launcher}")
            # Pasar todos los argumentos de línea de comandos
            args = sys.argv[1:] if len(sys.argv) > 1 else []
            subprocess.run([launcher] + args, cwd=script_dir)
        else:
            print("❌ No se encontró el launcher de Windows")
            print(f"   Buscado en: {launcher}")
            
    elif sistema == "macos":
        launcher = os.path.join(script_dir, "macos", "INICIAR.sh")
        if os.path.exists(launcher):
            print(f"🍎 Ejecutando launcher de macOS: {launcher}")
            # Hacer el script ejecutable
            os.chmod(launcher, 0o755)
            # Pasar todos los argumentos de línea de comandos
            args = sys.argv[1:] if len(sys.argv) > 1 else []
            subprocess.run([launcher] + args, cwd=script_dir)
        else:
            print("❌ No se encontró el launcher de macOS")
            print(f"   Buscado en: {launcher}")
            
    elif sistema == "linux":
        launcher = os.path.join(script_dir, "linux", "INICIAR.sh")
        if os.path.exists(launcher):
            print(f"🐧 Ejecutando launcher de Linux: {launcher}")
            # Hacer el script ejecutable
            os.chmod(launcher, 0o755)
            # Pasar todos los argumentos de línea de comandos
            args = sys.argv[1:] if len(sys.argv) > 1 else []
            subprocess.run([launcher] + args, cwd=script_dir)
        else:
            print("❌ No se encontró el launcher de Linux")
            print(f"   Buscado en: {launcher}")
    else:
        print(f"❌ Sistema operativo no soportado: {sistema}")
        print("   Sistemas soportados: Windows, macOS, Linux")

def mostrar_ayuda():
    """Muestra información de ayuda"""
    print("""
🍄 DescargasOrdenadas v3.0 - Launcher Principal Universal
========================================================

📋 INSTRUCCIONES DE USO:
-----------------------

1️⃣  EJECUCIÓN SIMPLE:
   python EJECUTAR.py
   
2️⃣  EJECUCIÓN CON ARGUMENTOS:
   python EJECUTAR.py --tarea-programada
   python EJECUTAR.py --inicio-sistema
   
3️⃣  SISTEMAS SIN PYTHON:
   • Windows: Ejecuta windows/INICIAR.bat
   • macOS:   Ejecuta macos/INICIAR.sh  
   • Linux:   Ejecuta linux/INICIAR.sh

📁 ESTRUCTURA DEL PROYECTO:
---------------------------
DescargasOrdenadas/
├── EJECUTAR.py              ← ¡ESTE ARCHIVO! (Launcher principal)
├── main.py                  ← Aplicación principal
├── windows/                 ← Todo para Windows
│   ├── INICIAR.bat         ← Launcher Windows (NO requiere Python)
│   ├── DescargasOrdenadas.bat ← Launcher Windows (requiere Python)
│   └── scripts/            ← Scripts específicos Windows
├── macos/                  ← Todo para macOS
│   ├── INICIAR.sh          ← Launcher macOS (NO requiere Python)
│   ├── DescargasOrdenadas.command ← Launcher macOS (requiere Python)
│   └── scripts/            ← Scripts específicos macOS
├── linux/                  ← Todo para Linux
│   ├── INICIAR.sh          ← Launcher Linux (NO requiere Python)
│   ├── DescargasOrdenadas.sh ← Launcher Linux (requiere Python)
│   └── scripts/            ← Scripts específicos Linux
└── utils/                  ← Utilidades generales
    ├── hacer_ejecutables.py ← Configura permisos Unix
    └── Configurar_TareaProgramada.py ← Config. tareas programadas

💡 CONSEJOS:
-----------
• Si tienes Python: Usa 'python EJECUTAR.py'
• Si NO tienes Python: Ve a la carpeta de tu sistema y ejecuta INICIAR
• Cada carpeta de sistema tiene sus propias instrucciones
• Los launchers INICIAR no requieren Python preinstalado
""")

def main():
    """Función principal"""
    # Configurar codificación para caracteres especiales
    if sys.stdout.encoding != 'utf-8':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    
    print("🍄 DescargasOrdenadas v3.0 - Launcher Principal Universal")
    print("=" * 55)
    
    # Verificar argumentos de ayuda
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h", "help", "ayuda"]:
        mostrar_ayuda()
        return
    
    # Detectar sistema operativo
    sistema = detectar_sistema()
    print(f"🔍 Sistema detectado: {sistema.upper()}")
    
    if sistema == "desconocido":
        print("❌ Sistema operativo no reconocido")
        print("💡 Intenta ejecutar manualmente el launcher de tu sistema:")
        print("   • Windows: windows/INICIAR.bat")
        print("   • macOS: macos/INICIAR.sh")
        print("   • Linux: linux/INICIAR.sh")
        return
    
    # Ejecutar launcher específico
    ejecutar_launcher(sistema)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Ejecución cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print("💡 Intenta ejecutar manualmente el launcher de tu sistema:")
        sistema = detectar_sistema()
        if sistema == "windows":
            print("   windows/INICIAR.bat")
        elif sistema == "macos":
            print("   macos/INICIAR.sh")
        elif sistema == "linux":
            print("   linux/INICIAR.sh")
        else:
            print("   Revisa la carpeta correspondiente a tu sistema") 