#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para integrar características v3.1 en gui_avanzada.py"""

import sys
from pathlib import Path

def integrar_imports():
    """Integra los imports de v3.1 en gui_avanzada.py"""
    
    archivo = Path("organizer/gui_avanzada.py")
    
    if not archivo.exists():
        print(f"❌ No se encuentra {archivo}")
        return False
    
    # Leer archivo actual
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Verificar si ya tiene los imports v3.1
    if "native_notifications" in contenido:
        print("✅ gui_avanzada.py ya tiene los imports v3.1")
        return True
    
    print("🔧 Inyectando imports v3.1...")
    
    # Buscar la línea después de los imports
    imports_v31 = '''
# ═══════════════════════════════════════════════════════════════
# IMPORTS v3.1 - Nuevas características
# ═══════════════════════════════════════════════════════════════

# Importar notificaciones nativas (v3.1)
try:
    from .native_notifications import obtener_notificador
    NOTIFICACIONES_DISPONIBLES = True
except ImportError:
    NOTIFICACIONES_DISPONIBLES = False

# Importar configuración portable (v3.1)
try:
    from .portable_config import obtener_config
    CONFIG_PORTABLE_DISPONIBLE = True
except ImportError:
    CONFIG_PORTABLE_DISPONIBLE = False

# Importar sistema de temas (v3.1)
try:
    from .temas import obtener_gestor_temas
    TEMAS_DISPONIBLES = True
except ImportError:
    TEMAS_DISPONIBLES = False

# Importar menú contextual (v3.1)
try:
    from .context_menu import GestorMenuContextual
    MENU_CONTEXTUAL_DISPONIBLE = sys.platform == "win32"
except ImportError:
    MENU_CONTEXTUAL_DISPONIBLE = False

# Importar sistema de actualizaciones (v3.1)
try:
    from .actualizaciones import obtener_gestor_actualizaciones
    ACTUALIZACIONES_DISPONIBLES = True
except ImportError:
    ACTUALIZACIONES_DISPONIBLES = False

'''
    
    # Buscar donde insertar
    lineas = contenido.split('\n')
    nueva_contenido = []
    insertado = False
    
    for i, linea in enumerate(lineas):
        nueva_contenido.append(linea)
        
        # Insertar después de los imports del organizador
        if not insertado and "from .autostart import GestorAutoarranque" in linea:
            nueva_contenido.append(imports_v31)
            insertado = True
    
    if not insertado:
        print("❌ No se pudo encontrar donde insertar los imports")
        return False
    
    # Guardar
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write('\n'.join(nueva_contenido))
    
    print(f"✅ Imports v3.1 integrados en {archivo}")
    return True

def integrar_inicializacion():
    """Integra la inicialización de módulos v3.1"""
    
    archivo = Path("organizer/gui_avanzada.py")
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Verificar si ya tiene la inicialización
    if "self.notificador = obtener_notificador()" in contenido or "self.config_portable = obtener_config()" in contenido:
        print("✅ gui_avanzada.py ya tiene la inicialización v3.1")
        return True
    
    print("🔧 Inyectando inicialización v3.1...")
    
    init_code = '''
        # ═══════════════════════════════════════════════════════════════
        # INICIALIZAR MÓDULOS v3.1
        # ═══════════════════════════════════════════════════════════════
        
        # Configuración portable
        if CONFIG_PORTABLE_DISPONIBLE:
            self.config_portable = obtener_config()
        else:
            self.config_portable = None
        
        # Sistema de temas
        if TEMAS_DISPONIBLES:
            self.gestor_temas = obtener_gestor_temas()
            if self.config_portable:
                tema_guardado = self.config_portable.obtener("tema", "azul_oscuro")
                self.gestor_temas.establecer_tema_actual(tema_guardado)
        else:
            self.gestor_temas = None
        
        # Notificaciones nativas
        if NOTIFICACIONES_DISPONIBLES:
            self.notificador = obtener_notificador()
            if self.config_portable:
                notif_hab = self.config_portable.obtener("notificaciones_habilitadas", True)
                if notif_hab:
                    self.notificador.habilitar()
                else:
                    self.notificador.deshabilitar()
        else:
            self.notificador = None
        
        # Menú contextual
        if MENU_CONTEXTUAL_DISPONIBLE:
            self.gestor_menu_contextual = GestorMenuContextual()
        else:
            self.gestor_menu_contextual = None
        
        # Sistema de actualizaciones
        if ACTUALIZACIONES_DISPONIBLES:
            self.gestor_actualizaciones = obtener_gestor_actualizaciones()
        else:
            self.gestor_actualizaciones = None
'''
    
    lineas = contenido.split('\n')
    nueva_contenido = []
    insertado = False
    
    for i, linea in enumerate(lineas):
        nueva_contenido.append(linea)
        
        # Insertar después de la inicialización del gestor de autoarranque
        if not insertado and "self.gestor_autoarranque = GestorAutoarranque()" in linea:
            nueva_contenido.append(init_code)
            insertado = True
    
    if not insertado:
        print("⚠️  No se pudo inyectar inicialización automáticamente")
        print("    Será necesario hacerlo manualmente")
        return False
    
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write('\n'.join(nueva_contenido))
    
    print("✅ Inicialización v3.1 integrada")
    return True

if __name__ == "__main__":
    print("═" * 70)
    print("   🍄 INTEGRADOR v3.1 - gui_avanzada.py")
    print("═" * 70)
    print()
    
    exito = True
    
    # Paso 1: Integrar imports
    if not integrar_imports():
        exito = False
    
    print()
    
    # Paso 2: Integrar inicialización
    if not integrar_inicializacion():
        exito = False
    
    print()
    print("═" * 70)
    
    if exito:
        print("✅ INTEGRACIÓN COMPLETADA")
        print()
        print("Ahora necesitas añadir los controles en la pestaña Principal.")
        print("Busca la sección de 'Configuración' y añade:")
        print("  • Checkbox de notificaciones")
        print("  • ComboBox de temas")
        print("  • Checkbox de menú contextual")
        print("  • Botón de actualizaciones")
    else:
        print("⚠️  INTEGRACIÓN PARCIAL")
        print("Revisa los mensajes de error arriba")
    
    print("═" * 70)
