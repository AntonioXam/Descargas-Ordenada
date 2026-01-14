#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script que FUERZA la integración de v3.1 en gui_avanzada.py"""

import sys
from pathlib import Path

def leer_archivo():
    """Lee el archivo actual."""
    archivo = Path("organizer/gui_avanzada.py")
    if not archivo.exists():
        print("❌ No se encuentra organizer/gui_avanzada.py")
        return None
    
    with open(archivo, 'r', encoding='utf-8') as f:
        return f.read()

def inyectar_imports(contenido):
    """Inyecta los imports v3.1 si no están."""
    # Verificar si ya están
    if "from .native_notifications import" in contenido:
        print("✅ Imports v3.1 ya presentes")
        return contenido
    
    print("🔧 Inyectando imports v3.1...")
    
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
    
    # Buscar donde insertar (después de los imports del organizador)
    linea_buscar = "from .autostart import GestorAutoarranque"
    if linea_buscar in contenido:
        contenido = contenido.replace(
            linea_buscar + "\n",
            linea_buscar + "\n" + imports_v31 + "\n"
        )
        print("✅ Imports v3.1 inyectados")
    else:
        print("⚠️  No se encontró la línea de referencia para imports")
    
    return contenido

def inyectar_inicializacion(contenido):
    """Inyecta la inicialización de módulos v3.1."""
    # Verificar si ya está
    if "self.notificador = obtener_notificador()" in contenido or "self.config_portable = obtener_config()" in contenido:
        print("✅ Inicialización v3.1 ya presente")
        return contenido
    
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
    
    # Buscar donde insertar (después de self.gestor_autoarranque)
    linea_buscar = "self.gestor_autoarranque = GestorAutoarranque()"
    if linea_buscar in contenido:
        contenido = contenido.replace(
            linea_buscar + "\n",
            linea_buscar + "\n" + init_code + "\n"
        )
        print("✅ Inicialización v3.1 inyectada")
    else:
        print("⚠️  No se encontró la línea de referencia para inicialización")
    
    return contenido

def inyectar_controles_gui(contenido):
    """Inyecta los controles visuales v3.1."""
    # Verificar si ya están
    if "combo_temas" in contenido and "chk_notificaciones" in contenido:
        print("✅ Controles GUI v3.1 ya presentes")
        return contenido
    
    print("🔧 Inyectando controles GUI v3.1...")
    
    controles_code = '''
        
        # ═══════════════════════════════════════════════════════════════
        # CONTROLES v3.1
        # ═══════════════════════════════════════════════════════════════
        
        # Notificaciones nativas
        if NOTIFICACIONES_DISPONIBLES:
            self.chk_notificaciones = QCheckBox("🔔 Notificaciones nativas del sistema")
            self.chk_notificaciones.setChecked(True)
            self.chk_notificaciones.setToolTip("Muestra notificaciones cuando se organizan archivos")
            self.chk_notificaciones.toggled.connect(self._toggle_notificaciones)
            config_layout.addWidget(self.chk_notificaciones)
        
        # Selector de tema
        if TEMAS_DISPONIBLES:
            tema_layout = QHBoxLayout()
            tema_layout.addWidget(QLabel("🎨 Tema visual:"))
            
            self.combo_temas = QComboBox()
            temas_disponibles = self.gestor_temas.obtener_nombres_temas()
            for tema_nombre in temas_disponibles:
                tema_display = tema_nombre.replace("_", " ").title()
                self.combo_temas.addItem(tema_display, tema_nombre)
            
            tema_actual = self.gestor_temas.tema_actual
            for i in range(self.combo_temas.count()):
                if self.combo_temas.itemData(i) == tema_actual:
                    self.combo_temas.setCurrentIndex(i)
                    break
            
            self.combo_temas.currentIndexChanged.connect(self._cambiar_tema)
            tema_layout.addWidget(self.combo_temas)
            config_layout.addLayout(tema_layout)
        
        # Menú contextual
        if MENU_CONTEXTUAL_DISPONIBLE:
            self.chk_menu_contextual = QCheckBox("🖱️ Menú contextual (Click derecho)")
            self.chk_menu_contextual.setChecked(False)
            self.chk_menu_contextual.setToolTip("Añade opción al menú de click derecho de Windows")
            self.chk_menu_contextual.toggled.connect(self._toggle_menu_contextual)
            config_layout.addWidget(self.chk_menu_contextual)
        
        # Botón de actualizaciones
        if ACTUALIZACIONES_DISPONIBLES:
            btn_actualizar = QPushButton("🔄 Buscar Actualizaciones")
            btn_actualizar.setToolTip("Verifica si hay nuevas versiones disponibles")
            btn_actualizar.clicked.connect(self._verificar_actualizaciones)
            config_layout.addWidget(btn_actualizar)
'''
    
    # Buscar donde insertar (después de chk_recursivo)
    linea_buscar = 'self.chk_recursivo = QCheckBox("🔍 Buscar en subcarpetas")\n        config_layout.addWidget(self.chk_recursivo)'
    
    if linea_buscar in contenido:
        contenido = contenido.replace(
            linea_buscar + "\n",
            linea_buscar + "\n" + controles_code + "\n"
        )
        print("✅ Controles GUI v3.1 inyectados")
    else:
        print("⚠️  No se encontró la línea de referencia para controles GUI")
    
    return contenido

def inyectar_metodos(contenido):
    """Inyecta los métodos de callback v3.1."""
    # Verificar si ya están
    if "_toggle_notificaciones" in contenido and "_cambiar_tema" in contenido:
        print("✅ Métodos v3.1 ya presentes")
        return contenido
    
    print("🔧 Inyectando métodos v3.1...")
    
    metodos_code = '''
    
    # ═══════════════════════════════════════════════════════════════
    # MÉTODOS v3.1
    # ═══════════════════════════════════════════════════════════════
    
    def _toggle_notificaciones(self, activo):
        """Activa/desactiva notificaciones nativas."""
        if self.notificador:
            if activo:
                self.notificador.habilitar()
            else:
                self.notificador.deshabilitar()
            
            if self.config_portable:
                self.config_portable.establecer("notificaciones_habilitadas", activo)
    
    def _cambiar_tema(self, index):
        """Cambia el tema visual."""
        if not self.gestor_temas:
            return
        
        tema_nombre = self.combo_temas.itemData(index)
        if tema_nombre:
            self.gestor_temas.establecer_tema_actual(tema_nombre)
            tema_obj = self.gestor_temas.obtener_tema_actual()
            self.setStyleSheet(tema_obj.obtener_stylesheet())
            
            if self.config_portable:
                self.config_portable.establecer("tema", tema_nombre)
    
    def _toggle_menu_contextual(self, activo):
        """Activa/desactiva menú contextual."""
        if not self.gestor_menu_contextual:
            return
        
        try:
            if activo:
                exito, mensaje = self.gestor_menu_contextual.registrar_menu_contextual("carpetas")
                if not exito:
                    self.chk_menu_contextual.setChecked(False)
                    QMessageBox.warning(self, "Error", f"No se pudo registrar: {mensaje}")
            else:
                self.gestor_menu_contextual.desregistrar_menu_contextual()
        except Exception as e:
            self.chk_menu_contextual.setChecked(False)
            QMessageBox.critical(self, "Error", str(e))
    
    def _verificar_actualizaciones(self):
        """Verifica actualizaciones disponibles."""
        if not self.gestor_actualizaciones:
            return
        
        try:
            hay_nueva, info = self.gestor_actualizaciones.verificar_actualizaciones(forzar=True)
            
            if hay_nueva and info:
                respuesta = QMessageBox.question(
                    self,
                    "Nueva Versión",
                    f"✨ Versión {info['version']} disponible!\\n\\n¿Abrir página de descarga?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if respuesta == QMessageBox.Yes:
                    self.gestor_actualizaciones.abrir_pagina_descarga()
            else:
                QMessageBox.information(
                    self,
                    "Actualizado",
                    f"✅ Estás en la última versión\\n\\nVersión: {self.gestor_actualizaciones.obtener_version_actual()}"
                )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo verificar: {e}")
'''
    
    # Insertar al final del archivo, antes del último if __name__
    if "if __name__ == '__main__':" in contenido:
        contenido = contenido.replace(
            "\nif __name__ == '__main__':",
            metodos_code + "\n\nif __name__ == '__main__':"
        )
        print("✅ Métodos v3.1 inyectados")
    else:
        # Si no hay if __name__, añadir al final
        contenido += metodos_code
        print("✅ Métodos v3.1 añadidos al final")
    
    return contenido

def guardar_archivo(contenido):
    """Guarda el archivo modificado."""
    archivo = Path("organizer/gui_avanzada.py")
    
    # Hacer backup
    backup = Path("organizer/gui_avanzada.py.backup_v3.1")
    if archivo.exists():
        with open(archivo, 'r', encoding='utf-8') as f:
            with open(backup, 'w', encoding='utf-8') as fb:
                fb.write(f.read())
        print(f"💾 Backup guardado en: {backup}")
    
    # Guardar nuevo contenido
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print(f"✅ Archivo guardado: {archivo}")

def main():
    print("="*70)
    print("   🍄 FORZAR INTEGRACIÓN v3.1 - gui_avanzada.py")
    print("="*70)
    print()
    
    # Leer archivo
    contenido = leer_archivo()
    if not contenido:
        return 1
    
    print(f"📄 Archivo actual: {len(contenido)} caracteres\n")
    
    # Inyectar cada componente
    contenido = inyectar_imports(contenido)
    contenido = inyectar_inicializacion(contenido)
    contenido = inyectar_controles_gui(contenido)
    contenido = inyectar_metodos(contenido)
    
    # Guardar
    print()
    guardar_archivo(contenido)
    
    print()
    print("="*70)
    print("✅ INTEGRACIÓN FORZADA COMPLETADA")
    print("="*70)
    print()
    print("🚀 Ahora puedes:")
    print("   1. Cerrar el editor si está abierto")
    print("   2. Ejecutar: python INICIAR.py --gui")
    print("   3. Verás los controles v3.1 en la pestaña Principal")
    print()
    print("="*70)
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
