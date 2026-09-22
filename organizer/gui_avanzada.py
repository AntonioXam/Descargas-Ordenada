#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GUI Avanzada para DescargasOrdenadas v3.0 con todas las funcionalidades
"""

import sys
import os
import logging
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    from PySide6.QtCore import (
        Qt, Signal, Slot, QThread, QTimer, QEvent, QSize, QPropertyAnimation,
        QEasingCurve, QRectF, QPointF,
    )
    from PySide6.QtGui import (
        QIcon, QAction, QPixmap, QPainter, QGuiApplication, QColor, QPen,
        QFont, QCursor,
    )
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QCheckBox, QListWidget, QListWidgetItem,
        QProgressBar, QMessageBox, QSystemTrayIcon, QTabWidget, QTextEdit,
        QSlider, QGroupBox, QComboBox, QPlainTextEdit, QInputDialog, QMenu,
        QFileDialog, QScrollArea, QProgressDialog, QFrame, QStackedWidget,
        QGraphicsOpacityEffect, QSizePolicy, QSplitter, QRadioButton
    )
except ImportError:
    print("PySide6 no instalado. Ejecuta: pip install PySide6")
    sys.exit(1)

from .file_organizer import OrganizadorArchivos
from .autostart import GestorAutoarranque
from .version import obtener_version
from . import estilos

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
    MENU_CONTEXTUAL_DISPONIBLE = True  # disponible en Windows, macOS y Linux
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


class Switch(QCheckBox):
    """Interruptor encendido/apagado estilo iOS (sobre QCheckBox)."""

    def __init__(self, texto="", parent=None):
        super().__init__(texto, parent)
        self.setCursor(Qt.PointingHandCursor)
        from PySide6.QtWidgets import QSizePolicy as _QSizePolicy
        self.setSizePolicy(_QSizePolicy.Preferred, _QSizePolicy.Fixed)
        self.setMinimumHeight(26)
        self.setMinimumWidth(self.sizeHint().width())

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        fm = self.fontMetrics()
        texto_w = fm.horizontalAdvance(self.text()) if self.text() else 0
        gap = 0
        alto = 22
        ancho_pill = 40
        y = (self.height() - alto) / 2

        activo = self.isChecked()
        habilitado = self.isEnabled()

        colores = estilos.hoja_estilo_switch(self._tema)
        if habilitado:
            color_on = QColor(colores["on"])
            color_off = QColor(colores["off"])
        else:
            color_on = QColor(colores["on_disabled"])
            color_off = QColor(colores["off_disabled"])

        p.setPen(Qt.NoPen)
        p.setBrush(color_on if activo else color_off)
        p.drawRoundedRect(QRectF(gap, y, ancho_pill, alto), alto / 2, alto / 2)

        # Círculo deslizante
        r = alto - 4
        margen = 2
        x_circ = gap + margen if not activo else gap + ancho_pill - r - margen
        p.setBrush(QColor(colores["thumb"]))
        p.drawEllipse(QPointF(x_circ + r / 2, self.height() / 2), r / 2, r / 2)

        if self.text():
            p.setPen(QColor(colores["texto"] if habilitado else colores["texto_disabled"]))
            p.drawText(QRectF(gap + ancho_pill + 10, 0, texto_w + 4, self.height()),
                       Qt.AlignVCenter | Qt.AlignLeft, self.text())
        p.end()

    def sizeHint(self):
        fm = self.fontMetrics()
        ancho = (40 + 10 + fm.horizontalAdvance(self.text())) if self.text() else 44
        return QSize(ancho, 26)

    _tema = "auto"


class Tarjeta(QFrame):
    """Tarjeta con esquinas redondeadas al estilo macOS."""

    def __init__(self, parent=None, destacada=False):
        super().__init__(parent)
        self.setProperty("rol", "tarjeta_destacada" if destacada else "tarjeta")
        self.setFrameShape(QFrame.NoFrame)


class Separador(QFrame):
    """Línea divisoria fina."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("rol", "separador")
        self.setFixedHeight(1)


class OrganizadorAvanzado(QMainWindow):
    """GUI completa con todas las funcionalidades avanzadas."""
    
    def __init__(self, directorio=None, auto_organizacion=False, intervalo_auto=None, modo_auto=None):
        super().__init__()

        # Preferencias de auto-organización (se completan desde la configuración)
        self._auto_intervalo_inicial = intervalo_auto
        self._auto_modo_inicial = modo_auto

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
        
        # Inicializar sistema de temas (claro / oscuro / automático del sistema)
        self.gestor_temas = None
        self._tema = self._cargar_preferencia_tema()
        Switch._tema = self._tema
        if TEMAS_DISPONIBLES:
            self.gestor_temas = obtener_gestor_temas()
            # Los temas antiguos (minimal_*) migran al sistema nuevo
            if self._tema not in ("claro", "oscuro", "auto"):
                self._tema = "auto"
        
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
        self._vista_actual = 0
        
        # Configuración ventana
        self.setWindowTitle("DescargasOrdenadas")
        self.setMinimumSize(760, 560)
        self._ajustar_tamano_inicial()
        
        self._setup_ui()
        self._aplicar_tema()
        self._setup_system_tray()
        self._inicializar_modulos()
        
        # Timer para organización automática (siempre existe)
        self.timer_auto = QTimer()
        self.timer_auto.timeout.connect(self._organizar_automatico)
        
        # Timer para verificar actualizaciones periódicamente
        self.timer_actualizaciones = QTimer()
        self.timer_actualizaciones.timeout.connect(self._verificar_actualizaciones_silencioso)
        
        # Restaurar el modo y el intervalo guardados y, si la configuración
        # tenía la organización automática activada, arrancar con ella.
        self._restaurar_preferencias_auto()

        auto_activa_guardada = auto_organizacion
        if not auto_activa_guardada and self.config_portable:
            auto_activa_guardada = bool(self.config_portable.obtener("auto_organizacion", False))

        if auto_activa_guardada:
            # Activar en cuanto la ventana está construida (sin esperas)
            self._activar_auto_guardada()
        
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
                self.resize(1040, 720)
                return
            
            geom = screen.availableGeometry()
            min_w, min_h = 760, 560

            ventana_guardada = {}
            if self.config_portable:
                ventana_guardada = self.config_portable.obtener("ventana", {}) or {}

            ancho_guardado = int(ventana_guardada.get("ancho", 0) or 0)
            alto_guardado = int(ventana_guardada.get("alto", 0) or 0)
            maximizada = bool(ventana_guardada.get("maximizada", False))

            if ancho_guardado >= min_w and alto_guardado >= min_h:
                ancho = min(ancho_guardado, geom.width())
                alto = min(alto_guardado, geom.height())
            else:
                # Ventana cómoda por defecto, sin ocupar todo el escritorio.
                ancho = min(max(min_w, int(geom.width() * 0.60)), geom.width())
                alto = min(max(min_h, int(geom.height() * 0.74)), geom.height())

            self.resize(ancho, alto)

            if maximizada:
                self.setWindowState(Qt.WindowMaximized)
            else:
                # Un pelín por encima del centro: se percibe mejor equilibrado
                x = geom.x() + (geom.width() - ancho) // 2
                y = geom.y() + max(0, (geom.height() - alto) // 2 - 20)
                self.move(x, y)
        except Exception:
            self.resize(1040, 720)

    def _guardar_geometria_ventana(self):
        """Guarda el tamaño y estado de la ventana para restaurarlos después."""
        if not self.config_portable:
            return
        try:
            self.config_portable.establecer(
                "ventana",
                {
                    "ancho": self.width(),
                    "alto": self.height(),
                    "maximizada": self.isMaximized()
                }
            )
        except Exception as e:
            logger.debug(f"No se pudo guardar la geometría de la ventana: {e}")
    
    def _cargar_preferencia_tema(self) -> str:
        """Devuelve el tema guardado ('claro', 'oscuro' o 'auto')."""
        guardado = None
        if self.config_portable:
            guardado = self.config_portable.obtener("tema", None)
        if guardado in ("claro", "oscuro", "auto"):
            return guardado
        # Compatibilidad con las claves antiguas
        if guardado in ("minimal_claro",):
            return "claro"
        if guardado in ("minimal_oscuro",):
            return "oscuro"
        return "auto"

    def _tema_efectivo(self) -> str:
        """Tema realmente aplicado (resuelve 'auto' con el del sistema)."""
        if self._tema == "auto":
            return estilos.tema_del_sistema()
        return self._tema

    def _aplicar_tema(self):
        """Aplica la hoja de estilo tipo Apple según el tema actual."""
        tema_efectivo = self._tema_efectivo()
        Switch._tema = tema_efectivo
        self.setStyleSheet(estilos.hoja_estilo(tema_efectivo))
        # Repintar los interruptores dibujados a mano
        for interruptor in self.findChildren(Switch):
            interruptor.update()
        self._actualizar_indicadores_tema()

    def _actualizar_indicadores_tema(self):
        """Ajusta a mano lo que la hoja de estilo no puede expresar."""
        tema = self._tema_efectivo()
        try:
            self._lbl_estado_tema.setText("Automático (sistema)" if self._tema == "auto"
                                          else ("Claro" if self._tema == "claro" else "Oscuro"))
        except Exception:
            pass
        if tema == "oscuro":
            self._color_cabecera = "#1C1C1E"
        else:
            self._color_cabecera = "#FFFFFF"


    def _setup_system_tray(self):
        """Configura bandeja del sistema completa."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self._agregar_log("Bandeja del sistema no disponible en este sistema")
            return
        
        # Crear icono para la bandeja
        self.tray_icon = QSystemTrayIcon(self)
        
        # Crear icono personalizado si no existe uno
        icon = self._crear_icono_personalizado()
        self.tray_icon.setIcon(icon)
        
        # Crear menú contextual
        tray_menu = QMenu()
        
        # Acciones del menú
        mostrar_action = QAction("Mostrar ventana", self)
        mostrar_action.triggered.connect(self._mostrar_ventana)
        tray_menu.addAction(mostrar_action)
        
        organizar_action = QAction("Organizar ahora", self)
        organizar_action.triggered.connect(self._organizar)
        tray_menu.addAction(organizar_action)
        
        tray_menu.addSeparator()
        
        # Toggle auto-organización
        self.auto_action = QAction("Organización automática", self)
        self.auto_action.setCheckable(True)
        self.auto_action.triggered.connect(self._toggle_auto_organizacion)
        tray_menu.addAction(self.auto_action)
        
        tray_menu.addSeparator()
        
        # Información
        info_action = QAction(f"Carpeta: {os.path.basename(str(self.organizador.carpeta_descargas))}", self)
        info_action.setEnabled(False)
        tray_menu.addAction(info_action)
        
        tray_menu.addSeparator()
        
        salir_action = QAction("Salir", self)
        salir_action.triggered.connect(self._salir_completamente)
        tray_menu.addAction(salir_action)
        
        # Asignar menú al icono
        self.tray_icon.setContextMenu(tray_menu)
        
        # Conectar eventos
        self.tray_icon.activated.connect(self._tray_icon_activated)
        
        # Mostrar tooltip
        self.tray_icon.setToolTip("DescargasOrdenadas")
        
        # Mostrar icono
        self.tray_icon.show()
        
        self._agregar_log("Bandeja del sistema configurada")
    
    def _inicializar_modulos(self):
        """Inicializa módulos avanzados."""
        funciones = []
        carpeta = Path(self.organizador.carpeta_descargas)
        
        # IA
        try:
            from .ai_categorizer import CategorizadorIA
            self.ai_categorizer = CategorizadorIA(carpeta)
            funciones.append("IA")
            if hasattr(self, 'lbl_ia_estado'):
                self.lbl_ia_estado.setText("Categorización con IA activa")
        except Exception as e:
            self.ai_categorizer = None
            if hasattr(self, 'lbl_ia_estado'):
                self.lbl_ia_estado.setText("IA no disponible en este sistema")
            self._agregar_log(f"IA no disponible: {e}")
        
        # Fechas
        try:
            # Usar el organizador de fechas del organizador principal si está disponible
            if hasattr(self.organizador, 'organizador_fechas') and self.organizador.organizador_fechas:
                self.date_organizer = self.organizador.organizador_fechas
                logger.info("Usando organizador de fechas del organizador principal")
            else:
                # Fallback: crear instancia propia
                from .date_organizer import OrganizadorPorFecha
                self.date_organizer = OrganizadorPorFecha(carpeta)
                logger.info("Creando instancia propia del organizador de fechas")
                
            funciones.append("Fechas")
            
            # Verificar si fechas está activa
            try:
                if hasattr(self.date_organizer, 'activo') and self.date_organizer.activo:
                    if hasattr(self, 'lbl_estado_fechas'):
                        self.lbl_estado_fechas.setText("Organización por fechas activada")
                        if hasattr(self, 'btn_activar_fechas'):
                            self.btn_activar_fechas.setEnabled(False)
                        if hasattr(self, 'btn_desactivar_fechas'):
                            self.btn_desactivar_fechas.setEnabled(True)
            except Exception as e:
                logger.debug(f"Error verificando estado de fechas: {e}")
                
        except Exception as e:
            self.date_organizer = None
            self._agregar_log(f"Fechas no disponible: {e}")
        
        # Duplicados
        try:
            from .duplicate_detector import DetectorDuplicados
            self.duplicate_detector = DetectorDuplicados(carpeta)
            funciones.append("Duplicados")
        except Exception as e:
            self.duplicate_detector = None
            self._agregar_log(f"Duplicados no disponible: {e}")
        
        # Estadísticas
        try:
            from .statistics import EstadisticasOrganizador
            self.stats_manager = EstadisticasOrganizador(carpeta)
            funciones.append("Estadísticas")
        except Exception as e:
            self.stats_manager = None
            self._agregar_log(f"Estadísticas no disponible: {e}")
        
        # Reglas
        try:
            from .custom_rules import GestorReglasPersonalizadas
            self.custom_rules = GestorReglasPersonalizadas(carpeta)
            funciones.append("Reglas")
        except Exception as e:
            self.custom_rules = None
            self._agregar_log(f"Reglas personalizadas no disponible: {e}")
        
        # Informar de los módulos en el log y en la barra de estado
        # (la tarjeta principal se reserva para el estado de la auto-organización)
        if funciones:
            self._agregar_log("Módulos: " + " | ".join(funciones))
        else:
            self._agregar_log("Solo funcionalidades básicas disponibles")
        
        self._actualizar_datos()
    
    def _actualizar_datos(self):
        """Actualiza datos de las pestañas."""
        if hasattr(self, 'ai_categorizer') and self.ai_categorizer:
            self._actualizar_patrones()
        
        if hasattr(self, 'stats_manager') and self.stats_manager:
            self._actualizar_estadisticas()
    
    def _crear_icono_personalizado(self):
        """Icono de la bandeja: carpeta con flecha de ordenación.

        Se dibuja con QPainter cuidando siempre cerrarlo (try/finally): un
        QPainter sin cerrar al destruirse puede corromper la memoria y
        provocar un crash al arrancar.
        """
        try:
            from PySide6.QtCore import QPointF

            pixmap = QPixmap(256, 256)
            pixmap.fill(Qt.transparent)

            painter = QPainter()
            try:
                if not painter.begin(pixmap):
                    return self._icono_reserva()
                painter.setRenderHint(QPainter.Antialiasing)

                azul = QColor("#0A84FF")
                gris = QColor("#8E8E93")

                pluma_carpeta = QPen(gris, 256 * 0.075)
                pluma_carpeta.setCapStyle(Qt.RoundCap)
                pluma_carpeta.setJoinStyle(Qt.RoundJoin)
                painter.setPen(pluma_carpeta)
                painter.setBrush(Qt.NoBrush)

                margen = 256 * 0.16
                contorno_carpeta = [
                    QPointF(margen, 256 * 0.34),
                    QPointF(256 * 0.40, 256 * 0.34),
                    QPointF(256 * 0.46, 256 * 0.42),
                    QPointF(256 - margen, 256 * 0.42),
                    QPointF(256 - margen, 256 * 0.78),
                    QPointF(margen, 256 * 0.78),
                    QPointF(margen, 256 * 0.34),
                ]
                painter.drawPolyline(contorno_carpeta)

                pluma_flecha = QPen(azul, 256 * 0.075)
                pluma_flecha.setCapStyle(Qt.RoundCap)
                pluma_flecha.setJoinStyle(Qt.RoundJoin)
                painter.setPen(pluma_flecha)

                centro = 256 / 2
                painter.drawLine(QPointF(centro, 256 * 0.74), QPointF(centro, 256 * 0.30))
                painter.drawLine(QPointF(centro, 256 * 0.30), QPointF(centro - 256 * 0.12, 256 * 0.42))
                painter.drawLine(QPointF(centro, 256 * 0.30), QPointF(centro + 256 * 0.12, 256 * 0.42))
            finally:
                # Cerrar SIEMPRE el painter, incluso si algo falla a mitad
                if painter.isActive():
                    painter.end()

            if pixmap.isNull():
                return self._icono_reserva()
            return QIcon(pixmap)
        except Exception:
            return self._icono_reserva()

    def _icono_reserva(self):
        """Icono estándar de carpeta por si falla el dibujo."""
        try:
            from PySide6.QtWidgets import QStyle
            return self.style().standardIcon(QStyle.SP_DirIcon)
        except Exception:
            return QIcon()

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
        
        self._agregar_log("Ventana restaurada desde bandeja del sistema")
    
    def _ocultar_en_bandeja(self):
        """Oculta la ventana en la bandeja del sistema."""
        if self.tray_icon and self.tray_icon.isVisible():
            self._guardar_geometria_ventana()
            self.hide()
            self.en_bandeja = True
            
            # Ocultar consola
            self._ocultar_consola()
            
            # Mostrar notificación
            self.tray_icon.showMessage(
                "DescargasOrdenadas",
                "Aplicación minimizada a la bandeja del sistema",
                QSystemTrayIcon.Information,
                3000
            )
            
            self._agregar_log("Aplicación minimizada a bandeja del sistema")
        else:
            # Si no hay bandeja disponible, solo minimizar
            self.showMinimized()
    
    def _salir_completamente(self):
        """Cierra la aplicación completamente (desde menú o bandeja)."""
        self._agregar_log("Cerrando aplicación completamente...")
        self._cerrar_para_actualizar()

    def _cerrar_para_actualizar(self):
        """Cierre ordenado e inmediato, sin avisos ni diálogos que estorben.

        Sirve tanto para el botón Salir como para actualizar: el instalador
        necesita que no quede ningún archivo en uso, así que se cierra en orden
        y el script de actualización se encarga de reabrir al terminar.
        """
        try:
            self._guardar_geometria_ventana()
            self._cierre_programatico = True
            self.cerrar_completamente = True
            for temporizador in ("timer_auto", "timer_actualizaciones"):
                timer = getattr(self, temporizador, None)
                if timer is not None and timer.isActive():
                    timer.stop()
            if getattr(self, "tray_icon", None):
                self.tray_icon.hide()
            self._cerrar_consola()
            QApplication.quit()
        except Exception as e:
            logger.debug(f"Error durante el cierre: {e}")
        try:
            sys.exit(0)
        except SystemExit:
            raise
        except Exception:
            os._exit(0)

    def _toggle_auto_principal(self, activo):
        """Interruptor general de la organización automática."""
        if getattr(self, "_sincronizando_controles", False):
            return
        if activo:
            # Activar con el modo guardado (o Básico por defecto)
            modo = getattr(self, "_auto_modo_guardado", "basico")
            if modo == "detallado" and hasattr(self, "chk_auto_detallado"):
                self.chk_auto_detallado.setChecked(True)
            elif hasattr(self, "chk_auto_basico"):
                self.chk_auto_basico.setChecked(True)
        else:
            # Apagar: detiene el timer y limpia la preferencia
            if hasattr(self, "timer_auto") and self.timer_auto:
                self.timer_auto.stop()
            if hasattr(self, "chk_auto_basico") and self.chk_auto_basico.isChecked():
                self.chk_auto_basico.blockSignals(True)
                self.chk_auto_basico.setChecked(False)
                self.chk_auto_basico.blockSignals(False)
            if hasattr(self, "chk_auto_detallado") and self.chk_auto_detallado.isChecked():
                self.chk_auto_detallado.blockSignals(True)
                self.chk_auto_detallado.setChecked(False)
                self.chk_auto_detallado.blockSignals(False)
            self._agregar_log("Auto-organización DESACTIVADA")
            self._olvidar_preferencia_auto()
            self._actualizar_estado_auto_organizacion()

    def _toggle_auto_organizacion(self, activo):
        """Activa/desactiva la organización automática (compatibilidad)."""
        if hasattr(self, "chk_auto_principal"):
            self.chk_auto_principal.setChecked(activo)
    
    @Slot(bool)
    def _toggle_auto_organizacion_basico(self, activo):
        """Toggle auto-organización básica cada 30 segundos."""
        try:
            if activo:
                # Desactivar el modo detallado si estaba activo (sin propagar)
                if hasattr(self, 'chk_auto_detallado') and self.chk_auto_detallado.isChecked():
                    self.chk_auto_detallado.blockSignals(True)
                    self.chk_auto_detallado.setChecked(False)
                    self.chk_auto_detallado.blockSignals(False)
                
                if not hasattr(self, 'timer_auto') or self.timer_auto is None:
                    self.timer_auto = QTimer()
                    self.timer_auto.timeout.connect(self._organizar_automatico)
                
                # Obtener intervalo del selector
                intervalo_segundos = self.combo_intervalo_auto.currentData()
                intervalo_ms = intervalo_segundos * 1000
                intervalo_texto = self.combo_intervalo_auto.currentText()
                self.timer_auto.start(intervalo_ms)
                self._agregar_log(f"Auto-organización BÁSICA ACTIVADA ({intervalo_texto})")
                self._sincronizar_switch_principal(True)
                
                # Actualizar tooltip de la bandeja
                if getattr(self, 'tray_icon', None):
                    self.tray_icon.setToolTip(f"Auto-organización BÁSICA ({intervalo_texto})")
                    
                # Actualizar estado visual
                self._pintar_estado(True, "Básico")

                # Recordar la elección para el próximo arranque
                self._guardar_preferencia_auto()
            else:
                if hasattr(self, 'timer_auto') and self.timer_auto:
                    self.timer_auto.stop()
                
                self._agregar_log("Auto-organización BÁSICA DESACTIVADA")
                self._olvidar_preferencia_auto()
                self._sincronizar_switch_principal(False)
                self._actualizar_estado_auto_organizacion()
                
        except Exception as e:
            self._agregar_log(f"Error configurando auto-organización básica: {e}")
            QMessageBox.critical(self, "Error", f"Error: {e}")

    @Slot(bool)
    def _toggle_auto_organizacion_detallado(self, activo):
        """Toggle auto-organización detallada cada 30 segundos."""
        try:
            if activo:
                # Desactivar el modo básico si estaba activo (sin propagar)
                if hasattr(self, 'chk_auto_basico') and self.chk_auto_basico.isChecked():
                    self.chk_auto_basico.blockSignals(True)
                    self.chk_auto_basico.setChecked(False)
                    self.chk_auto_basico.blockSignals(False)
                
                if not hasattr(self, 'timer_auto') or self.timer_auto is None:
                    self.timer_auto = QTimer()
                    self.timer_auto.timeout.connect(self._organizar_automatico)
                
                # Obtener intervalo del selector
                intervalo_segundos = self.combo_intervalo_auto.currentData()
                intervalo_ms = intervalo_segundos * 1000
                intervalo_texto = self.combo_intervalo_auto.currentText()
                self.timer_auto.start(intervalo_ms)
                self._agregar_log(f"Auto-organización DETALLADA ACTIVADA ({intervalo_texto})")
                self._sincronizar_switch_principal(True)
                
                # Actualizar tooltip de la bandeja
                if getattr(self, 'tray_icon', None):
                    self.tray_icon.setToolTip(f"Auto-organización DETALLADA ({intervalo_texto})")
                    
                # Actualizar estado visual
                self._pintar_estado(True, "Detallado")

                # Recordar la elección para el próximo arranque
                self._guardar_preferencia_auto()
            else:
                if hasattr(self, 'timer_auto') and self.timer_auto:
                    self.timer_auto.stop()
                
                self._agregar_log("Auto-organización DETALLADA DESACTIVADA")
                self._olvidar_preferencia_auto()
                self._sincronizar_switch_principal(False)
                self._actualizar_estado_auto_organizacion()
                
        except Exception as e:
            self._agregar_log(f"Error configurando auto-organización detallada: {e}")
            QMessageBox.critical(self, "Error", f"Error: {e}")
    
    def _sincronizar_switch_principal(self, activo):
        """Mantiene el interruptor general coherente con los modos."""
        if getattr(self, "_sincronizando_controles", False):
            return
        if hasattr(self, "chk_auto_principal"):
            self.chk_auto_principal.blockSignals(True)
            self.chk_auto_principal.setChecked(activo)
            self.chk_auto_principal.blockSignals(False)

    def _actualizar_estado_auto_organizacion(self):
        """Actualiza la tarjeta de estado según los controles actuales."""
        modo = None
        if hasattr(self, 'chk_auto_detallado') and self.chk_auto_detallado.isChecked():
            modo = "Detallado"
        elif hasattr(self, 'chk_auto_basico') and self.chk_auto_basico.isChecked():
            modo = "Básico"

        timer = getattr(self, 'timer_auto', None)
        activo = bool(modo) and timer is not None and timer.isActive()
        self._pintar_estado(activo, modo)

        if not activo:
            if getattr(self, 'tray_icon', None):
                self.tray_icon.setToolTip("Organización automática inactiva")

    def _pintar_estado(self, activo, modo=None):
        """Actualiza la tarjeta superior de estado (Inicio)."""
        try:
            intervalo = self.combo_intervalo_auto.currentText() if hasattr(self, "combo_intervalo_auto") else ""
            if activo:
                self._punto_estado.setProperty("rol", "exito")
                self.lbl_estado.setText(f"Auto-organización activa · modo {modo or 'Básico'}")
                self.lbl_estado_detalle.setText(f"Revisando la carpeta cada {intervalo.lower()}")
                if getattr(self, 'tray_icon', None):
                    self.tray_icon.setToolTip(f"Auto-organización {modo or 'Básico'} ({intervalo})")
            else:
                self._punto_estado.setProperty("rol", "discreta")
                self.lbl_estado.setText("Auto-organización desactivada")
                self.lbl_estado_detalle.setText("Actívala para que la carpeta se ordene sola")
            # Refrescar el color del punto según la nueva propiedad
            self._punto_estado.setStyleSheet("")
            self._punto_estado.style().unpolish(self._punto_estado)
            self._punto_estado.style().polish(self._punto_estado)
        except Exception as e:
            logger.debug(f"No se pudo actualizar la tarjeta de estado: {e}")

    def _deshacer_organizacion(self):
        """Deshace toda la organización moviendo archivos de vuelta a la raíz."""
        reply = QMessageBox.question(
            self, "Deshacer Organización",
            "ADVERTENCIA: Esto moverá TODOS los archivos de las carpetas organizadas de vuelta a la raíz de Descargas.\n\n"
            "Esto te permitirá cambiar el tipo de organización limpiamente.\n\n"
            "¿Estás seguro de que quieres continuar?",
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
                                    self._agregar_log(f"{item.name} → raíz")
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
                                        self._agregar_log(f"Carpeta vacía eliminada: {item.name}")
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
                                self._agregar_log(f"Carpeta principal eliminada: {carpeta.name}")
                        except OSError:
                            pass
                
                # Limpiar huella de archivos organizados
                if hasattr(self.organizador, 'archivos_procesados'):
                    self.organizador.archivos_procesados.clear()
                    self.organizador._guardar_huella()
                
                mensaje = f"Organización deshecha!\n\n"
                mensaje += f"{archivos_movidos} archivos movidos a la raíz"
                if errores:
                    mensaje += f"\n{len(errores)} avisos (consulta la pestaña Actividad)"
                
                QMessageBox.information(self, "Operación Completada", mensaje)
                self._actualizar_datos()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al deshacer la organización: {e}")
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
                self._agregar_log(f"Auto-organización{modo_texto} {hora_actual}: {total} archivos organizados")
                
                # Notificación nativa
                if self.notificador and hasattr(self, '_debug_timer_count') and self._debug_timer_count % 10 == 0:
                    categorias = set(resultados.keys())
                    self.notificador.notificar_organizacion(total, categorias)
                
                # Actualizar tooltip de la bandeja para mostrar última actividad
                if getattr(self, 'tray_icon', None):
                    self.tray_icon.setToolTip(f"Última organización: {hora_actual} ({total} archivos)")
                    
                # Actualizar estadísticas si hay cambios
                self._actualizar_datos()
            else:
                # Log cada 5 ejecuciones para confirmar que funciona
                if self._debug_timer_count % 5 == 0:
                    self._agregar_log(f"Timer activo{modo_texto} {hora_actual}: revisando archivos... (#{self._debug_timer_count})")
                
                # Actualizar tooltip para mostrar que está funcionando
                if getattr(self, 'tray_icon', None):
                    self.tray_icon.setToolTip(f"Revisando: {hora_actual}")
                
        except Exception as e:
            self._agregar_log(f"Error en auto-organización: {e}")
    
    def _ocultar_consola(self):
        """Oculta la consola de Windows de forma optimizada."""
        if sys.platform != "win32":
            self._agregar_log("ℹ️  Ocultar consola no disponible en este sistema operativo")
            return False
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            user32 = ctypes.windll.user32

            console_window = kernel32.GetConsoleWindow()
            if not console_window:
                return False

            # SW_HIDE = 0, oculta completamente la ventana
            user32.ShowWindow(console_window, 0)

            # Minimizar el impacto en la barra de tareas
            GWL_EXSTYLE = -20
            WS_EX_TOOLWINDOW = 0x00000080

            try:
                current_style = user32.GetWindowLongW(console_window, GWL_EXSTYLE)
                user32.SetWindowLongW(console_window, GWL_EXSTYLE, current_style | WS_EX_TOOLWINDOW)
            except Exception:
                pass

            self._agregar_log("Consola externa ocultada completamente")
            return True
        except Exception as e:
            self._agregar_log(f"Error ocultando consola: {e}")
        return False

    def _mostrar_consola(self):
        """Muestra la consola de Windows."""
        if sys.platform != "win32":
            self._agregar_log("ℹ️  Mostrar consola no disponible en este sistema operativo")
            return False
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            user32 = ctypes.windll.user32

            console_window = kernel32.GetConsoleWindow()
            if not console_window:
                return False

            user32.ShowWindow(console_window, 5)  # SW_SHOW
            self._agregar_log("Consola externa mostrada")
            return True
        except Exception as e:
            self._agregar_log(f"Error mostrando consola: {e}")
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
        self._guardar_geometria_ventana()
        if self.cerrar_completamente:
            # Cierre definitivo
            if hasattr(self, 'tray_icon'):
                self.tray_icon.hide()
            # Cerrar consola al salir completamente
            self._cerrar_consola()
            event.accept()
        else:
            # Minimizar a bandeja en lugar de cerrar. En un cierre programático
            # (por ejemplo, al salir la aplicación entera) se acepta siempre.
            if getattr(self, "_cierre_programatico", False):
                if hasattr(self, 'tray_icon'):
                    self.tray_icon.hide()
                self._cerrar_consola()
                event.accept()
                return
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
        """Configura la interfaz principal con barra lateral estilo macOS."""
        central = QWidget()
        self.setCentralWidget(central)
        raiz = QHBoxLayout(central)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)

        # ----------------------------------------------------- barra lateral
        lateral = QWidget()
        lateral.setFixedWidth(212)
        lateral_layout = QVBoxLayout(lateral)
        lateral_layout.setContentsMargins(0, 0, 0, 0)
        lateral_layout.setSpacing(0)

        self.lista_lateral = QListWidget()
        self.lista_lateral.setProperty("rol", "lateral")
        self.lista_lateral.setFrameShape(QFrame.NoFrame)
        self.lista_lateral.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.lista_lateral.setIconSize(QSize(17, 17))
        self.lista_lateral.currentRowChanged.connect(self._cambiar_vista)
        lateral_layout.addWidget(self.lista_lateral, 1)

        # Estado del tema y versión, discretos al pie
        self._lbl_estado_tema = QLabel("")
        self._lbl_estado_tema.setProperty("rol", "discreta")
        self._lbl_estado_tema.setContentsMargins(18, 4, 18, 0)
        lateral_layout.addWidget(self._lbl_estado_tema)

        lbl_version = QLabel(f"v{obtener_version()}")
        lbl_version.setProperty("rol", "discreta")
        lbl_version.setContentsMargins(18, 0, 18, 14)
        lateral_layout.addWidget(lbl_version)

        raiz.addWidget(lateral)

        # ------------------------------------------------------------ stack
        contenido = QWidget()
        contenido_layout = QVBoxLayout(contenido)
        contenido_layout.setContentsMargins(24, 20, 24, 14)
        contenido_layout.setSpacing(14)

        # Cabecera: título + carpeta + acción principal
        cabecera = QHBoxLayout()
        cabecera.setSpacing(12)

        textos = QVBoxLayout()
        textos.setSpacing(2)
        self.lbl_titulo_vista = QLabel("Inicio")
        self.lbl_titulo_vista.setProperty("rol", "titulo")
        textos.addWidget(self.lbl_titulo_vista)

        self.lbl_carpeta_cabecera = QLabel(str(self.organizador.carpeta_descargas))
        self.lbl_carpeta_cabecera.setProperty("rol", "secundaria")
        self.lbl_carpeta_cabecera.setTextInteractionFlags(Qt.TextSelectableByMouse)
        textos.addWidget(self.lbl_carpeta_cabecera)

        cabecera.addLayout(textos, 1)

        self.btn_cabecera_principal = QPushButton("Cambiar carpeta")
        self.btn_cabecera_principal.setProperty("rol", "primario")
        self.btn_cabecera_principal.clicked.connect(self._seleccionar_carpeta)
        cabecera.addWidget(self.btn_cabecera_principal, 0, Qt.AlignVCenter)

        contenido_layout.addLayout(cabecera)

        self.stack = QStackedWidget()
        contenido_layout.addWidget(self.stack, 1)

        # Barra de progreso (indeterminada)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        contenido_layout.addWidget(self.progress_bar)

        raiz.addWidget(contenido, 1)

        self.statusBar().showMessage("Listo")

        # Vistas: se crean igual que antes pero dentro del stack
        self._vistas = []
        self._crear_vista_inicio()
        self._crear_vista_actividad()
        self._crear_vista_ajustes()
        self._crear_vista_avanzado()

        # Elementos de la barra lateral (icono del sistema + nombre)
        from PySide6.QtWidgets import QStyle
        entradas = [
            ("Inicio", QStyle.SP_ComputerIcon),
            ("Actividad", QStyle.SP_FileDialogDetailedView),
            ("Ajustes", QStyle.SP_FileDialogContentsView),
            ("Avanzado", QStyle.SP_FileDialogListView),
        ]
        for texto, icono_estandar in entradas:
            item = QListWidgetItem(self.style().standardIcon(icono_estandar), texto)
            self.lista_lateral.addItem(item)

        self.lista_lateral.setCurrentRow(0)

    def _cambiar_vista(self, indice):
        """Cambia la vista activa con una transición suave."""
        if indice < 0:
            return
        self.stack.setCurrentIndex(indice)
        self._vista_actual = indice
        titulos = ["Inicio", "Actividad", "Ajustes", "Avanzado"]
        if indice < len(titulos):
            self.lbl_titulo_vista.setText(titulos[indice])
        # El botón de cabecera solo tiene sentido en Inicio/Ajustes
        self.btn_cabecera_principal.setVisible(indice in (0, 2))
        self._animar_vista()

    def _animar_vista(self):
        """Fundido corto al cambiar de sección."""
        try:
            actual = self.stack.currentWidget()
            if actual is None:
                return
            # Si había una animación en curso, termínala limpiamente
            anterior = getattr(self, "_animacion_vista", None)
            if anterior is not None:
                try:
                    anterior.stop()
                except Exception:
                    pass
                anterior_widget = getattr(self, "_widget_animado", None)
                if anterior_widget is not None:
                    try:
                        anterior_widget.setGraphicsEffect(None)
                    except Exception:
                        pass

            efecto = QGraphicsOpacityEffect(actual)
            actual.setGraphicsEffect(efecto)
            animacion = QPropertyAnimation(efecto, b"opacity", self)
            animacion.setDuration(150)
            animacion.setStartValue(0.4)
            animacion.setEndValue(1.0)
            animacion.setEasingCurve(QEasingCurve.OutCubic)
            # Guardar referencias fuertes: si no, el recolector se lleva la
            # animación y el efecto se queda a medio aplicar (widget pálido).
            self._animacion_vista = animacion
            self._widget_animado = actual
            animacion.finished.connect(lambda w=actual: self._terminar_animacion(w))
            animacion.start()
        except Exception as e:
            logger.debug(f"No se pudo animar el cambio de vista: {e}")
            try:
                self.stack.currentWidget().setGraphicsEffect(None)
            except Exception:
                pass

    def _terminar_animacion(self, widget):
        """Deja el widget totalmente opaco al acabar el fundido."""
        try:
            widget.setGraphicsEffect(None)
            widget.update()
        except Exception:
            pass
        if getattr(self, "_widget_animado", None) is widget:
            self._widget_animado = None

    def _crear_vista_inicio(self):
        """Pantalla de inicio: estado, automático y acciones manuales."""
        vista = QWidget()
        layout = QVBoxLayout(vista)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # ---- Tarjeta de estado -----------------------------------------
        tarjeta_estado = Tarjeta()
        estado_layout = QHBoxLayout(tarjeta_estado)
        estado_layout.setContentsMargins(18, 16, 18, 16)
        estado_layout.setSpacing(14)

        punto = QLabel("●")
        punto.setProperty("rol", "acento")
        self._punto_estado = punto
        estado_layout.addWidget(punto)

        col = QVBoxLayout()
        col.setSpacing(2)
        self.lbl_estado = QLabel("Auto-organización desactivada")
        self.lbl_estado.setProperty("rol", "titulo")
        col.addWidget(self.lbl_estado)
        self.lbl_estado_detalle = QLabel("Actívala para que la carpeta se ordene sola")
        self.lbl_estado_detalle.setProperty("rol", "secundaria")
        col.addWidget(self.lbl_estado_detalle)
        estado_layout.addLayout(col, 1)
        layout.addWidget(tarjeta_estado)

        # ---- Tarjeta Automático ----------------------------------------
        auto_grupo = QGroupBox("Automático")
        auto_layout = QVBoxLayout(auto_grupo)
        auto_layout.setSpacing(14)

        fila_switch = QHBoxLayout()
        self.chk_auto_principal = Switch("Organización automática")
        self.chk_auto_principal.setToolTip("Organiza la carpeta sola, cada cierto tiempo")
        self.chk_auto_principal.toggled.connect(self._toggle_auto_principal)
        fila_switch.addWidget(self.chk_auto_principal)
        fila_switch.addStretch()
        auto_layout.addLayout(fila_switch)

        separador1 = Separador()
        auto_layout.addWidget(separador1)

        modo_layout = QHBoxLayout()
        lbl_modo = QLabel("Modo")
        lbl_modo.setProperty("rol", "etiqueta")
        modo_layout.addWidget(lbl_modo)
        modo_layout.addStretch()
        self.chk_auto_basico = QRadioButton("Básico")
        self.chk_auto_basico.setToolTip("Carpetas generales:\nDocumentos, Imágenes, Vídeos, Música, Comprimidos")
        self.chk_auto_basico.toggled.connect(self._toggle_auto_organizacion_basico)
        modo_layout.addWidget(self.chk_auto_basico)
        self.chk_auto_detallado = QRadioButton("Detallado")
        self.chk_auto_detallado.setToolTip("Subcarpetas por tipo:\nExcel → Hojas de cálculo/Excel, PNG → Imágenes/PNG")
        self.chk_auto_detallado.toggled.connect(self._toggle_auto_organizacion_detallado)
        modo_layout.addWidget(self.chk_auto_detallado)
        auto_layout.addLayout(modo_layout)

        tiempo_layout = QHBoxLayout()
        lbl_tiempo = QLabel("Revisar cada")
        lbl_tiempo.setProperty("rol", "etiqueta")
        tiempo_layout.addWidget(lbl_tiempo)
        tiempo_layout.addStretch()
        self.combo_intervalo_auto = QComboBox()
        for texto, seg in [
            ("30 segundos", 30), ("1 minuto", 60), ("5 minutos", 300),
            ("10 minutos", 600), ("30 minutos", 1800), ("1 hora", 3600),
            ("6 horas", 21600), ("12 horas", 43200), ("1 día", 86400),
        ]:
            self.combo_intervalo_auto.addItem(texto, seg)
        self.combo_intervalo_auto.setCurrentIndex(5)  # 1 hora por defecto
        self.combo_intervalo_auto.currentIndexChanged.connect(self._cambiar_intervalo_auto)
        tiempo_layout.addWidget(self.combo_intervalo_auto)
        auto_layout.addLayout(tiempo_layout)

        arranque_layout = QHBoxLayout()
        nombre_so = "Windows" if sys.platform == "win32" else ("macOS" if sys.platform == "darwin" else "Linux")
        self.chk_autoarranque = Switch(f"Iniciar al arrancar {nombre_so}")
        self.chk_autoarranque.blockSignals(True)
        self.chk_autoarranque.setChecked(self.gestor_autoarranque.verificar_autoarranque())
        self.chk_autoarranque.blockSignals(False)
        self.chk_autoarranque.setToolTip("La app se abre minimizada cuando enciendas el equipo")
        self.chk_autoarranque.toggled.connect(self._toggle_autoarranque)
        arranque_layout.addWidget(self.chk_autoarranque)
        arranque_layout.addStretch()
        auto_layout.addLayout(arranque_layout)

        layout.addWidget(auto_grupo)

        # ---- Tarjeta Manual --------------------------------------------
        acciones_grupo = QGroupBox("Ahora mismo")
        acciones_layout = QVBoxLayout(acciones_grupo)
        acciones_layout.setSpacing(10)

        fila_acciones = QHBoxLayout()
        fila_acciones.setSpacing(10)

        self.btn_organizar = QPushButton("Organizar ahora")
        self.btn_organizar.setProperty("rol", "primario")
        self.btn_organizar.clicked.connect(self._reorganizar)
        fila_acciones.addWidget(self.btn_organizar, 2)

        btn_deshacer = QPushButton("Deshacer")
        btn_deshacer.setProperty("rol", "peligro")
        btn_deshacer.setToolTip("Devuelve los archivos organizados a la raíz de la carpeta")
        btn_deshacer.clicked.connect(self._deshacer_organizacion)
        fila_acciones.addWidget(btn_deshacer, 1)

        acciones_layout.addLayout(fila_acciones)
        layout.addWidget(acciones_grupo)

        layout.addStretch()
        self._vistas.append(vista)
        self.stack.addWidget(self._contenedor_scroll(vista))

    def _crear_vista_ia(self, destino):
        """Vista de IA (dentro de Avanzado)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)

        ia_grupo = QGroupBox("Categorización con IA")
        ia_layout = QVBoxLayout(ia_grupo)
        ia_layout.setSpacing(12)

        self.lbl_ia_estado = QLabel("Verificando IA…")
        self.lbl_ia_estado.setProperty("rol", "secundaria")
        ia_layout.addWidget(self.lbl_ia_estado)

        confianza_layout = QHBoxLayout()
        lbl_conf = QLabel("Confianza")
        lbl_conf.setProperty("rol", "etiqueta")
        confianza_layout.addWidget(lbl_conf)
        self.slider_confianza = QSlider(Qt.Horizontal)
        self.slider_confianza.setRange(30, 95)
        self.slider_confianza.setValue(60)
        self.slider_confianza.valueChanged.connect(self._actualizar_confianza)
        confianza_layout.addWidget(self.slider_confianza, 1)
        self.lbl_confianza = QLabel("60 %")
        self.lbl_confianza.setProperty("rol", "secundaria")
        confianza_layout.addWidget(self.lbl_confianza)
        ia_layout.addLayout(confianza_layout)

        botones_ia = QHBoxLayout()
        btn_entrenar = QPushButton("Entrenar")
        btn_entrenar.clicked.connect(self._entrenar_ia)
        botones_ia.addWidget(btn_entrenar)
        btn_reset = QPushButton("Reiniciar modelo")
        btn_reset.setProperty("rol", "peligro")
        btn_reset.clicked.connect(self._reset_ia)
        botones_ia.addWidget(btn_reset)
        botones_ia.addStretch()
        ia_layout.addLayout(botones_ia)
        layout.addWidget(ia_grupo)

        self.text_patrones = QTextEdit()
        self.text_patrones.setReadOnly(True)
        self.text_patrones.setPlaceholderText("Los patrones aprendidos aparecerán aquí…")
        layout.addWidget(self.text_patrones, 1)

        contenedor = self._contenedor_scroll(tab)
        self.tabs_avanzado.addTab(contenedor, "IA")

    def _crear_vista_fechas(self, destino):
        """Vista de organización por fechas (dentro de Avanzado)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)

        self.lbl_estado_fechas = QLabel("Organización por fechas desactivada")
        self.lbl_estado_fechas.setProperty("rol", "titulo")
        layout.addWidget(self.lbl_estado_fechas)

        patron_group = QGroupBox("Patrón")
        patron_layout = QVBoxLayout(patron_group)
        patron_layout.setSpacing(8)

        self.combo_patron = QComboBox()
        patrones = [
            ("YYYY/MM-Mes", "2024/12-Diciembre (Año/Mes con nombre)"),
            ("YYYY/MM", "2024/12 (Año/Mes numérico)"),
            ("YYYY", "2024 (Solo año)"),
            ("MM-YYYY", "12-2024 (Mes-Año)"),
            ("Mes-YYYY", "Diciembre-2024 (Nombre mes-Año)"),
        ]
        for patron, descripcion in patrones:
            self.combo_patron.addItem(f"{patron} — {descripcion}", patron)
        self.combo_patron.currentTextChanged.connect(self._actualizar_ejemplo_fecha)
        patron_layout.addWidget(self.combo_patron)

        self.lbl_ejemplo = QLabel("")
        self.lbl_ejemplo.setProperty("rol", "secundaria")
        self.lbl_ejemplo.setWordWrap(True)
        patron_layout.addWidget(self.lbl_ejemplo)
        layout.addWidget(patron_group)

        acciones_group = QGroupBox("Acciones")
        acciones_layout = QHBoxLayout(acciones_group)
        self.btn_activar_fechas = QPushButton("Activar")
        self.btn_activar_fechas.setProperty("rol", "primario")
        self.btn_activar_fechas.clicked.connect(self._activar_fechas)
        acciones_layout.addWidget(self.btn_activar_fechas)
        self.btn_desactivar_fechas = QPushButton("Desactivar")
        self.btn_desactivar_fechas.clicked.connect(self._desactivar_fechas)
        self.btn_desactivar_fechas.setEnabled(False)
        acciones_layout.addWidget(self.btn_desactivar_fechas)
        btn_revertir = QPushButton("Revertir")
        btn_revertir.setProperty("rol", "peligro")
        btn_revertir.clicked.connect(self._revertir_fechas)
        acciones_layout.addWidget(btn_revertir)
        acciones_layout.addStretch()
        layout.addWidget(acciones_group)

        btn_previsualizar = QPushButton("Previsualizar cómo quedaría")
        btn_previsualizar.clicked.connect(self._previsualizar_organizacion_fechas)
        layout.addWidget(btn_previsualizar)

        layout.addStretch()
        self._actualizar_ejemplo_fecha()
        contenedor = self._contenedor_scroll(tab)
        self.tabs_avanzado.addTab(contenedor, "Fechas")

    def _crear_vista_duplicados(self, destino):
        """Vista de duplicados (dentro de Avanzado)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)

        botones = QHBoxLayout()
        btn_buscar = QPushButton("Buscar duplicados")
        btn_buscar.setProperty("rol", "primario")
        btn_buscar.clicked.connect(self._buscar_duplicados)
        botones.addWidget(btn_buscar)
        btn_eliminar = QPushButton("Eliminar duplicados")
        btn_eliminar.setProperty("rol", "peligro")
        btn_eliminar.clicked.connect(self._eliminar_duplicados)
        botones.addWidget(btn_eliminar)
        botones.addStretch()
        layout.addLayout(botones)

        self.text_duplicados = QPlainTextEdit()
        self.text_duplicados.setPlaceholderText("Los duplicados aparecerán aquí…")
        layout.addWidget(self.text_duplicados, 1)

        contenedor = self._contenedor_scroll(tab)
        self.tabs_avanzado.addTab(contenedor, "Duplicados")

    def _crear_vista_estadisticas(self, destino):
        """Vista de estadísticas (dentro de Avanzado)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)

        fila = QHBoxLayout()
        btn_actualizar = QPushButton("Actualizar")
        btn_actualizar.clicked.connect(self._actualizar_estadisticas)
        fila.addWidget(btn_actualizar)
        fila.addStretch()
        layout.addLayout(fila)

        self.text_stats = QPlainTextEdit()
        self.text_stats.setReadOnly(True)
        layout.addWidget(self.text_stats, 1)

        contenedor = self._contenedor_scroll(tab)
        self.tabs_avanzado.addTab(contenedor, "Estadísticas")

    def _contenedor_scroll(self, contenido: QWidget) -> QScrollArea:
        """Envuelve un widget en un área desplazable sin marco."""
        scroll = QScrollArea()
        scroll.setWidget(contenido)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setFrameShape(QScrollArea.NoFrame)
        return scroll

    def _crear_vista_actividad(self):
        """Vista de actividad: registros de lo que hace la app."""
        vista = QWidget()
        layout = QVBoxLayout(vista)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        fila_logs = QHBoxLayout()
        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.clicked.connect(self._limpiar_logs)
        fila_logs.addWidget(btn_limpiar)
        btn_exportar = QPushButton("Exportar…")
        btn_exportar.clicked.connect(self._exportar_logs)
        fila_logs.addWidget(btn_exportar)
        fila_logs.addStretch()

        if sys.platform == "win32":
            self.chk_mostrar_consola = QCheckBox("Mostrar consola externa")
            self.chk_mostrar_consola.setChecked(False)
            self.chk_mostrar_consola.toggled.connect(self._toggle_consola_externa)
            fila_logs.addWidget(self.chk_mostrar_consola)

        layout.addLayout(fila_logs)

        self.list_archivos = QListWidget()
        self.list_archivos.setMaximumHeight(110)
        layout.addWidget(self.list_archivos)

        self.text_logs = QPlainTextEdit()
        self.text_logs.setReadOnly(True)
        self.text_logs.setPlainText("DescargasOrdenadas\n" + "-" * 40 + "\n")
        layout.addWidget(self.text_logs, 1)

        self._vistas.append(vista)
        self.stack.addWidget(self._contenedor_scroll(vista))
        self._setup_log_capture()

    def _crear_vista_ajustes(self):
        """Vista de ajustes de la aplicación."""
        vista = QWidget()
        layout = QVBoxLayout(vista)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # --- Carpeta de trabajo --------------------------------------------
        carpeta_group = QGroupBox("Carpeta a organizar")
        carpeta_layout = QHBoxLayout(carpeta_group)
        self.lbl_carpeta_actual = QLabel(str(self.organizador.carpeta_descargas))
        self.lbl_carpeta_actual.setTextInteractionFlags(Qt.TextSelectableByMouse)
        carpeta_layout.addWidget(self.lbl_carpeta_actual, 1)
        btn_seleccionar_carpeta = QPushButton("Cambiar…")
        btn_seleccionar_carpeta.clicked.connect(self._seleccionar_carpeta)
        carpeta_layout.addWidget(btn_seleccionar_carpeta)
        btn_reset_carpeta = QPushButton("Restablecer")
        btn_reset_carpeta.setToolTip("Volver a la carpeta de descargas predeterminada")
        btn_reset_carpeta.clicked.connect(self._reset_carpeta_descargas)
        carpeta_layout.addWidget(btn_reset_carpeta)
        layout.addWidget(carpeta_group)

        # --- Integración con el sistema ------------------------------------
        sistema_group = QGroupBox("Integración con el sistema")
        sistema_layout = QVBoxLayout(sistema_group)
        sistema_layout.setSpacing(10)

        nombre_so = "Windows" if sys.platform == "win32" else ("macOS" if sys.platform == "darwin" else "Linux")
        if MENU_CONTEXTUAL_DISPONIBLE:
            self.chk_menu_contextual = Switch(f"Menú contextual ({nombre_so})")
            self.chk_menu_contextual.setChecked(self.gestor_menu_contextual.verificar_registro())
            if nombre_so == "macOS":
                self.chk_menu_contextual.setToolTip("Clic derecho en Finder → Acciones rápidas → Organizar con DescargasOrdenadas")
            elif nombre_so == "Linux":
                self.chk_menu_contextual.setToolTip("Clic derecho → Abrir con…, y en los scripts del explorador (Nautilus)")
            else:
                self.chk_menu_contextual.setToolTip("Clic derecho sobre una carpeta → Organizar con DescargasOrdenadas")
            self.chk_menu_contextual.toggled.connect(self._toggle_menu_contextual)
            sistema_layout.addWidget(self.chk_menu_contextual)

            self.lbl_menu_contextual_info = QLabel(
                "Al usarlo, la carpeta se organiza en segundo plano sin abrir la ventana."
            )
            self.lbl_menu_contextual_info.setProperty("rol", "secundaria")
            self.lbl_menu_contextual_info.setWordWrap(True)
            sistema_layout.addWidget(self.lbl_menu_contextual_info)

        layout.addWidget(sistema_group)

        # --- Organización --------------------------------------------------
        organizacion_group = QGroupBox("Organización")
        organizacion_layout = QVBoxLayout(organizacion_group)
        organizacion_layout.setSpacing(10)

        self.chk_subcarpetas = Switch("Usar subcarpetas detalladas")
        self.chk_subcarpetas.setChecked(False)
        self.chk_subcarpetas.setToolTip(
            "Sin marcar: organización BÁSICA (Comprimidos, Imágenes, Vídeos…)\n"
            "Marcado: organización DETALLADA (Comprimidos/Zip, Imágenes/PNG…)"
        )
        self.chk_subcarpetas.toggled.connect(self._toggle_subcarpetas)
        organizacion_layout.addWidget(self.chk_subcarpetas)

        self.chk_recursivo = Switch("Buscar también en subcarpetas")
        organizacion_layout.addWidget(self.chk_recursivo)

        if NOTIFICACIONES_NATIVAS:
            self.chk_notificaciones = Switch("Notificaciones del sistema")
            self.chk_notificaciones.setChecked(True)
            self.chk_notificaciones.setToolTip("Notifica cuando se organizan archivos")
            self.chk_notificaciones.toggled.connect(self._toggle_notificaciones)
            organizacion_layout.addWidget(self.chk_notificaciones)
        layout.addWidget(organizacion_group)

        # --- Apariencia ----------------------------------------------------
        apariencia_group = QGroupBox("Apariencia")
        apariencia_layout = QHBoxLayout(apariencia_group)
        lbl_tema = QLabel("Tema")
        lbl_tema.setProperty("rol", "etiqueta")
        apariencia_layout.addWidget(lbl_tema)
        apariencia_layout.addStretch()

        self.combo_temas = QComboBox()
        for clave, display in [("auto", "Automático (sistema)"), ("claro", "Claro"), ("oscuro", "Oscuro")]:
            self.combo_temas.addItem(display, clave)
        for i in range(self.combo_temas.count()):
            if self.combo_temas.itemData(i) == self._tema:
                self.combo_temas.setCurrentIndex(i)
                break
        self.combo_temas.currentIndexChanged.connect(self._cambiar_tema)
        apariencia_layout.addWidget(self.combo_temas)
        layout.addWidget(apariencia_group)

        # --- Consola (solo Windows) ----------------------------------------
        if sys.platform == "win32":
            consola_group = QGroupBox("Consola")
            consola_layout = QHBoxLayout(consola_group)
            self.btn_ocultar_consola = QPushButton("Ocultar")
            self.btn_ocultar_consola.setToolTip("Oculta la ventana de consola externa")
            self.btn_ocultar_consola.clicked.connect(self._ocultar_consola)
            consola_layout.addWidget(self.btn_ocultar_consola)
            self.btn_mostrar_consola = QPushButton("Mostrar")
            self.btn_mostrar_consola.setToolTip("Muestra la ventana de consola externa")
            self.btn_mostrar_consola.clicked.connect(self._mostrar_consola)
            consola_layout.addWidget(self.btn_mostrar_consola)
            self.btn_reiniciar_sin_consola = QPushButton("Reiniciar sin consola")
            self.btn_reiniciar_sin_consola.setToolTip("Reinicia la aplicación sin ventana de consola")
            self.btn_reiniciar_sin_consola.clicked.connect(self._crear_proceso_sin_consola)
            consola_layout.addWidget(self.btn_reiniciar_sin_consola)
            consola_layout.addStretch()
            layout.addWidget(consola_group)

        # --- Actualizaciones -----------------------------------------------
        if ACTUALIZACIONES_DISPONIBLES:
            actualizaciones_group = QGroupBox("Actualizaciones")
            actualizaciones_layout = QHBoxLayout(actualizaciones_group)
            btn_verificar_actualizaciones = QPushButton("Buscar actualizaciones")
            btn_verificar_actualizaciones.clicked.connect(self._verificar_actualizaciones)
            actualizaciones_layout.addWidget(btn_verificar_actualizaciones)
            lbl_version = QLabel(
                f"Versión {self.gestor_actualizaciones.obtener_version_actual()}"
            )
            lbl_version.setProperty("rol", "secundaria")
            actualizaciones_layout.addWidget(lbl_version)
            actualizaciones_layout.addStretch()
            layout.addWidget(actualizaciones_group)

        layout.addStretch()
        self._vistas.append(vista)
        self.stack.addWidget(self._contenedor_scroll(vista))

    def _crear_vista_avanzado(self):
        """Herramientas avanzadas agrupadas en una sola vista."""
        vista = QWidget()
        layout = QVBoxLayout(vista)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        aviso = QLabel(
            "Herramientas opcionales. La organización normal ya está cubierta en Inicio."
        )
        aviso.setProperty("rol", "secundaria")
        aviso.setWordWrap(True)
        layout.addWidget(aviso)

        self.tabs_avanzado = QTabWidget()
        layout.addWidget(self.tabs_avanzado, 1)

        self._crear_vista_ia(destino=self.tabs_avanzado)
        self._crear_vista_fechas(destino=self.tabs_avanzado)
        self._crear_vista_duplicados(destino=self.tabs_avanzado)
        self._crear_vista_estadisticas(destino=self.tabs_avanzado)

        self._vistas.append(vista)
        self.stack.addWidget(self._contenedor_scroll(vista))


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
        self.text_logs.setPlainText("DescargasOrdenadas\n" + "-" * 40 + "\n")
    
    def _exportar_logs(self):
        """Exporta los logs a un archivo."""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"descargasordenadas_logs_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.text_logs.toPlainText())
            
            QMessageBox.information(self, "Logs Exportados", 
                                  f"Logs exportados a: {filename}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudieron exportar los registros: {e}")
    
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
            self._agregar_log(f"Error gestionando consola: {e}")
    
    def _agregar_log(self, mensaje):
        """Agrega un mensaje al área de logs (tolerante a que aún no exista)."""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {mensaje}"

        widget = getattr(self, "text_logs", None)
        if widget is None:
            logger.info(mensaje)
            return
        try:
            widget.appendPlainText(formatted_msg)
            scrollbar = widget.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        except RuntimeError:
            # El widget ya fue destruido (cierre de la ventana)
            logger.info(mensaje)
    
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
            f"{'Con subcarpetas específicas (Excel → Hojas de cálculo/Excel)' if usar_subcarpetas else 'Solo carpetas principales (Excel → Hojas de cálculo)'}",
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
                QMessageBox.information(self, "Reorganización", f"{total} archivos reorganizados (modo {modo})")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")
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
                modo = "BÁSICO (solo carpetas principales)" 
                tooltip = "Excel → Hojas de cálculo\nPNG → Imágenes"
                
            self.chk_subcarpetas.setToolTip(f"Modo actual: {modo}\n\nEjemplos:\n{tooltip}")
            
            logger.info(f"Modo de organización cambiado a: {'DETALLADO' if usar_subcarpetas else 'BÁSICO'}")
            
        except Exception as e:
            logger.error(f"Error cambiando modo de organización: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo cambiar el modo: {e}")

    def _toggle_notificaciones(self, activo):
        """Toggle notificaciones nativas."""
        if self.notificador:
            if activo:
                self.notificador.habilitar()
                self._agregar_log("Notificaciones nativas habilitadas")
            else:
                self.notificador.deshabilitar()
                self._agregar_log("Notificaciones nativas deshabilitadas")
            
            # Guardar preferencia en configuración portable
            if self.config_portable:
                self.config_portable.establecer("notificaciones_habilitadas", activo)
    
    def _cambiar_tema(self, index):
        """Cambia el tema visual de la aplicación."""
        if not self.gestor_temas:
            return
        
        tema_nombre = self.combo_temas.itemData(index)
        if tema_nombre:
            self._tema = tema_nombre
            self.gestor_temas.establecer_tema_actual(
                "minimal_claro" if tema_nombre == "claro" else "minimal_oscuro"
            )
            self._aplicar_tema()
            
            # Guardar en configuración
            if self.config_portable:
                self.config_portable.establecer("tema", tema_nombre)
            
            self._agregar_log(f"Tema cambiado a: {self.combo_temas.currentText()}")
    
    def _toggle_menu_contextual(self, activo):
        """Toggle integración menú contextual."""
        if not self.gestor_menu_contextual:
            return
        
        try:
            if activo:
                exito, mensaje = self.gestor_menu_contextual.registrar_menu_contextual("carpetas")
                if exito:
                    self._agregar_log("Menú contextual registrado")
                    if self.notificador:
                        self.notificador.mostrar(
                            "Menú contextual",
                            "Ya puedes organizar con clic derecho sobre una carpeta.",
                            tipo="success", duracion=4,
                        )
                else:
                    self._agregar_log(f"Error: {mensaje}")
                    self.chk_menu_contextual.blockSignals(True)
                    self.chk_menu_contextual.setChecked(False)
                    self.chk_menu_contextual.blockSignals(False)
                    QMessageBox.warning(self, "Error", f"No se pudo registrar el menú contextual:\n{mensaje}")
            else:
                exito, mensaje = self.gestor_menu_contextual.desregistrar_menu_contextual()
                if exito:
                    self._agregar_log("Menú contextual eliminado")
                else:
                    self._agregar_log(f"Error: {mensaje}")
        except Exception as e:
            self._agregar_log(f"Error configurando menú contextual: {e}")
            self.chk_menu_contextual.setChecked(False)
            QMessageBox.critical(self, "Error", f"Error: {e}")
    
    def _verificar_actualizaciones_silencioso(self):
        """Verifica actualizaciones en segundo plano sin mostrar mensaje si no hay."""
        if not self.gestor_actualizaciones:
            return
        
        try:
            self._agregar_log("Verificando actualizaciones en segundo plano...")
            hay_actualizacion, info = self.gestor_actualizaciones.verificar_actualizaciones()
            
            if hay_actualizacion and info:
                version = info.get('version', 'Desconocida')
                self._agregar_log(f"✨ ¡Nueva versión {version} disponible!")
                self._mostrar_notificacion_actualizacion(info)
            else:
                self._agregar_log("Ya tienes la última versión")
        except Exception as e:
            self._agregar_log(f"Error verificando actualizaciones: {e}")
    
    def _verificar_actualizaciones(self):
        """Verifica actualizaciones y muestra el resultado."""
        if not self.gestor_actualizaciones:
            return
        
        self._agregar_log("Verificando actualizaciones...")
        
        try:
            hay_actualizacion, info = self.gestor_actualizaciones.verificar_actualizaciones(forzar=True)
            
            if hay_actualizacion and info:
                self._mostrar_notificacion_actualizacion(info)
            else:
                QMessageBox.information(
                    self,
                    "Actualizado",
                    f"Estás usando la última versión\n\n"
                    f"Versión actual: {self.gestor_actualizaciones.obtener_version_actual()}"
                )
                self._agregar_log("No hay actualizaciones disponibles")
        except Exception as e:
            self._agregar_log(f"Error verificando actualizaciones: {e}")
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
        msg.setWindowTitle("Nueva Versión Disponible")
        msg.setText(f"✨ ¡Hay una nueva versión disponible!\n\n"
                   f"Versión: {version}\n"
                   f"📝 {nombre}")
        msg.setInformativeText(f"{descripcion}...")
        msg.setIcon(QMessageBox.Information)
        
        # Botones personalizados
        btn_descargar = msg.addButton("Descargar e Instalar", QMessageBox.AcceptRole)
        btn_abrir_web = msg.addButton("🌐 Abrir en Navegador", QMessageBox.ActionRole)
        btn_cancelar = msg.addButton("Cancelar", QMessageBox.RejectRole)
        
        msg.setDefaultButton(btn_descargar)
        msg.exec()
        
        if msg.clickedButton() == btn_descargar:
            self._descargar_e_instalar_actualizacion(info)
        elif msg.clickedButton() == btn_abrir_web:
            self.gestor_actualizaciones.abrir_pagina_descarga()
        
        self._agregar_log(f"Nueva versión disponible: {version}")
    
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
            # Descargar el instalador nativo (.exe/.pkg/.deb)
            self._agregar_log(f"Descargando v{version}...")
            exito, resultado = self.gestor_actualizaciones.descargar_instalador_nativo(
                info,
                callback_progreso=actualizar_progreso
            )

            if not exito:
                progress.close()
                QMessageBox.critical(
                    self,
                    "Error de Descarga",
                    f"Error descargando actualización:\n\n{resultado}"
                )
                return

            progress.close()

            # Actualización segura: cerrar esta app → instalar encima → reabrir.
            # En Windows es imprescindible cerrar antes, o el asistente no puede
            # reemplazar el .exe en uso.
            self._agregar_log(f"Instalador descargado: {resultado}")
            aviso = QMessageBox(self)
            aviso.setWindowTitle("Instalar actualización")
            aviso.setText(f"DescargasOrdenadas v{version} se instalará ahora.")
            aviso.setInformativeText(
                "La aplicación se cerrará, el instalador se ejecutará y volverá a "
                "abrirse automáticamente al terminar.\n\n"
                "No se abrirá ninguna copia duplicada."
            )
            aviso.setIcon(QMessageBox.Information)
            btn_instalar = aviso.addButton("Instalar y reabrir", QMessageBox.AcceptRole)
            aviso.addButton("Más tarde", QMessageBox.RejectRole)
            aviso.exec()
            if aviso.clickedButton() is not btn_instalar:
                return

            exito_instalacion, mensaje = self.gestor_actualizaciones.actualizar_e_instalar(
                resultado, cerrar_app=self._cerrar_para_actualizar
            )
            if not exito_instalacion:
                QMessageBox.warning(self, "Error", f"{mensaje}")
                return

            self._agregar_log(f"Actualización en marcha: {mensaje}")
        except Exception as e:
            progress.close()
            self._agregar_log(f"Error durante actualización: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error durante el proceso de actualización:\n\n{e}"
            )
    
    @Slot(bool)
    def _toggle_autoarranque(self, activo):
        """Toggle autoarranque."""
        try:
            modo = "detallado"
            if hasattr(self, "chk_auto_basico") and self.chk_auto_basico.isChecked():
                modo = "basico"
            try:
                exito, mensaje = self.gestor_autoarranque.configurar_autoarranque(activo, modo=modo)
            except TypeError:
                exito, mensaje = self.gestor_autoarranque.configurar_autoarranque(activo)
            if not exito:
                QMessageBox.warning(self, "Error Autoarranque", f"{mensaje}")
                self.chk_autoarranque.blockSignals(True)
                self.chk_autoarranque.setChecked(False)
                self.chk_autoarranque.blockSignals(False)
                return

            if self.config_portable:
                self.config_portable.establecer("autoarranque", activo)

            if self.notificador:
                estado = "activado" if activo else "desactivado"
                self.notificador.mostrar(
                    "Autoarranque",
                    f"Inicio automático {estado}.",
                    tipo="success",
                    duracion=4
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo configurar el autoarranque: {e}")
            self.chk_autoarranque.blockSignals(True)
            self.chk_autoarranque.setChecked(False)
            self.chk_autoarranque.blockSignals(False)
    
    def _crear_acceso_directo_startup(self):
        """Activa el arranque con Windows usando el gestor oficial de autoarranque.

        Se apoya en GestorAutoarranque (registro HKCU) y no en accesos directos
        sueltos: así la app y el autoarranque siempre coinciden y no se crean
        copias duplicadas al iniciar sesión.
        """
        if sys.platform != "win32":
            QMessageBox.information(self, "No disponible", "Esta opción solo existe en Windows.")
            return
        modo = "basico" if (hasattr(self, "chk_auto_basico") and self.chk_auto_basico.isChecked()) else "detallado"
        try:
            exito, mensaje = self.gestor_autoarranque.configurar_autoarranque(True, modo=modo)
            if exito:
                self._agregar_log(f"Autoarranque activado: {mensaje}")
                QMessageBox.information(self, "Arranque automático", mensaje)
            else:
                QMessageBox.warning(self, "Error", mensaje)
        except Exception as e:
            self._agregar_log(f"No se pudo activar el autoarranque: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo activar el arranque automático:\n{e}")

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
                self.lbl_estado_fechas.setText("Organización por fechas activada")
                self.btn_activar_fechas.setEnabled(False)
                self.btn_desactivar_fechas.setEnabled(True)
                
                if hasattr(self, '_actualizar_estadisticas'):
                    self._actualizar_estadisticas()
                
                QMessageBox.information(self, "Fechas Activadas", 
                                      f"Organización por fechas activada exitosamente\n\n"
                                      f"Patrón configurado: {patron}\n\n"
                                      f"Los nuevos archivos se organizarán en:\n"
                                      f"Downloads/Fechas/{patron}/Categoría/\n\n"
                                      f"ℹ️ Solo afecta archivos organizados a partir de ahora")
            else:
                QMessageBox.warning(self, "Error", "El módulo de fechas no está disponible.\n\n"
                                  "Verifique que el módulo date_organizer esté instalado correctamente.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo activar la organización por fechas:\n\n{str(e)}")
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
                self.lbl_estado_fechas.setText("Organización por fechas desactivada")
                self.btn_activar_fechas.setEnabled(True)
                self.btn_desactivar_fechas.setEnabled(False)
                
                if hasattr(self, '_actualizar_estadisticas'):
                    self._actualizar_estadisticas()
                
                QMessageBox.information(self, "Fechas Desactivadas", 
                                      f"Organización por fechas desactivada\n\n"
                                      f"Los archivos volverán a organizarse de forma normal:\n"
                                      f"Downloads/Categoría/Subcategoría/\n\n"
                                      f"ℹ️ Los archivos ya organizados por fechas no se mueven automáticamente")
            else:
                QMessageBox.warning(self, "Error", "El módulo de fechas no está disponible.\n\n"
                                  "Verifique que el módulo date_organizer esté instalado correctamente.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo desactivar la organización por fechas:\n\n{str(e)}")
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
            QMessageBox.information(self, "IA", "Modelo reiniciado")
            self._actualizar_patrones()
    
    def _actualizar_patrones(self):
        """Actualiza patrones IA."""
        if not self.ai_categorizer:
            self.text_patrones.setText("IA no disponible en este sistema")
            return
        
        try:
            stats = self.ai_categorizer.analizar_patrones_usuario()
            texto = "Patrones aprendidos:\n\n"
            
            for categoria, datos in stats.get('patrones_por_categoria', {}).items():
                texto += f"{categoria}:\n"
                for palabra, peso in list(datos.items())[:5]:  # Top 5
                    texto += f"  • {palabra}: {peso:.2f}\n"
                texto += "\n"
            
            self.text_patrones.setText(texto)
        except:
            self.text_patrones.setText("No se pudieron cargar los patrones")
    
    def _revertir_fechas(self):
        """Revierte organización por fechas."""
        if not self.date_organizer:
            return
        
        reply = QMessageBox.question(self, "Revertir", "¿Revertir organización por fechas?")
        if reply == QMessageBox.Yes:
            resultado = self.date_organizer.revertir_organizacion_fechas(True)
            QMessageBox.information(self, "Revertido", f"{resultado.get('archivos_revertidos', 0)} archivos devueltos a su sitio")
    
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
            self.lbl_ejemplo.setText(f"Ejemplo: {ejemplo}")
            
            # Cambiar color según patrón para mejor visualización
            self.lbl_ejemplo.setObjectName("etiquetaSecundaria")
            
        except Exception as e:
            logger.debug(f"Error actualizando ejemplo de fecha: {e}")
            self.lbl_ejemplo.setText("Ejemplo: Downloads/Fechas/2024/12-Diciembre/Documentos/PDFs/")
    
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
            texto_previsualizacion = f"PREVISUALIZACIÓN DE ORGANIZACIÓN\n"
            texto_previsualizacion += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            texto_previsualizacion += f"Patrón seleccionado: {patron_actual}\n\n"
            texto_previsualizacion += f"Se encontraron {len(archivos_encontrados)} archivos de ejemplo:\n\n"
            
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
                    
                    texto_previsualizacion += f"{i:2d}. {archivo.name}\n"
                    texto_previsualizacion += f"    Fecha: {fecha_archivo.strftime('%d/%m/%Y %H:%M')}\n"
                    texto_previsualizacion += f"    Destino: {ruta_destino}\n\n"
                    
                except Exception as e:
                    texto_previsualizacion += f"{i:2d}. Error procesando {archivo.name}: {e}\n\n"
            
            texto_previsualizacion += f"\nEsta es solo una simulación. Los archivos no se han movido."
            
            # Mostrar diálogo con previsualización
            dialog = QMessageBox(self)
            dialog.setWindowTitle("Previsualización de Organización por Fechas")
            dialog.setText("Vista previa de cómo se organizarían los archivos:")
            dialog.setDetailedText(texto_previsualizacion)
            dialog.setIcon(QMessageBox.Information)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo generar la previsualización:\n\n{str(e)}")
    
    def _buscar_duplicados(self):
        """Busca duplicados."""
        if not self.duplicate_detector:
            QMessageBox.warning(self, "No Disponible", "Detector de duplicados no disponible")
            return
        
        try:
            self.text_duplicados.setPlainText("Buscando duplicados…")
            resultado = self.duplicate_detector.escanear_duplicados()
            
            if not resultado.get('duplicados_encontrados'):
                self.text_duplicados.setPlainText("No se han encontrado duplicados.")
                return
            
            duplicados = resultado['duplicados_encontrados']
            texto = f"{len(duplicados)} grupos de duplicados:\n\n"
            
            for i, grupo in enumerate(duplicados, 1):
                archivos = grupo.get('archivos', [])
                if len(archivos) > 1:
                    texto += f"Grupo {i} ({len(archivos)} archivos):\n"
                    for archivo_info in archivos:
                        ruta = archivo_info.get('ruta', 'N/A')
                        tamaño = archivo_info.get('tamaño', 0)
                        texto += f"  {ruta} ({self._formatear_bytes(tamaño)})\n"
                    texto += "\n"
            
            self.text_duplicados.setPlainText(texto)
        except Exception as e:
            self.text_duplicados.setPlainText(f"Error: {e}")
    
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
                    f"{resultado.get('archivos_eliminados', 0)} duplicados eliminados\n" +
                    f"{self._formatear_bytes(resultado.get('espacio_liberado', 0))} liberados"
                )
                self._buscar_duplicados()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")
    
    def _actualizar_estadisticas(self):
        """Actualiza estadísticas."""
        if not self.stats_manager:
            self.text_stats.setPlainText("Estadísticas no disponibles")
            return
        
        try:
            # El método generar_reporte_completo devuelve una string, no un dict
            reporte_texto = self.stats_manager.generar_reporte_completo()
            self.text_stats.setPlainText(reporte_texto)
        except Exception as e:
            self.text_stats.setPlainText(f"No se pudieron cargar las estadísticas: {e}")
    
    def _formatear_bytes(self, bytes_size: int) -> str:
        """Formatea bytes en formato legible."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"

    def _seleccionar_carpeta(self):
        """Permite elegir una carpeta: organizarla una vez o usarla como base."""
        nueva_carpeta = QFileDialog.getExistingDirectory(
            self, 
            "Seleccionar carpeta", 
            str(self.organizador.carpeta_descargas)
        )
        if not nueva_carpeta:
            return

        ruta = Path(nueva_carpeta)
        aviso = self._comprobar_permisos_gui(ruta)
        if aviso:
            QMessageBox.warning(self, "Sin permisos", aviso)
            self._agregar_log(f"{aviso}")
            return

        dialogo = QMessageBox(self)
        dialogo.setWindowTitle("Carpeta seleccionada")
        dialogo.setText(f"¿Qué quieres hacer con:\n{ruta}?")
        dialogo.setIcon(QMessageBox.Question)
        btn_organizar = dialogo.addButton("Organizarla ahora", QMessageBox.AcceptRole)
        btn_base = dialogo.addButton("Usarla como carpeta principal", QMessageBox.ActionRole)
        dialogo.addButton("Cancelar", QMessageBox.RejectRole)
        dialogo.exec()

        if dialogo.clickedButton() is btn_organizar:
            self._cambiar_carpeta_y_organizar(ruta, Path(self.organizador.carpeta_descargas))
        elif dialogo.clickedButton() is btn_base:
            self._establecer_carpeta_base(ruta)

    def organizar_carpeta_externa(self, peticion: dict):
        """Organiza una carpeta pedida desde fuera (menú contextual del sistema).

        Se ejecuta en la instancia que ya está abierta, sin abrir una ventana
        nueva. Al terminar avisa con una notificación y, si algo falla por
        permisos, lo explica en el registro y con un aviso al usuario.
        """
        try:
            carpeta = Path(str(peticion.get("carpeta", ""))).expanduser()
        except Exception:
            return
        if not carpeta:
            return

        if not carpeta.exists() or not carpeta.is_dir():
            self._agregar_log(f"La carpeta no existe: {carpeta}")
            return

        if not os.access(carpeta, os.W_OK) or not os.access(carpeta, os.R_OK):
            self._avisar_permisos(carpeta)
            return

        self._agregar_log(f"Organizando carpeta externa: {carpeta}")

        modo_detallado = False
        if hasattr(self, "chk_auto_detallado") and self.chk_auto_detallado.isChecked():
            modo_detallado = True
        elif hasattr(self, "chk_subcarpetas"):
            modo_detallado = self.chk_subcarpetas.isChecked()

        class HiloCarpetaExterna(QThread):
            terminado = Signal(bool, str, int, list)

            def __init__(self, ruta, subcarpetas, padre):
                super().__init__(padre)
                self.ruta = ruta
                self.subcarpetas = subcarpetas

            def run(self):
                try:
                    organizador = OrganizadorArchivos(
                        carpeta_descargas=str(self.ruta),
                        usar_subcarpetas=self.subcarpetas,
                    )
                    resultados, errores = organizador.organizar()
                    total = sum(
                        len(files) for cat in resultados.values() for files in cat.values()
                    )
                    self.terminado.emit(True, str(self.ruta), total, errores)
                except PermissionError as e:
                    self.terminado.emit(False, f"permisos:{e}", 0, [])
                except Exception as e:
                    self.terminado.emit(False, str(e), 0, [])

        def al_terminar(exito, detalle, total, errores):
            if exito:
                mensaje = f"{total} archivo{'s' if total != 1 else ''} en {carpeta.name}"
                self._agregar_log(f"{mensaje}")
                if total > 0 and self.notificador:
                    self.notificador.mostrar(
                        "Carpeta organizada", mensaje, tipo="success", duracion=5
                    )
                if errores:
                    self._agregar_log(
                        f"{len(errores)} archivo(s) no se pudieron mover (revisa los avisos)"
                    )
            elif detalle.startswith("permisos:"):
                self._avisar_permisos(carpeta)
            else:
                self._agregar_log(f"No se pudo organizar {carpeta}: {detalle}")
                if self.notificador:
                    self.notificador.mostrar(
                        "No se pudo organizar", detalle, tipo="error", duracion=8
                    )

        hilo = HiloCarpetaExterna(carpeta, modo_detallado, self)
        hilo.terminado.connect(al_terminar)
        self._hilo_carpeta_externa = hilo
        hilo.start()

    def _avisar_permisos(self, carpeta: Path):
        """Explica con claridad un problema de permisos, sin fallar."""
        if sys.platform == "darwin":
            mensaje = (
                f"macOS bloquea el acceso a {carpeta}.\n\n"
                "Ajustes del sistema → Privacidad y seguridad → Archivos y carpetas."
            )
        elif sys.platform == "win32":
            mensaje = (
                f"Windows bloquea el acceso a {carpeta}.\n\n"
                "Prueba con una carpeta de tu perfil de usuario."
            )
        else:
            mensaje = f"Sin permisos sobre {carpeta}.\n\nRevisa el propietario de la carpeta."
        self._agregar_log(f"{mensaje}")
        if self.notificador:
            self.notificador.mostrar("Permisos necesarios", mensaje, tipo="error", duracion=10)

    def _cambiar_carpeta_y_organizar(self, nueva_carpeta: Path, carpeta_anterior: Path):
        """Cambia a la carpeta elegida, la organiza y vuelve a la anterior."""
        # Guardamos el modo actual de subcarpetas para no alterar la config
        usar_subcarpetas = self.chk_subcarpetas.isChecked() if hasattr(self, "chk_subcarpetas") else True

        progreso = QProgressDialog(
            f"Organizando:\n{nueva_carpeta}",
            None, 0, 0, self
        )
        progreso.setWindowTitle("DescargasOrdenadas")
        progreso.setWindowModality(Qt.WindowModal)
        progreso.setCancelButton(None)
        progreso.setMinimumDuration(0)
        progreso.setFixedWidth(420)
        progreso.show()
        QApplication.processEvents()

        # Pausar la auto-organización mientras trabajamos con otra carpeta
        timer_estaba_activo = bool(getattr(self, "timer_auto", None) and self.timer_auto.isActive())
        if timer_estaba_activo and hasattr(self, "timer_auto"):
            self.timer_auto.stop()

        class HiloCambioCarpeta(QThread):
            terminado = Signal(bool, str)

            def __init__(self, carpeta, subcarpetas, padre):
                super().__init__(padre)
                self.carpeta = carpeta
                self.subcarpetas = subcarpetas
                self.padre = padre

            def run(self):
                try:
                    from .file_organizer import OrganizadorArchivos
                    organizador_temporal = OrganizadorArchivos(
                        carpeta_descargas=str(self.carpeta),
                        usar_subcarpetas=self.subcarpetas,
                    )
                    organizador_temporal.organizar()
                    self.terminado.emit(True, str(self.carpeta))
                except Exception as e:
                    self.terminado.emit(False, str(e))

        def al_terminar(exito, detalle):
            progreso.close()
            if exito:
                self._agregar_log(f"Carpeta organizada: {nueva_carpeta}")
                if self.notificador:
                    self.notificador.mostrar(
                        "Carpeta organizada",
                        f"{nueva_carpeta.name} lista.",
                        tipo="success", duracion=4,
                    )
            else:
                self._agregar_log(f"Error organizando {nueva_carpeta}: {detalle}")
                QMessageBox.warning(self, "Error", f"No se pudo organizar la carpeta:\n{detalle}")

        hilo = HiloCambioCarpeta(nueva_carpeta, usar_subcarpetas, self)
        hilo.terminado.connect(al_terminar)
        self._hilo_cambio_carpeta = hilo  # evitar que lo recoja el recolector
        hilo.start()

        # Mantener la carpeta de trabajo anterior y actualizar la interfaz
        self.organizador.carpeta_descargas = carpeta_anterior
        self.organizador.carpeta_config = carpeta_anterior / ".config"
        self.lbl_carpeta_actual.setText(str(carpeta_anterior))
        if hasattr(self, "lbl_carpeta_cabecera"):
            self.lbl_carpeta_cabecera.setText(str(carpeta_anterior))

    def _establecer_carpeta_base(self, nueva_carpeta: Path):
        """Guarda la carpeta elegida como carpeta principal de la aplicación.

        A partir de aquí es la carpeta que se organiza al abrir y con el menú
        contextual, y sobrevive a los reinicios.
        """
        aviso = self._comprobar_permisos_gui(nueva_carpeta)
        if aviso:
            QMessageBox.warning(self, "Sin permisos", aviso)
            self._agregar_log(f"{aviso}")
            return

        try:
            self.organizador.carpeta_descargas = nueva_carpeta
            self.organizador.carpeta_config = nueva_carpeta / ".config"
            if self.config_portable:
                self.config_portable.establecer("carpeta_base", str(nueva_carpeta))

            self.lbl_carpeta_actual.setText(str(nueva_carpeta))
            if hasattr(self, "lbl_carpeta_cabecera"):
                self.lbl_carpeta_cabecera.setText(str(nueva_carpeta))

            # Re-inicializar los módulos que dependen de la carpeta
            self._inicializar_modulos()
            self._actualizar_datos()
            self._agregar_log(f"Carpeta principal establecida: {nueva_carpeta}")
            if self.notificador:
                self.notificador.mostrar(
                    "Carpeta principal",
                    f"Ahora se organiza {nueva_carpeta.name}.",
                    tipo="success", duracion=4,
                )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo establecer la carpeta:\n{e}")

    def _comprobar_permisos_gui(self, carpeta: Path) -> Optional[str]:
        """Devuelve un aviso legible si no se puede trabajar con la carpeta."""
        try:
            if not carpeta.exists() or not carpeta.is_dir():
                return f"La carpeta no existe:\n{carpeta}"
            if not os.access(carpeta, os.R_OK) or not os.access(carpeta, os.W_OK):
                if sys.platform == "darwin":
                    return (
                        f"macOS bloquea el acceso a:\n{carpeta}\n\n"
                        "Ajustes del sistema → Privacidad y seguridad → "
                        "Archivos y carpetas, y concede acceso a DescargasOrdenadas."
                    )
                return f"Sin permisos de lectura/escritura sobre:\n{carpeta}"
        except Exception as e:
            return f"No se puede comprobar el acceso a la carpeta:\n{e}"
        return None

    def _reset_carpeta_descargas(self):
        """Restablece la carpeta de descargas a la predeterminada del sistema."""
        from .file_organizer import OrganizadorArchivos

        organizador_temp = OrganizadorArchivos.__new__(OrganizadorArchivos)
        carpeta_predeterminada = organizador_temp._detectar_carpeta_descargas()

        if self.config_portable:
            self.config_portable.establecer("carpeta_base", None)

        self.organizador.carpeta_descargas = carpeta_predeterminada
        self.organizador.carpeta_config = carpeta_predeterminada / ".config"

        self.lbl_carpeta_actual.setText(str(carpeta_predeterminada))
        if hasattr(self, "lbl_carpeta_cabecera"):
            self.lbl_carpeta_cabecera.setText(str(carpeta_predeterminada))

        self._inicializar_modulos()
        self._actualizar_datos()

        QMessageBox.information(
            self,
            "Carpeta restablecida",
            f"La carpeta vuelve a ser la predeterminada:\n{carpeta_predeterminada}",
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
                
                self._agregar_log(f"Reiniciando con comando: {' '.join(comando)}")
                
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
                
                self._agregar_log("Reiniciando sin consola...")

                # La nueva copia debe arrancar DESPUÉS de que esta libere el
                # bloqueo de instancia única; si no, se cerraría sola. Se usa
                # un .bat intermedio que espera y luego lanza la app.
                espera = Path(tempfile.gettempdir()) / "descargasordenadas_reinicio.bat"
                destino = " ".join(f'"{parte}"' for parte in self._comando_reinicio_sin_consola())
                espera.write_text(
                    "@echo off\r\n"
                    "timeout /t 2 /nobreak >nul\r\n"
                    f"start \"\" {destino}\r\n"
                    "del \"%~f0\"\r\n",
                    encoding="latin-1", errors="replace",
                )
                subprocess.Popen(
                    ["cmd", "/c", str(espera)],
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    close_fds=True,
                )
                # Cerrar esta instancia (libera el bloqueo) sin diálogos
                self.cerrar_completamente = True
                QTimer.singleShot(400, lambda: self._salir_completamente())
                return True
            except Exception as e:
                self._agregar_log(f"Error creando proceso sin consola: {e}")
        else:
                self._agregar_log("Reinicio sin consola solo disponible en Windows")
        return False

    def _comando_reinicio_sin_consola(self) -> list:
        """Comando para relanzar la app sin ventana de consola (Windows)."""
        if getattr(sys, "frozen", False):
            return [sys.executable, "--minimizado"]
        proyecto_dir = Path(sys.argv[0]).parent
        bat_sin_consola = proyecto_dir / "windows" / "DescargasOrdenadas_SinConsola.bat"
        bat_principal = proyecto_dir / "windows" / "DescargasOrdenadas.bat"
        if bat_sin_consola.exists():
            return [str(bat_sin_consola), "--minimizado"]
        if bat_principal.exists():
            return [str(bat_principal), "--minimizado"]
        python_exe = sys.executable
        if python_exe.endswith('python.exe'):
            python_exe = python_exe.replace('python.exe', 'pythonw.exe')
        return [python_exe, sys.argv[0], "--minimizado"]
    

    def _restaurar_preferencias_auto(self):
        """Restaura el modo (básico/detallado) y el intervalo guardados."""
        if self._sincronizando_controles:
            return
        self._sincronizando_controles = True
        try:
            intervalo = self._auto_intervalo_inicial
            modo = self._auto_modo_inicial

            if self.config_portable:
                if intervalo is None:
                    try:
                        intervalo = int(self.config_portable.obtener("auto_intervalo", 3600) or 3600)
                    except (TypeError, ValueError):
                        intervalo = 3600
                if modo not in ("basico", "detallado"):
                    modo = self.config_portable.obtener("auto_modo", "basico")

            if modo not in ("basico", "detallado"):
                modo = "basico"

            # Seleccionar el intervalo guardado en el desplegable
            if hasattr(self, "combo_intervalo_auto") and intervalo:
                indice = self.combo_intervalo_auto.findData(int(intervalo))
                if indice >= 0:
                    self.combo_intervalo_auto.setCurrentIndex(indice)

            self._auto_modo_guardado = modo

            # El interruptor general arranca apagado; si la configuración tenía
            # la organización automática activada, _activar_auto_guardada lo
            # enciende al poco de abrir la ventana.
            if hasattr(self, "chk_auto_principal"):
                self.chk_auto_principal.blockSignals(True)
                self.chk_auto_principal.setChecked(False)
                self.chk_auto_principal.blockSignals(False)

            # Marcar la casilla correspondiente sin disparar el timer todavía
            if modo == "basico" and hasattr(self, "chk_auto_basico"):
                self.chk_auto_basico.blockSignals(True)
                self.chk_auto_basico.setChecked(True)
                if hasattr(self, "chk_auto_detallado"):
                    self.chk_auto_detallado.blockSignals(True)
                    self.chk_auto_detallado.setChecked(False)
                    self.chk_auto_detallado.blockSignals(False)
                self.chk_auto_basico.blockSignals(False)
            elif hasattr(self, "chk_auto_detallado"):
                self.chk_auto_detallado.blockSignals(True)
                self.chk_auto_detallado.setChecked(True)
                if hasattr(self, "chk_auto_basico"):
                    self.chk_auto_basico.blockSignals(True)
                    self.chk_auto_basico.setChecked(False)
                    self.chk_auto_basico.blockSignals(False)
                self.chk_auto_detallado.blockSignals(False)
        except Exception as e:
            logger.debug(f"No se pudieron restaurar las preferencias de auto-organización: {e}")
        finally:
            self._sincronizando_controles = False

    def _activar_auto_guardada(self):
        """Arranca la auto-organización con el modo previamente guardado."""
        modo = getattr(self, "_auto_modo_guardado", "basico")
        try:
            if hasattr(self, "timer_auto") and self.timer_auto is None:
                pass
            # Asegurar el timer
            if not hasattr(self, "timer_auto") or self.timer_auto is None:
                from PySide6.QtCore import QTimer as _QTimer
                self.timer_auto = _QTimer()
                self.timer_auto.timeout.connect(self._organizar_automatico)

            # Activar primero el interruptor general (sin señales para no reentrar)
            if hasattr(self, "chk_auto_principal"):
                self.chk_auto_principal.blockSignals(True)
                self.chk_auto_principal.setChecked(True)
                self.chk_auto_principal.blockSignals(False)

            # Marcar el modo guardado (con señales para refrescar la tarjeta)
            if modo == "basico" and hasattr(self, "chk_auto_basico"):
                if not self.chk_auto_basico.isChecked():
                    self.chk_auto_basico.setChecked(True)
            elif hasattr(self, "chk_auto_detallado") and not self.chk_auto_detallado.isChecked():
                self.chk_auto_detallado.setChecked(True)

            # Garantizar el timer activo con el intervalo actual
            if hasattr(self, "timer_auto"):
                intervalo_seg = int(self.combo_intervalo_auto.currentData() or 3600)
                self.timer_auto.start(max(30, intervalo_seg) * 1000)
            intervalo_texto = self.combo_intervalo_auto.currentText() if hasattr(self, "combo_intervalo_auto") else ""
            self._agregar_log(f"Auto-organización ACTIVADA al abrir ({modo}, cada {intervalo_texto})")
            self._actualizar_estado_auto_organizacion()
        except Exception as e:
            logger.debug(f"No se pudo activar la auto-organización guardada: {e}")

    def _guardar_preferencia_auto(self):
        """Guarda qué modo está activo y cada cuánto se revisa la carpeta."""
        if not self.config_portable:
            return
        if getattr(self, "_sincronizando_controles", False):
            return
        try:
            modo = "detallado" if (hasattr(self, "chk_auto_detallado") and self.chk_auto_detallado.isChecked()) else "basico"
            if hasattr(self, "combo_intervalo_auto"):
                intervalo = int(self.combo_intervalo_auto.currentData() or 3600)
            else:
                intervalo = 30
            self.config_portable.establecer("auto_modo", modo)
            self.config_portable.establecer("auto_intervalo", intervalo)
            activo_general = self.chk_auto_principal.isChecked() if hasattr(self, "chk_auto_principal") else True
            self.config_portable.establecer("auto_organizacion", bool(activo_general))
            self._sincronizar_autoarranque(modo)
        except Exception as e:
            logger.debug(f"No se pudieron guardar las preferencias de auto-organización: {e}")

    def _olvidar_preferencia_auto(self):
        """Desactiva la auto-organización recordada para el próximo arranque."""
        if not self.config_portable:
            return
        if getattr(self, "_sincronizando_controles", False):
            return
        # Si el otro modo sigue activo, mantenemos la preferencia guardada
        otro_activo = False
        if hasattr(self, "chk_auto_basico") and self.chk_auto_basico.isChecked():
            otro_activo = True
        if hasattr(self, "chk_auto_detallado") and self.chk_auto_detallado.isChecked():
            otro_activo = True
        if otro_activo:
            return
        try:
            self.config_portable.establecer("auto_organizacion", False)
            # Si el autoarranque sigue activo, lo reescribimos sin modo para que
            # el próximo inicio no reactive la auto-organización.
            if self.config_portable.obtener("autoarranque", False):
                exito, msg = self.gestor_autoarranque.configurar_autoarranque(True, modo=None)
                logger.debug(f"Autoarranque reescrito sin modo: exito={exito}, mensaje={msg}")
        except Exception as e:
            logger.debug(f"No se pudo desactivar la auto-organización guardada: {e}")

    def _sincronizar_autoarranque(self, modo):
        """Reescribe el autoarranque del sistema con el modo actual."""
        if not self.config_portable:
            return
        if not self.config_portable.obtener("autoarranque", False):
            return
        # Evitar reentradas: actualizar el autoarranque puede volver a disparar
        # las casillas y repetir el ciclo.
        if getattr(self, "_sincronizando_autoarranque", False):
            return
        self._sincronizando_autoarranque = True
        try:
            self.gestor_autoarranque.configurar_autoarranque(True, modo=modo)
        except TypeError:
            self.gestor_autoarranque.configurar_autoarranque(True)
        except Exception as e:
            logger.debug(f"No se pudo actualizar el autoarranque: {e}")
        finally:
            self._sincronizando_autoarranque = False

    def _cambiar_intervalo_auto(self, index):
        """Cambia el intervalo de auto-organización."""
        if self.config_portable:
            try:
                self.config_portable.establecer("auto_intervalo", int(self.combo_intervalo_auto.currentData() or 3600))
            except Exception:
                pass

        if hasattr(self, 'timer_auto') and self.timer_auto and self.timer_auto.isActive():
            # Si el timer está activo, reiniciar con el nuevo intervalo
            intervalo_ms = self.combo_intervalo_auto.currentData() * 1000
            self.timer_auto.setInterval(intervalo_ms)

            intervalo_texto = self.combo_intervalo_auto.currentText()
            self._agregar_log(f"⏱️ Intervalo de auto-organización cambiado a: {intervalo_texto}")
    
    def _quitar_acceso_directo_startup(self):
        """Desactiva el arranque con el sistema usando el gestor oficial."""
        try:
            exito, mensaje = self.gestor_autoarranque.configurar_autoarranque(False)
            if exito:
                if self.config_portable:
                    self.config_portable.establecer("autoarranque", False)
                self._agregar_log(f"Autoarranque desactivado: {mensaje}")
            else:
                QMessageBox.warning(self, "Error", mensaje)
        except Exception as e:
            self._agregar_log(f"No se pudo desactivar el autoarranque: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo desactivar el arranque automático:\n{e}")

def run_advanced_gui(
    directorio=None,
    minimizado=False,
    auto_organizacion=False,
    intervalo_auto=None,
    modo_auto=None,
    guardia_instancia=None,
):
    """Ejecuta la GUI avanzada."""
    app = QApplication.instance() or QApplication(sys.argv)

    window = OrganizadorAvanzado(
        directorio,
        auto_organizacion=auto_organizacion,
        intervalo_auto=intervalo_auto,
        modo_auto=modo_auto,
    )

    # Canal para que una segunda ejecución muestre esta ventana o pida
    # organizar una carpeta (menú contextual) en vez de abrir otra copia.
    if guardia_instancia is not None:
        try:
            guardia_instancia.conectar_activacion(window._mostrar_ventana)
            guardia_instancia.conectar_accion("organizar", window.organizar_carpeta_externa)
            guardia_instancia.iniciar_servidor()
        except Exception as e:
            logger.debug(f"No se pudo preparar el canal de instancia única: {e}")

    if not minimizado:
        window.show()
    else:
        # Si se inicia minimizado, ir directo a la bandeja
        window._ocultar_en_bandeja()

    try:
        return app.exec()
    finally:
        if guardia_instancia is not None:
            try:
                guardia_instancia.liberar()
            except Exception:
                pass
