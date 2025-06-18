#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import requests
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime

try:
    from PySide6.QtCore import Qt, QSize, Signal, Slot, QThread, QUrl
    from PySide6.QtGui import QIcon, QColor, QPixmap, QFont, QAction, QDesktopServices
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
        QPushButton, QLabel, QCheckBox, QListWidget, QListWidgetItem,
        QProgressBar, QFileDialog, QColorDialog, QMessageBox, QMenu,
        QSystemTrayIcon, QToolBar, QStatusBar, QSplitter, QFrame,
        QComboBox, QTabWidget, QTextEdit, QSpinBox, QSlider, 
        QGroupBox, QRadioButton, QButtonGroup, QTableWidget, 
        QTableWidgetItem, QHeaderView, QPlainTextEdit
    )
except ImportError as e:
    logging.error(f"Error al importar PySide6: {e}")
    print("PySide6 no está instalado. Intente ejecutar: pip install PySide6")
    sys.exit(1)

# Importamos componentes locales
from .file_organizer import OrganizadorArchivos
from .autostart import GestorAutoarranque

# Importar módulos avanzados si están disponibles
try:
    from .ai_categorizer import CategorizadorIA
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

try:
    from .date_organizer import OrganizadorPorFecha
    DATE_ORGANIZER_AVAILABLE = True
except ImportError:
    DATE_ORGANIZER_AVAILABLE = False

try:
    from .duplicate_detector import DetectorDuplicados
    DUPLICATE_DETECTOR_AVAILABLE = True
except ImportError:
    DUPLICATE_DETECTOR_AVAILABLE = False

try:
    from .statistics import GestorEstadisticas
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False

try:
    from .custom_rules import GestorReglasPersonalizadas
    CUSTOM_RULES_AVAILABLE = True
except ImportError:
    CUSTOM_RULES_AVAILABLE = False

logger = logging.getLogger('organizador.gui')

class TareaOrganizacion(QThread):
    """Hilo para ejecutar la organización de archivos en segundo plano."""
    
    # Señales
    progreso = Signal(str, str, str)  # archivo, categoría, subcategoría
    completado = Signal(dict, list)  # resultados, errores
    error = Signal(str)  # mensaje de error
    
    def __init__(self, organizador: OrganizadorArchivos, organizar_subcarpetas: bool = False, reorganizar_todo: bool = False):
        super().__init__()
        self.organizador = organizador
        self.organizar_subcarpetas = organizar_subcarpetas
        self.reorganizar_todo = reorganizar_todo
    
    def run(self):
        """Ejecuta la tarea de organización en segundo plano."""
        try:
            callback = lambda archivo, categoria, subcategoria: self.progreso.emit(archivo, categoria, subcategoria)
            
            if self.reorganizar_todo:
                # Usar el nuevo método de reorganización completa
                resultados, errores = self.organizador.reorganizar_completamente(callback=callback)
            else:
                # Usar el método tradicional
                resultados, errores = self.organizador.organizar(
                    callback=callback,
                    organizar_subcarpetas=self.organizar_subcarpetas
                )
            
            self.completado.emit(resultados, errores)
        except Exception as e:
            self.error.emit(f"Error durante la organización: {e}")
            logger.error(f"Error en el hilo de organización: {e}", exc_info=True)


class ItemArchivo(QListWidgetItem):
    """Item personalizado para mostrar archivos en la lista."""
    
    def __init__(self, nombre: str, categoria: str, subcategoria: str = None, parent=None):
        super().__init__(nombre, parent)
        self.categoria = categoria
        self.subcategoria = subcategoria or "General"
        self.setIcon(self._obtener_icono(categoria))
        self.timestamp = datetime.now().strftime("%H:%M:%S")
        
        if subcategoria and subcategoria != "General":
            self.setText(f"[{self.timestamp}] {nombre} → {categoria}/{subcategoria}")
        else:
            self.setText(f"[{self.timestamp}] {nombre} → {categoria}")
        
    def _obtener_icono(self, categoria: str) -> QIcon:
        """Obtiene el icono correspondiente a la categoría."""
        # Iconos por defecto para cada categoría
        iconos = {
            'Imágenes': 'image',
            'Vídeos': 'video',
            'Audio': 'audio',
            'Documentos': 'document',
            'Hojas de cálculo': 'spreadsheet',
            'Presentaciones': 'presentation',
            'PDFs': 'pdf',
            'Ebooks': 'book',
            'Ejecutables': 'application',
            'Comprimidos': 'archive',
            'Código': 'code',
            'Carpetas': 'folder',
            'Descargas P2P': 'network-wired',
            'Archivos 3D': '3d',
            'Otros': 'file'
        }
        
        # Buscar el icono en los recursos
        icono_id = iconos.get(categoria, 'file')
        return QIcon.fromTheme(icono_id, QIcon())


class OrganizadorApp(QMainWindow):
    """Ventana principal de la aplicación con funcionalidades avanzadas."""
    
    def __init__(self, directorio_personalizado=None):
        super().__init__()
        
        # Inicializar componentes
        if directorio_personalizado:
            self.organizador = OrganizadorArchivos(carpeta_descargas=str(directorio_personalizado), usar_subcarpetas=True)
        else:
            self.organizador = OrganizadorArchivos(usar_subcarpetas=True)
        self.gestor_autoarranque = GestorAutoarranque()
        self._cerrar_completamente = False
        
        # Inicializar módulos avanzados
        self._inicializar_modulos_avanzados()
        
        # Configuración de la ventana
        self.setWindowTitle("🍄 DescargasOrdenadas v3.0 - Edición Avanzada")
        self.setMinimumSize(900, 700)
        
        # Configurar UI
        self._setup_ui()
        
        # Bandeja del sistema
        self._setup_system_tray()
        
        # Conectar señales
        self._conectar_senales()
        
        # Cargar estado del autoarranque
        self._cargar_estado_autoarranque()
    
    def _inicializar_modulos_avanzados(self):
        """Inicializa los módulos avanzados disponibles."""
        carpeta_descargas = Path(self.organizador.carpeta_descargas)
        
        # IA Categorizador
        if AI_AVAILABLE:
            try:
                self.ai_categorizer = CategorizadorIA(carpeta_descargas)
                logger.info("🤖 Categorizador IA inicializado")
            except Exception as e:
                logger.error(f"Error inicializando IA: {e}")
                self.ai_categorizer = None
        else:
            self.ai_categorizer = None
        
        # Organizador por fechas
        if DATE_ORGANIZER_AVAILABLE:
            try:
                self.date_organizer = OrganizadorPorFecha(carpeta_descargas)
                logger.info("📅 Organizador por fechas inicializado")
            except Exception as e:
                logger.error(f"Error inicializando organizador de fechas: {e}")
                self.date_organizer = None
        else:
            self.date_organizer = None
        
        # Detector de duplicados
        if DUPLICATE_DETECTOR_AVAILABLE:
            try:
                self.duplicate_detector = DetectorDuplicados(carpeta_descargas)
                logger.info("🔍 Detector de duplicados inicializado")
            except Exception as e:
                logger.error(f"Error inicializando detector de duplicados: {e}")
                self.duplicate_detector = None
        else:
            self.duplicate_detector = None
        
        # Estadísticas
        if STATS_AVAILABLE:
            try:
                self.stats_manager = GestorEstadisticas(carpeta_descargas)
                logger.info("📊 Gestor de estadísticas inicializado")
            except Exception as e:
                logger.error(f"Error inicializando estadísticas: {e}")
                self.stats_manager = None
        else:
            self.stats_manager = None
        
        # Reglas personalizadas
        if CUSTOM_RULES_AVAILABLE:
            try:
                self.custom_rules = GestorReglasPersonalizadas(carpeta_descargas)
                logger.info("⚙️ Reglas personalizadas inicializadas")
            except Exception as e:
                logger.error(f"Error inicializando reglas personalizadas: {e}")
                self.custom_rules = None
        else:
            self.custom_rules = None
    
    def _setup_ui(self):
        """Configura la interfaz de usuario con pestañas avanzadas."""
        # Widget central con pestañas
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Información de la carpeta
        carpeta_layout = QHBoxLayout()
        self.lbl_carpeta = QLabel(f"📁 Carpeta: {self.organizador.carpeta_descargas}")
        carpeta_layout.addWidget(self.lbl_carpeta)
        
        # Botón para cambiar carpeta
        btn_cambiar_carpeta = QPushButton("📂 Cambiar")
        btn_cambiar_carpeta.setMaximumWidth(100)
        btn_cambiar_carpeta.clicked.connect(self._cambiar_carpeta)
        carpeta_layout.addWidget(btn_cambiar_carpeta)
        
        # Botón para resetear a descargas
        btn_reset_carpeta = QPushButton("↻")
        btn_reset_carpeta.setMaximumWidth(40)
        btn_reset_carpeta.setToolTip("Volver a carpeta de descargas")
        btn_reset_carpeta.clicked.connect(self._resetear_carpeta)
        carpeta_layout.addWidget(btn_reset_carpeta)
        
        main_layout.addLayout(carpeta_layout)
        
        # Pestañas principales
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Pestaña 1: Organización Principal
        self._setup_tab_organizacion()
        
        # Pestaña 2: IA y Categorización
        if AI_AVAILABLE:
            self._setup_tab_ai()
        
        # Pestaña 3: Organización por Fechas
        if DATE_ORGANIZER_AVAILABLE:
            self._setup_tab_fechas()
        
        # Pestaña 4: Duplicados
        if DUPLICATE_DETECTOR_AVAILABLE:
            self._setup_tab_duplicados()
        
        # Pestaña 5: Estadísticas
        if STATS_AVAILABLE:
            self._setup_tab_estadisticas()
        
        # Pestaña 6: Reglas Personalizadas
        if CUSTOM_RULES_AVAILABLE:
            self._setup_tab_reglas()
        
        # Barra de progreso global
        self.barra_progreso = QProgressBar()
        self.barra_progreso.setVisible(False)
        main_layout.addWidget(self.barra_progreso)
        
        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("🍄 DescargasOrdenadas v3.0 - Listo para organizar")
    
    def _setup_tab_organizacion(self):
        """Configura la pestaña de organización principal."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Controles principales
        controles_group = QGroupBox("🚀 Controles de Organización")
        controles_layout = QHBoxLayout(controles_group)
        
        self.btn_organizar = QPushButton("🚀 Organizar Nuevos")
        self.btn_organizar.setToolTip("Organiza solo archivos nuevos")
        controles_layout.addWidget(self.btn_organizar)
        
        self.btn_reorganizar = QPushButton("🔄 Reorganizar Todo")
        self.btn_reorganizar.setToolTip("Reorganiza TODOS los archivos")
        controles_layout.addWidget(self.btn_reorganizar)
        
        layout.addWidget(controles_group)
        
        # Configuración
        config_group = QGroupBox("⚙️ Configuración")
        config_layout = QVBoxLayout(config_group)
        
        self.chk_autoarranque = QCheckBox("🔄 Auto-iniciar al arrancar el sistema")
        config_layout.addWidget(self.chk_autoarranque)
        
        self.chk_usar_subcarpetas = QCheckBox("📁 Usar subcarpetas detalladas")
        self.chk_usar_subcarpetas.setChecked(True)
        config_layout.addWidget(self.chk_usar_subcarpetas)
        
        self.chk_organizar_subcarpetas = QCheckBox("🔍 Organizar dentro de carpetas existentes")
        config_layout.addWidget(self.chk_organizar_subcarpetas)
        
        layout.addWidget(config_group)
        
        # Lista de archivos procesados
        self.list_archivos = QListWidget()
        self.list_archivos.setContextMenuPolicy(Qt.CustomContextMenu)
        layout.addWidget(self.list_archivos)
        
        self.tab_widget.addTab(tab, "🏠 Principal")
    
    def _setup_tab_ai(self):
        """Configura la pestaña de IA y categorización."""
        if not self.ai_categorizer:
            return
            
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Estado de la IA
        ia_group = QGroupBox("🤖 Categorización Inteligente")
        ia_layout = QVBoxLayout(ia_group)
        
        self.lbl_ia_estado = QLabel("Estado: ✅ Activo")
        ia_layout.addWidget(self.lbl_ia_estado)
        
        # Control de confianza
        confianza_layout = QHBoxLayout()
        confianza_layout.addWidget(QLabel("Nivel de confianza:"))
        
        self.slider_confianza = QSlider(Qt.Horizontal)
        self.slider_confianza.setRange(30, 95)
        self.slider_confianza.setValue(int(self.ai_categorizer.confianza_minima * 100))
        self.slider_confianza.valueChanged.connect(self._actualizar_confianza_ia)
        confianza_layout.addWidget(self.slider_confianza)
        
        self.lbl_confianza = QLabel(f"{self.slider_confianza.value()}%")
        confianza_layout.addWidget(self.lbl_confianza)
        
        ia_layout.addLayout(confianza_layout)
        
        # Botones de IA
        botones_ia_layout = QHBoxLayout()
        
        self.btn_entrenar_ia = QPushButton("🧠 Entrenar con historial")
        self.btn_entrenar_ia.clicked.connect(self._entrenar_ia)
        botones_ia_layout.addWidget(self.btn_entrenar_ia)
        
        self.btn_limpiar_ia = QPushButton("🧹 Limpiar modelo")
        self.btn_limpiar_ia.clicked.connect(self._limpiar_modelo_ia)
        botones_ia_layout.addWidget(self.btn_limpiar_ia)
        
        ia_layout.addLayout(botones_ia_layout)
        
        layout.addWidget(ia_group)
        
        # Patrones aprendidos
        patrones_group = QGroupBox("📊 Patrones Aprendidos")
        patrones_layout = QVBoxLayout(patrones_group)
        
        self.text_patrones = QTextEdit()
        self.text_patrones.setMaximumHeight(200)
        self.text_patrones.setReadOnly(True)
        patrones_layout.addWidget(self.text_patrones)
        
        self.btn_actualizar_patrones = QPushButton("🔄 Actualizar Patrones")
        self.btn_actualizar_patrones.clicked.connect(self._actualizar_patrones_ia)
        patrones_layout.addWidget(self.btn_actualizar_patrones)
        
        layout.addWidget(patrones_group)
        
        self.tab_widget.addTab(tab, "🤖 IA")
        
        # Actualizar patrones al inicio
        self._actualizar_patrones_ia()
    
    def _setup_tab_fechas(self):
        """Configura la pestaña de organización por fechas."""
        if not self.date_organizer:
            return
            
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Control de activación
        fechas_group = QGroupBox("📅 Organización por Fechas")
        fechas_layout = QVBoxLayout(fechas_group)
        
        self.chk_fechas_activo = QCheckBox("🔄 Activar organización por fechas")
        self.chk_fechas_activo.setChecked(self.date_organizer.activo)
        self.chk_fechas_activo.toggled.connect(self._toggle_organizacion_fechas)
        fechas_layout.addWidget(self.chk_fechas_activo)
        
        # Selector de patrón
        patron_layout = QHBoxLayout()
        patron_layout.addWidget(QLabel("Patrón de organización:"))
        
        self.combo_patron_fechas = QComboBox()
        self.combo_patron_fechas.addItems([
            "YYYY/MM-Mes",  # 2024/12-Diciembre
            "YYYY/MM",      # 2024/12
            "YYYY",         # 2024
            "MM-YYYY",      # 12-2024
            "Mes-YYYY"      # Diciembre-2024
        ])
        self.combo_patron_fechas.setCurrentText(self.date_organizer.patron_fechas)
        self.combo_patron_fechas.currentTextChanged.connect(self._cambiar_patron_fechas)
        patron_layout.addWidget(self.combo_patron_fechas)
        
        fechas_layout.addLayout(patron_layout)
        
        # Ejemplo de carpeta resultante
        self.lbl_ejemplo_fecha = QLabel()
        self._actualizar_ejemplo_fecha()
        fechas_layout.addWidget(self.lbl_ejemplo_fecha)
        
        # Botón de revertir
        self.btn_revertir_fechas = QPushButton("↩️ Revertir organización por fechas")
        self.btn_revertir_fechas.clicked.connect(self._revertir_organizacion_fechas)
        fechas_layout.addWidget(self.btn_revertir_fechas)
        
        layout.addWidget(fechas_group)
        
        self.tab_widget.addTab(tab, "📅 Fechas")
    
    def _setup_tab_duplicados(self):
        """Configura la pestaña del detector de duplicados."""
        if not self.duplicate_detector:
            return
            
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Controles de duplicados
        duplicados_group = QGroupBox("🔍 Detector de Duplicados")
        duplicados_layout = QVBoxLayout(duplicados_group)
        
        # Botones de acción
        botones_layout = QHBoxLayout()
        
        self.btn_buscar_duplicados = QPushButton("🔍 Buscar Duplicados")
        self.btn_buscar_duplicados.clicked.connect(self._buscar_duplicados)
        botones_layout.addWidget(self.btn_buscar_duplicados)
        
        self.btn_limpiar_duplicados = QPushButton("🧹 Eliminar Duplicados")
        self.btn_limpiar_duplicados.clicked.connect(self._eliminar_duplicados)
        botones_layout.addWidget(self.btn_limpiar_duplicados)
        
        duplicados_layout.addLayout(botones_layout)
        
        layout.addWidget(duplicados_group)
        
        # Tabla de duplicados encontrados
        self.table_duplicados = QTableWidget()
        self.table_duplicados.setColumnCount(4)
        self.table_duplicados.setHorizontalHeaderLabels(["Archivo", "Tamaño", "Duplicados", "Acción"])
        self.table_duplicados.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table_duplicados)
        
        self.tab_widget.addTab(tab, "🔍 Duplicados")
    
    def _setup_tab_estadisticas(self):
        """Configura la pestaña de estadísticas."""
        if not self.stats_manager:
            return
            
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Botón de actualizar
        self.btn_actualizar_stats = QPushButton("🔄 Actualizar Estadísticas")
        self.btn_actualizar_stats.clicked.connect(self._actualizar_estadisticas)
        layout.addWidget(self.btn_actualizar_stats)
        
        # Área de estadísticas
        self.text_estadisticas = QPlainTextEdit()
        self.text_estadisticas.setReadOnly(True)
        layout.addWidget(self.text_estadisticas)
        
        self.tab_widget.addTab(tab, "📊 Estadísticas")
        
        # Cargar estadísticas iniciales
        self._actualizar_estadisticas()
    
    def _setup_tab_reglas(self):
        """Configura la pestaña de reglas personalizadas."""
        if not self.custom_rules:
            return
            
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Controles de reglas
        reglas_group = QGroupBox("⚙️ Reglas Personalizadas")
        reglas_layout = QVBoxLayout(reglas_group)
        
        # Tabla de reglas
        self.table_reglas = QTableWidget()
        self.table_reglas.setColumnCount(4)
        self.table_reglas.setHorizontalHeaderLabels(["Patrón", "Categoría", "Activa", "Acciones"])
        reglas_layout.addWidget(self.table_reglas)
        
        # Botones de reglas
        botones_reglas_layout = QHBoxLayout()
        
        self.btn_agregar_regla = QPushButton("➕ Agregar Regla")
        self.btn_agregar_regla.clicked.connect(self._agregar_regla)
        botones_reglas_layout.addWidget(self.btn_agregar_regla)
        
        self.btn_actualizar_reglas = QPushButton("🔄 Actualizar")
        self.btn_actualizar_reglas.clicked.connect(self._actualizar_reglas)
        botones_reglas_layout.addWidget(self.btn_actualizar_reglas)
        
        reglas_layout.addLayout(botones_reglas_layout)
        
        layout.addWidget(reglas_group)
        
        self.tab_widget.addTab(tab, "⚙️ Reglas")
        
        # Cargar reglas iniciales
        self._actualizar_reglas()
    
    def _setup_system_tray(self):
        """Configura el icono de la bandeja del sistema."""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("folder", QIcon()))
        
        # Menú de la bandeja
        tray_menu = QMenu()
        
        # Acciones
        mostrar_accion = QAction("Mostrar", self)
        mostrar_accion.triggered.connect(self.show)
        
        organizar_accion = QAction("🚀 Organizar nuevos", self)
        organizar_accion.triggered.connect(self.iniciar_organizacion)
        
        reorganizar_accion = QAction("🔄 Reorganizar todo", self)
        reorganizar_accion.triggered.connect(self.iniciar_reorganizacion)
        
        salir_accion = QAction("Salir", self)
        salir_accion.triggered.connect(self.cerrar_aplicacion)
        
        # Añadir acciones al menú
        tray_menu.addAction(mostrar_accion)
        tray_menu.addAction(organizar_accion)
        tray_menu.addAction(reorganizar_accion)
        tray_menu.addSeparator()
        tray_menu.addAction(salir_accion)
        
        # Asignar menú al icono
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._tray_icon_activated)
        
        # Mostrar el icono
        self.tray_icon.show()
    
    def _tray_icon_activated(self, reason):
        """Maneja la activación del icono de la bandeja del sistema."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
    
    def _conectar_senales(self):
        """Conecta las señales de los widgets con sus slots."""
        # Botón de organizar
        self.btn_organizar.clicked.connect(self.iniciar_organizacion)
        
        # Botón de reorganizar todo
        self.btn_reorganizar.clicked.connect(self.iniciar_reorganizacion)
        
        # Checkbox de autoarranque
        self.chk_autoarranque.stateChanged.connect(self._toggle_autoarranque)
        
        # Selector de modo de organización
        self.chk_usar_subcarpetas.stateChanged.connect(self._toggle_usar_subcarpetas)
        
        # Checkbox para organizar dentro de subcarpetas
        self.chk_organizar_subcarpetas.stateChanged.connect(self._toggle_organizar_subcarpetas)
        
        # Lista de archivos (menú contextual)
        self.list_archivos.customContextMenuRequested.connect(self._mostrar_menu_contextual)
    
    def _cargar_estado_autoarranque(self):
        """Carga el estado actual del autoarranque."""
        estado = self.gestor_autoarranque.verificar_autoarranque()
        self.chk_autoarranque.setChecked(estado)
    
    def _toggle_autoarranque(self, estado):
        """Activa o desactiva el autoarranque."""
        activar = estado == Qt.Checked
        resultado, mensaje = self.gestor_autoarranque.configurar_autoarranque(activar)
        
        if resultado:
            if activar:
                self.status_bar.showMessage(f"Autoarranque activado. La aplicación se iniciará y organizará automáticamente al iniciar sesión.")
                # Mostrar mensaje adicional
                QMessageBox.information(
                    self,
                    "Autoarranque configurado",
                    "La aplicación se iniciará automáticamente al iniciar sesión y organizará los archivos de descargas."
                )
            else:
                self.status_bar.showMessage("Autoarranque desactivado.")
        else:
            self.status_bar.showMessage(f"Error: {mensaje}")
            self.chk_autoarranque.setChecked(not activar)  # Revertir cambio
    
    def _toggle_usar_subcarpetas(self, estado):
        """Activa o desactiva el uso de subcarpetas según el estado del checkbox."""
        activar = estado == Qt.CheckState.Checked.value
        self.organizador.usar_subcarpetas = activar
        self.status_bar.showMessage("Modo de organización actualizado", 5000)
    
    def _toggle_organizar_subcarpetas(self, estado):
        """Activa o desactiva la organización de subcarpetas según el estado del checkbox."""
        activar = estado == Qt.CheckState.Checked.value
        self.status_bar.showMessage("Modo de organización actualizado", 5000)
    
    def _mostrar_menu_contextual(self, posicion):
        """Muestra el menú contextual para la lista de archivos."""
        menu = QMenu()
        
        # Acciones
        limpiar_accion = QAction("Limpiar lista", self)
        limpiar_accion.triggered.connect(self.list_archivos.clear)
        
        abrir_carpeta_accion = QAction("Abrir carpeta de descargas", self)
        abrir_carpeta_accion.triggered.connect(
            lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.organizador.carpeta_descargas)))
        )
        
        # Añadir acciones al menú
        menu.addAction(limpiar_accion)
        menu.addAction(abrir_carpeta_accion)
        
        # Mostrar el menú
        menu.exec(self.list_archivos.mapToGlobal(posicion))
    
    @Slot()
    def iniciar_organizacion(self):
        """Inicia el proceso de organización de archivos en segundo plano."""
        # Actualizar configuración de subcarpetas
        self.organizador.usar_subcarpetas = self.chk_usar_subcarpetas.isChecked()
        organizar_subcarpetas = self.chk_organizar_subcarpetas.isChecked()
        
        # Deshabilitar botones
        self.btn_organizar.setEnabled(False)
        self.btn_reorganizar.setEnabled(False)
        self.status_bar.showMessage("Organizando archivos...")
        
        # Mostrar barra de progreso
        self.barra_progreso.setVisible(True)
        self.barra_progreso.setRange(0, 0)  # Modo indeterminado
        
        # Crear y configurar el hilo de organización
        self.tarea = TareaOrganizacion(self.organizador, organizar_subcarpetas)
        self.tarea.progreso.connect(self._actualizar_progreso)
        self.tarea.completado.connect(self._organizacion_completada)
        self.tarea.error.connect(self._organizacion_error)
        
        # Iniciar el hilo
        self.tarea.start()
    
    @Slot()
    def iniciar_reorganizacion(self):
        """Inicia el proceso de reorganización completa de archivos en segundo plano."""
        # Actualizar configuración de subcarpetas
        self.organizador.usar_subcarpetas = self.chk_usar_subcarpetas.isChecked()
        
        # Confirmar con el usuario
        respuesta = QMessageBox.question(
            self,
            "Reorganizar Todo",
            "⚠️ Esta opción reorganizará TODOS los archivos, incluso los ya organizados.\n\n"
            "Esto puede tomar más tiempo y mover archivos que pueden haber sido "
            "reubicados manualmente.\n\n"
            "¿Estás seguro de que quieres continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if respuesta != QMessageBox.StandardButton.Yes:
            return
        
        # Deshabilitar botones
        self.btn_organizar.setEnabled(False)
        self.btn_reorganizar.setEnabled(False)
        self.status_bar.showMessage("Reorganizando TODOS los archivos...")
        
        # Mostrar barra de progreso
        self.barra_progreso.setVisible(True)
        self.barra_progreso.setRange(0, 0)  # Modo indeterminado
        
        # Limpiar lista para mostrar solo la reorganización actual
        self.list_archivos.clear()
        
        # Crear y configurar el hilo de reorganización
        self.tarea = TareaOrganizacion(self.organizador, reorganizar_todo=True)
        self.tarea.progreso.connect(self._actualizar_progreso)
        self.tarea.completado.connect(self._organizacion_completada)
        self.tarea.error.connect(self._organizacion_error)
        
        # Iniciar el hilo
        self.tarea.start()
    
    @Slot(str, str, str)
    def _actualizar_progreso(self, archivo, categoria, subcategoria):
        """Actualiza el progreso de la organización."""
        # Añadir archivo a la lista
        item = ItemArchivo(archivo, categoria, subcategoria)
        self.list_archivos.addItem(item)
        
        # Desplazar al final
        self.list_archivos.scrollToBottom()
    
    @Slot(dict, list)
    def _organizacion_completada(self, resultados, errores):
        """Maneja la finalización de la organización."""
        # Ocultar barra de progreso
        self.barra_progreso.setVisible(False)
        
        # Habilitar botones
        self.btn_organizar.setEnabled(True)
        self.btn_reorganizar.setEnabled(True)
        
        # Contar el total de archivos organizados
        total_archivos = 0
        for categoria, subcategorias in resultados.items():
            for subcategoria, archivos in subcategorias.items():
                total_archivos += len(archivos)
        
        if total_archivos > 0:
            mensaje = f"Organización completada: {total_archivos} archivos organizados"
            self.status_bar.showMessage(mensaje, 5000)
            
            # Notificación en la bandeja
            self.tray_icon.showMessage(
                "DescargasOrdenadas",
                mensaje,
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )
        else:
            self.status_bar.showMessage("No se encontraron archivos para organizar", 5000)
        
        # Mostrar errores si hay
        if errores:
            error_msg = "\n".join(errores)
            QMessageBox.warning(
                self,
                "Errores durante la organización",
                f"Se produjeron {len(errores)} errores durante la organización:\n\n{error_msg}"
            )
    
    @Slot(str)
    def _organizacion_error(self, mensaje):
        """Maneja errores durante la organización."""
        # Ocultar barra de progreso
        self.barra_progreso.setVisible(False)
        
        # Habilitar botones
        self.btn_organizar.setEnabled(True)
        self.btn_reorganizar.setEnabled(True)
        
        # Mostrar error
        QMessageBox.critical(self, "Error", mensaje)
        self.status_bar.showMessage("Error durante la organización", 5000)
    
    def closeEvent(self, event):
        """Maneja el evento de cierre de la ventana."""
        # Minimizar a la bandeja en lugar de cerrar
        if self.tray_icon.isVisible() and not self._cerrar_completamente:
            QMessageBox.information(
                self,
                "DescargasOrdenadas",
                "La aplicación seguirá ejecutándose en la bandeja del sistema.\n"
                "Para cerrarla completamente, usa el menú de la bandeja."
            )
            self.hide()
            event.ignore()
        else:
            event.accept()
    
    def cerrar_aplicacion(self):
        """Cierra completamente la aplicación."""
        self._cerrar_completamente = True
        self.close()
        QApplication.quit()
    
    def _cambiar_carpeta(self):
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
            self.lbl_carpeta.setText(f"📁 Carpeta: {nueva_carpeta}")
            
            # Reinitializar módulos avanzados con la nueva carpeta
            self._inicializar_modulos_avanzados()
            
            # Mostrar mensaje de confirmación
            QMessageBox.information(
                self, 
                "Carpeta Cambiada", 
                f"✅ Carpeta de trabajo cambiada a:\n{nueva_carpeta}"
            )
    
    def _resetear_carpeta(self):
        """Restablece la carpeta de descargas a la predeterminada."""
        from .file_organizer import OrganizadorArchivos
        # Obtener la carpeta de descargas predeterminada
        organizador_temp = OrganizadorArchivos()
        carpeta_predeterminada = organizador_temp._detectar_carpeta_descargas()
        
        # Actualizar el organizador
        self.organizador.carpeta_descargas = carpeta_predeterminada
        self.organizador.carpeta_config = self.organizador.carpeta_descargas / ".config"
        
        # Actualizar la interfaz
        self.lbl_carpeta.setText(f"📁 Carpeta: {carpeta_predeterminada}")
        
        # Reinitializar módulos avanzados
        self._inicializar_modulos_avanzados()
        
        # Mostrar mensaje de confirmación
        QMessageBox.information(
            self, 
            "Carpeta Restablecida", 
            f"✅ Carpeta restablecida a la predeterminada:\n{carpeta_predeterminada}"
        )


def run_app(directorio=None, minimizado=False):
    """
    Ejecuta la aplicación.
    
    Args:
        directorio: Directorio personalizado a organizar (opcional).
        minimizado: Si es True, inicia la aplicación minimizada en la bandeja del sistema.
    """
    # Crear aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName("DescargasOrdenadas")
    app.setApplicationVersion("2.0")
    app.setQuitOnLastWindowClosed(False)
    
    # Crear ventana principal
    ventana = OrganizadorApp(directorio_personalizado=directorio)
    
    # Si se solicita iniciar minimizado, iniciar en bandeja del sistema
    if minimizado:
        ventana.hide()
        # Mostrar un mensaje en la bandeja del sistema
        if ventana.tray_icon and ventana.tray_icon.isSystemTrayAvailable():
            ventana.tray_icon.showMessage(
                "DescargasOrdenadas",
                "La aplicación se está ejecutando en segundo plano. Haga clic para mostrar.",
                QSystemTrayIcon.Information,
                3000
            )
    else:
        ventana.show()
    
    # Ejecutar loop de eventos
    sys.exit(app.exec()) 