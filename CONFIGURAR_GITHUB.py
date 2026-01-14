#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script interactivo para configurar tu usuario de GitHub
en el sistema de actualizaciones automáticas
"""

from pathlib import Path
import re

def configurar_github():
    print("═══════════════════════════════════════════════════════════════════════════════")
    print("   ⚙️ CONFIGURAR GITHUB - Sistema de Actualizaciones Automáticas")
    print("═══════════════════════════════════════════════════════════════════════════════\n")
    
    print("Este script configurará tu usuario y repositorio de GitHub para que")
    print("los usuarios puedan descargar actualizaciones automáticamente.\n")
    
    # Solicitar datos
    print("📝 Por favor, proporciona la siguiente información:\n")
    
    usuario = input("👤 Tu usuario de GitHub: ").strip()
    if not usuario:
        print("\n❌ El usuario no puede estar vacío")
        return False
    
    repositorio = input("📦 Nombre del repositorio [Descargas-Ordenada]: ").strip()
    if not repositorio:
        repositorio = "Descargas-Ordenada"
    
    print(f"\n🔍 Configuración a aplicar:")
    print(f"   • Usuario: {usuario}")
    print(f"   • Repositorio: {repositorio}")
    print(f"   • URL completa: https://github.com/{usuario}/{repositorio}\n")
    
    confirmar = input("¿Es correcto? (s/n): ").strip().lower()
    if confirmar not in ['s', 'si', 'sí', 'y', 'yes']:
        print("\n❌ Configuración cancelada")
        return False
    
    # Modificar archivo
    archivo = Path("organizer/actualizaciones_mejorado.py")
    
    if not archivo.exists():
        print(f"\n❌ No se encontró el archivo: {archivo}")
        return False
    
    print(f"\n📄 Leyendo {archivo}...")
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar y reemplazar
    print("🔧 Aplicando cambios...")
    
    # Reemplazar GITHUB_USER
    contenido = re.sub(
        r'GITHUB_USER = ".*?"',
        f'GITHUB_USER = "{usuario}"',
        contenido
    )
    
    # Reemplazar GITHUB_REPO
    contenido = re.sub(
        r'GITHUB_REPO = ".*?"',
        f'GITHUB_REPO = "{repositorio}"',
        contenido
    )
    
    # Guardar
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print(f"✅ Archivo actualizado: {archivo}\n")
    
    print("═══════════════════════════════════════════════════════════════════════════════")
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("═══════════════════════════════════════════════════════════════════════════════\n")
    
    print("📋 PRÓXIMOS PASOS:")
    print()
    print("1. Sube tu proyecto a GitHub:")
    print(f"   git init")
    print(f"   git add .")
    print(f'   git commit -m "v3.2.0 - Mejoras finales"')
    print(f"   git branch -M main")
    print(f"   git remote add origin https://github.com/{usuario}/{repositorio}.git")
    print(f"   git push -u origin main")
    print()
    print("2. Crea una release en GitHub:")
    print(f"   • Ve a: https://github.com/{usuario}/{repositorio}/releases/new")
    print(f"   • Tag: v3.2.0")
    print(f"   • Title: v3.2.0 - Mejoras Finales")
    print(f"   • Descripción: Añade las novedades de v3.2")
    print(f"   • Adjunta el .zip del proyecto (opcional pero recomendado)")
    print(f"   • Publica la release")
    print()
    print("3. ¡Prueba el sistema de actualizaciones!")
    print(f"   • Ejecuta la aplicación")
    print(f"   • Click en 'Buscar Actualizaciones'")
    print(f"   • Debería conectarse a tu repositorio")
    print()
    print("═══════════════════════════════════════════════════════════════════════════════\n")
    
    return True

if __name__ == "__main__":
    try:
        configurar_github()
        input("\nPresiona Enter para salir...")
    except KeyboardInterrupt:
        print("\n\n❌ Configuración cancelada por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        input("\nPresiona Enter para salir...")
