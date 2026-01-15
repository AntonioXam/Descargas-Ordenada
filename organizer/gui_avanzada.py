#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GUI Avanzada para DescargasOrdenadas v3.0 con todas las funcionalidades
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime

try:
    from PySide6.QtCore import Qt, Signal, Slot, QThread, QTimer, QEvent
    from PySide6.QtGui import QIcon, QAction, QPixmap, QPainter, QGuiApplication
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
        QPushButton, QLabel, QCheckBox, QListWidget, QProgressBar, 
        QMessageBox, QSystemTrayIcon, QTabWidget, QTextEdit, QSlider, 
        QGroupBox, QComboBox, QPlainTextEdit, QInputDialog, QMenu,
        QFileDialog
    )
except ImportError:
    print("❌ PySide6 no instalado. Ejecuta: pip install PySide6")
    sys.exit(1)

from .file_organizer import OrganizadorArchivos
from .autostart import GestorAutoarranque

# Importar notificaciones nativas
try:
    from .native_notifications import NotificadorNativo
    NOTIFICACIONES_NATIVAS = True
except ImportError:
    NOTIFICACIONES_NATIVAS = False

# Importar configuración portable
try:
    from .portable_config import obtener_config
    CONFIG_PORTABLE = True
except ImportError:
    CONFIG_PORTABLE = False

# Importar sistema de temas
try:
    from .temas import obtener_gestor_temas
    TEMAS_DISPONIBLES = True
except ImportError:
    TEMAS_DISPONIBLES = False

# Importar menú contextual
try:
    from .context_menu import GestorMenuContextual
    MENU_CONTEXTUAL_DISPONIBLE = sys.platform == "win32"
except ImportError:
    MENU_CONTEXTUAL_DISPONIBLE = False

# Importar sistema de actualizaciones (versión mejorada con descarga)
try:
    from .actualizaciones_mejorado import obtener_gestor_actualizaciones
    ACTUALIZACIONES_DISPONIBLES = True
except ImportError:
    try:
        from .actualizaciones import obtener_gestor_actualizaciones
        ACTUALIZACIONES_DISPONIBLES = True
    except ImportError:
        ACTUALIZACIONES_DISPONIBLES = False

logger = logging.getLogger('organizador.gui_avanzada')

class OrganizadorAvanzado(QMainWindow):
    """GUI completa con todas las funcionalidades avanzadas."""
    
    def __init__(self, directorio=None, auto_organizacion=False):
        super().__init__()
        
        # Inicializar organizador (MODO AVANZADO por defecto - con subcarpetas)
        if directorio:
            self.organizador = OrganizadorArchivos(carpeta_descargas=str(directorio), usar_subcarpetas=True)
        else:
            self.organizador = OrganizadorArchivos(usar_subcarpetas=True)
        
        self.gestor_autoarranque = GestorAutoarranque()
        
        # Inicializar menú contextual
        if MENU_CONTEXTUAL_DISPONIBLE:
            self.gestor_menu_contextual = GestorMenuContextual()
        else:
            self.gestor_menu_contextual = None
        
        # Inicializar sistema de actualizaciones
        if ACTUALIZACIONES_DISPONIBLES:
            self.gestor_actualizaciones = obtener_gestor_actualizaciones()
        else:
            self.gestor_actualizaciones = None
        
        # Inicializar configuración portable
        if CONFIG_PORTABLE:
            self.config_portable = obtener_config()
        else:
            self.config_portable = None
        
        # Inicializar sistema de temas
        if TEMAS_DISPONIBLES:
            self.gestor_temas = obtener_gestor_temas()
            # Cargar tema guardado
            if self.config_portable:
                tema_guardado = self.config_portable.obtener("tema", "azul_oscuro")
                self.gestor_temas.establecer_tema_actual(tema_guardado)
        else:
            self.gestor_temas = None
        
        # Inicializar notificaciones nativas
        if NOTIFICACIONES_NATIVAS:
            self.notificador = NotificadorNativo()
            if self.config_portable:
                # Cargar preferencia de notificaciones
                notif_habilitadas = self.config_portable.obtener("notificaciones_habilitadas", True)
                if not notif_habilitadas:
                    self.notificador.deshabilitar()
        else:
            self.notificador = None
        
        # Estado de la aplicación
        self.en_bandeja = False
        self.cerrar_completamente = False
        self._sincronizando_controles = False
        
        # Configuración ventana
        self.setWindowTitle("🍄 DescargasOrdenadas - Organizador Automático")
        self.setMinimumSize(1100, 800)
        self._ajustar_tamano_inicial()
        
        self._setup_ui()
        self._aplicar_tema()  # Aplicar tema (reemplaza _aplicar_estilos_modernos)
        self._setup_system_tray()
        self._inicializar_modulos()
        
        # Timer para organización automática
        self.timer_auto = QTimer()
        self.timer_auto.timeout.connect(self._organizar_automatico)
        
        # Timer para verificar actualizaciones periódicamente
        self.timer_actualizaciones = QTimer()
        self.timer_actualizaciones.timeout.connect(self._verificar_actualizaciones_silencioso)
        
        # Activar auto-organización si está habilitada al inicio (para autostart)
        if auto_organizacion:
            # Delay de 5 segundos para que la aplicación se inicie completamente
            QTimer.singleShot(5000, lambda: self._toggle_auto_organizacion(True))
        
        # Verificar actualizaciones al inicio (después de 10 segundos)
        if self.gestor_actualizaciones:
            QTimer.singleShot(10000, self._verificar_actualizaciones_silencioso)
            # Verificar cada 24 horas (86400000 ms) mientras la app está abierta
            self.timer_actualizaciones.start(86400000)  # 24 horas
    
    def _ajustar_tamano_inicial(self):
        """Ajusta el tamaño inicial según la resolución para mostrar todo correctamente."""
        try:
            screen = QGuiApplication.primaryScreen()
            if not screen:
                self.resize(1200, 850)
                return
            
            geom = screen.availableGeometry()
            objetivo_w = int(geom.width() * 0.9)
            objetivo_h = int(geom.height() * 0.9)
            
            min_w, min_h = 1100, 800
            ancho = min(max(min_w, objetivo_w), geom.width())
            alto = min(max(min_h, objetivo_h), geom.height())
            
            self.resize(ancho, alto)
            
            # Centrar la ventana
            x = geom.x() + (geom.width() - ancho) // 2
            y = geom.y() + (geom.height() - alto) // 2
            self.move(x, y)
        except Exception:
            self.resize(1200, 850)
    
    def _aplicar_tema(self):
        """Aplica el tema visual actual."""
        if self.gestor_temas:
            tema = self.gestor_temas.obtener_tema_actual()
            self.setStyleSheet(tema.obtener_stylesheet())
        else:
            # Fallback al tema azul oscuro estático
            self._aplicar_estilos_modernos()
    
    def _aplicar_estilos_modernos(self):
        """Aplica estilos modernos con tema oscuro mejorado (fallback)."""
        self.setStyleSheet("""
            QMainWindow { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #1a1a2e, stop:1 #16213e);
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 2px solid #0f3460;
                background-color: #16213e;
                border-radius: 10px;
                margin-top: 8px;
                padding: 5px;
            }
            QTabBar::tab {
                padding: 14px 24px;
                margin-right: 4px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #0f3460, stop:1 #0a2647);
                border: 1px solid #1a1a2e;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-weight: bold;
                color: #b0b0c0;
                font-size: 13px;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #00d4ff, stop:1 #0084ff);
                color: #ffffff;
                border-bottom: 3px solid #00d4ff;
                padding-bottom: 11px;
            }
            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #16537e, stop:1 #113f67);
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0f3460;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #1a1a2e, stop:1 #16213e);
                color: #ffffff;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px 0 10px;
                color: #00d4ff;
                background-color: transparent;
                font-weight: bold;
            }
            QCheckBox {
                spacing: 10px;
                font-weight: normal;
                color: #e0e0e0;
                font-size: 13px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 5px;
                border: 2px solid #0f3460;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #16213e, stop:1 #0a2647);
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #00d4ff, stop:1 #0084ff);
                border-color: #00d4ff;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMy41IDhMNi41IDExTDEyLjUgNSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz48L3N2Zz4=);
            }
            QCheckBox::indicator:hover {
                border-color: #00d4ff;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #1a3a5a, stop:1 #0f2a47);
            }
            QLabel {
                color: #ffffff;
                font-size: 13px;
            }
            QListWidget {
                border: 2px solid #0f3460;
                border-radius: 8px;
                background-color: #0a1929;
                color: #e0e0e0;
                padding: 5px;
                selection-background-color: #00d4ff;
                selection-color: #000000;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin: 2px 0;
            }
            QListWidget::item:hover {
                background-color: #16213e;
            }
            QTextEdit, QPlainTextEdit {
                border: 2px solid #0f3460;
                border-radius: 8px;
                background-color: #0a1929;
                color: #e0e0e0;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                line-height: 1.5;
            }
            QSlider::groove:horizontal {
                border: 1px solid #505050;
                height: 6px;
                background: #3d3d3d;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #45a049;
                width: 18px;
                border-radius: 9px;
                margin: -6px 0;
            }
            QSlider::handle:horizontal:hover {
                background: #66BB6A;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #00d4ff, stop:1 #0084ff);
                color: white;
                border: none;
                padding: 14px 24px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 13px;
                min-height: 18px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #00e1ff, stop:1 #00a3ff);
                box-shadow: 0 6px 8px rgba(0, 212, 255, 0.4);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #0084ff, stop:1 #0066cc);
                padding: 16px 24px 12px 24px;
            }
            QPushButton:disabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a3e, stop:1 #1a1a2e);
                color: #666677;
            }
            QComboBox {
                border: 1px solid #505050;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: #3d3d3d;
                color: #ffffff;
                font-size: 13px;
                min-height: 20px;
            }
            QComboBox:hover {
                border-color: #4CAF50;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid #ffffff;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #505050;
                background-color: #3d3d3d;
                color: #ffffff;
                selection-background-color: #4CAF50;
            }
            QProgressBar {
                border: 2px solid #0f3460;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                background-color: #0a1929;
                color: #ffffff;
                height: 24px;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #00d4ff, stop:1 #00a3ff);
                border-radius: 6px;
            }
        """)
    
    def _setup_system_tray(self):
        """Configura bandeja del sistema completa."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self._agregar_log("❌ Bandeja del sistema no disponible en este sistema")
            return
        
        # Crear icono para la bandeja
        self.tray_icon = QSystemTrayIcon(self)
        
        # Crear icono personalizado si no existe uno
        icon = self._crear_icono_personalizado()
        self.tray_icon.setIcon(icon)
        
        # Crear menú contextual
        tray_menu = QMenu()
        
        # Acciones del menú
        mostrar_action = QAction("📂 Mostrar Ventana", self)
        mostrar_action.triggered.connect(self._mostrar_ventana)
        tray_menu.addAction(mostrar_action)
        
        organizar_action = QAction("🔄 Organizar Ahora", self)
        organizar_action.triggered.connect(self._organizar)
        tray_menu.addAction(organizar_action)
        
        tray_menu.addSeparator()
        
        # Toggle auto-organización
        self.auto_action = QAction("⚡ Auto-Organización", self)
        self.auto_action.setCheckable(True)
        self.auto_action.triggered.connect(self._toggle_auto_organizacion)
        tray_menu.addAction(self.auto_action)
        
        tray_menu.addSeparator()
        
        # Información
        info_action = QAction(f"📁 {os.path.basename(self.organizador.carpeta_descargas)}", self)
        info_action.setEnabled(False)
        tray_menu.addAction(info_action)
        
        tray_menu.addSeparator()
        
        salir_action = QAction("❌ Salir", self)
        salir_action.triggered.connect(self._salir_completamente)
        tray_menu.addAction(salir_action)
        
        # Asignar menú al icono
        self.tray_icon.setContextMenu(tray_menu)
        
        # Conectar eventos
        self.tray_icon.activated.connect(self._tray_icon_activated)
        
        # Mostrar tooltip
        self.tray_icon.setToolTip("🍄 DescargasOrdenadas - Organizador Activo")
        
        # Mostrar icono
        self.tray_icon.show()
        
        self._agregar_log("✅ Bandeja del sistema configurada")
    
    def _inicializar_modulos(self):
        """Inicializa módulos avanzados."""
        funciones = []
        carpeta = Path(self.organizador.carpeta_descargas)
        
        # IA
        try:
            from .ai_categorizer import CategorizadorIA
            self.ai_categorizer = CategorizadorIA(carpeta)
            funciones.append("🤖 IA")
            if hasattr(self, 'lbl_ia_estado'):
                self.lbl_ia_estado.setText("✅ IA Categorización: Activa")
        except Exception as e:
            self.ai_categorizer = None
            if hasattr(self, 'lbl_ia_estado'):
                self.lbl_ia_estado.setText("❌ IA: No disponible")
            self._agregar_log(f"⚠️ IA no disponible: {e}")
        
        # Fechas
        try:
            # Usar el organizador de fechas del organizador principal si está disponible
            if hasattr(self.organizador, 'organizador_fechas') and self.organizador.organizador_fechas:
                self.date_organizer = self.organizador.organizador_fechas
                logger.info("📅 Usando organizador de fechas del organizador principal")
            else:
                # Fallback: crear instancia propia
                from .date_organizer import OrganizadorPorFecha
                self.date_organizer = OrganizadorPorFecha(carpeta)
                logger.info("📅 Creando instancia propia del organizador de fechas")
                
            funciones.append("📅 Fechas")
            
            # Verificar si fechas está activa
            try:
                if hasattr(self.date_organizer, 'activo') and self.date_organizer.activo:
                    if hasattr(self, 'lbl_estado_fechas'):
                        self.lbl_estado_fechas.setText("✅ Organización por fechas: ACTIVADA")
                        self.lbl_estado_fechas.setStyleSheet("""
                            font-weight: bold; 
                            padding: 15px; 
                            color: #ffffff;
                            background-color: #4CAF50;
                            border-radius: 8px;
                            font-size: 15px;
                            text-align: center;
                        """)
                        if hasattr(self, 'btn_activar_fechas'):
                            self.btn_activar_fechas.setEnabled(False)
                        if hasattr(self, 'btn_desactivar_fechas'):
                            self.btn_desactivar_fechas.setEnabled(True)
            except Exception as e:
                logger.debug(f"Error verificando estado de fechas: {e}")
                
        except Exception as e:
            self.date_organizer = None
            self._agregar_log(f"⚠️ Fechas no disponible: {e}")
        
        # Duplicados
        try:
            from .duplicate_detector import DetectorDuplicados
            self.duplicate_detector = DetectorDuplicados(carpeta)
            funciones.append("🔍 Duplicados")
        except Exception as e:
            self.duplicate_detector = None
            self._agregar_log(f"⚠️ Duplicados no disponible: {e}")
        
        # Estadísticas
        try:
            from .statistics import EstadisticasOrganizador
            self.stats_manager = EstadisticasOrganizador(carpeta)
            funciones.append("📊 Stats")
        except Exception as e:
            self.stats_manager = None
            self._agregar_log(f"⚠️ Estadísticas no disponible: {e}")
        
        # Reglas
        try:
            from .custom_rules import GestorReglasPersonalizadas
            self.custom_rules = GestorReglasPersonalizadas(carpeta)
            funciones.append("⚙️ Reglas")
        except Exception as e:
            self.custom_rules = None
            self._agregar_log(f"⚠️ Reglas personalizadas no disponible: {e}")
        
        # Actualizar estado
        if hasattr(self, 'lbl_estado'):
            if funciones:
                self.lbl_estado.setText("✅ " + " | ".join(funciones))
            else:
                self.lbl_estado.setText("❌ Solo funcionalidades básicas")
        
        self._actualizar_datos()
    
    def _actualizar_datos(self):
        """Actualiza datos de las pestañas."""
        if hasattr(self, 'ai_categorizer') and self.ai_categorizer:
            self._actualizar_patrones()
        
        if hasattr(self, 'stats_manager') and self.stats_manager:
            self._actualizar_estadisticas()
    
    def _crear_icono_personalizado(self):
        """Crea un icono personalizado para la bandeja."""
        try:
            # Crear un pixmap de 64x64
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Dibujar fondo circular
            painter.setBrush(Qt.green)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(4, 4, 56, 56)
            
            # Dibujar símbolo de carpeta
            painter.setPen(Qt.white)
            painter.setFont(painter.font())
            painter.drawText(pixmap.rect(), Qt.AlignCenter, "📁")
            
            painter.end()
            
            return QIcon(pixmap)
        except:
            # Fallback a icono por defecto
            return self.style().standardIcon(self.style().SP_DirIcon)
    
    def _tray_icon_activated(self, reason):
        """Maneja la activación del icono de la bandeja."""
        if reason == QSystemTrayIcon.Trigger:  # Click simple
            self._mostrar_ocultar_ventana()
        elif reason == QSystemTrayIcon.DoubleClick:  # Doble click
            self._mostrar_ventana()
    
    def _mostrar_ocultar_ventana(self):
        """Alterna entre mostrar y ocultar la ventana."""
        if self.isVisible():
            self._ocultar_en_bandeja()
        else:
            self._mostrar_ventana()
    
    def _mostrar_ventana(self):
        """Muestra la ventana desde la bandeja."""
        self.show()
        self.raise_()
        self.activateWindow()
        self.en_bandeja = False
        
        # Mostrar consola si estaba oculta
        self._mostrar_consola()
        
        self._agregar_log("📂 Ventana restaurada desde bandeja del sistema")
    
    def _ocultar_en_bandeja(self):
        """Oculta la ventana en la bandeja del sistema."""
        if self.tray_icon and self.tray_icon.isVisible():
            self.hide()
            self.en_bandeja = True
            
            # Ocultar consola
            self._ocultar_consola()
            
            # Mostrar notificación
            self.tray_icon.showMessage(
                "🍄 DescargasOrdenadas",
                "Aplicación minimizada a la bandeja del sistema",
                QSystemTrayIcon.Information,
                3000
            )
            
            self._agregar_log("📱 Aplicación minimizada a bandeja del sistema")
        else:
            # Si no hay bandeja disponible, solo minimizar
            self.showMinimized()
    
    def _salir_completamente(self):
        """Cierra la aplicación completamente."""
        self._agregar_log("🚪 Cerrando aplicación completamente...")
        
        # Detener timer si está activo
        if hasattr(self, 'timer_auto') and self.timer_auto.isActive():
            self.timer_auto.stop()
        
        if hasattr(self, 'timer_actualizaciones') and self.timer_actualizaciones.isActive():
            self.timer_actualizaciones.stop()
        
        # Cerrar la consola completamente
        self._cerrar_consola()
        
        self.cerrar_completamente = True
        
        # Ocultar el tray icon
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
        
        # Cerrar la aplicación Qt
        QApplication.quit()
        
        # Forzar cierre del proceso Python de múltiples formas
        import sys
        import os
        
        # Método 1: Salida normal de Python
        sys.exit(0)
        
        # Método 2: Terminar proceso si el anterior falla (último recurso)
        try:
            os._exit(0)
        except:
            pass
    
    def _toggle_auto_organizacion(self, activo):
        """Activa/desactiva la organización automática (mantener compatibilidad)."""
        # Esta función mantiene compatibilidad con código existente
        # Activa el modo básico por defecto
        if hasattr(self, 'chk_auto_basico'):
            self.chk_auto_basico.setChecked(activo)
    
    @Slot(bool)
    def _toggle_auto_organizacion_basico(self, activo):
        """Toggle auto-organización básica cada 30 segundos."""
        try:
            if activo:
                # Desactivar el modo detallado si estaba activo
                if hasattr(self, 'chk_auto_detallado'):
                    self.chk_auto_detallado.setChecked(False)
                
                if not hasattr(self, 'timer_auto') or self.timer_auto is None:
                    self.timer_auto = QTimer()
                    self.timer_auto.timeout.connect(self._organizar_automatico)
                
                # Obtener intervalo del selector
                intervalo_segundos = self.combo_intervalo_auto.currentData()
                intervalo_ms = intervalo_segundos * 1000
                intervalo_texto = self.combo_intervalo_auto.currentText()
                self.timer_auto.start(intervalo_ms)
                self._agregar_log(f"⚡ Auto-organización BÁSICA ACTIVADA ({intervalo_texto})")
                
                # Actualizar tooltip de la bandeja
                if self.tray_icon:
                    self.tray_icon.setToolTip(f"🍄 DescargasOrdenadas - Auto BÁSICA ({intervalo_texto})")
                    
                # Actualizar estado visual
                self.lbl_estado.setText(f"📁 Auto-organización BÁSICA: ACTIVADA ({intervalo_texto})")
                self.lbl_estado.setStyleSheet("""
                    font-weight: bold; 
                    padding: 10px; 
                    color: #ffffff;
                    background-color: #4CAF50;
                    border-radius: 6px;
                    font-size: 14px;
                """)
            else:
                if hasattr(self, 'timer_auto') and self.timer_auto:
                    self.timer_auto.stop()
                
                self._agregar_log("⏸️ Auto-organización BÁSICA DESACTIVADA")
                self._actualizar_estado_auto_organizacion()
                
        except Exception as e:
            self._agregar_log(f"❌ Error configurando auto-organización básica: {e}")
            QMessageBox.critical(self, "Error", f"❌ Error: {e}")

    @Slot(bool)
    def _toggle_auto_organizacion_detallado(self, activo):
        """Toggle auto-organización detallada cada 30 segundos."""
        try:
            if activo:
                # Desactivar el modo básico si estaba activo
                if hasattr(self, 'chk_auto_basico'):
                    self.chk_auto_basico.setChecked(False)
                
                if not hasattr(self, 'timer_auto') or self.timer_auto is None:
                    self.timer_auto = QTimer()
                    self.timer_auto.timeout.connect(self._organizar_automatico)
                
                # Obtener intervalo del selector
                intervalo_segundos = self.combo_intervalo_auto.currentData()
                intervalo_ms = intervalo_segundos * 1000
                intervalo_texto = self.combo_intervalo_auto.currentText()
                self.timer_auto.start(intervalo_ms)
                self._agregar_log(f"⚡ Auto-organización DETALLADA ACTIVADA ({intervalo_texto})")
                
                # Actualizar tooltip de la bandeja
                if self.tray_icon:
                    self.tray_icon.setToolTip(f"🍄 DescargasOrdenadas - Auto DETALLADA ({intervalo_texto})")
                    
                # Actualizar estado visual
                self.lbl_estado.setText(f"🔧 Auto-organización DETALLADA: ACTIVADA ({intervalo_texto})")
                self.lbl_estado.setStyleSheet("""
                    font-weight: bold; 
                    padding: 10px; 
                    color: #ffffff;
                    background-color: #2196F3;
                    border-radius: 6px;
                    font-size: 14px;
                """)
            else:
                if hasattr(self, 'timer_auto') and self.timer_auto:
                    self.timer_auto.stop()
                
                self._agregar_log("⏸️ Auto-organización DETALLADA DESACTIVADA")
                self._actualizar_estado_auto_organizacion()
                
        except Exception as e:
            self._agregar_log(f"❌ Error configurando auto-organización detallada: {e}")
            QMessageBox.critical(self, "Error", f"❌ Error: {e}")
    
    def _actualizar_estado_auto_organizacion(self):
        """Actualiza el estado visual cuando no hay auto-organización activa."""
        # Verificar si algún modo sigue activo
        auto_activa = False
        if hasattr(self, 'chk_auto_basico') and self.chk_auto_basico.isChecked():
            auto_activa = True
        if hasattr(self, 'chk_auto_detallado') and self.chk_auto_detallado.isChecked():
            auto_activa = True
            
        if not auto_activa:
            # Actualizar tooltip de la bandeja
            if self.tray_icon:
                self.tray_icon.setToolTip("🍄 DescargasOrdenadas - Auto-organización INACTIVA")
                
            # Actualizar estado visual
            self.lbl_estado.setText("⏸️ Auto-organización: DESACTIVADA")
            self.lbl_estado.setStyleSheet("""
                font-weight: bold; 
                padding: 10px; 
                color: #ffffff;
                background-color: #f44336;
                border-radius: 6px;
                font-size: 14px;
            """)

    def _deshacer_organizacion(self):
        """Deshace toda la organización moviendo archivos de vuelta a la raíz."""
        reply = QMessageBox.question(
            self, "⚠️ Deshacer Organización",
            "🚨 ADVERTENCIA: Esto moverá TODOS los archivos de las carpetas organizadas de vuelta a la raíz de Descargas.\n\n"
            "Esto te permitirá cambiar el tipo de organización limpiamente.\n\n"
            "⚠️ ¿Estás seguro de que quieres continuar?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.progress_bar.setVisible(True)
                self.progress_bar.setRange(0, 0)
                
                carpeta_descargas = Path(self.organizador.carpeta_descargas)
                archivos_movidos = 0
                errores = []
                
                # Buscar todas las carpetas organizadas
                carpetas_a_revisar = []
                for item in carpeta_descargas.iterdir():
                    if item.is_dir() and item.name not in ['.config', '.git', '__pycache__']:
                        carpetas_a_revisar.append(item)
                
                # Mover archivos recursivamente de vuelta a la raíz
                def mover_archivos_de_carpeta(carpeta, nivel=0):
                    nonlocal archivos_movidos, errores
                    
                    if nivel > 10:  # Evitar bucles infinitos
                        return
                        
                    try:
                        for item in carpeta.iterdir():
                            if item.is_file():
                                # Encontrar un nombre único en la raíz
                                nombre_destino = item.name
                                contador = 1
                                while (carpeta_descargas / nombre_destino).exists():
                                    nombre_base, extension = os.path.splitext(item.name)
                                    nombre_destino = f"{nombre_base}_{contador}{extension}"
                                    contador += 1
                                
                                try:
                                    destino = carpeta_descargas / nombre_destino
                                    item.rename(destino)
                                    archivos_movidos += 1
                                    self._agregar_log(f"📁➡️📄 {item.name} → raíz")
                                except Exception as e:
                                    errores.append(f"Error moviendo {item.name}: {e}")
                                    
                            elif item.is_dir():
                                # Recursivamente mover archivos de subcarpetas
                                mover_archivos_de_carpeta(item, nivel + 1)
                    except Exception as e:
                        errores.append(f"Error procesando carpeta {carpeta.name}: {e}")
                
                # Procesar todas las carpetas
                for carpeta in carpetas_a_revisar:
                    mover_archivos_de_carpeta(carpeta)
                
                # Eliminar carpetas vacías
                def eliminar_carpetas_vacias(carpeta):
                    try:
                        for item in carpeta.iterdir():
                            if item.is_dir():
                                eliminar_carpetas_vacias(item)
                                try:
                                    if not any(item.iterdir()):  # Si está vacía
                                        item.rmdir()
                                        self._agregar_log(f"🗑️ Carpeta vacía eliminada: {item.name}")
                                except OSError:
                                    pass  # No pasa nada si no se puede eliminar
                    except Exception:
                        pass
                
                for carpeta in carpetas_a_revisar:
                    if carpeta.exists():
                        eliminar_carpetas_vacias(carpeta)
                        try:
                            if not any(carpeta.iterdir()):
                                carpeta.rmdir()
                                self._agregar_log(f"🗑️ Carpeta principal eliminada: {carpeta.name}")
                        except OSError:
                            pass
                
                # Limpiar huella de archivos organizados
                if hasattr(self.organizador, 'archivos_procesados'):
                    self.organizador.archivos_procesados.clear()
                    self.organizador._guardar_huella()
                
                mensaje = f"✅ Organización deshecha!\n\n"
                mensaje += f"📁 {archivos_movidos} archivos movidos a la raíz"
                if errores:
                    mensaje += f"\n⚠️ {len(errores)} errores (ver logs)"
                
                QMessageBox.information(self, "Operación Completada", mensaje)
                self._actualizar_datos()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ Error deshaciendo organización: {e}")
            finally:
                self.progress_bar.setVisible(False)
    
    def _organizar_automatico(self):
        """Organiza archivos automáticamente en segundo plano."""
        try:
            import datetime
            hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
            
            # DEBUG: Mostrar que el timer está funcionando
            if hasattr(self, '_debug_timer_count'):
                self._debug_timer_count += 1
            else:
                self._debug_timer_count = 1
            
            # Determinar qué modo usar basado en qué checkbox está activo
            usar_subcarpetas = None
            modo_texto = ""
            
            if hasattr(self, 'chk_auto_detallado') and self.chk_auto_detallado.isChecked():
                usar_subcarpetas = True
                modo_texto = " (DETALLADO)"
            elif hasattr(self, 'chk_auto_basico') and self.chk_auto_basico.isChecked():
                usar_subcarpetas = False
                modo_texto = " (BÁSICO)"
            else:
                # Fallback: usar la configuración del checkbox normal
                usar_subcarpetas = self.chk_subcarpetas.isChecked()
                modo_texto = f" ({'DETALLADO' if usar_subcarpetas else 'BÁSICO'})"
            
            # Aplicar configuración
            self.organizador.usar_subcarpetas = usar_subcarpetas
            
            # Reorganizar todo de forma silenciosa (incluye subcarpetas)
            resultados, errores = self.organizador.reorganizar_completamente()
            total = sum(len(files) for cat in resultados.values() for files in cat.values())
            
            # Log de actividad (con o sin archivos)
            if total > 0:
                self._agregar_log(f"⚡ Auto-organización{modo_texto} {hora_actual}: {total} archivos organizados")
                
                # Notificación nativa
                if self.notificador and hasattr(self, '_debug_timer_count') and self._debug_timer_count % 10 == 0:
                    categorias = set(resultados.keys())
                    self.notificador.notificar_organizacion(total, categorias)
                
                # Actualizar tooltip de la bandeja para mostrar última actividad
                if self.tray_icon:
                    self.tray_icon.setToolTip(f"🍄 DescargasOrdenadas - Última org: {hora_actual} ({total} archivos)")
                    
                # Actualizar estadísticas si hay cambios
                self._actualizar_datos()
            else:
                # Log cada 5 ejecuciones para confirmar que funciona
                if self._debug_timer_count % 5 == 0:
                    self._agregar_log(f"🔍 Timer activo{modo_texto} {hora_actual}: revisando archivos... (#{self._debug_timer_count})")
                
                # Actualizar tooltip para mostrar que está funcionando
                if self.tray_icon:
                    self.tray_icon.setToolTip(f"🍄 DescargasOrdenadas - Revisando: {hora_actual} (Activo)")
                
        except Exception as e:
            self._agregar_log(f"❌ Error en auto-organización: {e}")
    
    def _ocultar_consola(self):
        """Oculta la consola de Windows de forma optimizada."""
        if sys.platform == "win32":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                user32 = ctypes.windll.user32
                
                console_window = kernel32.GetConsoleWindow()
                if console_window:
                    # SW_HIDE = 0, oculta completamente la ventana
                    user32.ShowWindow(console_window, 0)
                    
                    # Minimizar el impacto en la barra de tareas
                    # WS_EX_TOOLWINDOW evita que aparezca en la barra de tareas
                    GWL_EXSTYLE = -20
                    WS_EX_TOOLWINDOW = 0x00000080
                    
                    try:
                        current_style = user32.GetWindowLongW(console_window, GWL_EXSTYLE)
                        user32.SetWindowLongW(console_window, GWL_EXSTYLE, current_style | WS_EX_TOOLWINDOW)
                    except:
                        pass
                    
                    self._agregar_log("🔇 Consola externa ocultada completamente")
                    return True
            except Exception as e:
                self._agregar_log(f"❌ Error ocultando consola: {e}")
        else:
            self._agregar_log("ℹ️  Ocultar consola no disponible en este sistema operativo")
        return False

    def _mostrar_consola(self):
        """Muestra la consola de Windows."""
        if sys.platform == "win32":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                user32 = ctypes.windll.user32
                
                console_window = kernel32.GetConsoleWindow()
                if console_window:
                    user32.ShowWindow(console_window, 5)  # SW_SHOW
                    self._agregar_log("🔊 Consola externa mostrada")
                    return True
            except Exception as e:
                self._agregar_log(f"❌ Error mostrando consola: {e}")
        else:
            self._agregar_log("ℹ️  Mostrar consola no disponible en este sistema operativo")
        return False

    def _cerrar_consola(self):
        """Cierra la ventana de consola del sistema de forma más efectiva."""
        try:
            if sys.platform == "win32":
                import ctypes
                import time
                
                console_window = ctypes.windll.kernel32.GetConsoleWindow()
                if console_window:
                    # Método 1: Ocultar primero para evitar parpadeo
                    ctypes.windll.user32.ShowWindow(console_window, 0)  # SW_HIDE
                    
                    # Método 2: Liberar la consola del proceso
                    try:
                        ctypes.windll.kernel32.FreeConsole()
                    except:
                        pass
                    
                    # Método 3: Enviar señal de cierre (más suave)
                    try:
                        ctypes.windll.user32.PostMessageW(console_window, 0x0010, 0, 0)  # WM_CLOSE
                    except:
                        pass
                    
                    # Dar un pequeño tiempo para que se cierre de forma limpia
                    time.sleep(0.05)
                        
        except Exception as e:
            logger.debug(f"No se pudo cerrar consola: {e}")
    
    def changeEvent(self, event):
        """Maneja eventos de cambio de estado de la ventana."""
        if event.type() == QEvent.Type.WindowStateChange:
            if self.isMinimized():
                # Si se minimiza, ir a la bandeja
                self._ocultar_en_bandeja()
                event.ignore()
                return
        
        super().changeEvent(event)
    
    def closeEvent(self, event):
        """Maneja el evento de cierre de la ventana."""
        if self.cerrar_completamente:
            # Cierre definitivo
            if hasattr(self, 'tray_icon'):
                self.tray_icon.hide()
            # Cerrar consola al salir completamente
            self._cerrar_consola()
            event.accept()
        else:
            # Minimizar a bandeja en lugar de cerrar
            if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
                self._ocultar_en_bandeja()
                event.ignore()
            else:
                # Si no hay bandeja, preguntar al usuario
                reply = QMessageBox.question(
                    self, 
                    "Cerrar Aplicación",
                    "¿Deseas cerrar completamente la aplicación?\n\n"
                    "• Sí: Cerrar completamente\n"
                    "• No: Minimizar a barra de tareas",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.cerrar_completamente = True
                    self._cerrar_consola()
                    event.accept()
                else:
                    self.showMinimized()
                    event.ignore()

    def _setup_ui(self):
        """Configura la interfaz principal."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        self.header = QLabel(f"🍄 DescargasOrdenadas | 📁 {self.organizador.carpeta_descargas}")
        self.header.setStyleSheet("""
            font-weight: bold; 
            font-size: 14px; 
            padding: 15px; 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 #4a90e2, stop:1 #67b26f);
            color: white;
            border-radius: 8px;
            margin-bottom: 5px;
        """)
        layout.addWidget(self.header)
        
        # Pestañas
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Footer con versión
        footer = QLabel("v3.2.0")
        footer.setAlignment(Qt.AlignRight)
        footer.setStyleSheet("""
            color: #888;
            font-size: 10px;
            padding: 5px 10px;
        """)
        layout.addWidget(footer)
        
        self._crear_tab_principal()
        self._crear_tab_ia()
        self._crear_tab_fechas()
        self._crear_tab_duplicados()
        self._crear_tab_estadisticas()
        self._crear_tab_logs()
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.statusBar().showMessage("🍄 Listo - Todas las funcionalidades cargadas")
    
    def _crear_tab_principal(self):
        """Pestaña principal de organización."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Botones principales
        botones_group = QGroupBox("🚀 Organización")
        botones_layout = QHBoxLayout(botones_group)
        
        btn_reorganizar = QPushButton("🔄  Organizar TODOS los archivos")
        btn_reorganizar.setStyleSheet("""
            QPushButton {
                padding: 12px; 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #FF9800, stop:1 #f57c00);
                color: white; 
                font-size: 14px; 
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f57c00, stop:1 #ef6c00);
            }
            QPushButton:pressed {
                background: #ef6c00;
            }
        """)
        btn_reorganizar.clicked.connect(self._reorganizar)
        botones_layout.addWidget(btn_reorganizar)
        
        # Botón deshacer todo
        btn_deshacer = QPushButton("↩️  Deshacer cambios")
        btn_deshacer.setStyleSheet("""
            QPushButton {
                padding: 12px; 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f44336, stop:1 #d32f2f);
                color: white; 
                font-size: 14px; 
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #d32f2f, stop:1 #c62828);
            }
            QPushButton:pressed {
                background: #c62828;
            }
        """)
        btn_deshacer.setToolTip("Saca TODOS los archivos de las carpetas organizadas y los deja en la raíz de Descargas")
        btn_deshacer.clicked.connect(self._deshacer_organizacion)
        botones_layout.addWidget(btn_deshacer)
        
        layout.addWidget(botones_group)
        
        # Configuraciones
        config_group = QGroupBox("⚙️ Configuración")
        config_layout = QVBoxLayout(config_group)
        
        # Selección de carpeta
        carpeta_layout = QHBoxLayout()
        self.lbl_carpeta_actual = QLabel(f"📁 Carpeta actual: {os.path.basename(self.organizador.carpeta_descargas)}")
        self.lbl_carpeta_actual.setStyleSheet("font-weight: bold; color: #4CAF50;")
        carpeta_layout.addWidget(self.lbl_carpeta_actual)
        
        btn_seleccionar_carpeta = QPushButton("📂  Seleccionar otra carpeta")
        btn_seleccionar_carpeta.setStyleSheet("""
            QPushButton {
                padding: 8px 16px; 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2196F3, stop:1 #1976D2);
                color: white; 
                font-size: 12px; 
                font-weight: bold;
                border-radius: 5px;
                border: none;
                max-width: 150px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #1976D2, stop:1 #1565C0);
            }
            QPushButton:pressed {
                background: #1565C0;
            }
        """)
        btn_seleccionar_carpeta.clicked.connect(self._seleccionar_carpeta)
        carpeta_layout.addWidget(btn_seleccionar_carpeta)
        
        btn_reset_carpeta = QPushButton("↻ Descargas")
        btn_reset_carpeta.setStyleSheet("""
            QPushButton {
                padding: 8px 12px; 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #757575, stop:1 #616161);
                color: white; 
                font-size: 12px; 
                font-weight: bold;
                border-radius: 5px;
                border: none;
                max-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #616161, stop:1 #424242);
            }
            QPushButton:pressed {
                background: #424242;
            }
        """)
        btn_reset_carpeta.setToolTip("Volver a la carpeta de descargas predeterminada")
        btn_reset_carpeta.clicked.connect(self._reset_carpeta_descargas)
        carpeta_layout.addWidget(btn_reset_carpeta)
        
        config_layout.addLayout(carpeta_layout)
        
        # Grupo de inicio automático
        autostart_layout = QHBoxLayout()
        autostart_layout.addWidget(QLabel("🚀 Inicio con Windows:"))
        
        # Botón para crear acceso directo en startup
        btn_crear_acceso_startup = QPushButton("✅  Activar inicio automático")
        btn_crear_acceso_startup.setStyleSheet("""
            QPushButton {
                padding: 12px 20px; 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white; 
                font-size: 13px; 
                font-weight: bold;
                border-radius: 6px;
                border: none;
                min-width: 160px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #66BB6A, stop:1 #4CAF50);
            }
        """)
        btn_crear_acceso_startup.setToolTip("La aplicación se iniciará automáticamente al encender Windows")
        btn_crear_acceso_startup.clicked.connect(self._crear_acceso_directo_startup)
        autostart_layout.addWidget(btn_crear_acceso_startup)
        
        # Botón para quitar acceso directo del startup
        btn_quitar_acceso_startup = QPushButton("❌  Desactivar inicio automático")
        btn_quitar_acceso_startup.setStyleSheet("""
            QPushButton {
                padding: 12px 20px; 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f44336, stop:1 #d32f2f);
                color: white; 
                font-size: 13px; 
                font-weight: bold;
                border-radius: 6px;
                border: none;
                min-width: 160px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #EF5350, stop:1 #f44336);
            }
        """)
        btn_quitar_acceso_startup.setToolTip("La aplicación NO se iniciará automáticamente con Windows")
        btn_quitar_acceso_startup.clicked.connect(self._quitar_acceso_directo_startup)
        autostart_layout.addWidget(btn_quitar_acceso_startup)
        
        autostart_layout.addStretch()
        
        config_layout.addLayout(autostart_layout)
        
        # Grupo de auto-organización con selector de tiempo
        auto_group = QGroupBox("⚡ Auto-organización Automática")
        auto_layout = QVBoxLayout(auto_group)
        
        # Selector de intervalo de tiempo
        tiempo_layout = QHBoxLayout()
        tiempo_layout.addWidget(QLabel("⏱️  Revisar cada:"))
        
        self.combo_intervalo_auto = QComboBox()
        self.combo_intervalo_auto.addItem("⚡ 30 segundos", 30)
        self.combo_intervalo_auto.addItem("⚡ 1 minuto", 60)
        self.combo_intervalo_auto.addItem("🕐 5 minutos", 300)
        self.combo_intervalo_auto.addItem("🕐 10 minutos", 600)
        self.combo_intervalo_auto.addItem("🕐 30 minutos", 1800)
        self.combo_intervalo_auto.addItem("🕒 1 hora", 3600)
        self.combo_intervalo_auto.addItem("🕕 6 horas", 21600)
        self.combo_intervalo_auto.addItem("🕘 12 horas", 43200)
        self.combo_intervalo_auto.addItem("📅 1 día", 86400)
        self.combo_intervalo_auto.setCurrentIndex(0)  # 30 segundos por defecto
        self.combo_intervalo_auto.currentIndexChanged.connect(self._cambiar_intervalo_auto)
        self.combo_intervalo_auto.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #505050;
                border-radius: 6px;
                background-color: #3d3d3d;
                color: #ffffff;
                font-size: 13px;
                min-width: 150px;
            }
            QComboBox:hover { border-color: #4CAF50; }
        """)
        tiempo_layout.addWidget(self.combo_intervalo_auto)
        tiempo_layout.addStretch()
        auto_layout.addLayout(tiempo_layout)
        
        self.chk_auto_basico = QCheckBox("📁  Modo BÁSICO - Solo carpetas principales")
        self.chk_auto_basico.setToolTip("Organiza en carpetas generales:\n\n📄 Documentos\n🖼️ Imágenes\n🎬 Videos\n🎵 Música\n📦 Comprimidos")
        self.chk_auto_basico.toggled.connect(lambda checked: self._toggle_auto_organizacion_basico(checked))
        auto_layout.addWidget(self.chk_auto_basico)
        
        self.chk_auto_detallado = QCheckBox("🔧  Modo DETALLADO - Con subcarpetas específicas")
        self.chk_auto_detallado.setToolTip("Organiza con subcarpetas por tipo:\n\n📊 Excel → Hojas de cálculo/Excel\n🖼️ PNG → Imágenes/PNG\n📦 ZIP → Comprimidos/ZIP")
        self.chk_auto_detallado.toggled.connect(lambda checked: self._toggle_auto_organizacion_detallado(checked))
        auto_layout.addWidget(self.chk_auto_detallado)
        
        config_layout.addWidget(auto_group)
        
        self.chk_subcarpetas = QCheckBox("📁 Usar subcarpetas detalladas")
        self.chk_subcarpetas.setChecked(False)  # MODO BÁSICO por defecto
        self.chk_subcarpetas.setToolTip("Si no está marcado: organización BÁSICA (Comprimidos, Imágenes, Videos, etc.)\nSi está marcado: organización DETALLADA (Comprimidos/Zip, Imágenes/PNG, etc.)")
        self.chk_subcarpetas.toggled.connect(self._toggle_subcarpetas)
        config_layout.addWidget(self.chk_subcarpetas)
        
        self.chk_recursivo = QCheckBox("🔍 Buscar en subcarpetas")
        config_layout.addWidget(self.chk_recursivo)
        
        # Notificaciones nativas
        if NOTIFICACIONES_NATIVAS:
            self.chk_notificaciones = QCheckBox("🔔 Notificaciones nativas del sistema")
            self.chk_notificaciones.setChecked(True)
            self.chk_notificaciones.setToolTip("Muestra notificaciones del sistema cuando se organizan archivos")
            self.chk_notificaciones.toggled.connect(self._toggle_notificaciones)
            config_layout.addWidget(self.chk_notificaciones)
        
        # Selector de tema
        if TEMAS_DISPONIBLES:
            tema_layout = QHBoxLayout()
            tema_layout.addWidget(QLabel("🎨 Tema visual:"))
            
            self.combo_temas = QComboBox()
            temas_disponibles = self.gestor_temas.obtener_nombres_temas()
            for tema_nombre in temas_disponibles:
                # Capitalizar y traducir nombre
                tema_display = tema_nombre.replace("_", " ").title()
                self.combo_temas.addItem(tema_display, tema_nombre)
            
            # Seleccionar tema actual
            tema_actual = self.gestor_temas.tema_actual
            for i in range(self.combo_temas.count()):
                if self.combo_temas.itemData(i) == tema_actual:
                    self.combo_temas.setCurrentIndex(i)
                    break
            
            self.combo_temas.currentIndexChanged.connect(self._cambiar_tema)
            tema_layout.addWidget(self.combo_temas)
            
            config_layout.addLayout(tema_layout)
        
        # Integración menú contextual (solo Windows)
        if MENU_CONTEXTUAL_DISPONIBLE:
            menu_contextual_layout = QHBoxLayout()
            
            self.chk_menu_contextual = QCheckBox("🖱️ Menú contextual (Click derecho)")
            self.chk_menu_contextual.setChecked(self.gestor_menu_contextual.verificar_registro())
            self.chk_menu_contextual.setToolTip("Añade 'Organizar con DescargasOrdenadas' al menú click derecho")
            self.chk_menu_contextual.toggled.connect(self._toggle_menu_contextual)
            menu_contextual_layout.addWidget(self.chk_menu_contextual)
            
            config_layout.addLayout(menu_contextual_layout)
        
        # Botón verificar actualizaciones
        if ACTUALIZACIONES_DISPONIBLES:
            actualizaciones_layout = QHBoxLayout()
            
            btn_verificar_actualizaciones = QPushButton("🔄 Buscar Actualizaciones")
            btn_verificar_actualizaciones.setStyleSheet("""
                QPushButton {
                    padding: 10px 20px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #9C27B0, stop:1 #7B1FA2);
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                    border-radius: 8px;
                    border: none;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #AB47BC, stop:1 #9C27B0);
                }
            """)
            btn_verificar_actualizaciones.clicked.connect(self._verificar_actualizaciones)
            actualizaciones_layout.addWidget(btn_verificar_actualizaciones)
            
            version_actual = self.gestor_actualizaciones.obtener_version_actual()
            lbl_version = QLabel(f"Versión actual: {version_actual}")
            lbl_version.setStyleSheet("color: #b0b0c0; font-size: 11px;")
            actualizaciones_layout.addWidget(lbl_version)
            
            actualizaciones_layout.addStretch()
            
            config_layout.addLayout(actualizaciones_layout)
        
        layout.addWidget(config_group)
        
        # Estado de funcionalidades
        estado_group = QGroupBox("⚡ Funcionalidades Avanzadas")
        estado_layout = QVBoxLayout(estado_group)
        
        self.lbl_estado = QLabel("🔄 Cargando funcionalidades...")
        estado_layout.addWidget(self.lbl_estado)
        
        layout.addWidget(estado_group)
        
        # Lista de archivos
        self.list_archivos = QListWidget()
        layout.addWidget(self.list_archivos)
        
        self.tabs.addTab(tab, "🏠 Principal")
    
    def _crear_tab_ia(self):
        """Pestaña de IA."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Control IA
        ia_group = QGroupBox("🤖 Categorización Inteligente con IA")
        ia_layout = QVBoxLayout(ia_group)
        
        self.lbl_ia_estado = QLabel("🔄 Verificando IA...")
        ia_layout.addWidget(self.lbl_ia_estado)
        
        # Confianza
        confianza_layout = QHBoxLayout()
        confianza_layout.addWidget(QLabel("Nivel de confianza:"))
        
        self.slider_confianza = QSlider(Qt.Horizontal)
        self.slider_confianza.setRange(30, 95)
        self.slider_confianza.setValue(60)
        self.slider_confianza.valueChanged.connect(self._actualizar_confianza)
        confianza_layout.addWidget(self.slider_confianza)
        
        self.lbl_confianza = QLabel("60%")
        confianza_layout.addWidget(self.lbl_confianza)
        
        ia_layout.addLayout(confianza_layout)
        
        # Botones IA
        botones_ia = QHBoxLayout()
        
        btn_entrenar = QPushButton("🧠 Entrenar IA")
        btn_entrenar.clicked.connect(self._entrenar_ia)
        botones_ia.addWidget(btn_entrenar)
        
        btn_reset = QPushButton("🔄 Reiniciar")
        btn_reset.clicked.connect(self._reset_ia)
        botones_ia.addWidget(btn_reset)
        
        ia_layout.addLayout(botones_ia)
        layout.addWidget(ia_group)
        
        # Patrones
        self.text_patrones = QTextEdit()
        self.text_patrones.setMaximumHeight(300)
        self.text_patrones.setReadOnly(True)
        layout.addWidget(self.text_patrones)
        
        self.tabs.addTab(tab, "🤖 IA")
    
    def _crear_tab_fechas(self):
        """Pestaña de organización por fechas."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Control fechas
        fechas_group = QGroupBox("📅 Organización por Fechas")
        fechas_layout = QVBoxLayout(fechas_group)
        
        # Estado actual
        self.lbl_estado_fechas = QLabel("❌ Organización por fechas: DESACTIVADA")
        self.lbl_estado_fechas.setStyleSheet("""
            font-weight: bold; 
            padding: 15px; 
            color: #ffffff;
            background-color: #f44336;
            border-radius: 8px;
            font-size: 15px;
            text-align: center;
        """)
        fechas_layout.addWidget(self.lbl_estado_fechas)
        
        # Botones de control
        botones_fechas_layout = QHBoxLayout()
        
        self.btn_activar_fechas = QPushButton("✅ ACTIVAR Organización por Fechas")
        self.btn_activar_fechas.setStyleSheet("""
            QPushButton {
                padding: 12px; 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2196F3, stop:1 #1976D2);
                color: white; 
                font-size: 13px; 
                font-weight: bold;
                border-radius: 6px;
                border: none;
                min-height: 20px;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #42A5F5, stop:1 #2196F3);
            }
        """)
        self.btn_activar_fechas.clicked.connect(self._activar_fechas)
        botones_fechas_layout.addWidget(self.btn_activar_fechas)
        
        self.btn_desactivar_fechas = QPushButton("❌ DESACTIVAR Organización por Fechas")
        self.btn_desactivar_fechas.setStyleSheet("""
            QPushButton {
                padding: 12px; 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f44336, stop:1 #d32f2f);
                color: white; 
                font-size: 13px; 
                font-weight: bold;
                border-radius: 6px;
                border: none;
                min-height: 20px;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #EF5350, stop:1 #f44336);
            }
        """)
        self.btn_desactivar_fechas.clicked.connect(self._desactivar_fechas)
        self.btn_desactivar_fechas.setEnabled(False)
        botones_fechas_layout.addWidget(self.btn_desactivar_fechas)
        
        fechas_layout.addLayout(botones_fechas_layout)
        
        # Configuración de patrón con descripción
        patron_group = QGroupBox("🗓️ Configuración de Patrón")
        patron_layout = QVBoxLayout(patron_group)
        
        # Selector de patrón
        patron_selector_layout = QHBoxLayout()
        patron_selector_layout.addWidget(QLabel("Patrón de organización:"))
        
        self.combo_patron = QComboBox()
        self.combo_patron.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #505050;
                border-radius: 6px;
                background-color: #3d3d3d;
                color: #ffffff;
                font-size: 13px;
                min-width: 200px;
            }
            QComboBox:hover {
                border-color: #4CAF50;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 5px;
            }
        """)
        
        # Agregar opciones con descripciones
        patrones = [
            ("YYYY/MM-Mes", "2024/12-Diciembre (Año/Mes con nombre)"),
            ("YYYY/MM", "2024/12 (Año/Mes numérico)"),
            ("YYYY", "2024 (Solo año)"),
            ("MM-YYYY", "12-2024 (Mes-Año)"),
            ("Mes-YYYY", "Diciembre-2024 (Nombre mes-Año)")
        ]
        
        for patron, descripcion in patrones:
            self.combo_patron.addItem(f"{patron} - {descripcion}", patron)
        
        self.combo_patron.currentTextChanged.connect(self._actualizar_ejemplo_fecha)
        patron_selector_layout.addWidget(self.combo_patron)
        patron_layout.addLayout(patron_selector_layout)
        
        # Vista previa dinámica
        self.lbl_ejemplo = QLabel("📁 Ejemplo: Downloads/Fechas/2024/12-Diciembre/Documentos/PDFs/")
        self.lbl_ejemplo.setStyleSheet("""
            padding: 12px; 
            background-color: #2d2d2d; 
            border: 2px solid #4CAF50;
            border-radius: 6px; 
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 12px;
            color: #4CAF50;
        """)
        patron_layout.addWidget(self.lbl_ejemplo)
        
        # Información adicional
        info_fechas = QLabel("""
ℹ️  <b>Información sobre Organización por Fechas:</b><br/>
• Los archivos se organizan por su fecha de modificación<br/>
• Se mantiene la estructura de categorías y subcategorías<br/>
• Solo afecta archivos organizados después de la activación<br/>
• Se puede revertir la organización en cualquier momento
        """)
        info_fechas.setStyleSheet("""
            color: #cccccc; 
            font-size: 11px; 
            padding: 10px;
            background-color: #2d2d2d;
            border-radius: 6px;
            border-left: 4px solid #2196F3;
        """)
        info_fechas.setWordWrap(True)
        patron_layout.addWidget(info_fechas)
        
        fechas_layout.addWidget(patron_group)
        
        # Acciones adicionales
        acciones_group = QGroupBox("🔧 Acciones Avanzadas")
        acciones_layout = QHBoxLayout(acciones_group)
        
        # Revertir
        btn_revertir = QPushButton("↩️ Revertir Organización por Fechas")
        btn_revertir.setStyleSheet("""
            QPushButton {
                padding: 10px 15px; 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #9C27B0, stop:1 #7B1FA2);
                color: white; 
                font-size: 12px; 
                font-weight: bold;
                border-radius: 6px;
                border: none;
                min-height: 16px;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #AB47BC, stop:1 #9C27B0);
            }
        """)
        btn_revertir.clicked.connect(self._revertir_fechas)
        acciones_layout.addWidget(btn_revertir)
        
        # Previsualizar
        btn_previsualizar = QPushButton("👀 Previsualizar Organización")
        btn_previsualizar.setStyleSheet("""
            QPushButton {
                padding: 10px 15px; 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #FF9800, stop:1 #F57C00);
                color: white; 
                font-size: 12px; 
                font-weight: bold;
                border-radius: 6px;
                border: none;
                min-height: 16px;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #FFB74D, stop:1 #FF9800);
            }
        """)
        btn_previsualizar.clicked.connect(self._previsualizar_organizacion_fechas)
        acciones_layout.addWidget(btn_previsualizar)
        
        fechas_layout.addWidget(acciones_group)
        
        layout.addWidget(fechas_group)
        
        # Actualizar ejemplo inicial
        self._actualizar_ejemplo_fecha()
        
        self.tabs.addTab(tab, "📅 Fechas")
    
    def _crear_tab_duplicados(self):
        """Pestaña de duplicados."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Controles
        dup_group = QGroupBox("🔍 Detector de Duplicados")
        dup_layout = QVBoxLayout(dup_group)
        
        botones = QHBoxLayout()
        
        btn_buscar = QPushButton("🔍 Buscar Duplicados")
        btn_buscar.clicked.connect(self._buscar_duplicados)
        botones.addWidget(btn_buscar)
        
        btn_eliminar = QPushButton("🗑️ Eliminar Duplicados")
        btn_eliminar.clicked.connect(self._eliminar_duplicados)
        botones.addWidget(btn_eliminar)
        
        dup_layout.addLayout(botones)
        layout.addWidget(dup_group)
        
        # Resultados
        self.text_duplicados = QPlainTextEdit()
        self.text_duplicados.setPlaceholderText("Los duplicados aparecerán aquí...")
        layout.addWidget(self.text_duplicados)
        
        self.tabs.addTab(tab, "🔍 Duplicados")
    
    def _crear_tab_estadisticas(self):
        """Pestaña de estadísticas."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Control
        btn_actualizar = QPushButton("🔄 Actualizar Estadísticas")
        btn_actualizar.clicked.connect(self._actualizar_estadisticas)
        layout.addWidget(btn_actualizar)
        
        # Estadísticas
        self.text_stats = QPlainTextEdit()
        self.text_stats.setReadOnly(True)
        layout.addWidget(self.text_stats)
        
        self.tabs.addTab(tab, "📊 Stats")
    
    def _crear_tab_logs(self):
        """Pestaña de logs y consola interna."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Grupo de control de consola
        consola_group = QGroupBox("🖥️ Control de Consola")
        consola_layout = QVBoxLayout()
        
        # Botones de control de consola
        consola_buttons_layout = QHBoxLayout()
        
        self.btn_ocultar_consola = QPushButton("🔇 Ocultar Consola")
        self.btn_ocultar_consola.setToolTip("Oculta la ventana de consola externa (solo Windows)")
        self.btn_ocultar_consola.clicked.connect(self._ocultar_consola)
        consola_buttons_layout.addWidget(self.btn_ocultar_consola)
        
        self.btn_mostrar_consola = QPushButton("🔊 Mostrar Consola")
        self.btn_mostrar_consola.setToolTip("Muestra la ventana de consola externa (solo Windows)")
        self.btn_mostrar_consola.clicked.connect(self._mostrar_consola)
        consola_buttons_layout.addWidget(self.btn_mostrar_consola)
        
        self.btn_reiniciar_sin_consola = QPushButton("🔄 Reiniciar sin Consola")
        self.btn_reiniciar_sin_consola.setToolTip("Reinicia la aplicación sin ventana de consola")
        self.btn_reiniciar_sin_consola.clicked.connect(self._crear_proceso_sin_consola)
        consola_buttons_layout.addWidget(self.btn_reiniciar_sin_consola)
        
        # Deshabilitar botones en sistemas no Windows
        if sys.platform != "win32":
            self.btn_ocultar_consola.setEnabled(False)
            self.btn_mostrar_consola.setEnabled(False)
            self.btn_reiniciar_sin_consola.setEnabled(False)
        
        consola_layout.addLayout(consola_buttons_layout)
        
        # Información sobre consola
        info_consola = QLabel("ℹ️  La consola externa se puede ocultar, pero algunos logs seguirán apareciendo aquí.")
        info_consola.setWordWrap(True)
        info_consola.setStyleSheet("color: #cccccc; font-size: 11px; font-style: italic; padding: 10px;")
        consola_layout.addWidget(info_consola)
        
        consola_group.setLayout(consola_layout)
        layout.addWidget(consola_group)
        
        # Controles
        controles_layout = QHBoxLayout()
        
        btn_limpiar = QPushButton("🗑️ Limpiar Logs")
        btn_limpiar.setStyleSheet("""
            QPushButton {
                padding: 8px 15px; 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #6c757d, stop:1 #5a6268);
                color: white; 
                font-size: 11px; 
                font-weight: bold;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover { background: #5a6268; }
        """)
        btn_limpiar.clicked.connect(self._limpiar_logs)
        controles_layout.addWidget(btn_limpiar)
        
        btn_exportar = QPushButton("💾 Exportar Logs")
        btn_exportar.setStyleSheet("""
            QPushButton {
                padding: 8px 15px; 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #17a2b8, stop:1 #138496);
                color: white; 
                font-size: 11px; 
                font-weight: bold;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover { background: #138496; }
        """)
        btn_exportar.clicked.connect(self._exportar_logs)
        controles_layout.addWidget(btn_exportar)
        
        controles_layout.addStretch()
        
        # Checkbox para mostrar/ocultar consola externa
        self.chk_mostrar_consola = QCheckBox("🖥️ Mostrar consola externa")
        self.chk_mostrar_consola.setChecked(False)
        self.chk_mostrar_consola.toggled.connect(self._toggle_consola_externa)
        controles_layout.addWidget(self.chk_mostrar_consola)
        
        layout.addLayout(controles_layout)
        
        # Área de logs
        self.text_logs = QPlainTextEdit()
        self.text_logs.setReadOnly(True)
        self.text_logs.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 11px;
                border: 1px solid #454545;
                border-radius: 6px;
                padding: 5px;
            }
        """)
        self.text_logs.setPlainText("🍄 DescargasOrdenadas - Sistema de Logs\n" + "="*60 + "\n")
        layout.addWidget(self.text_logs)
        
        self.tabs.addTab(tab, "📋 Logs")
        
        # Configurar captura de logs
        self._setup_log_capture()
    
    def _setup_log_capture(self):
        """Configura la captura de logs en la pestaña interna."""
        import logging
        
        # Handler personalizado para capturar logs
        class GuiLogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                
            def emit(self, record):
                try:
                    msg = self.format(record)
                    # Agregar timestamp y formatear
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    level_color = {
                        'INFO': '🟢',
                        'WARNING': '🟡', 
                        'ERROR': '🔴',
                        'DEBUG': '🔵'
                    }.get(record.levelname, '⚪')
                    
                    formatted_msg = f"[{timestamp}] {level_color} {msg}"
                    
                    # Agregar al widget directamente
                    try:
                        self.text_widget.appendPlainText(formatted_msg)
                        scrollbar = self.text_widget.verticalScrollBar()
                        scrollbar.setValue(scrollbar.maximum())
                    except:
                        pass
                except:
                    pass
        
        # Crear handler
        self.log_handler = GuiLogHandler(self.text_logs)
        self.log_handler.setFormatter(
            logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        )
        
        # Agregar a loggers principales
        logging.getLogger('DescargasOrdenadas').addHandler(self.log_handler)
        logging.getLogger('organizador').addHandler(self.log_handler)
        logging.getLogger('organizer').addHandler(self.log_handler)
    
    def _limpiar_logs(self):
        """Limpia el área de logs."""
        self.text_logs.clear()
        self.text_logs.setPlainText("🍄 DescargasOrdenadas - Sistema de Logs\n" + "="*60 + "\n")
    
    def _exportar_logs(self):
        """Exporta los logs a un archivo."""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"descargasordenadas_logs_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.text_logs.toPlainText())
            
            QMessageBox.information(self, "Logs Exportados", 
                                  f"✅ Logs exportados a: {filename}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"❌ Error exportando logs: {e}")
    
    def _toggle_consola_externa(self, mostrar):
        """Muestra u oculta la consola externa."""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Obtener handle de la consola
            kernel32 = ctypes.windll.kernel32
            user32 = ctypes.windll.user32
            
            console_window = kernel32.GetConsoleWindow()
            if console_window:
                if mostrar:
                    user32.ShowWindow(console_window, 1)  # SW_SHOW
                    self._agregar_log("🖥️ Consola externa mostrada")
                else:
                    user32.ShowWindow(console_window, 0)  # SW_HIDE
                    self._agregar_log("🖥️ Consola externa ocultada")
        except Exception as e:
            self._agregar_log(f"❌ Error gestionando consola: {e}")
    
    def _agregar_log(self, mensaje):
        """Agrega un mensaje al área de logs."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] 📋 {mensaje}"
        
        self.text_logs.appendPlainText(formatted_msg)
        # Auto-scroll al final
        scrollbar = self.text_logs.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _organizar(self):
        """Compatibilidad: ahora organiza todo usando el flujo de reorganización."""
        self._reorganizar()
    
    def _reorganizar(self):
        """Reorganiza todos los archivos."""
        usar_subcarpetas = self.chk_subcarpetas.isChecked()
        modo = "DETALLADO" if usar_subcarpetas else "BÁSICO"
        
        reply = QMessageBox.question(
            self, "Reorganizar TODO",
            f"¿Reorganizar TODOS los archivos en modo {modo}?\n\n"
            f"{'📁 Con subcarpetas específicas (Excel → Hojas de cálculo/Excel)' if usar_subcarpetas else '⚡ Solo carpetas principales (Excel → Hojas de cálculo)'}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.progress_bar.setVisible(True)
                self.progress_bar.setRange(0, 0)
                
                # Aplicar configuración de subcarpetas dinámicamente
                self.organizador.usar_subcarpetas = usar_subcarpetas
                
                resultados, errores = self.organizador.reorganizar_completamente()
                
                total = sum(len(files) for cat in resultados.values() for files in cat.values())
                QMessageBox.information(self, "Reorganización", f"✅ {total} archivos reorganizados (modo {modo})")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ Error: {e}")
            finally:
                self.progress_bar.setVisible(False)
    
    @Slot(bool)
    def _toggle_subcarpetas(self, usar_subcarpetas):
        """Cambia el modo de organización entre básico y detallado."""
        try:
            # Recrear el organizador con la nueva configuración
            carpeta_actual = self.organizador.carpeta_descargas
            self.organizador = OrganizadorArchivos(
                carpeta_descargas=str(carpeta_actual), 
                usar_subcarpetas=usar_subcarpetas
            )
            
            # Actualizar estado visual
            if usar_subcarpetas:
                modo = "🔧 DETALLADO (con subcarpetas específicas)"
                tooltip = "Excel → Hojas de cálculo/Excel\nPNG → Imágenes/PNG"
            else:
                modo = "⚡ BÁSICO (solo carpetas principales)" 
                tooltip = "Excel → Hojas de cálculo\nPNG → Imágenes"
                
            self.chk_subcarpetas.setToolTip(f"Modo actual: {modo}\n\nEjemplos:\n{tooltip}")
            
            logger.info(f"Modo de organización cambiado a: {'DETALLADO' if usar_subcarpetas else 'BÁSICO'}")
            
        except Exception as e:
            logger.error(f"Error cambiando modo de organización: {e}")
            QMessageBox.critical(self, "Error", f"❌ Error cambiando modo: {e}")

    def _toggle_notificaciones(self, activo):
        """Toggle notificaciones nativas."""
        if self.notificador:
            if activo:
                self.notificador.habilitar()
                self._agregar_log("🔔 Notificaciones nativas habilitadas")
            else:
                self.notificador.deshabilitar()
                self._agregar_log("🔕 Notificaciones nativas deshabilitadas")
            
            # Guardar preferencia en configuración portable
            if self.config_portable:
                self.config_portable.establecer("notificaciones_habilitadas", activo)
    
    def _cambiar_tema(self, index):
        """Cambia el tema visual de la aplicación."""
        if not self.gestor_temas:
            return
        
        tema_nombre = self.combo_temas.itemData(index)
        if tema_nombre:
            self.gestor_temas.establecer_tema_actual(tema_nombre)
            self._aplicar_tema()
            
            # Guardar en configuración
            if self.config_portable:
                self.config_portable.establecer("tema", tema_nombre)
            
            self._agregar_log(f"🎨 Tema cambiado a: {self.combo_temas.currentText()}")
    
    def _toggle_menu_contextual(self, activo):
        """Toggle integración menú contextual."""
        if not self.gestor_menu_contextual:
            return
        
        try:
            if activo:
                exito, mensaje = self.gestor_menu_contextual.registrar_menu_contextual("carpetas")
                if exito:
                    self._agregar_log("🖱️ Menú contextual registrado")
                    QMessageBox.information(
                        self,
                        "Menú Contextual",
                        "✅ Menú contextual registrado correctamente\n\n"
                        "Ahora puedes hacer click derecho en cualquier carpeta\n"
                        "y seleccionar '🍄 Organizar con DescargasOrdenadas'"
                    )
                else:
                    self._agregar_log(f"❌ Error: {mensaje}")
                    self.chk_menu_contextual.setChecked(False)
                    QMessageBox.warning(self, "Error", f"No se pudo registrar el menú contextual:\n{mensaje}")
            else:
                exito, mensaje = self.gestor_menu_contextual.desregistrar_menu_contextual()
                if exito:
                    self._agregar_log("🗑️ Menú contextual eliminado")
                else:
                    self._agregar_log(f"❌ Error: {mensaje}")
        except Exception as e:
            self._agregar_log(f"❌ Error configurando menú contextual: {e}")
            self.chk_menu_contextual.setChecked(False)
            QMessageBox.critical(self, "Error", f"Error: {e}")
    
    def _verificar_actualizaciones_silencioso(self):
        """Verifica actualizaciones en segundo plano sin mostrar mensaje si no hay."""
        if not self.gestor_actualizaciones:
            return
        
        try:
            self._agregar_log("🔍 Verificando actualizaciones en segundo plano...")
            hay_actualizacion, info = self.gestor_actualizaciones.verificar_actualizaciones()
            
            if hay_actualizacion and info:
                version = info.get('version', 'Desconocida')
                self._agregar_log(f"✨ ¡Nueva versión {version} disponible!")
                self._mostrar_notificacion_actualizacion(info)
            else:
                self._agregar_log("✅ Ya tienes la última versión")
        except Exception as e:
            self._agregar_log(f"⚠️ Error verificando actualizaciones: {e}")
    
    def _verificar_actualizaciones(self):
        """Verifica actualizaciones y muestra el resultado."""
        if not self.gestor_actualizaciones:
            return
        
        self._agregar_log("🔍 Verificando actualizaciones...")
        
        try:
            hay_actualizacion, info = self.gestor_actualizaciones.verificar_actualizaciones(forzar=True)
            
            if hay_actualizacion and info:
                self._mostrar_notificacion_actualizacion(info)
            else:
                QMessageBox.information(
                    self,
                    "Actualizado",
                    f"✅ Estás usando la última versión\n\n"
                    f"Versión actual: {self.gestor_actualizaciones.obtener_version_actual()}"
                )
                self._agregar_log("✅ No hay actualizaciones disponibles")
        except Exception as e:
            self._agregar_log(f"❌ Error verificando actualizaciones: {e}")
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudo verificar actualizaciones:\n{e}\n\n"
                f"Verifica tu conexión a internet"
            )
    
    def _mostrar_notificacion_actualizacion(self, info):
        """Muestra notificación con opción de descarga automática."""
        version = info.get('version', 'Desconocida')
        nombre = info.get('nombre', '')
        descripcion = info.get('descripcion', '')[:200]
        
        # Crear diálogo personalizado
        msg = QMessageBox(self)
        msg.setWindowTitle("🎉 Nueva Versión Disponible")
        msg.setText(f"✨ ¡Hay una nueva versión disponible!\n\n"
                   f"📦 Versión: {version}\n"
                   f"📝 {nombre}")
        msg.setInformativeText(f"{descripcion}...")
        msg.setIcon(QMessageBox.Information)
        
        # Botones personalizados
        btn_descargar = msg.addButton("⬇️ Descargar e Instalar", QMessageBox.AcceptRole)
        btn_abrir_web = msg.addButton("🌐 Abrir en Navegador", QMessageBox.ActionRole)
        btn_cancelar = msg.addButton("❌ Cancelar", QMessageBox.RejectRole)
        
        msg.setDefaultButton(btn_descargar)
        msg.exec()
        
        if msg.clickedButton() == btn_descargar:
            self._descargar_e_instalar_actualizacion(info)
        elif msg.clickedButton() == btn_abrir_web:
            self.gestor_actualizaciones.abrir_pagina_descarga()
        
        self._agregar_log(f"🎉 Nueva versión disponible: {version}")
    
    def _descargar_e_instalar_actualizacion(self, info):
        """Descarga e instala la actualización automáticamente."""
        from PySide6.QtWidgets import QProgressDialog
        from PySide6.QtCore import Qt
        
        version = info.get('version', 'Desconocida')
        
        # Crear diálogo de progreso
        progress = QProgressDialog(
            f"Descargando DescargasOrdenadas v{version}...",
            "Cancelar",
            0, 100,
            self
        )
        progress.setWindowTitle("Descargando Actualización")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.show()
        
        # Callback para actualizar progreso
        def actualizar_progreso(porcentaje):
            progress.setValue(porcentaje)
            QApplication.processEvents()
        
        try:
            # Descargar
            self._agregar_log(f"⬇️ Descargando v{version}...")
            exito, resultado = self.gestor_actualizaciones.descargar_actualizacion(
                info,
                callback_progreso=actualizar_progreso
            )
            
            if not exito:
                progress.close()
                QMessageBox.critical(
                    self,
                    "Error de Descarga",
                    f"❌ Error descargando actualización:\n\n{resultado}"
                )
                return
            
            # Instalar
            progress.setLabelText("Instalando actualización...")
            progress.setValue(100)
            self._agregar_log(f"📦 Instalando v{version}...")
            
            exito_instalacion, mensaje = self.gestor_actualizaciones.instalar_actualizacion(resultado)
            progress.close()
            
            if exito_instalacion:
                # Mostrar mensaje de éxito
                QMessageBox.information(
                    self,
                    "✅ Actualización Completada",
                    f"{mensaje}\n\n🔄 La aplicación se reiniciará automáticamente en 3 segundos..."
                )
                
                self._agregar_log("✅ Actualización completada - Reiniciando...")
                
                # Reiniciar automáticamente
                QApplication.processEvents()
                import time
                time.sleep(1)
                
                self.gestor_actualizaciones.reiniciar_aplicacion()
            else:
                QMessageBox.critical(
                    self,
                    "Error de Instalación",
                    f"❌ Error instalando actualización:\n\n{mensaje}"
                )
        
        except Exception as e:
            progress.close()
            self._agregar_log(f"❌ Error durante actualización: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"❌ Error durante el proceso de actualización:\n\n{e}"
            )
    
    @Slot(bool)
    def _toggle_autoarranque(self, activo):
        """Toggle autoarranque."""
        try:
            exito, mensaje = self.gestor_autoarranque.configurar_autoarranque(activo)
            if not exito:
                QMessageBox.warning(self, "Error Autoarranque", f"❌ {mensaje}")
                self.chk_autoarranque.setChecked(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Error configurando autoarranque: {e}")
            self.chk_autoarranque.setChecked(False)
    
    def _crear_acceso_directo_startup(self):
        """Crea un acceso directo en la carpeta de inicio de Windows (shell:startup)."""
        if sys.platform != "win32":
            QMessageBox.warning(self, "No Disponible", "Esta función solo está disponible en Windows")
            return
        
        try:
            try:
                import win32com.client
            except ImportError:
                QMessageBox.critical(
                    self, 
                    "Módulo Faltante",
                    "❌ El módulo 'pywin32' no está instalado.\n\n"
                    "Instálalo con: pip install pywin32"
                )
                return
            
            # Obtener carpeta de inicio (startup)
            startup_folder = Path(os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup'))
            
            # Verificar que existe
            if not startup_folder.exists():
                QMessageBox.critical(self, "Error", f"No se puede acceder a la carpeta de inicio:\n{startup_folder}")
                return
            
            # Determinar el archivo a ejecutar
            script_dir = Path(__file__).parent.parent.absolute()
            
            # Buscar el launcher sin consola primero
            launcher_sin_consola = script_dir / "INICIAR_SIN_CONSOLA.bat"
            launcher_pyw = script_dir / "INICIAR_SIN_CONSOLA.pyw"
            launcher_bat = script_dir / "INICIAR.bat"
            
            # Determinar qué launcher usar
            if launcher_sin_consola.exists():
                target_file = launcher_sin_consola
                descripcion = "DescargasOrdenadas v3.0 - Inicio sin consola"
            elif launcher_pyw.exists():
                target_file = launcher_pyw
                descripcion = "DescargasOrdenadas v3.0 - Inicio sin consola (Python)"
            elif launcher_bat.exists():
                target_file = launcher_bat
                descripcion = "DescargasOrdenadas v3.0 - Inicio automático"
            else:
                QMessageBox.critical(self, "Error", "No se encontró ningún launcher para crear el acceso directo")
                return
            
            # Crear nombre del acceso directo
            shortcut_path = startup_folder / "DescargasOrdenadas.lnk"
            
            # Crear el acceso directo
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(target_file)
            shortcut.WorkingDirectory = str(script_dir)
            shortcut.Description = descripcion
            shortcut.Arguments = "--autostart --minimizado"
            
            # Buscar icono
            ico_path = script_dir / "resources" / "favicon.ico"
            if ico_path.exists():
                shortcut.IconLocation = str(ico_path)
            
            shortcut.save()
            
            self._agregar_log(f"✅ Acceso directo creado en: {shortcut_path}")
            
            QMessageBox.information(
                self, 
                "Acceso Directo Creado",
                f"✅ Acceso directo creado exitosamente en:\n\n"
                f"{startup_folder}\n\n"
                f"📋 Archivo: DescargasOrdenadas.lnk\n"
                f"🎯 Objetivo: {target_file.name}\n\n"
                f"La aplicación se iniciará automáticamente al iniciar Windows."
            )
            
        except Exception as e:
            self._agregar_log(f"❌ Error creando acceso directo: {e}")
            QMessageBox.critical(
                self, 
                "Error",
                f"❌ Error al crear el acceso directo:\n\n{str(e)}"
            )
    
    def _activar_fechas(self):
        """Activar organización por fechas"""
        try:
            # Buscar el organizador de fechas en diferentes ubicaciones
            organizador_fechas = None
            
            if hasattr(self.organizador, 'organizador_fechas') and self.organizador.organizador_fechas:
                organizador_fechas = self.organizador.organizador_fechas
            elif hasattr(self, 'date_organizer') and self.date_organizer:
                organizador_fechas = self.date_organizer
            
            if organizador_fechas:
                patron = self.combo_patron.currentData()
                if not patron:
                    patron = self.combo_patron.currentText()
                
                resultado = organizador_fechas.activar(patron)
                
                # Actualizar estado visual
                self.lbl_estado_fechas.setText("✅ Organización por fechas: ACTIVADA")
                self.lbl_estado_fechas.setStyleSheet("""
                    font-weight: bold; 
                    padding: 10px; 
                    color: #ffffff;
                    background-color: #4CAF50;
                    border-radius: 6px;
                    font-size: 14px;
                """)
                self.btn_activar_fechas.setEnabled(False)
                self.btn_desactivar_fechas.setEnabled(True)
                
                if hasattr(self, '_actualizar_estadisticas'):
                    self._actualizar_estadisticas()
                
                QMessageBox.information(self, "Fechas Activadas", 
                                      f"✅ Organización por fechas activada exitosamente\n\n"
                                      f"📋 Patrón configurado: {patron}\n\n"
                                      f"📁 Los nuevos archivos se organizarán en:\n"
                                      f"Downloads/Fechas/{patron}/Categoría/\n\n"
                                      f"ℹ️ Solo afecta archivos organizados a partir de ahora")
            else:
                QMessageBox.warning(self, "Error", "❌ El módulo de fechas no está disponible\n\n"
                                  "Verifique que el módulo date_organizer esté instalado correctamente.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"❌ Error al activar organización por fechas:\n\n{str(e)}")
            import traceback
            print(f"Error detallado en fechas: {traceback.format_exc()}")
    
    def _desactivar_fechas(self):
        """Desactivar organización por fechas"""
        try:
            # Buscar el organizador de fechas en diferentes ubicaciones
            organizador_fechas = None
            
            if hasattr(self.organizador, 'organizador_fechas') and self.organizador.organizador_fechas:
                organizador_fechas = self.organizador.organizador_fechas
            elif hasattr(self, 'date_organizer') and self.date_organizer:
                organizador_fechas = self.date_organizer
            
            if organizador_fechas:
                resultado = organizador_fechas.desactivar()
                
                # Actualizar estado visual
                self.lbl_estado_fechas.setText("❌ Organización por fechas: DESACTIVADA")
                self.lbl_estado_fechas.setStyleSheet("""
                    font-weight: bold; 
                    padding: 10px; 
                    color: #ffffff;
                    background-color: #f44336;
                    border-radius: 6px;
                    font-size: 14px;
                """)
                self.btn_activar_fechas.setEnabled(True)
                self.btn_desactivar_fechas.setEnabled(False)
                
                if hasattr(self, '_actualizar_estadisticas'):
                    self._actualizar_estadisticas()
                
                QMessageBox.information(self, "Fechas Desactivadas", 
                                      f"❌ Organización por fechas desactivada\n\n"
                                      f"📁 Los archivos volverán a organizarse de forma normal:\n"
                                      f"Downloads/Categoría/Subcategoría/\n\n"
                                      f"ℹ️ Los archivos ya organizados por fechas no se mueven automáticamente")
            else:
                QMessageBox.warning(self, "Error", "❌ El módulo de fechas no está disponible\n\n"
                                  "Verifique que el módulo date_organizer esté instalado correctamente.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"❌ Error al desactivar organización por fechas:\n\n{str(e)}")
            import traceback
            print(f"Error detallado en fechas: {traceback.format_exc()}")
    
    @Slot(int)
    def _actualizar_confianza(self, valor):
        """Actualiza confianza IA."""
        self.lbl_confianza.setText(f"{valor}%")
        if self.ai_categorizer:
            self.ai_categorizer.ajustar_confianza(valor / 100.0)
    
    def _entrenar_ia(self):
        """Entrena la IA."""
        if not self.ai_categorizer:
            QMessageBox.warning(self, "IA No Disponible", "IA no está disponible")
            return
        
        QMessageBox.information(self, "Entrenar IA", "🧠 IA entrenada con historial")
        self._actualizar_patrones()
    
    def _reset_ia(self):
        """Reinicia IA."""
        if not self.ai_categorizer:
            return
        
        reply = QMessageBox.question(self, "Reset IA", "¿Reiniciar modelo?")
        if reply == QMessageBox.Yes:
            self.ai_categorizer.limpiar_modelo()
            QMessageBox.information(self, "IA", "🔄 Modelo reiniciado")
            self._actualizar_patrones()
    
    def _actualizar_patrones(self):
        """Actualiza patrones IA."""
        if not self.ai_categorizer:
            self.text_patrones.setText("❌ IA no disponible")
            return
        
        try:
            stats = self.ai_categorizer.analizar_patrones_usuario()
            texto = "🤖 Patrones de IA:\n\n"
            
            for categoria, datos in stats.get('patrones_por_categoria', {}).items():
                texto += f"📂 {categoria}:\n"
                for palabra, peso in list(datos.items())[:5]:  # Top 5
                    texto += f"  • {palabra}: {peso:.2f}\n"
                texto += "\n"
            
            self.text_patrones.setText(texto)
        except:
            self.text_patrones.setText("❌ Error cargando patrones")
    
    def _revertir_fechas(self):
        """Revierte organización por fechas."""
        if not self.date_organizer:
            return
        
        reply = QMessageBox.question(self, "Revertir", "¿Revertir organización por fechas?")
        if reply == QMessageBox.Yes:
            resultado = self.date_organizer.revertir_organizacion_fechas(True)
            QMessageBox.information(self, "Revertido", f"✅ {resultado.get('archivos_revertidos', 0)} archivos revertidos")
    
    def _actualizar_ejemplo_fecha(self):
        """Actualiza el ejemplo visual del patrón de fechas seleccionado."""
        try:
            from datetime import datetime
            
            # Obtener patrón seleccionado
            patron_actual = self.combo_patron.currentData()
            if not patron_actual:
                patron_actual = self.combo_patron.currentText().split(" - ")[0] if " - " in self.combo_patron.currentText() else "YYYY/MM-Mes"
            
            # Fecha actual para ejemplo
            fecha_actual = datetime.now()
            
            # Simular estructura de carpetas
            ejemplos_estructura = {
                "YYYY/MM-Mes": f"Downloads/Fechas/{fecha_actual.year}/{fecha_actual.month:02d}-{fecha_actual.strftime('%B')}/Documentos/PDFs/",
                "YYYY/MM": f"Downloads/Fechas/{fecha_actual.year}/{fecha_actual.month:02d}/Documentos/PDFs/",
                "YYYY": f"Downloads/Fechas/{fecha_actual.year}/Documentos/PDFs/",
                "MM-YYYY": f"Downloads/Fechas/{fecha_actual.month:02d}-{fecha_actual.year}/Documentos/PDFs/",
                "Mes-YYYY": f"Downloads/Fechas/{fecha_actual.strftime('%B')}-{fecha_actual.year}/Documentos/PDFs/"
            }
            
            # Obtener ejemplo para el patrón
            ejemplo = ejemplos_estructura.get(patron_actual, ejemplos_estructura["YYYY/MM-Mes"])
            
            # Actualizar label con colores
            self.lbl_ejemplo.setText(f"📁 Ejemplo: {ejemplo}")
            
            # Cambiar color según patrón para mejor visualización
            colores_patron = {
                "YYYY/MM-Mes": "#4CAF50",  # Verde
                "YYYY/MM": "#2196F3",      # Azul
                "YYYY": "#FF9800",         # Naranja
                "MM-YYYY": "#9C27B0",      # Púrpura
                "Mes-YYYY": "#F44336"      # Rojo
            }
            
            color = colores_patron.get(patron_actual, "#4CAF50")
            
            self.lbl_ejemplo.setStyleSheet(f"""
                padding: 12px; 
                background-color: #2d2d2d; 
                border: 2px solid {color};
                border-radius: 6px; 
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                color: {color};
            """)
            
        except Exception as e:
            logger.debug(f"Error actualizando ejemplo de fecha: {e}")
            self.lbl_ejemplo.setText("📁 Ejemplo: Downloads/Fechas/2024/12-Diciembre/Documentos/PDFs/")
    
    def _previsualizar_organizacion_fechas(self):
        """Muestra una previsualización de cómo se organizarían los archivos."""
        try:
            import os
            from pathlib import Path
            
            # Obtener carpeta de descargas
            carpeta_descargas = Path(self.organizador.carpeta_descargas)
            
            if not carpeta_descargas.exists():
                QMessageBox.warning(self, "Error", f"La carpeta {carpeta_descargas} no existe")
                return
            
            # Buscar archivos en la carpeta
            archivos_encontrados = []
            extensiones_comunes = {'.pdf', '.doc', '.docx', '.jpg', '.png', '.mp4', '.zip', '.exe', '.txt'}
            
            try:
                for archivo in carpeta_descargas.iterdir():
                    if archivo.is_file() and archivo.suffix.lower() in extensiones_comunes:
                        archivos_encontrados.append(archivo)
                        if len(archivos_encontrados) >= 10:  # Limitar a 10 ejemplos
                            break
            except PermissionError:
                QMessageBox.warning(self, "Error", "No se puede acceder a la carpeta de descargas")
                return
            
            if not archivos_encontrados:
                QMessageBox.information(self, "Previsualización", 
                                      "No se encontraron archivos para previsualizar en la carpeta de descargas")
                return
            
            # Obtener patrón seleccionado
            patron_actual = self.combo_patron.currentData()
            if not patron_actual:
                patron_actual = self.combo_patron.currentText().split(" - ")[0] if " - " in self.combo_patron.currentText() else "YYYY/MM-Mes"
            
            # Simular organización
            texto_previsualizacion = f"🔍 PREVISUALIZACIÓN DE ORGANIZACIÓN\n"
            texto_previsualizacion += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            texto_previsualizacion += f"📋 Patrón seleccionado: {patron_actual}\n\n"
            texto_previsualizacion += f"📁 Se encontraron {len(archivos_encontrados)} archivos de ejemplo:\n\n"
            
            for i, archivo in enumerate(archivos_encontrados, 1):
                try:
                    # Obtener fecha del archivo
                    fecha_archivo = datetime.fromtimestamp(archivo.stat().st_mtime)
                    
                    # Simular categorización
                    extension = archivo.suffix.lower()
                    if extension in ['.pdf']:
                        categoria = "Documentos"
                        subcategoria = "PDFs"
                    elif extension in ['.doc', '.docx']:
                        categoria = "Documentos"
                        subcategoria = "Word"
                    elif extension in ['.jpg', '.png']:
                        categoria = "Imágenes"
                        subcategoria = "Fotos"
                    elif extension in ['.mp4']:
                        categoria = "Videos"
                        subcategoria = "MP4"
                    elif extension in ['.zip']:
                        categoria = "Comprimidos"
                        subcategoria = "ZIP"
                    else:
                        categoria = "Otros"
                        subcategoria = "General"
                    
                    # Generar ruta de destino según patrón
                    if patron_actual == "YYYY/MM-Mes":
                        carpeta_fecha = f"{fecha_archivo.year}/{fecha_archivo.month:02d}-{fecha_archivo.strftime('%B')}"
                    elif patron_actual == "YYYY/MM":
                        carpeta_fecha = f"{fecha_archivo.year}/{fecha_archivo.month:02d}"
                    elif patron_actual == "YYYY":
                        carpeta_fecha = f"{fecha_archivo.year}"
                    elif patron_actual == "MM-YYYY":
                        carpeta_fecha = f"{fecha_archivo.month:02d}-{fecha_archivo.year}"
                    elif patron_actual == "Mes-YYYY":
                        carpeta_fecha = f"{fecha_archivo.strftime('%B')}-{fecha_archivo.year}"
                    else:
                        carpeta_fecha = f"{fecha_archivo.year}/{fecha_archivo.month:02d}-{fecha_archivo.strftime('%B')}"
                    
                    ruta_destino = f"Downloads/Fechas/{carpeta_fecha}/{categoria}/{subcategoria}/"
                    
                    texto_previsualizacion += f"{i:2d}. 📄 {archivo.name}\n"
                    texto_previsualizacion += f"    📅 Fecha: {fecha_archivo.strftime('%d/%m/%Y %H:%M')}\n"
                    texto_previsualizacion += f"    📁 Destino: {ruta_destino}\n\n"
                    
                except Exception as e:
                    texto_previsualizacion += f"{i:2d}. ❌ Error procesando {archivo.name}: {e}\n\n"
            
            texto_previsualizacion += f"\n💡 Esta es solo una simulación. Los archivos no se han movido."
            
            # Mostrar diálogo con previsualización
            dialog = QMessageBox(self)
            dialog.setWindowTitle("🔍 Previsualización de Organización por Fechas")
            dialog.setText("Vista previa de cómo se organizarían los archivos:")
            dialog.setDetailedText(texto_previsualizacion)
            dialog.setIcon(QMessageBox.Information)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Error generando previsualización:\n\n{str(e)}")
    
    def _buscar_duplicados(self):
        """Busca duplicados."""
        if not self.duplicate_detector:
            QMessageBox.warning(self, "No Disponible", "Detector de duplicados no disponible")
            return
        
        try:
            self.text_duplicados.setPlainText("🔍 Buscando...")
            resultado = self.duplicate_detector.escanear_duplicados()
            
            if not resultado.get('duplicados_encontrados'):
                self.text_duplicados.setPlainText("✅ No hay duplicados")
                return
            
            duplicados = resultado['duplicados_encontrados']
            texto = f"🔍 {len(duplicados)} grupos de duplicados:\n\n"
            
            for i, grupo in enumerate(duplicados, 1):
                archivos = grupo.get('archivos', [])
                if len(archivos) > 1:
                    texto += f"Grupo {i} ({len(archivos)} archivos):\n"
                    for archivo_info in archivos:
                        ruta = archivo_info.get('ruta', 'N/A')
                        tamaño = archivo_info.get('tamaño', 0)
                        texto += f"  📁 {ruta} ({self._formatear_bytes(tamaño)})\n"
                    texto += "\n"
            
            self.text_duplicados.setPlainText(texto)
        except Exception as e:
            self.text_duplicados.setPlainText(f"❌ Error: {e}")
    
    def _eliminar_duplicados(self):
        """Elimina duplicados."""
        if not self.duplicate_detector:
            return
        
        reply = QMessageBox.question(self, "Eliminar", "¿Eliminar duplicados? Se conservará la copia más reciente.")
        if reply == QMessageBox.Yes:
            try:
                resultado = self.duplicate_detector.eliminar_duplicados(estrategia='mas_nuevo', confirmar=True)
                QMessageBox.information(
                    self, "Duplicados",
                    f"✅ {resultado.get('archivos_eliminados', 0)} duplicados eliminados\n" +
                    f"💾 {self._formatear_bytes(resultado.get('espacio_liberado', 0))} liberados"
                )
                self._buscar_duplicados()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ Error: {e}")
    
    def _actualizar_estadisticas(self):
        """Actualiza estadísticas."""
        if not self.stats_manager:
            self.text_stats.setPlainText("❌ Estadísticas no disponibles")
            return
        
        try:
            # El método generar_reporte_completo devuelve una string, no un dict
            reporte_texto = self.stats_manager.generar_reporte_completo()
            self.text_stats.setPlainText(reporte_texto)
        except Exception as e:
            self.text_stats.setPlainText(f"❌ Error cargando estadísticas: {e}")
    
    def _formatear_bytes(self, bytes_size: int) -> str:
        """Formatea bytes en formato legible."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"

    def _seleccionar_carpeta(self):
        """Permite seleccionar una nueva carpeta para organizar."""
        nueva_carpeta = QFileDialog.getExistingDirectory(
            self, 
            "Seleccionar Carpeta para Organizar", 
            str(self.organizador.carpeta_descargas)
        )
        if nueva_carpeta:
            # Actualizar el organizador con la nueva carpeta
            self.organizador.carpeta_descargas = Path(nueva_carpeta)
            self.organizador.carpeta_config = self.organizador.carpeta_descargas / ".config"
            
            # Actualizar la interfaz
            self.lbl_carpeta_actual.setText(f"📁 Carpeta actual: {os.path.basename(nueva_carpeta)}")
            
            # Actualizar el header
            if hasattr(self, 'header'):
                self.header.setText(f"🍄 DescargasOrdenadas | 📁 {nueva_carpeta}")
            
            # Reinitializar módulos avanzados con la nueva carpeta
            self._inicializar_modulos()
            self._actualizar_datos()
            
            # Mostrar mensaje de confirmación
            QMessageBox.information(
                self, 
                "Carpeta Cambiada", 
                f"✅ Carpeta de trabajo cambiada a:\n{nueva_carpeta}"
            )
    
    def _reset_carpeta_descargas(self):
        """Restablece la carpeta de descargas a la predeterminada."""
        from .file_organizer import OrganizadorArchivos
        # Obtener la carpeta de descargas predeterminada
        organizador_temp = OrganizadorArchivos()
        carpeta_predeterminada = organizador_temp._detectar_carpeta_descargas()
        
        # Actualizar el organizador
        self.organizador.carpeta_descargas = carpeta_predeterminada
        self.organizador.carpeta_config = self.organizador.carpeta_descargas / ".config"
        
        # Actualizar la interfaz
        self.lbl_carpeta_actual.setText(f"📁 Carpeta actual: {os.path.basename(carpeta_predeterminada)}")
        
        # Actualizar el header
        if hasattr(self, 'header'):
            self.header.setText(f"🍄 DescargasOrdenadas | 📁 {carpeta_predeterminada}")
        
        # Reinitializar módulos avanzados
        self._inicializar_modulos()
        self._actualizar_datos()
        
        # Mostrar mensaje de confirmación
        QMessageBox.information(
            self, 
            "Carpeta Restablecida", 
            f"✅ Carpeta restablecida a la predeterminada:\n{carpeta_predeterminada}"
        )

    def _crear_proceso_sin_consola(self):
        """Crea un nuevo proceso sin consola y cierra el actual."""
        if sys.platform == "win32":
            try:
                import subprocess
                
                # Determinar ruta del proyecto
                if getattr(sys, 'frozen', False):
                    # Si es ejecutable empaquetado
                    comando = [sys.executable, "--minimizado"]
                else:
                    # Usar el .bat sin consola si existe
                    proyecto_dir = Path(sys.argv[0]).parent
                    bat_sin_consola = proyecto_dir / "windows" / "DescargasOrdenadas_SinConsola.bat"
                    bat_principal = proyecto_dir / "windows" / "DescargasOrdenadas.bat"
                    
                    if bat_sin_consola.exists():
                        comando = [str(bat_sin_consola), "--minimizado"]
                    elif bat_principal.exists():
                        comando = [str(bat_principal), "--minimizado"]
                    else:
                        # Fallback a método Python directo
                        python_exe = sys.executable
                        if python_exe.endswith('python.exe'):
                            python_exe = python_exe.replace('python.exe', 'pythonw.exe')
                        comando = [python_exe, sys.argv[0], "--minimizado"]
                
                self._agregar_log(f"🔄 Reiniciando con comando: {' '.join(comando)}")
                
                # Iniciar proceso sin consola
                if str(comando[0]).endswith('.bat'):
                    # Para archivos .bat, usar diferentes flags
                    subprocess.Popen(
                        comando,
                        creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        shell=True
                    )
                else:
                    # Para ejecutables Python
                    subprocess.Popen(
                        comando,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                
                self._agregar_log("🔄 Reiniciando sin consola...")
                # Cerrar aplicación actual después de un pequeño delay
                QTimer.singleShot(1000, lambda: self._salir_completamente())
                return True
            except Exception as e:
                self._agregar_log(f"❌ Error creando proceso sin consola: {e}")
        else:
                self._agregar_log("ℹ️  Reinicio sin consola solo disponible en Windows")
        return False
    

    def _cambiar_intervalo_auto(self, index):
        """Cambia el intervalo de auto-organización."""
        if hasattr(self, 'timer_auto') and self.timer_auto and self.timer_auto.isActive():
            # Si el timer está activo, reiniciar con el nuevo intervalo
            intervalo_ms = self.combo_intervalo_auto.currentData() * 1000
            self.timer_auto.setInterval(intervalo_ms)
            
            intervalo_texto = self.combo_intervalo_auto.currentText()
            self._agregar_log(f"⏱️ Intervalo de auto-organización cambiado a: {intervalo_texto}")
    
    def _quitar_acceso_directo_startup(self):
        """Elimina el acceso directo de la carpeta de inicio de Windows."""
        if sys.platform != "win32":
            QMessageBox.warning(self, "No Disponible", "Esta función solo está disponible en Windows")
            return
        
        try:
            # Obtener carpeta de inicio (startup)
            startup_folder = Path(os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup'))
            shortcut_path = startup_folder / "DescargasOrdenadas.lnk"
            
            if shortcut_path.exists():
                shortcut_path.unlink()
                self._agregar_log(f"✅ Acceso directo eliminado de: {startup_folder}")
                
                QMessageBox.information(
                    self,
                    "Acceso Directo Eliminado",
                    f"✅ Acceso directo eliminado exitosamente de:\n\n"
                    f"{startup_folder}\n\n"
                    f"La aplicación ya NO se iniciará automáticamente con Windows."
                )
            else:
                QMessageBox.information(
                    self,
                    "No Encontrado",
                    f"ℹ️  No se encontró ningún acceso directo en:\n\n"
                    f"{startup_folder}\n\n"
                    f"Es posible que ya haya sido eliminado."
                )
        except Exception as e:
            self._agregar_log(f"❌ Error eliminando acceso directo: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"❌ Error al eliminar el acceso directo:\n\n{str(e)}"
            )

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
    
    def _aplicar_tema(self):
        """Aplica el tema actual."""
        if self.gestor_temas:
            tema_obj = self.gestor_temas.obtener_tema_actual()
            self.setStyleSheet(tema_obj.obtener_stylesheet())
    
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
    


def run_advanced_gui(directorio=None, minimizado=False, auto_organizacion=False):
    """Ejecuta la GUI avanzada."""
    app = QApplication.instance() or QApplication(sys.argv)
    
    window = OrganizadorAvanzado(directorio, auto_organizacion=auto_organizacion)
    
    if not minimizado:
        window.show()
    else:
        # Si se inicia minimizado, ir directo a la bandeja
        window._ocultar_en_bandeja()
    
    return app.exec() 