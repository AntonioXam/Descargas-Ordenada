#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🍄 DescargasOrdenadas v3.1 - Instalador Inteligente
Instala y verifica todas las dependencias necesarias
"""

import sys
import subprocess
import importlib.util
from pathlib import Path

# Colores para Windows
try:
    import colorama
    colorama.init()
    COLOR_VERDE = '\033[92m'
    COLOR_ROJO = '\033[91m'
    COLOR_AMARILLO = '\033[93m'
    COLOR_AZUL = '\033[94m'
    COLOR_RESET = '\033[0m'
    TIENE_COLOR = True
except:
    COLOR_VERDE = ''
    COLOR_ROJO = ''
    COLOR_AMARILLO = ''
    COLOR_AZUL = ''
    COLOR_RESET = ''
    TIENE_COLOR = False

def imprimir(mensaje, color=''):
    """Imprime con color si está disponible."""
    print(f"{color}{mensaje}{COLOR_RESET}")

def verificar_python():
    """Verifica la versión de Python."""
    version = sys.version_info
    imprimir(f"\n🐍 Python {version.major}.{version.minor}.{version.micro}", COLOR_AZUL)
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        imprimir("❌ ERROR: Se requiere Python 3.8 o superior", COLOR_ROJO)
        return False
    
    imprimir("✅ Versión de Python compatible", COLOR_VERDE)
    return True

def esta_instalado(paquete, import_name=None):
    """Verifica si un paquete está instalado."""
    if import_name is None:
        import_name = paquete
    
    spec = importlib.util.find_spec(import_name)
    return spec is not None

def instalar_paquete(paquete, descripcion=""):
    """Instala un paquete usando pip."""
    imprimir(f"\n📦 Instalando {paquete}...", COLOR_AZUL)
    if descripcion:
        imprimir(f"   {descripcion}", COLOR_AMARILLO)
    
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", paquete],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT
        )
        imprimir(f"✅ {paquete} instalado correctamente", COLOR_VERDE)
        return True
    except subprocess.CalledProcessError:
        imprimir(f"❌ Error instalando {paquete}", COLOR_ROJO)
        return False

def verificar_dependencias():
    """Verifica todas las dependencias."""
    imprimir("\n" + "="*70, COLOR_AZUL)
    imprimir("   🔍 VERIFICANDO DEPENDENCIAS EXISTENTES", COLOR_AZUL)
    imprimir("="*70, COLOR_AZUL)
    
    dependencias = {
        "PySide6": {"import": "PySide6", "desc": "Interfaz gráfica", "critico": True},
        "Pillow": {"import": "PIL", "desc": "Procesamiento de imágenes", "critico": True},
        "watchdog": {"import": "watchdog", "desc": "Monitor de archivos", "critico": True},
        "pywin32": {"import": "win32com.client", "desc": "Windows APIs", "critico": True},
        "requests": {"import": "requests", "desc": "Actualizaciones automáticas", "critico": False},
        "plyer": {"import": "plyer", "desc": "Notificaciones nativas", "critico": False},
    }
    
    faltantes = []
    opcionales_faltantes = []
    
    for paquete, info in dependencias.items():
        if esta_instalado(paquete, info["import"]):
            imprimir(f"✅ {paquete} - {info['desc']}", COLOR_VERDE)
        else:
            if info["critico"]:
                imprimir(f"❌ {paquete} - {info['desc']} (FALTA)", COLOR_ROJO)
                faltantes.append((paquete, info["desc"]))
            else:
                imprimir(f"⚠️  {paquete} - {info['desc']} (OPCIONAL - FALTA)", COLOR_AMARILLO)
                opcionales_faltantes.append((paquete, info["desc"]))
    
    return faltantes, opcionales_faltantes

def instalar_todas_dependencias(faltantes, opcionales):
    """Instala todas las dependencias faltantes."""
    if not faltantes and not opcionales:
        imprimir("\n✅ Todas las dependencias ya están instaladas!", COLOR_VERDE)
        return True
    
    imprimir("\n" + "="*70, COLOR_AZUL)
    imprimir("   📦 INSTALANDO DEPENDENCIAS", COLOR_AZUL)
    imprimir("="*70, COLOR_AZUL)
    
    exito = True
    
    # Instalar dependencias críticas
    if faltantes:
        imprimir("\n📋 Dependencias CRÍTICAS:", COLOR_AMARILLO)
        for paquete, desc in faltantes:
            if not instalar_paquete(paquete, desc):
                exito = False
    
    # Instalar dependencias opcionales
    if opcionales:
        imprimir("\n📋 Dependencias OPCIONALES (recomendadas):", COLOR_AMARILLO)
        for paquete, desc in opcionales:
            instalar_paquete(paquete, desc)
    
    return exito

def verificar_estructura_proyecto():
    """Verifica que la estructura del proyecto esté completa."""
    imprimir("\n" + "="*70, COLOR_AZUL)
    imprimir("   📁 VERIFICANDO ESTRUCTURA DEL PROYECTO", COLOR_AZUL)
    imprimir("="*70, COLOR_AZUL)
    
    archivos_necesarios = [
        "INICIAR.py",
        "INICIAR_SIN_CONSOLA.bat",
        "INICIAR_SIN_CONSOLA.pyw",
        "organizer/file_organizer.py",
        "organizer/gui_avanzada.py",
        "organizer/autostart.py",
        "organizer/native_notifications.py",
        "organizer/portable_config.py",
        "organizer/temas.py",
        "organizer/context_menu.py",
        "organizer/actualizaciones.py",
    ]
    
    todos_presentes = True
    
    for archivo in archivos_necesarios:
        ruta = Path(archivo)
        if ruta.exists():
            imprimir(f"✅ {archivo}", COLOR_VERDE)
        else:
            imprimir(f"❌ {archivo} (FALTA)", COLOR_ROJO)
            todos_presentes = False
    
    return todos_presentes

def mostrar_resumen_final():
    """Muestra el resumen final de la instalación."""
    imprimir("\n" + "="*70, COLOR_AZUL)
    imprimir("   🎉 INSTALACIÓN COMPLETADA", COLOR_AZUL)
    imprimir("="*70, COLOR_AZUL)
    
    imprimir("\n📊 RESUMEN:", COLOR_AMARILLO)
    
    # Verificar instalaciones finales
    dependencias = {
        "PySide6": "PySide6",
        "Pillow": "PIL",
        "watchdog": "watchdog",
        "pywin32": "win32com.client",
        "requests": "requests",
        "plyer": "plyer",
    }
    
    criticas_ok = 0
    opcionales_ok = 0
    
    imprimir("\n📦 Dependencias Críticas:", COLOR_AMARILLO)
    for paquete in ["PySide6", "Pillow", "watchdog", "pywin32"]:
        if esta_instalado(paquete, dependencias[paquete]):
            imprimir(f"   ✅ {paquete}", COLOR_VERDE)
            criticas_ok += 1
        else:
            imprimir(f"   ❌ {paquete}", COLOR_ROJO)
    
    imprimir("\n📦 Dependencias Opcionales (v3.1):", COLOR_AMARILLO)
    for paquete in ["requests", "plyer"]:
        if esta_instalado(paquete, dependencias[paquete]):
            imprimir(f"   ✅ {paquete}", COLOR_VERDE)
            opcionales_ok += 1
        else:
            imprimir(f"   ⚠️  {paquete} (no instalado)", COLOR_AMARILLO)
    
    imprimir("\n🚀 PARA INICIAR LA APLICACIÓN:", COLOR_AZUL)
    imprimir("   1. Doble clic en: INICIAR_SIN_CONSOLA.bat", COLOR_VERDE)
    imprimir("   2. O ejecuta: python INICIAR.py --gui", COLOR_VERDE)
    
    imprimir("\n🧪 PARA VERIFICAR:", COLOR_AZUL)
    imprimir("   python PRUEBAS_v3.1.py", COLOR_VERDE)
    
    if opcionales_ok < 2:
        imprimir("\n💡 RECOMENDACIÓN:", COLOR_AMARILLO)
        imprimir("   Para aprovechar TODAS las características v3.1, instala:", COLOR_AMARILLO)
        if not esta_instalado("plyer", "plyer"):
            imprimir("   • pip install plyer  (notificaciones nativas)", COLOR_AMARILLO)
        if not esta_instalado("requests", "requests"):
            imprimir("   • pip install requests  (actualizaciones automáticas)", COLOR_AMARILLO)
    
    imprimir("\n" + "="*70, COLOR_AZUL)

def main():
    """Función principal del instalador."""
    imprimir("="*70, COLOR_AZUL)
    imprimir("   🍄 DESCARGASORDENADAS v3.1", COLOR_AZUL)
    imprimir("   Instalador Inteligente de Dependencias", COLOR_AZUL)
    imprimir("="*70, COLOR_AZUL)
    
    # 1. Verificar Python
    if not verificar_python():
        imprimir("\n❌ Instalación cancelada: Python incompatible", COLOR_ROJO)
        input("\nPresiona Enter para salir...")
        return 1
    
    # 2. Verificar estructura
    if not verificar_estructura_proyecto():
        imprimir("\n⚠️  Advertencia: Algunos archivos del proyecto faltan", COLOR_AMARILLO)
        respuesta = input("\n¿Continuar de todos modos? (s/n): ").lower()
        if respuesta != 's':
            return 1
    
    # 3. Verificar dependencias existentes
    faltantes, opcionales = verificar_dependencias()
    
    # 4. Confirmar instalación
    if faltantes or opcionales:
        imprimir(f"\n📋 Se instalarán {len(faltantes)} dependencias críticas y {len(opcionales)} opcionales", COLOR_AMARILLO)
        respuesta = input("\n¿Continuar con la instalación? (s/n): ").lower()
        if respuesta != 's':
            imprimir("\n❌ Instalación cancelada por el usuario", COLOR_ROJO)
            return 1
        
        # 5. Instalar dependencias
        if not instalar_todas_dependencias(faltantes, opcionales):
            imprimir("\n⚠️  Algunas dependencias no se pudieron instalar", COLOR_AMARILLO)
            input("\nPresiona Enter para continuar...")
    
    # 6. Mostrar resumen final
    mostrar_resumen_final()
    
    input("\n\nPresiona Enter para salir...")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        imprimir("\n\n❌ Instalación interrumpida por el usuario", COLOR_ROJO)
        sys.exit(1)
    except Exception as e:
        imprimir(f"\n\n❌ Error inesperado: {e}", COLOR_ROJO)
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
        sys.exit(1)
