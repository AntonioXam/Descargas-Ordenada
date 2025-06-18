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
    from PySide6.QtGui import QIcon, QAction, QPixmap, QPainter
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

logger = logging.getLogger('organizador.gui_avanzada')

class OrganizadorAvanzado(QMainWindow):
    """GUI completa con todas las funcionalidades avanzadas."""
    
    def __init__(self, directorio=None):
        super().__init__()
        
        # Inicializar organizador
        if directorio:
            self.organizador = OrganizadorArchivos(carpeta_descargas=str(directorio), usar_subcarpetas=True)
        else:
            self.organizador = OrganizadorArchivos(usar_subcarpetas=True)
        
        self.gestor_autoarranque = GestorAutoarranque()
        
        # Estado de la aplicación
        self.en_bandeja = False
        self.cerrar_completamente = False
        self._sincronizando_controles = False
        
        # Configuración ventana
        self.setWindowTitle("🍄 DescargasOrdenadas v3.0 - Funcionalidades Completas")
        self.setMinimumSize(1000, 700)
        
        self._setup_ui()
        self._aplicar_estilos_modernos()
        self._setup_system_tray()
        self._inicializar_modulos()
        
        # Timer para organización automática
        self.timer_auto = QTimer()
        self.timer_auto.timeout.connect(self._organizar_automatico)
    
    def _aplicar_estilos_modernos(self):
        """Aplica estilos modernos con tema oscuro."""
        self.setStyleSheet("""
            QMainWindow { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2b2b2b, stop:1 #1e1e1e);
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 2px solid #404040;
                background-color: #2d2d2d;
                border-radius: 8px;
                margin-top: 5px;
            }
            QTabBar::tab {
                padding: 12px 20px;
                margin-right: 3px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #404040, stop:1 #353535);
                border: 1px solid #555555;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                color: #cccccc;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #4CAF50, stop:1 #45a049);
                color: #ffffff;
                border-bottom: 2px solid #4CAF50;
            }
            QTabBar::tab:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #505050, stop:1 #454545);
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #505050;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #2d2d2d;
                color: #ffffff;
                font-size: 13px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #ffffff;
                background-color: #2d2d2d;
            }
            QCheckBox {
                spacing: 8px;
                font-weight: normal;
                color: #ffffff;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #666666;
                background-color: #3d3d3d;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border-color: #4CAF50;
            }
            QCheckBox::indicator:hover {
                border-color: #888888;
            }
            QLabel {
                color: #ffffff;
                font-size: 13px;
            }
            QListWidget {
                border: 1px solid #505050;
                border-radius: 6px;
                background-color: #3d3d3d;
                color: #ffffff;
                selection-background-color: #4CAF50;
                selection-color: #ffffff;
            }
            QTextEdit, QPlainTextEdit {
                border: 1px solid #505050;
                border-radius: 6px;
                background-color: #3d3d3d;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
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
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                min-height: 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #66BB6A, stop:1 #4CAF50);
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #3d8b40, stop:1 #2e7d32);
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #999999;
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
                border: 1px solid #505050;
                border-radius: 6px;
                text-align: center;
                font-weight: bold;
                background-color: #3d3d3d;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #4CAF50, stop:1 #66BB6A);
                border-radius: 5px;
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
        self.tray_icon.setToolTip("🍄 DescargasOrdenadas v3.0 - Organizador Activo")
        
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
            from .date_organizer import OrganizadorPorFecha
            self.date_organizer = OrganizadorPorFecha(carpeta)
            funciones.append("📅 Fechas")
            
            # Verificar si fechas está activa
            try:
                config_fechas = self.date_organizer.configuracion
                if config_fechas.get('activo', False) and hasattr(self, 'lbl_estado_fechas'):
                    self.lbl_estado_fechas.setText("✅ Organización por fechas: ACTIVADA")
                    self.lbl_estado_fechas.setStyleSheet("""
                        font-weight: bold; 
                        padding: 10px; 
                        color: #ffffff;
                        background-color: #4CAF50;
                        border-radius: 6px;
                        font-size: 14px;
                    """)
                    if hasattr(self, 'btn_activar_fechas'):
                        self.btn_activar_fechas.setEnabled(False)
                    if hasattr(self, 'btn_desactivar_fechas'):
                        self.btn_desactivar_fechas.setEnabled(True)
            except:
                pass  # Si hay error leyendo config, mantener estado por defecto
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
        
        # Cerrar la consola completamente
        self._cerrar_consola()
        
        self.cerrar_completamente = True
        QApplication.quit()
    
    def _toggle_auto_organizacion(self, activo):
        """Activa/desactiva la organización automática."""
        # Prevenir recursión durante sincronización
        if self._sincronizando_controles:
            return
            
        if activo:
            # Iniciar timer cada 30 segundos
            self.timer_auto.start(30000)
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.setToolTip("🍄 DescargasOrdenadas v3.0 - Auto-Organización ACTIVA")
            self._agregar_log("⚡ Auto-organización activada (cada 30 segundos)")
            
            # Sincronizar controles sin recursión
            self._sincronizando_controles = True
            if hasattr(self, 'auto_action'):
                self.auto_action.setChecked(True)
            if hasattr(self, 'chk_auto_organizacion'):
                self.chk_auto_organizacion.setChecked(True)
            self._sincronizando_controles = False
            
            # Notificación única al activar (no molesta)
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.showMessage(
                    "⚡ Auto-Organización Activada",
                    "Funcionando silenciosamente en segundo plano cada 30s",
                    QSystemTrayIcon.Information,
                    2000
                )
        else:
            self.timer_auto.stop()
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.setToolTip("🍄 DescargasOrdenadas v3.0 - Organizador Activo")
            self._agregar_log("⏹️ Auto-organización desactivada")
            
            # Sincronizar controles sin recursión
            self._sincronizando_controles = True
            if hasattr(self, 'auto_action'):
                self.auto_action.setChecked(False)
            if hasattr(self, 'chk_auto_organizacion'):
                self.chk_auto_organizacion.setChecked(False)
            self._sincronizando_controles = False
    
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
            
            # Organizar solo archivos nuevos de forma silenciosa
            resultados, errores = self.organizador.organizar()
            total = sum(len(files) for cat in resultados.values() for files in cat.values())
            
            # Log de actividad (con o sin archivos)
            if total > 0:
                self._agregar_log(f"⚡ Auto-organización {hora_actual}: {total} archivos organizados")
                
                # Actualizar tooltip de la bandeja para mostrar última actividad
                if self.tray_icon:
                    self.tray_icon.setToolTip(f"🍄 DescargasOrdenadas - Última org: {hora_actual} ({total} archivos)")
                    
                # Actualizar estadísticas si hay cambios
                self._actualizar_datos()
            else:
                # Log cada 5 ejecuciones para confirmar que funciona
                if self._debug_timer_count % 5 == 0:
                    self._agregar_log(f"🔍 Timer activo {hora_actual}: revisando archivos... (#{self._debug_timer_count})")
                
                # Actualizar tooltip para mostrar que está funcionando
                if self.tray_icon:
                    self.tray_icon.setToolTip(f"🍄 DescargasOrdenadas - Revisando: {hora_actual} (Activo)")
                
        except Exception as e:
            self._agregar_log(f"❌ Error en auto-organización: {e}")
    
    def _ocultar_consola(self):
        """Oculta la consola del sistema."""
        try:
            if sys.platform == "win32":
                import ctypes
                console_window = ctypes.windll.kernel32.GetConsoleWindow()
                if console_window:
                    ctypes.windll.user32.ShowWindow(console_window, 0)  # SW_HIDE
            # En Linux/Mac la consola se maneja diferente, normalmente no es necesario ocultarla
        except Exception as e:
            logger.debug(f"No se pudo ocultar consola: {e}")
    
    def _mostrar_consola(self):
        """Muestra la consola del sistema."""
        try:
            if sys.platform == "win32":
                import ctypes
                console_window = ctypes.windll.kernel32.GetConsoleWindow()
                if console_window:
                    ctypes.windll.user32.ShowWindow(console_window, 5)  # SW_SHOW
        except Exception as e:
            logger.debug(f"No se pudo mostrar consola: {e}")
    
    def _cerrar_consola(self):
        """Cierra la ventana de consola del sistema."""
        try:
            if sys.platform == "win32":
                import ctypes
                console_window = ctypes.windll.kernel32.GetConsoleWindow()
                if console_window:
                    # Cerrar la ventana de consola
                    ctypes.windll.user32.PostMessageW(console_window, 0x0010, 0, 0)  # WM_CLOSE
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
        self.header = QLabel(f"🍄 DescargasOrdenadas v3.0 | 📁 {self.organizador.carpeta_descargas}")
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
        
        btn_organizar = QPushButton("🚀 Organizar Nuevos")
        btn_organizar.setStyleSheet("""
            QPushButton {
                padding: 12px; 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white; 
                font-size: 14px; 
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #45a049, stop:1 #3d8b40);
            }
            QPushButton:pressed {
                background: #3d8b40;
            }
        """)
        btn_organizar.clicked.connect(self._organizar)
        botones_layout.addWidget(btn_organizar)
        
        btn_reorganizar = QPushButton("🔄 Reorganizar TODO")
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
        
        layout.addWidget(botones_group)
        
        # Configuraciones
        config_group = QGroupBox("⚙️ Configuración")
        config_layout = QVBoxLayout(config_group)
        
        # Selección de carpeta
        carpeta_layout = QHBoxLayout()
        self.lbl_carpeta_actual = QLabel(f"📁 Carpeta actual: {os.path.basename(self.organizador.carpeta_descargas)}")
        self.lbl_carpeta_actual.setStyleSheet("font-weight: bold; color: #4CAF50;")
        carpeta_layout.addWidget(self.lbl_carpeta_actual)
        
        btn_seleccionar_carpeta = QPushButton("📂 Cambiar Carpeta")
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
        
        self.chk_autoarranque = QCheckBox("🔄 Iniciar con el sistema")
        self.chk_autoarranque.toggled.connect(self._toggle_autoarranque)
        config_layout.addWidget(self.chk_autoarranque)
        
        self.chk_auto_organizacion = QCheckBox("⚡ Auto-organización cada 30 segundos")
        self.chk_auto_organizacion.setToolTip("Organiza automáticamente archivos nuevos cada 30 segundos")
        self.chk_auto_organizacion.toggled.connect(self._toggle_auto_organizacion)
        config_layout.addWidget(self.chk_auto_organizacion)
        
        self.chk_subcarpetas = QCheckBox("📁 Usar subcarpetas detalladas")
        self.chk_subcarpetas.setChecked(True)
        config_layout.addWidget(self.chk_subcarpetas)
        
        self.chk_recursivo = QCheckBox("🔍 Buscar en subcarpetas")
        config_layout.addWidget(self.chk_recursivo)
        
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
            padding: 10px; 
            color: #ffffff;
            background-color: #f44336;
            border-radius: 6px;
            font-size: 14px;
        """)
        fechas_layout.addWidget(self.lbl_estado_fechas)
        
        # Botones de control
        botones_fechas_layout = QHBoxLayout()
        
        self.btn_activar_fechas = QPushButton("✅ ACTIVAR Organización por Fechas")
        self.btn_activar_fechas.setStyleSheet("""
            QPushButton {
                padding: 10px; 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2196F3, stop:1 #1976D2);
                color: white; 
                font-size: 12px; 
                font-weight: bold;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover { background: #1976D2; }
        """)
        self.btn_activar_fechas.clicked.connect(self._activar_fechas)
        botones_fechas_layout.addWidget(self.btn_activar_fechas)
        
        self.btn_desactivar_fechas = QPushButton("❌ DESACTIVAR Organización por Fechas")
        self.btn_desactivar_fechas.setStyleSheet("""
            QPushButton {
                padding: 10px; 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f44336, stop:1 #d32f2f);
                color: white; 
                font-size: 12px; 
                font-weight: bold;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover { background: #d32f2f; }
        """)
        self.btn_desactivar_fechas.clicked.connect(self._desactivar_fechas)
        self.btn_desactivar_fechas.setEnabled(False)
        botones_fechas_layout.addWidget(self.btn_desactivar_fechas)
        
        fechas_layout.addLayout(botones_fechas_layout)
        
        # Patrón
        patron_layout = QHBoxLayout()
        patron_layout.addWidget(QLabel("Patrón:"))
        
        self.combo_patron = QComboBox()
        self.combo_patron.addItems([
            "YYYY/MM-Mes",
            "YYYY/MM", 
            "YYYY",
            "MM-YYYY",
            "Mes-YYYY"
        ])
        patron_layout.addWidget(self.combo_patron)
        
        fechas_layout.addLayout(patron_layout)
        
        # Ejemplo
        self.lbl_ejemplo = QLabel("📁 Ejemplo: Downloads/Fechas/2024/12-Diciembre/Documentos/")
        self.lbl_ejemplo.setStyleSheet("padding: 8px; background-color: #f5f5f5; border-radius: 4px; font-family: monospace;")
        fechas_layout.addWidget(self.lbl_ejemplo)
        
        # Revertir
        btn_revertir = QPushButton("↩️ Revertir Organización por Fechas")
        btn_revertir.setStyleSheet("""
            QPushButton {
                padding: 8px; 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #9C27B0, stop:1 #7B1FA2);
                color: white; 
                font-size: 11px; 
                font-weight: bold;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover { background: #7B1FA2; }
        """)
        btn_revertir.clicked.connect(self._revertir_fechas)
        fechas_layout.addWidget(btn_revertir)
        
        layout.addWidget(fechas_group)
        
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
        self.text_logs.setPlainText("🍄 DescargasOrdenadas v3.0 - Sistema de Logs Interno\n" + "="*60 + "\n")
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
        self.text_logs.setPlainText("🍄 DescargasOrdenadas v3.0 - Sistema de Logs Interno\n" + "="*60 + "\n")
    
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
        """Organiza archivos nuevos."""
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            
            resultados, errores = self.organizador.organizar(
                organizar_subcarpetas=self.chk_recursivo.isChecked()
            )
            
            total = sum(len(files) for cat in resultados.values() for files in cat.values())
            
            mensaje = f"✅ {total} archivos organizados"
            if errores:
                mensaje += f"\n⚠️ {len(errores)} errores"
            
            QMessageBox.information(self, "Organización Completada", mensaje)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Error: {e}")
        finally:
            self.progress_bar.setVisible(False)
    
    def _reorganizar(self):
        """Reorganiza todos los archivos."""
        reply = QMessageBox.question(
            self, "Reorganizar TODO",
            "¿Reorganizar TODOS los archivos?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.progress_bar.setVisible(True)
                self.progress_bar.setRange(0, 0)
                
                resultados, errores = self.organizador.reorganizar_completamente()
                
                total = sum(len(files) for cat in resultados.values() for files in cat.values())
                QMessageBox.information(self, "Reorganización", f"✅ {total} archivos reorganizados")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ Error: {e}")
            finally:
                self.progress_bar.setVisible(False)
    
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
                self.header.setText(f"🍄 DescargasOrdenadas v3.0 | 📁 {nueva_carpeta}")
            
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
            self.header.setText(f"🍄 DescargasOrdenadas v3.0 | 📁 {carpeta_predeterminada}")
        
        # Reinitializar módulos avanzados
        self._inicializar_modulos()
        self._actualizar_datos()
        
        # Mostrar mensaje de confirmación
        QMessageBox.information(
            self, 
            "Carpeta Restablecida", 
            f"✅ Carpeta restablecida a la predeterminada:\n{carpeta_predeterminada}"
        )


def run_advanced_gui(directorio=None, minimizado=False):
    """Ejecuta la GUI avanzada."""
    app = QApplication.instance() or QApplication(sys.argv)
    
    window = OrganizadorAvanzado(directorio)
    
    if not minimizado:
        window.show()
    
    return app.exec() 