#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de pruebas para DescargasOrdenadas v3.1
Verifica que todos los módulos se cargan correctamente
"""

import sys
import os
from pathlib import Path

print("═" * 70)
print("🍄 DescargasOrdenadas v3.1 - Script de Pruebas")
print("═" * 70)
print()

# Añadir directorio actual al path
script_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(script_dir))

# Lista de pruebas
pruebas_exitosas = []
pruebas_fallidas = []

def prueba(nombre, funcion):
    """Ejecuta una prueba y registra el resultado."""
    try:
        funcion()
        pruebas_exitosas.append(nombre)
        print(f"✅ {nombre}")
        return True
    except Exception as e:
        pruebas_fallidas.append((nombre, str(e)))
        print(f"❌ {nombre}: {e}")
        return False

print("🔍 Verificando módulos principales...")
print("-" * 70)

# Test 1: Importar INICIAR
def test_iniciar():
    import INICIAR
    assert hasattr(INICIAR, 'main')

prueba("Módulo INICIAR", test_iniciar)

# Test 2: Importar file_organizer
def test_file_organizer():
    from organizer.file_organizer import OrganizadorArchivos
    organizador = OrganizadorArchivos()
    assert organizador is not None

prueba("Módulo file_organizer", test_file_organizer)

# Test 3: Importar gui_avanzada
def test_gui_avanzada():
    # No importar GUI completa para evitar crear ventanas
    import organizer.gui_avanzada as gui_avanzada
    assert hasattr(gui_avanzada, 'OrganizadorAvanzado')

prueba("Módulo gui_avanzada", test_gui_avanzada)

# Test 4: Importar autostart
def test_autostart():
    from organizer.autostart import GestorAutoarranque
    gestor = GestorAutoarranque()
    assert gestor is not None

prueba("Módulo autostart", test_autostart)

print()
print("🆕 Verificando NUEVOS módulos v3.1...")
print("-" * 70)

# Test 5: Notificaciones nativas
def test_notificaciones():
    from organizer.native_notifications import NotificadorNativo
    notificador = NotificadorNativo()
    assert notificador is not None
    # Verificar métodos principales
    assert hasattr(notificador, 'mostrar')
    assert hasattr(notificador, 'notificar_organizacion')

prueba("Módulo native_notifications", test_notificaciones)

# Test 6: Configuración portable
def test_config_portable():
    from organizer.portable_config import obtener_config
    config = obtener_config()
    assert config is not None
    # Verificar métodos principales
    assert hasattr(config, 'obtener')
    assert hasattr(config, 'establecer')
    # Test de lectura/escritura
    config.establecer("test_key", "test_value")
    valor = config.obtener("test_key")
    assert valor == "test_value"

prueba("Módulo portable_config", test_config_portable)

# Test 7: Sistema de temas
def test_temas():
    from organizer.temas import obtener_gestor_temas
    gestor = obtener_gestor_temas()
    assert gestor is not None
    # Verificar que hay temas
    temas = gestor.obtener_nombres_temas()
    assert len(temas) >= 5
    assert "azul_oscuro" in temas
    assert "verde_oscuro" in temas
    assert "purpura" in temas
    # Obtener un tema
    tema = gestor.obtener_tema("azul_oscuro")
    assert tema is not None
    # Verificar que genera stylesheet
    stylesheet = tema.obtener_stylesheet()
    assert len(stylesheet) > 100

prueba("Módulo temas", test_temas)

# Test 8: Menú contextual
def test_menu_contextual():
    if sys.platform == "win32":
        from organizer.context_menu import GestorMenuContextual
        gestor = GestorMenuContextual()
        assert gestor is not None
        assert hasattr(gestor, 'registrar_menu_contextual')
        assert hasattr(gestor, 'desregistrar_menu_contextual')
    else:
        # En otros sistemas, solo verificar que el módulo existe
        import organizer.context_menu

prueba("Módulo context_menu", test_menu_contextual)

# Test 9: Actualizaciones
def test_actualizaciones():
    from organizer.actualizaciones import obtener_gestor_actualizaciones
    gestor = obtener_gestor_actualizaciones()
    assert gestor is not None
    # Verificar métodos principales
    assert hasattr(gestor, 'verificar_actualizaciones')
    assert hasattr(gestor, 'obtener_version_actual')
    # Verificar versión
    version = gestor.obtener_version_actual()
    assert version == "3.1.0"

prueba("Módulo actualizaciones", test_actualizaciones)

print()
print("🔧 Verificando dependencias opcionales...")
print("-" * 70)

# Test 10: plyer (opcional)
def test_plyer():
    try:
        import plyer
        print(f"   ℹ️  plyer versión: {plyer.__version__ if hasattr(plyer, '__version__') else 'desconocida'}")
    except ImportError:
        print("   ⚠️  plyer no instalado (opcional)")
        raise

prueba("Dependencia plyer", test_plyer)

# Test 11: requests (opcional)
def test_requests():
    try:
        import requests
        print(f"   ℹ️  requests versión: {requests.__version__}")
    except ImportError:
        print("   ⚠️  requests no instalado (opcional)")
        raise

prueba("Dependencia requests", test_requests)

print()
print("═" * 70)
print("📊 RESULTADOS DE LAS PRUEBAS")
print("═" * 70)
print()
print(f"✅ Pruebas exitosas: {len(pruebas_exitosas)}")
for nombre in pruebas_exitosas:
    print(f"   • {nombre}")

if pruebas_fallidas:
    print()
    print(f"❌ Pruebas fallidas: {len(pruebas_fallidas)}")
    for nombre, error in pruebas_fallidas:
        print(f"   • {nombre}: {error}")
else:
    print()
    print("🎉 ¡TODAS LAS PRUEBAS PASARON!")

print()
print("═" * 70)
print("💡 RECOMENDACIONES:")
print("═" * 70)

# Verificar si faltan dependencias opcionales
dependencias_faltantes = []
for nombre, error in pruebas_fallidas:
    if "plyer" in nombre.lower():
        dependencias_faltantes.append("plyer")
    if "requests" in nombre.lower():
        dependencias_faltantes.append("requests")

if dependencias_faltantes:
    print()
    print("⚠️  Dependencias opcionales faltantes:")
    for dep in dependencias_faltantes:
        print(f"   • {dep}")
    print()
    print("📦 Instalar con: pip install " + " ".join(dependencias_faltantes))
    print()
    print("ℹ️  La aplicación funcionará sin estas dependencias, pero")
    print("   algunas características estarán deshabilitadas:")
    if "plyer" in dependencias_faltantes:
        print("   - Sin plyer: No habrá notificaciones nativas del sistema")
    if "requests" in dependencias_faltantes:
        print("   - Sin requests: No se podrán verificar actualizaciones")
else:
    print()
    print("✅ Todas las dependencias opcionales están instaladas")
    print("✅ Todas las características están disponibles")

print()
print("═" * 70)
print("🚀 La aplicación está lista para ejecutarse con:")
print("═" * 70)
print()
print("   • INICIAR_SIN_CONSOLA.bat  (Recomendado - Sin consola)")
print("   • INICIAR.bat              (Con consola para depuración)")
print("   • pythonw INICIAR_SIN_CONSOLA.pyw")
print()
print("═" * 70)
print()

# Código de salida
if pruebas_fallidas:
    # Verificar si solo fallaron las opcionales
    solo_opcionales = all("plyer" in nombre.lower() or "requests" in nombre.lower() 
                          for nombre, _ in pruebas_fallidas)
    if solo_opcionales:
        print("✅ Todos los módulos principales funcionan correctamente")
        print("⚠️  Solo faltan dependencias opcionales")
        sys.exit(0)
    else:
        print("❌ Hay errores en módulos principales")
        sys.exit(1)
else:
    print("✅ TODO PERFECTO - Listo para usar")
    sys.exit(0)
