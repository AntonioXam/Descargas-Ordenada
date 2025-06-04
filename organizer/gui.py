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
        QComboBox
    )
except ImportError as e:
    logging.error(f"Error al importar PySide6: {e}")
    print("PySide6 no está instalado. Intente ejecutar: pip install PySide6")
    sys.exit(1)

# Importamos componentes locales
from .file_organizer import OrganizadorArchivos
from .autostart import GestorAutoarranque

logger = logging.getLogger('organizador.gui')

class TareaOrganizacion(QThread):
    """Hilo para ejecutar la organización de archivos en segundo plano."""
    
    # Señales
    progreso = Signal(str, str, str)  # archivo, categoría, subcategoría
    completado = Signal(dict, list)  # resultados, errores
    error = Signal(str)  # mensaje de error
    
    def __init__(self, organizador: OrganizadorArchivos, organizar_subcarpetas: bool = False):
        super().__init__()
        self.organizador = organizador
        self.organizar_subcarpetas = organizar_subcarpetas
    
    def run(self):
        """Ejecuta la tarea de organización en segundo plano."""
        try:
            resultados, errores = self.organizador.organizar(
                callback=lambda archivo, categoria, subcategoria: 
                    self.progreso.emit(archivo, categoria, subcategoria),
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
    """Ventana principal de la aplicación."""
    
    def __init__(self):
        super().__init__()
        
        # Inicializar componentes
        self.organizador = OrganizadorArchivos(usar_subcarpetas=True)
        self.gestor_autoarranque = GestorAutoarranque()
        self._cerrar_completamente = False
        
        # Configuración de la ventana
        self.setWindowTitle("DescargasOrdenadas")
        self.setMinimumSize(700, 500)
        
        # Configurar UI
        self._setup_ui()
        
        # Bandeja del sistema
        self._setup_system_tray()
        
        # Conectar señales
        self._conectar_senales()
        
        # Cargar estado del autoarranque
        self._cargar_estado_autoarranque()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Barra de herramientas
        toolbar = QToolBar("Barra de herramientas")
        self.addToolBar(toolbar)
        
        # Botón de organizar
        self.btn_organizar = QPushButton("Organizar ahora")
        self.btn_organizar.setIcon(QIcon.fromTheme("view-refresh", QIcon()))
        toolbar.addWidget(self.btn_organizar)
        
        toolbar.addSeparator()
        
        # Checkbox de autoarranque
        self.chk_autoarranque = QCheckBox("Auto-iniciar al arrancar el sistema")
        toolbar.addWidget(self.chk_autoarranque)
        
        toolbar.addSeparator()
        
        # Selector de modo de organización
        self.chk_usar_subcarpetas = QCheckBox("Usar subcarpetas")
        self.chk_usar_subcarpetas.setChecked(self.organizador.usar_subcarpetas)
        toolbar.addWidget(self.chk_usar_subcarpetas)
        
        toolbar.addSeparator()
        
        # Checkbox para organizar dentro de subcarpetas
        self.chk_organizar_subcarpetas = QCheckBox("Organizar dentro de carpetas")
        self.chk_organizar_subcarpetas.setToolTip("Buscar archivos para organizar también dentro de subcarpetas")
        toolbar.addWidget(self.chk_organizar_subcarpetas)
        
        # Información de la carpeta de descargas
        self.lbl_carpeta = QLabel(f"Carpeta: {self.organizador.carpeta_descargas}")
        main_layout.addWidget(self.lbl_carpeta)
        
        # Lista de archivos procesados
        self.list_archivos = QListWidget()
        self.list_archivos.setContextMenuPolicy(Qt.CustomContextMenu)
        main_layout.addWidget(self.list_archivos)
        
        # Barra de progreso
        self.barra_progreso = QProgressBar()
        self.barra_progreso.setVisible(False)
        main_layout.addWidget(self.barra_progreso)
        
        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo")
    
    def _setup_system_tray(self):
        """Configura el icono de la bandeja del sistema."""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("folder", QIcon()))
        
        # Menú de la bandeja
        tray_menu = QMenu()
        
        # Acciones
        mostrar_accion = QAction("Mostrar", self)
        mostrar_accion.triggered.connect(self.show)
        
        organizar_accion = QAction("Organizar ahora", self)
        organizar_accion.triggered.connect(self.iniciar_organizacion)
        
        salir_accion = QAction("Salir", self)
        salir_accion.triggered.connect(self.cerrar_aplicacion)
        
        # Añadir acciones al menú
        tray_menu.addAction(mostrar_accion)
        tray_menu.addAction(organizar_accion)
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
        """Activa o desactiva el autoarranque según el estado del checkbox."""
        activar = estado == Qt.CheckState.Checked.value
        exito, mensaje = self.gestor_autoarranque.configurar_autoarranque(activar)
        
        if exito:
            self.status_bar.showMessage(mensaje, 5000)
        else:
            QMessageBox.warning(self, "Error de autoarranque", mensaje)
            # Revertir el estado del checkbox
            self.chk_autoarranque.setChecked(not activar)
    
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
        
        # Deshabilitar botón
        self.btn_organizar.setEnabled(False)
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
        
        # Habilitar botón
        self.btn_organizar.setEnabled(True)
        
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
        
        # Habilitar botón
        self.btn_organizar.setEnabled(True)
        
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


def run_app():
    """Inicia la aplicación."""
    app = QApplication(sys.argv)
    app.setApplicationName("DescargasOrdenadas")
    app.setApplicationDisplayName("Organizador de Descargas")
    app.setQuitOnLastWindowClosed(False)
    
    # Configurar estilo
    app.setStyle("Fusion")
    
    # Crear y mostrar la ventana principal
    window = OrganizadorApp()
    window.show()
    
    # Ejecutar el bucle de eventos
    sys.exit(app.exec()) 