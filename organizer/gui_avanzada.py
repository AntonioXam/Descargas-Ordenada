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
        QEasingCurve, QRectF, QPointF, QTime,
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
        QGraphicsOpacityEffect, QSizePolicy, QSplitter, QRadioButton, QDialog,
        QTimeEdit
    )
except ImportError:
    print("PySide6 no instalado. Ejecuta: pip install PySide6")
    sys.exit(1)

from .file_organizer import OrganizadorArchivos
from .autostart import GestorAutoarranque
from .version import obtener_version
from . import efectos, errores, estilos, iconos, programacion, primer_arranque
from . import permission_manager as permisos

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
    ACTUALIZACIONES_HEREDADAS = False
except ImportError:
    try:
        from .actualizaciones import obtener_gestor_actualizaciones
        ACTUALIZACIONES_DISPONIBLES = True
        ACTUALIZACIONES_HEREDADAS = True
    except ImportError:
        ACTUALIZACIONES_DISPONIBLES = False
        ACTUALIZACIONES_HEREDADAS = False

logger = logging.getLogger('organizador.gui_avanzada')

if ACTUALIZACIONES_HEREDADAS:
    # Un respaldo silencioso esconde que faltan funciones: mejor dejarlo dicho.
    logger.warning(
        "No se encontró el sistema de actualizaciones actual; se usa el heredado "
        "(sin descarga integrada). Reinstala la aplicación para recuperarlo."
    )

# Medidas del layout adaptable (en píxeles lógicos)
ANCHO_LATERAL_COMPACTO = 64
ANCHO_LATERAL_NORMAL = 200
ANCHO_LATERAL_AMPLIO = 224
ANCHO_CONTENIDO_MAXIMO = 980

# Opacidad del fondo cuando hay un material nativo detrás (vibrancy/Mica).
# Lo bastante baja para que se vea el material y lo bastante alta para que el
# texto no pierda legibilidad. Las tarjetas se quedan casi opacas: ver
# ``estilos.colores_translucidos``.
OPACIDAD_CON_EFECTO = 0.70


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


class DialogoPrevisualizacion(QDialog):
    """Ventana que muestra qué se moverá antes de organizar.

    Enseña el resumen por categoría, el listado de archivos con su destino y
    permite confirmar o cancelar. Nada se toca hasta pulsar «Organizar».
    """

    def __init__(self, plan: dict, modo: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Previsualización")
        self.setModal(True)
        self.setMinimumSize(620, 520)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(14)

        # --- Cabecera con el resumen -------------------------------------
        cabecera = QVBoxLayout()
        cabecera.setSpacing(4)
        titulo = QLabel(f"{plan.get('total', 0)} archivos listos para organizar")
        titulo.setProperty("rol", "titulo")
        cabecera.addWidget(titulo)

        tamano = plan.get("tamaño", 0)
        detalle = QLabel(
            f"Modo {modo} · {self._formatear_bytes(tamano)} en total"
            + (f" · {plan.get('ya_ordenados', 0)} ya estaban en su sitio"
               if plan.get("ya_ordenados") else "")
        )
        detalle.setProperty("rol", "secundaria")
        cabecera.addWidget(detalle)
        layout.addLayout(cabecera)

        # --- Resumen por categoría ---------------------------------------
        categorias = plan.get("categorias", {})
        if categorias:
            chips = QHBoxLayout()
            chips.setSpacing(8)
            chips.setContentsMargins(0, 0, 0, 0)
            for nombre, cuenta in sorted(categorias.items(), key=lambda x: -x[1])[:5]:
                etiqueta = QLabel(f"{nombre}: {cuenta}")
                etiqueta.setProperty("rol", "chip")
                chips.addWidget(etiqueta)
            chips.addStretch()
            layout.addLayout(chips)

        # --- Lista de movimientos ----------------------------------------
        self.lista = QListWidget()
        self.lista.setAlternatingRowColors(False)
        for movimiento in plan.get("movimientos", [])[:500]:
            item = QListWidgetItem(
                f"{movimiento['nombre']}  →  {movimiento['categoria']}"
                + (f"/{movimiento['subcategoria']}"
                   if movimiento.get("subcategoria") not in (None, "General") else "")
            )
            item.setToolTip(movimiento.get("destino", ""))
            self.lista.addItem(item)
        layout.addWidget(self.lista, 1)

        # --- Avisos ------------------------------------------------------
        errores = plan.get("errores", [])
        if errores:
            aviso = QLabel(f"{len(errores)} aviso(s): " + errores[0])
            aviso.setProperty("rol", "aviso")
            aviso.setWordWrap(True)
            layout.addWidget(aviso)

        recordatorio = QLabel(
            "Nada se ha movido todavía. Los archivos a medio descargar no se tocan."
        )
        recordatorio.setProperty("rol", "secundaria")
        recordatorio.setWordWrap(True)
        layout.addWidget(recordatorio)

        # --- Botones -----------------------------------------------------
        botones = QHBoxLayout()
        botones.addStretch()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        botones.addWidget(btn_cancelar)

        btn_organizar = QPushButton("Organizar ahora")
        btn_organizar.setProperty("rol", "primario")
        btn_organizar.setDefault(True)
        btn_organizar.clicked.connect(self.accept)
        botones.addWidget(btn_organizar)
        layout.addLayout(botones)

    def _formatear_bytes(self, cantidad: int) -> str:
        """Convierte bytes a una unidad legible."""
        valor = float(cantidad or 0)
        for unidad in ("B", "KB", "MB", "GB", "TB"):
            if valor < 1024:
                return f"{valor:.1f} {unidad}"
            valor /= 1024
        return f"{valor:.1f} PB"


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

        # Sistema de permisos: la puerta por la que pasa todo lo que depende del
        # sistema operativo, para poder pedirlo antes de fallar.
        self.permisos = permisos.obtener_gestor_permisos(
            Path(self.organizador.carpeta_descargas)
        )
        # Se recalcula en cuanto la ventana recupera el foco, para detectar que
        # el usuario acaba de conceder un permiso sin tener que reiniciar.
        self._permisos_pendientes = set()
        
        # Inicializar menú contextual
        if MENU_CONTEXTUAL_DISPONIBLE:
            self.gestor_menu_contextual = GestorMenuContextual()
            # Si la Acción rápida de Finder quedó con el formato antiguo (no
            # aparecía o daba error), se regenera sola al abrir la app.
            try:
                self.gestor_menu_contextual.reparar_macos()
            except Exception as e:
                logger.debug(f"No se pudo revisar la Acción rápida: {e}")
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
        
        # Hora programada (organización diaria a una hora concreta)
        self._hora_programada = None
        if self.config_portable:
            guardada = self.config_portable.obtener("hora_programada", None)
            if guardada and programacion.parsear_hora(guardada):
                self._hora_programada = guardada

        # Tema visual (claro / oscuro / automático del sistema). La única
        # fuente de verdad de la apariencia es ``estilos.py``.
        self._tema = self._cargar_preferencia_tema()
        # Las preferencias antiguas (``minimal_claro`` / ``minimal_oscuro``)
        # migran al sistema nuevo.
        if self._tema not in ("claro", "oscuro", "auto"):
            self._tema = "auto"
        Switch._tema = self._tema
        
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
        self._configurar_atajos()
        self._configurar_arrastrar_soltar()
        # El efecto nativo necesita una ventana ya creada; se aplica en cuanto
        # haya identificador nativo (showEvent lo garantiza).
        self._efecto_nativo_activo = False
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
        """Aplica la hoja de estilo tipo Apple según el tema actual.

        Si el sistema admite efectos nativos (vibrancy en macOS, Mica en
        Windows 11), el fondo se vuelve ligeramente translúcido para dejar ver
        el material del escritorio; si no, se usa el fondo opaco habitual.
        """
        tema_efectivo = self._tema_efectivo()
        Switch._tema = tema_efectivo

        # Con un material nativo detrás, el fondo se vuelve translúcido para
        # que se aprecie. Sin efecto, todo opaco: el aspecto de siempre.
        opacidad = 1.0
        if getattr(self, "_efecto_nativo_activo", False):
            opacidad = OPACIDAD_CON_EFECTO
        self.setStyleSheet(
            estilos.hoja_estilo(tema_efectivo, opacidad=opacidad)
        )
        # Repintar los interruptores dibujados a mano
        for interruptor in self.findChildren(Switch):
            interruptor.update()
        # Los iconos son SVG pintados en el color del tema, así que hay que
        # vaciar la caché y volver a dibujarlos al cambiar de tema.
        iconos.limpiar_cache()
        self._refrescar_iconos_lateral()
        self._actualizar_indicadores_tema()

    def _aplicar_efecto_nativo(self):
        """Activa el efecto del sistema (vibrancy/Mica) y ajusta los estilos."""
        try:
            self._efecto_nativo_activo = efectos.aplicar_efecto_ventana(self)
        except Exception as e:
            logger.debug(f"Sin efecto nativo: {e}")
            self._efecto_nativo_activo = False
        if self._efecto_nativo_activo:
            self._aplicar_tema()

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


    def _configurar_atajos(self):
        """Registra los atajos de teclado de la aplicación.

        En macOS se usa la tecla Command; en Windows y Linux, Ctrl.
        """
        try:
            from PySide6.QtGui import QShortcut, QKeySequence

            modificador = "Meta" if sys.platform == "darwin" else "Ctrl"

            atajos = [
                (f"{modificador}+O", self._reorganizar, "Organizar ahora"),
                (f"{modificador}+Z", self._deshacer_del_historial, "Deshacer la última organización"),
                (f"{modificador}+R", lambda: self._verificar_actualizaciones(), "Buscar actualizaciones"),
                (f"{modificador}+1", lambda: self._cambiar_vista(0), "Ir a Inicio"),
                (f"{modificador}+2", lambda: self._cambiar_vista(1), "Ir a Historial"),
                (f"{modificador}+3", lambda: self._cambiar_vista(2), "Ir a Actividad"),
                (f"{modificador}+4", lambda: self._cambiar_vista(3), "Ir a Ajustes"),
                (f"{modificador}+5", lambda: self._cambiar_vista(4), "Ir a Avanzado"),
                ("Escape", self._ocultar_en_bandeja, "Minimizar a la bandeja"),
                ("F5", lambda: self._actualizar_datos(), "Refrescar datos"),
            ]
            self._atajos = []
            for secuencia, funcion, _descripcion in atajos:
                atajo = QShortcut(QKeySequence(secuencia), self)
                atajo.activated.connect(funcion)
                self._atajos.append(atajo)
            logger.debug(f"{len(self._atajos)} atajos de teclado configurados")
        except Exception as e:
            logger.debug(f"No se pudieron configurar los atajos: {e}")

    def _configurar_arrastrar_soltar(self):
        """Permite arrastrar carpetas sobre la ventana para organizarlas."""
        try:
            self.setAcceptDrops(True)
        except Exception as e:
            logger.debug(f"No se pudo activar arrastrar y soltar: {e}")

    def dragEnterEvent(self, event):
        """Acepta el arrastre si trae al menos una carpeta."""
        try:
            if event.mimeData().hasUrls():
                for url in event.mimeData().urls():
                    if url.isLocalFile() and Path(url.toLocalFile()).is_dir():
                        event.acceptProposedAction()
                        return
        except Exception:
            pass
        event.ignore()

    def dropEvent(self, event):
        """Organiza las carpetas que se suelten sobre la ventana."""
        try:
            carpetas = [
                Path(url.toLocalFile())
                for url in event.mimeData().urls()
                if url.isLocalFile() and Path(url.toLocalFile()).is_dir()
            ]
        except Exception:
            carpetas = []

        if not carpetas:
            event.ignore()
            return
        event.acceptProposedAction()

        carpeta = carpetas[0]
        aviso = self._comprobar_permisos_gui(carpeta)
        if aviso:
            QMessageBox.warning(self, "Sin permisos", aviso)
            return

        if len(carpetas) == 1:
            dialogo = QMessageBox(self)
            dialogo.setWindowTitle("Carpeta soltada")
            dialogo.setText(f"¿Qué quieres hacer con:\n{carpeta}?")
            btn_organizar = dialogo.addButton("Organizarla ahora", QMessageBox.AcceptRole)
            btn_base = dialogo.addButton("Usarla como principal", QMessageBox.ActionRole)
            dialogo.addButton("Cancelar", QMessageBox.RejectRole)
            dialogo.exec()
            if dialogo.clickedButton() is btn_organizar:
                self._cambiar_carpeta_y_organizar(carpeta, Path(self.organizador.carpeta_descargas))
            elif dialogo.clickedButton() is btn_base:
                self._establecer_carpeta_base(carpeta)
        else:
            self._agregar_log(f"Organizando {len(carpetas)} carpetas soltadas")
            for ruta in carpetas:
                self._cambiar_carpeta_y_organizar(ruta, Path(self.organizador.carpeta_descargas))

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

        # Se llama también al cambiar de carpeta, así que es el sitio adecuado
        # para mantener el motor de permisos apuntando a la carpeta correcta.
        if getattr(self, "permisos", None) is not None:
            self._sincronizar_carpeta_permisos()
        
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

        if hasattr(self, 'lista_historial'):
            self._actualizar_historial()

    # ----------------------------------------------------------- historial

    def _registrar_en_historial(self, resultados, usar_subcarpetas: bool):
        """Guarda la operación en el historial para poder deshacerla luego."""
        try:
            from .historial import obtener_historial

            operacion = obtener_historial().registrar(
                resultados,
                Path(self.organizador.carpeta_descargas),
                "detallado" if usar_subcarpetas else "basico",
            )
            if operacion and hasattr(self, "lista_historial"):
                self._actualizar_historial()
        except Exception as e:
            logger.debug(f"No se pudo registrar la operación: {e}")

    def _resumen_movimientos(self, resultados: dict) -> str:
        """Texto corto con el reparto por categoría (para los avisos)."""
        lineas = []
        for categoria, subcategorias in sorted(resultados.items()):
            total = sum(len(archivos) for archivos in subcategorias.values())
            if total:
                lineas.append(f"· {categoria}: {total}")
        return "\n".join(lineas[:6])

    def _actualizar_historial(self):
        """Rellena la lista de operaciones guardadas."""
        if not hasattr(self, "lista_historial"):
            return
        try:
            from .historial import obtener_historial

            self.lista_historial.clear()
            operaciones = obtener_historial().operaciones()
            if not operaciones:
                item = QListWidgetItem("Todavía no hay organizaciones registradas")
                item.setFlags(Qt.NoItemFlags)
                self.lista_historial.addItem(item)
                self.btn_deshacer_historial.setEnabled(False)
                return

            for operacion in operaciones:
                item = QListWidgetItem(obtener_historial().descripcion(operacion))
                item.setData(Qt.UserRole, operacion)
                self.lista_historial.addItem(item)
            self.lista_historial.setCurrentRow(0)
            self.btn_deshacer_historial.setEnabled(True)
        except Exception as e:
            logger.debug(f"No se pudo actualizar el historial: {e}")

    def _deshacer_del_historial(self):
        """Devuelve a su sitio los archivos de la operación seleccionada."""
        item = self.lista_historial.currentItem()
        if item is None:
            return
        operacion = item.data(Qt.UserRole)
        if not operacion:
            return

        reply = QMessageBox.question(
            self, "Deshacer organización",
            f"¿Devolver a su sitio los archivos de esta operación?\n\n"
            f"{item.text()}\n\n"
            "Solo se moverán los que sigan donde se dejaron.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            from .historial import obtener_historial

            resultado = obtener_historial().deshacer(operacion)
            devueltos = resultado.get("devueltos", 0)
            omitidos = resultado.get("omitidos", 0)
            errores = resultado.get("errores", [])

            mensaje = f"{devueltos} archivo{'s' if devueltos != 1 else ''} devueltos a su sitio."
            if omitidos:
                mensaje += f"\n{omitidos} ya no estaban donde se dejaron (no se han tocado)."
            if errores:
                mensaje += f"\n{len(errores)} no se pudieron mover."
            QMessageBox.information(self, "Deshacer", mensaje)
            self._agregar_log(f"Deshecha organización: {devueltos} archivos devueltos")
            self._actualizar_historial()
            self._actualizar_datos()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo deshacer:\n{e}")

    # ------------------------------------------------------- programación

    def _toggle_programacion(self, activo: bool):
        """Activa o desactiva la organización diaria a una hora concreta."""
        if activo:
            hora = self.edit_hora.time().toString("HH:mm")
            self._hora_programada = hora
            if self.config_portable:
                self.config_portable.establecer("hora_programada", hora)
            self._agregar_log(f"Organización diaria programada a las {hora}")
        else:
            self._hora_programada = None
            if self.config_portable:
                self.config_portable.establecer("hora_programada", None)
            self._agregar_log("Programación diaria desactivada")

        if hasattr(self, "edit_hora"):
            self.edit_hora.setEnabled(bool(activo))
        self._reprogramar_tarea_diaria()
        self._actualizar_texto_programacion()

    def _programacion_hora_cambiada(self, hora):
        """Guarda la nueva hora elegida y reprograma la tarea."""
        if not self._hora_programada:
            return
        texto = hora.toString("HH:mm")
        self._hora_programada = texto
        if self.config_portable:
            self.config_portable.establecer("hora_programada", texto)
        self._reprogramar_tarea_diaria()
        self._actualizar_texto_programacion()
        self._agregar_log(f"Hora de organización diaria cambiada a las {texto}")

    def _reprogramar_tarea_diaria(self):
        """Prepara el temporizador para la próxima ejecución programada."""
        try:
            if not hasattr(self, "timer_programado"):
                self.timer_programado = QTimer(self)
                self.timer_programado.timeout.connect(self._organizacion_programada)
            self.timer_programado.stop()

            if not self._hora_programada:
                return
            restante = programacion.segundos_hasta_la_hora(self._hora_programada)
            if restante is None or restante <= 0:
                return
            # Qt usa milisegundos y su máximo es ~24 días: cabe de sobra
            self.timer_programado.start(restante * 1000)
            logger.debug(f"Programación diaria en {restante} s")
        except Exception as e:
            logger.debug(f"No se pudo programar la tarea diaria: {e}")

    def _organizacion_programada(self):
        """Ejecuta la organización programada y deja lista la siguiente."""
        try:
            self._agregar_log("Organización programada: en marcha")
            usar_subcarpetas = self.chk_subcarpetas.isChecked()
            self.organizador.usar_subcarpetas = usar_subcarpetas
            resultados, errores = self.organizador.reorganizar_completamente()
            total = sum(len(files) for cat in resultados.values() for files in cat.values())
            if total:
                self._registrar_en_historial(resultados, usar_subcarpetas)
                self._agregar_log(f"Organización programada completada: {total} archivos")
                if self.notificador:
                    self.notificador.notificar_organizacion(total, set(resultados.keys()))
            else:
                self._agregar_log("Organización programada: no había nada que mover")
            self._actualizar_datos()
        except Exception as e:
            self._agregar_log(f"Error en la organización programada: {e}")
        finally:
            # Dejar preparada la del día siguiente
            self._reprogramar_tarea_diaria()
            self._actualizar_texto_programacion()

    def _actualizar_texto_programacion(self):
        """Refresca el texto que describe la programación actual."""
        if not hasattr(self, "lbl_programacion"):
            return
        try:
            if self._hora_programada:
                self.lbl_programacion.setText(
                    programacion.descripcion(self._hora_programada)
                )
            else:
                self.lbl_programacion.setText(
                    "Sin programación diaria. Usa el automático de Inicio para intervalos."
                )
        except Exception as e:
            logger.debug(f"No se pudo actualizar el texto de programación: {e}")

    # ------------------------------------------------------------- disco

    def _analizar_disco(self):
        """Muestra un informe de uso de disco de la carpeta actual."""
        try:
            from .analisis_disco import AnalizadorDisco

            self._agregar_log("Analizando el uso de disco…")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            QApplication.processEvents()

            analizador = AnalizadorDisco(Path(self.organizador.carpeta_descargas))
            informe = analizador.informe()
        except Exception as e:
            if hasattr(self, "text_disco"):
                self.text_disco.setPlainText(f"No se pudo analizar: {e}")
            return
        finally:
            self.progress_bar.setVisible(False)

        if hasattr(self, "text_disco"):
            self.text_disco.setPlainText(informe)
        self._agregar_log("Análisis de disco terminado")

    def _limpiar_historial(self):
        """Vacía el historial de operaciones."""
        reply = QMessageBox.question(
            self, "Vaciar historial",
            "¿Olvidar todas las organizaciones registradas?\n\n"
            "Los archivos ya organizados no se tocan.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        try:
            from .historial import obtener_historial

            obtener_historial().limpiar()
            self._actualizar_historial()
            self._agregar_log("Historial vaciado")
        except Exception as e:
            logger.debug(f"No se pudo vaciar el historial: {e}")

    
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
        """Icono de carpeta propio por si falla el dibujo."""
        try:
            return iconos.icono("carpeta", 20, tema=self._tema)
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

    # ============================================================
    #  Auto-organización: un único punto de verdad
    # ============================================================
    # El switch principal decide si está encendida; los radios de modo y el
    # desplegable de intervalo son la configuración que se aplicará. Todo
    # cambio pasa por _aplicar_auto_organizacion, de forma que la interfaz,
    # el temporizador y la configuración guardada nunca se contradicen.

    def _auto_activo(self) -> bool:
        """Indica si el interruptor general está encendido."""
        principal = getattr(self, "chk_auto_principal", None)
        return bool(principal is not None and principal.isChecked())

    def _modo_seleccionado(self) -> str:
        """Modo elegido en los radios ('basico' o 'detallado')."""
        detallado = getattr(self, "chk_auto_detallado", None)
        if detallado is not None and detallado.isChecked():
            return "detallado"
        return "basico"

    def _intervalo_seleccionado(self) -> int:
        """Intervalo elegido en el desplegable, en segundos (mínimo 30)."""
        combo = getattr(self, "combo_intervalo_auto", None)
        if combo is None:
            return 3600
        try:
            return max(30, int(combo.currentData() or 3600))
        except (TypeError, ValueError):
            return 3600

    def _aplicar_auto_organizacion(self, activo: bool, modo=None,
                                   anunciar: bool = False):
        """Aplica de golpe switch, modo e intervalo (timer + interfaz + config).

        Es el único sitio donde se enciende, se apaga o se reconfigura la
        auto-organización. Cualquier control llama aquí, así nunca se quedan
        desincronizados.

        Args:
            activo: si debe estar encendida.
            modo: 'basico' o 'detallado'; si es None se usa el de los radios.
            anunciar: escribir el cambio en la pestaña Actividad.
        """
        modo = modo or self._modo_seleccionado()
        if modo not in ("basico", "detallado"):
            modo = "basico"
        intervalo = self._intervalo_seleccionado()

        # --- temporizador -------------------------------------------------
        if getattr(self, "timer_auto", None) is None:
            self.timer_auto = QTimer(self)
            self.timer_auto.timeout.connect(self._organizar_automatico)
        if activo:
            # start() reinicia la cuenta: el nuevo intervalo se aplica ya
            self.timer_auto.start(intervalo * 1000)
        else:
            self.timer_auto.stop()

        # --- interfaz (sin señales para no reentrar) ----------------------
        self._sincronizando_controles = True
        try:
            principal = getattr(self, "chk_auto_principal", None)
            if principal is not None:
                principal.blockSignals(True)
                principal.setChecked(activo)
                principal.blockSignals(False)

            # Los radios son exclusivos: marcar el correcto desmarca el otro.
            # Se marcan en bucle para que Qt haga la exclusión por nosotros.
            for radio, valor in (
                (getattr(self, "chk_auto_basico", None), "basico"),
                (getattr(self, "chk_auto_detallado", None), "detallado"),
            ):
                if radio is None:
                    continue
                radio.blockSignals(True)
                radio.setChecked(valor == modo)
                radio.blockSignals(False)
        finally:
            self._sincronizando_controles = False

        # --- estado y avisos ----------------------------------------------
        self._auto_modo_guardado = modo
        nombre_modo = "Básico" if modo == "basico" else "Detallado"
        self._pintar_estado(activo, nombre_modo)

        if getattr(self, "tray_icon", None):
            if activo:
                self.tray_icon.setToolTip(
                    f"Auto-organización {nombre_modo.upper()} ({intervalo} s)"
                )
            else:
                self.tray_icon.setToolTip("Organización automática inactiva")

        if anunciar:
            if activo:
                self._agregar_log(
                    f"Auto-organización {nombre_modo} ACTIVADA "
                    f"({self.combo_intervalo_auto.currentText()})"
                )
            else:
                self._agregar_log("Auto-organización DESACTIVADA")

        # --- persistencia --------------------------------------------------
        self._guardar_estado_auto(activo, modo, intervalo)

    def _guardar_estado_auto(self, activo: bool, modo: str, intervalo: int):
        """Guarda switch, modo e intervalo, y sincroniza el autoarranque."""
        if not self.config_portable:
            return
        try:
            self.config_portable.establecer("auto_organizacion", bool(activo))
            self.config_portable.establecer("auto_modo", modo)
            self.config_portable.establecer("auto_intervalo", int(intervalo))

            # Si el autoarranque del sistema está activo, se reescribe con el
            # modo elegido; si la auto-organización se apagó, se deja el
            # autoarranque sin modo para que al iniciar no organice sola.
            if self.config_portable.obtener("autoarranque", False):
                self._sincronizar_autoarranque(modo if activo else None)
        except Exception as e:
            logger.debug(f"No se pudo guardar el estado de la auto-organización: {e}")

    # ------------------------------------------------- controles de la vista

    def _toggle_auto_principal(self, activo):
        """Interruptor general: enciende o apaga la organización automática."""
        if getattr(self, "_sincronizando_controles", False):
            return
        self._aplicar_auto_organizacion(activo, anunciar=True)

    def _toggle_auto_organizacion(self, activo):
        """Compatibilidad: el interruptor general manda."""
        if getattr(self, "chk_auto_principal", None) is not None:
            self.chk_auto_principal.setChecked(activo)

    @Slot(bool)
    def _toggle_auto_organizacion_basico(self, activo):
        """El usuario ha elegido el modo Básico."""
        if getattr(self, "_sincronizando_controles", False) or not activo:
            return
        self._aplicar_auto_organizacion(self._auto_activo(), modo="basico", anunciar=True)

    @Slot(bool)
    def _toggle_auto_organizacion_detallado(self, activo):
        """El usuario ha elegido el modo Detallado."""
        if getattr(self, "_sincronizando_controles", False) or not activo:
            return
        self._aplicar_auto_organizacion(self._auto_activo(), modo="detallado", anunciar=True)

    def _cambiar_intervalo_auto(self, index):
        """Cambia cada cuánto se revisa la carpeta (con efecto inmediato)."""
        if getattr(self, "_sincronizando_controles", False):
            return
        self._aplicar_auto_organizacion(self._auto_activo(), anunciar=True)

    def _sincronizar_switch_principal(self, activo):
        """Mantiene el interruptor general coherente (uso interno)."""
        if getattr(self, "_sincronizando_controles", False):
            return
        if getattr(self, "chk_auto_principal", None) is not None:
            self.chk_auto_principal.setChecked(activo)

    def _actualizar_estado_auto_organizacion(self):
        """Refresca la tarjeta de estado a partir del estado real."""
        timer = getattr(self, "timer_auto", None)
        activo = bool(getattr(self, "chk_auto_principal", None)
                      and self.chk_auto_principal.isChecked()
                      and timer is not None and timer.isActive())
        nombre_modo = "Detallado" if self._modo_seleccionado() == "detallado" else "Básico"
        self._pintar_estado(activo, nombre_modo)
        if not activo and getattr(self, "tray_icon", None):
            self.tray_icon.setToolTip("Organización automática inactiva")

    def _pintar_estado(self, activo, modo=None):
        """Actualiza la tarjeta superior de estado (Inicio)."""
        try:
            intervalo = self.combo_intervalo_auto.currentText() if hasattr(self, "combo_intervalo_auto") else ""
            if activo:
                self._punto_estado.setProperty("estado", "activo")
                self.lbl_estado.setText(f"Auto-organización activa · modo {modo or 'Básico'}")
                self.lbl_estado_detalle.setText(f"Revisando la carpeta cada {intervalo.lower()}")
                if getattr(self, 'tray_icon', None):
                    self.tray_icon.setToolTip(f"Auto-organización {modo or 'Básico'} ({intervalo})")
            else:
                self._punto_estado.setProperty("estado", "inactivo")
                self.lbl_estado.setText("Auto-organización desactivada")
                self.lbl_estado_detalle.setText("Actívala para que la carpeta se ordene sola")
            # Refrescar el color del punto según la nueva propiedad
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

        if event.type() == QEvent.Type.ActivationChange and self.isActiveWindow():
            # El usuario vuelve de Ajustes del sistema: puede haber concedido
            # un permiso, así que se comprueba sin obligarle a reiniciar.
            QTimer.singleShot(0, self._revisar_permisos_pendientes)

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
        """Configura la interfaz: barra lateral adaptativa y contenido centrado.

        En ventanas anchas el contenido se limita a un ancho máximo y se centra
        (como hacen los paneles de Ajustes del Sistema), de modo que los
        controles no se estiren hasta las esquinas. La barra lateral se estrecha
        o ensancha según el espacio disponible.
        """
        central = QWidget()
        self.setCentralWidget(central)
        raiz = QHBoxLayout(central)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)

        # ----------------------------------------------------- barra lateral
        self.panel_lateral = QWidget()
        self.panel_lateral.setObjectName("panelLateral")
        self.panel_lateral.setFixedWidth(ANCHO_LATERAL_NORMAL)
        lateral_layout = QVBoxLayout(self.panel_lateral)
        lateral_layout.setContentsMargins(0, 0, 0, 0)
        lateral_layout.setSpacing(0)

        self.lista_lateral = QListWidget()
        self.lista_lateral.setProperty("rol", "lateral")
        self.lista_lateral.setFrameShape(QFrame.NoFrame)
        self.lista_lateral.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.lista_lateral.setIconSize(QSize(17, 17))
        self.lista_lateral.setSpacing(2)
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

        raiz.addWidget(self.panel_lateral)

        # ------------------------------------------------------------ zona
        self.zona_contenido = QWidget()
        zona_layout = QVBoxLayout(self.zona_contenido)
        zona_layout.setContentsMargins(0, 0, 0, 0)
        zona_layout.setSpacing(0)

        # Contenedor centrado: el ancho efectivo lo fija _actualizar_layout()
        self._centro = QWidget()
        self._centro.setObjectName("contenidoCentrado")
        contenido_layout = QVBoxLayout(self._centro)
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

        # Centrado horizontal: márgenes elásticos a los lados
        fila_centro = QHBoxLayout()
        fila_centro.setContentsMargins(0, 0, 0, 0)
        fila_centro.setSpacing(0)
        fila_centro.addStretch(1)
        fila_centro.addWidget(self._centro, 0)
        fila_centro.addStretch(1)
        zona_layout.addLayout(fila_centro)

        raiz.addWidget(self.zona_contenido, 1)

        self.statusBar().showMessage("Listo")

        # Vistas dentro del stack
        self._vistas = []
        self._crear_vista_inicio()
        self._crear_vista_historial()
        self._crear_vista_actividad()
        self._crear_vista_ajustes()
        self._crear_vista_avanzado()

        # Elementos de la barra lateral (icono propio + nombre)
        self._entradas_lateral = [
            ("Inicio", "inicio"),
            ("Historial", "historial"),
            ("Actividad", "actividad"),
            ("Ajustes", "ajustes"),
            ("Avanzado", "avanzado"),
        ]
        for texto, nombre_icono in self._entradas_lateral:
            item = QListWidgetItem()
            item.setText(texto)
            item.setData(Qt.UserRole, nombre_icono)
            self.lista_lateral.addItem(item)
        self._refrescar_iconos_lateral()

        self.lista_lateral.setCurrentRow(0)
        self._actualizar_layout()

    def _refrescar_iconos_lateral(self):
        """Redibuja los iconos de la barra lateral con el color del tema.

        Hace falta repetirlo al cambiar de tema: los iconos son SVG pintados en
        el color del texto, no máscaras que Qt pueda recolorear solo.
        """
        if not hasattr(self, "lista_lateral"):
            return
        for indice in range(self.lista_lateral.count()):
            item = self.lista_lateral.item(indice)
            nombre = item.data(Qt.UserRole)
            if not nombre:
                continue
            item.setIcon(iconos.icono_lateral(nombre, 18, tema=self._tema))

    def _aplicar_modo_lateral(self, compacta: bool):
        """Muestra la barra lateral solo con iconos o con icono y texto."""
        for indice in range(self.lista_lateral.count()):
            item = self.lista_lateral.item(indice)
            # El texto completo se recuerda la primera vez
            if item.data(Qt.UserRole + 1) is None:
                item.setData(Qt.UserRole + 1, item.text())
            texto = item.data(Qt.UserRole + 1)
            item.setText("" if compacta else texto)
            item.setToolTip(texto if compacta else "")
            item.setTextAlignment(
                Qt.AlignCenter if compacta else (Qt.AlignLeft | Qt.AlignVCenter)
            )

    def showEvent(self, event):
        """Aplica el efecto del sistema la primera vez que se muestra.

        Hace falta esperar a que la ventana exista de verdad para poder pedirle
        su identificador nativo a Qt.
        """
        super().showEvent(event)
        if not getattr(self, "_efecto_nativo_intentado", False):
            self._efecto_nativo_intentado = True
            QTimer.singleShot(0, self._aplicar_efecto_nativo)

        # El asistente de permisos se muestra una sola vez, y con la ventana ya
        # visible, para que no aparezca antes que la propia aplicación.
        if not getattr(self, "_asistente_comprobado", False):
            self._asistente_comprobado = True
            QTimer.singleShot(400, self._mostrar_asistente_si_toca)

    def _mostrar_asistente_si_toca(self):
        """Presenta los permisos la primera vez que se abre la aplicación."""
        try:
            if not primer_arranque.debe_mostrarse(self.config_portable):
                return
            self.mostrar_asistente_permisos()
        except Exception as e:
            logger.debug(f"No se pudo mostrar el asistente: {e}")

    def mostrar_asistente_permisos(self):
        """Abre el asistente de permisos (también desde Ajustes)."""
        try:
            dialogo = primer_arranque.DialogoPrimerArranque(self.permisos, self)
            dialogo.exec()
            primer_arranque.marcar_como_visto(self.config_portable)
            self._actualizar_centro_permisos()
            self._agregar_log("Revisión de permisos completada")
        except Exception as e:
            logger.debug(f"No se pudo abrir el asistente de permisos: {e}")

    def resizeEvent(self, event):
        """Recalcula el layout al cambiar el tamaño de la ventana."""
        super().resizeEvent(event)
        self._actualizar_layout()

    def _actualizar_layout(self):
        """Adapta barra lateral y ancho del contenido al tamaño disponible.

        - Barra lateral: compacta en ventanas estrechas, normal en el resto.
        - Contenido: ancho máximo legible y centrado; el espacio sobrante se
          reparte a los lados para que nada quede descolgado en las esquinas.
        """
        try:
            ancho = self.width()

            # Barra lateral: el ancho se guarda en una variable propia porque
            # Qt puede aplicar setFixedWidth antes de que lo consultemos.
            if ancho < 860:
                ancho_lateral = ANCHO_LATERAL_COMPACTO
            elif ancho > 1600:
                ancho_lateral = ANCHO_LATERAL_AMPLIO
            else:
                ancho_lateral = ANCHO_LATERAL_NORMAL

            if getattr(self, "_ancho_lateral_aplicado", None) != ancho_lateral:
                self._ancho_lateral_aplicado = ancho_lateral
                self.panel_lateral.setFixedWidth(ancho_lateral)
                self._aplicar_modo_lateral(ancho_lateral == ANCHO_LATERAL_COMPACTO)

            # Ancho del contenido centrado
            disponible = max(320, ancho - ancho_lateral - 48)
            ancho_contenido = min(disponible, ANCHO_CONTENIDO_MAXIMO)
            self._centro.setMaximumWidth(ANCHO_CONTENIDO_MAXIMO)
            self._centro.setMinimumWidth(min(ancho_contenido, ANCHO_CONTENIDO_MAXIMO))

            # Los márgenes laterales del centro se reducen en ventanas pequeñas
            margen = 24 if ancho > 900 else 16
            layout = self._centro.layout()
            if layout is not None:
                layout.setContentsMargins(margen, 20, margen, 14)
        except Exception as e:
            logger.debug(f"No se pudo ajustar el layout: {e}")

    def _cambiar_vista(self, indice):
        """Cambia la vista activa con una transición suave."""
        if indice < 0:
            return
        self.stack.setCurrentIndex(indice)
        self._vista_actual = indice
        titulos = ["Inicio", "Historial", "Actividad", "Ajustes", "Avanzado"]
        if indice < len(titulos):
            self.lbl_titulo_vista.setText(titulos[indice])
        # El botón de cabecera solo tiene sentido en Inicio y Ajustes
        self.btn_cabecera_principal.setVisible(indice in (0, 3))
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
        punto.setProperty("rol", "punto")
        punto.setProperty("estado", "inactivo")
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

    def _crear_vista_disco(self, destino=None):
        """Vista de análisis de disco: qué ocupa espacio y qué se puede limpiar."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)

        fila = QHBoxLayout()
        btn_analizar = QPushButton("Analizar uso de disco")
        btn_analizar.setProperty("rol", "primario")
        btn_analizar.clicked.connect(self._analizar_disco)
        fila.addWidget(btn_analizar)
        aviso = QLabel("Solo lectura: no se borra ni se mueve nada.")
        aviso.setProperty("rol", "secundaria")
        fila.addWidget(aviso)
        fila.addStretch()
        layout.addLayout(fila)

        self.text_disco = QPlainTextEdit()
        self.text_disco.setReadOnly(True)
        self.text_disco.setPlaceholderText(
            "Pulsa «Analizar» para ver qué ocupa espacio en la carpeta."
        )
        layout.addWidget(self.text_disco, 1)

        contenedor = self._contenedor_scroll(tab)
        if destino is not None:
            destino.addTab(contenedor, "Disco")
        else:
            self._vistas.append(tab)
            self.stack.addWidget(self._contenedor_scroll(tab))

    def _crear_vista_historial(self):
        """Vista de historial: últimas organizaciones, con opción de deshacer."""
        vista = QWidget()
        layout = QVBoxLayout(vista)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        aviso = QLabel(
            "Cada organización queda registrada aquí para poder deshacerla cuando quieras."
        )
        aviso.setProperty("rol", "secundaria")
        aviso.setWordWrap(True)
        layout.addWidget(aviso)

        self.lista_historial = QListWidget()
        self.lista_historial.currentItemChanged.connect(
            lambda *_: self.btn_deshacer_historial.setEnabled(
                self.lista_historial.currentItem() is not None
                and self.lista_historial.currentItem().data(Qt.UserRole) is not None
            )
        )
        layout.addWidget(self.lista_historial, 1)

        botones = QHBoxLayout()
        self.btn_deshacer_historial = QPushButton("Deshacer seleccionada")
        self.btn_deshacer_historial.setToolTip(
            "Devuelve esos archivos a donde estaban antes de organizarlos"
        )
        self.btn_deshacer_historial.clicked.connect(self._deshacer_del_historial)
        botones.addWidget(self.btn_deshacer_historial)

        btn_refrescar = QPushButton("Actualizar")
        btn_refrescar.clicked.connect(self._actualizar_historial)
        botones.addWidget(btn_refrescar)

        btn_limpiar = QPushButton("Vaciar historial")
        btn_limpiar.setProperty("rol", "peligro")
        btn_limpiar.clicked.connect(self._limpiar_historial)
        botones.addWidget(btn_limpiar)
        botones.addStretch()
        layout.addLayout(botones)

        self._vistas.append(vista)
        self.stack.addWidget(self._contenedor_scroll(vista))

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

        # --- Permisos ------------------------------------------------------
        layout.addWidget(self._crear_centro_permisos())

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

        # --- Programación --------------------------------------------------
        programacion_group = QGroupBox("Programación diaria")
        programacion_layout = QVBoxLayout(programacion_group)
        programacion_layout.setSpacing(10)

        fila_hora = QHBoxLayout()
        self.chk_programar = Switch("Organizar a una hora concreta")
        self.chk_programar.setToolTip(
            "Además del automático, organiza la carpeta todos los días a esta hora"
        )
        self.chk_programar.setChecked(bool(self._hora_programada))
        self.chk_programar.toggled.connect(self._toggle_programacion)
        fila_hora.addWidget(self.chk_programar)
        fila_hora.addStretch()

        self.edit_hora = QTimeEdit()
        self.edit_hora.setDisplayFormat("HH:mm")
        self.edit_hora.setWrapping(True)
        if self._hora_programada:
            partes = programacion.parsear_hora(self._hora_programada)
            if partes:
                self.edit_hora.setTime(QTime(partes[0], partes[1]))
        if not self._hora_programada:
            self.edit_hora.setTime(QTime(22, 0))
        self.edit_hora.timeChanged.connect(self._programacion_hora_cambiada)
        self.edit_hora.setEnabled(bool(self._hora_programada))
        fila_hora.addWidget(self.edit_hora)
        programacion_layout.addLayout(fila_hora)

        self.lbl_programacion = QLabel("")
        self.lbl_programacion.setProperty("rol", "secundaria")
        programacion_layout.addWidget(self.lbl_programacion)
        layout.addWidget(programacion_group)
        self._actualizar_texto_programacion()

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

    def _dar_ancho_a_tabs(self, barra):
        """Fija el ancho mínimo de la barra de pestañas según sus títulos.

        Dentro de un área desplazable, el ``QTabBar`` puede quedarse con muy
        poco ancho y recortar los nombres; aquí se mide el texto real de cada
        pestaña (con su fuente y relleno) y se reserva ese espacio.
        """
        try:
            from PySide6.QtGui import QFontMetrics

            fuente = barra.font()
            metrica = QFontMetrics(fuente)
            # Relleno lateral de las pestañas según la hoja de estilo + iconos
            relleno = 34
            ancho = 0
            for indice in range(barra.count()):
                texto = barra.tabText(indice)
                ancho += metrica.horizontalAdvance(texto) + relleno
            if ancho:
                barra.setMinimumWidth(ancho + 8)
                self.tabs_avanzado.setMinimumWidth(ancho + 8)
                logger.debug(f"Ancho reservado para las pestañas: {ancho + 8}px")
        except Exception as e:
            logger.debug(f"No se pudo ajustar el ancho de las pestañas: {e}")

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
        # Las pestañas deben verse enteras: sin recorte ni compresión
        barra_tabs = self.tabs_avanzado.tabBar()
        barra_tabs.setExpanding(False)
        barra_tabs.setUsesScrollButtons(True)
        barra_tabs.setElideMode(Qt.ElideNone)
        # El QTabBar hereda un ancho mínimo pequeño cuando vive dentro de un
        # scroll: fijarlo al tamaño que piden sus títulos evita que se corten.
        ancho_necesario = 0
        from PySide6.QtWidgets import QStyleOptionTab
        self.tabs_avanzado.setDocumentMode(True)
        layout.addWidget(self.tabs_avanzado, 1)
        QTimer.singleShot(0, lambda: self._dar_ancho_a_tabs(barra_tabs))

        self._crear_vista_ia(destino=self.tabs_avanzado)
        self._crear_vista_fechas(destino=self.tabs_avanzado)
        self._crear_vista_duplicados(destino=self.tabs_avanzado)
        self._crear_vista_estadisticas(destino=self.tabs_avanzado)
        self._crear_vista_disco(destino=self.tabs_avanzado)

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
        """Organiza los archivos mostrando antes qué se va a mover."""
        usar_subcarpetas = self.chk_subcarpetas.isChecked()
        modo = "detallado" if usar_subcarpetas else "básico"

        # 1) Calcular el plan sin tocar nada
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            QApplication.processEvents()
            self.organizador.usar_subcarpetas = usar_subcarpetas
            plan = self.organizador.planificar_organizacion()
        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "Error", f"No se pudo analizar la carpeta:\n{e}")
            return
        finally:
            self.progress_bar.setVisible(False)

        # 2) Enseñar el plan y pedir confirmación
        if not self._confirmar_plan(plan, modo):
            return

        # 3) Ejecutar
        try:
            self.btn_organizar.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            QApplication.processEvents()

            resultados, errores = self.organizador.reorganizar_completamente()
            total = sum(len(files) for cat in resultados.values() for files in cat.values())

            self._registrar_en_historial(resultados, usar_subcarpetas)
            self._actualizar_datos()

            if total == 0:
                QMessageBox.information(
                    self, "Nada que hacer",
                    "Todos los archivos ya estaban en su sitio."
                )
            else:
                resumen = self._resumen_movimientos(resultados)
                aviso = f"\n\n{len(errores)} avisos (consulta Actividad)" if errores else ""
                QMessageBox.information(
                    self, "Organización completada",
                    f"{total} archivo{'s' if total != 1 else ''} ordenados.\n\n{resumen}{aviso}"
                )
                self._agregar_log(f"Organización completada: {total} archivos (modo {modo})")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo organizar:\n{e}")
            self._agregar_log(f"Error en la organización: {e}")
        finally:
            self.btn_organizar.setEnabled(True)
            self.progress_bar.setVisible(False)

    def _confirmar_plan(self, plan: dict, modo: str) -> bool:
        """Muestra el plan de organización y devuelve True si se confirma.

        Es la parte de «previsualizar antes de organizar»: se ve qué archivos
        se moverán, a qué carpeta, cuánto espacio y qué se queda fuera.
        """
        total = plan.get("total", 0)
        errores = plan.get("errores", [])
        ya_ordenados = plan.get("ya_ordenados", 0)

        if total == 0:
            detalle = "No hay archivos pendientes de organizar."
            if ya_ordenados:
                detalle += f"\n\nYa hay {ya_ordenados} archivo(s) en su sitio."
            if errores:
                detalle += f"\n\n{len(errores)} aviso(s):\n" + "\n".join(errores[:3])
            QMessageBox.information(self, "Nada que organizar", detalle)
            return False

        dialogo = DialogoPrevisualizacion(plan, modo, self)
        return dialogo.exec() == QDialog.Accepted

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
        """Cambia el tema visual de la aplicación (claro / oscuro / automático)."""
        tema_nombre = self.combo_temas.itemData(index)
        if not tema_nombre:
            return

        self._tema = tema_nombre
        self._aplicar_tema()

        # Guardar en configuración
        if self.config_portable:
            self.config_portable.establecer("tema", tema_nombre)

        self._agregar_log(f"Tema cambiado a: {self.combo_temas.currentText()}")
    
    def _crear_centro_permisos(self) -> QGroupBox:
        """Construye el centro de permisos: estado en vivo y botón para resolver.

        Responde de un vistazo a la pregunta «¿por qué no me funciona esto?»,
        que hasta ahora obligaba a leer el registro.
        """
        grupo = QGroupBox("Permisos")
        layout = QVBoxLayout(grupo)
        layout.setSpacing(8)

        self._filas_permisos = {}

        for capacidad in permisos.CATALOGO:
            fila = QWidget()
            fila_layout = QHBoxLayout(fila)
            fila_layout.setContentsMargins(0, 2, 0, 2)
            fila_layout.setSpacing(10)

            punto = QLabel("●")
            punto.setProperty("rol", "punto")
            punto.setFixedWidth(16)
            fila_layout.addWidget(punto)

            textos = QVBoxLayout()
            textos.setSpacing(1)

            nombre = QLabel(capacidad.nombre)
            nombre.setProperty("rol", "etiqueta")
            textos.addWidget(nombre)

            detalle = QLabel("")
            detalle.setProperty("rol", "secundaria")
            detalle.setWordWrap(True)
            textos.addWidget(detalle)

            fila_layout.addLayout(textos, 1)

            boton = QPushButton("Conceder…")
            boton.setProperty("rol", "plano")
            boton.setToolTip(f"Sirve para {capacidad.para_que}")
            boton.clicked.connect(
                lambda _=False, c=capacidad.id: self._accion_permiso(c)
            )
            fila_layout.addWidget(boton, 0, Qt.AlignTop)

            layout.addWidget(fila)
            self._filas_permisos[capacidad.id] = (punto, detalle, boton)

        nota = QLabel(
            "Los permisos son opcionales salvo el acceso a la carpeta. Si falta "
            "alguno, la aplicación funciona con menos funciones y lo indica."
        )
        nota.setProperty("rol", "discreta")
        nota.setWordWrap(True)
        layout.addWidget(nota)

        btn_revisar = QPushButton("Volver a revisar los permisos…")
        btn_revisar.setProperty("rol", "plano")
        btn_revisar.clicked.connect(self.mostrar_asistente_permisos)
        layout.addWidget(btn_revisar, 0, Qt.AlignLeft)

        # Primer pintado del estado (la comprobación de red se omite aquí
        # porque implica una llamada de red que el usuario no ha pedido).
        QTimer.singleShot(0, self._actualizar_centro_permisos)
        return grupo

    def _toggle_menu_contextual(self, activo):
        """Toggle integración menú contextual."""
        if not self.gestor_menu_contextual:
            return

        try:
            if activo:
                # Antes de intentarlo: si el sistema necesita un permiso, se
                # pide. Es preferible pedirlo a registrar a ciegas y fallar.
                if not self._asegurar_permiso("acceso_total_disco"):
                    self._revertir_switch_menu_contextual()
                    return

                exito, mensaje = self.gestor_menu_contextual.registrar_menu_contextual("carpetas")
                if exito:
                    self._agregar_log("Menú contextual registrado")
                    if self.notificador:
                        self.notificador.mostrar(
                            "Menú contextual",
                            "Ya puedes organizar con clic derecho sobre una carpeta.",
                            tipo="success", duracion=4,
                        )
                    # Un registro correcto pero con el Finder sin refrescar deja
                    # la acción invisible: hay que decirlo, no ocultarlo.
                    if "Aviso:" in mensaje:
                        self._agregar_log(mensaje.split("Aviso:", 1)[1].strip())
                else:
                    self._agregar_log(f"No se pudo registrar: {mensaje}")
                    self._revertir_switch_menu_contextual()
                    self._mostrar_permiso_o_error("Menú contextual", mensaje)
            else:
                exito, mensaje = self.gestor_menu_contextual.desregistrar_menu_contextual()
                if exito:
                    self._agregar_log("Menú contextual eliminado")
                else:
                    self._agregar_log(f"Error: {mensaje}")
        except Exception as e:
            self._agregar_log(f"Error configurando menú contextual: {e}")
            self._revertir_switch_menu_contextual()
            QMessageBox.critical(self, "Error", f"Error: {e}")

    def _revertir_switch_menu_contextual(self):
        """Devuelve el interruptor a su posición real sin re-disparar el aviso."""
        if not hasattr(self, "chk_menu_contextual"):
            return
        self.chk_menu_contextual.blockSignals(True)
        self.chk_menu_contextual.setChecked(False)
        self.chk_menu_contextual.blockSignals(False)

    # ------------------------------------------------------------ permisos

    def _asegurar_permiso(self, capacidad_id: str) -> bool:
        """Comprueba un permiso y, si falta, lo pide **antes** de fallar.

        Devuelve True si la operación puede seguir. Si falta el permiso, muestra
        qué hace falta, para qué sirve y un botón que lleva al sitio exacto
        donde concederlo.
        """
        try:
            resultado = self.permisos.comprobar(capacidad_id)
        except KeyError:
            return True

        if resultado.disponible:
            return True

        capacidad = resultado.capacidad
        texto = f"Hace falta para {capacidad.para_que}."
        if resultado.detalle:
            texto = f"{resultado.detalle}\n\n{texto}"
        if capacidad.degradacion:
            texto += f"\n\n{capacidad.degradacion}"

        caja = QMessageBox(self)
        caja.setIcon(QMessageBox.Warning)
        caja.setWindowTitle("Permiso necesario")
        caja.setText(capacidad.nombre)
        caja.setInformativeText(texto)

        boton_pedir = None
        if resultado.accion:
            boton_pedir = caja.addButton(resultado.accion, QMessageBox.AcceptRole)
        caja.addButton("Ahora no", QMessageBox.RejectRole)
        caja.exec()

        if boton_pedir is not None and caja.clickedButton() is boton_pedir:
            self._solicitar_permiso(capacidad_id)
        return False

    def _accion_permiso(self, capacidad_id: str):
        """Qué hace el botón de una fila del centro de permisos.

        La conexión a internet no se «concede»: se comprueba. El resto de
        permisos sí llevan al sitio donde se conceden.
        """
        if capacidad_id == "red":
            self._actualizar_centro_permisos(incluir_red=True)
            return
        self._solicitar_permiso(capacidad_id)

    def _solicitar_permiso(self, capacidad_id: str):
        """Abre el sitio donde se concede el permiso y queda a la espera."""
        try:
            resultado = self.permisos.solicitar(capacidad_id)
        except KeyError:
            return

        self._permisos_pendientes.add(capacidad_id)
        self._actualizar_centro_permisos()

        if resultado.detalle:
            QMessageBox.information(self, resultado.capacidad.nombre, resultado.detalle)

    def _mostrar_permiso_o_error(self, titulo: str, mensaje: str):
        """Explica un fallo, y ofrece pedir el permiso si es lo que falta."""
        caja = QMessageBox(self)
        caja.setIcon(QMessageBox.Warning)
        caja.setWindowTitle(titulo)
        caja.setText("No se pudo completar la operación")
        caja.setInformativeText(mensaje)
        caja.addButton(QMessageBox.Ok)
        caja.exec()

    def _revisar_permisos_pendientes(self):
        """Detecta permisos concedidos fuera de la app sin necesidad de reiniciar.

        Se llama cuando la ventana recupera el foco: el usuario suele salir a
        Ajustes del sistema, conceder el permiso y volver.
        """
        if not getattr(self, "_permisos_pendientes", None):
            return

        concedidos = []
        for capacidad_id in list(self._permisos_pendientes):
            try:
                if self.permisos.comprobar(capacidad_id).disponible:
                    concedidos.append(capacidad_id)
            except KeyError:
                self._permisos_pendientes.discard(capacidad_id)

        if not concedidos:
            return

        for capacidad_id in concedidos:
            self._permisos_pendientes.discard(capacidad_id)

        nombres = ", ".join(
            permisos.CAPACIDADES_POR_ID[c].nombre
            for c in concedidos
            if c in permisos.CAPACIDADES_POR_ID
        )
        self._agregar_log(f"Permiso concedido: {nombres}")
        if self.notificador:
            self.notificador.mostrar(
                "Permiso concedido", nombres, tipo="success", duracion=4
            )
        self._actualizar_centro_permisos()

    def _actualizar_centro_permisos(self, incluir_red: bool = False):
        """Repinta el estado del centro de permisos de Ajustes.

        La conexión a internet se deja sin comprobar salvo que la pida el
        usuario: comprobarla implica una llamada de red, y no tiene sentido
        hacer tráfico cada vez que se abre Ajustes.
        """
        filas = getattr(self, "_filas_permisos", None)
        if not filas:
            return
        for capacidad_id, widgets in filas.items():
            punto, detalle, boton = widgets

            if capacidad_id == "red" and not incluir_red:
                punto.setProperty("estado", "inactivo")
                punto.style().unpolish(punto)
                punto.style().polish(punto)
                detalle.setText("Todavía sin comprobar.")
                boton.setText("Comprobar")
                boton.setVisible(True)
                continue

            try:
                resultado = self.permisos.comprobar(capacidad_id)
            except KeyError:
                continue
            punto.setProperty("estado", self._estado_a_color(resultado.estado))
            punto.style().unpolish(punto)
            punto.style().polish(punto)

            if resultado.detalle:
                detalle.setText(resultado.detalle)
            else:
                detalle.setText(resultado.estado.etiqueta)

            # El botón solo tiene sentido mientras falte el permiso.
            boton.setText("Conceder…")
            boton.setVisible(not resultado.disponible)

    @staticmethod
    def _estado_a_color(estado) -> str:
        """Traduce un estado de permiso al color del punto indicador."""
        if estado.disponible:
            return "activo"
        if estado is permisos.EstadoPermiso.DENEGADO:
            return "error"
        if estado is permisos.EstadoPermiso.PENDIENTE:
            return "aviso"
        return "inactivo"

    def _verificar_actualizaciones_silencioso(self):
        """Verifica actualizaciones en segundo plano sin mostrar mensaje si no hay."""
        if not self.gestor_actualizaciones:
            return
        
        try:
            self._agregar_log("Verificando actualizaciones en segundo plano...")
            hay_actualizacion, info = self.gestor_actualizaciones.verificar_actualizaciones()
            
            if hay_actualizacion and info:
                version = info.get('version', 'Desconocida')
                self._agregar_log(f"¡Nueva versión {version} disponible!")
                self._mostrar_notificacion_actualizacion(info)
            elif self.gestor_actualizaciones.comprobacion_fallida():
                self._agregar_log(
                    "No se pudo comprobar la actualización ahora; se reintentará más tarde"
                )
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
            elif self.gestor_actualizaciones.comprobacion_fallida():
                # No es lo mismo «no hay nada nuevo» que «no se pudo mirar»
                QMessageBox.warning(
                    self,
                    "No se pudo comprobar",
                    "GitHub no ha respondido a la comprobación (puede ser un límite "
                    "temporal de peticiones).\n\n"
                    "Vuelve a intentarlo dentro de unos minutos: no se ha podido "
                    "confirmar si hay una versión nueva."
                )
                self._agregar_log("Comprobación de actualizaciones no disponible (se reintentará)")
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
        """Devuelve un aviso legible si no se puede trabajar con la carpeta.

        Delega en el motor de permisos, que comprueba la escritura de verdad
        creando un archivo temporal. ``os.access`` puede mentir cuando hay
        listas de control de acceso o un entorno aislado, así que no basta.
        """
        gestor = permisos.obtener_gestor_permisos(Path(carpeta))
        ok, mensaje = gestor.requerir("carpeta_descargas")
        if ok:
            # La carpeta de referencia del gestor pasa a ser la nueva.
            self.permisos.carpeta_descargas = Path(carpeta)
            return None

        sugerencia = gestor.comprobar("carpeta_descargas").accion
        if sugerencia:
            mensaje = f"{mensaje}\n\nSugerencia: {sugerencia.lower()}."
        return mensaje

    def _sincronizar_carpeta_permisos(self):
        """Mantiene el motor de permisos apuntando a la carpeta actual."""
        try:
            self.permisos.carpeta_descargas = Path(self.organizador.carpeta_descargas)
        except Exception as e:
            logger.debug(f"No se pudo sincronizar la carpeta de permisos: {e}")

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
        """Carga modo e intervalo guardados sin encender la auto-organización.

        El switch principal se queda apagado; si la configuración dice que
        estaba activa, ``_activar_auto_guardada`` la enciende justo después.
        """
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
            combo = getattr(self, "combo_intervalo_auto", None)
            if combo is not None and intervalo:
                indice = combo.findData(int(intervalo))
                if indice >= 0:
                    combo.setCurrentIndex(indice)

            self._auto_modo_guardado = modo

            # Dejar los controles en el modo guardado, pero apagados: si la
            # auto-organización estaba activa, se enciende a continuación.
            principal = getattr(self, "chk_auto_principal", None)
            if principal is not None:
                principal.blockSignals(True)
                principal.setChecked(False)
                principal.blockSignals(False)

            for radio, valor in (
                (getattr(self, "chk_auto_basico", None), "basico"),
                (getattr(self, "chk_auto_detallado", None), "detallado"),
            ):
                if radio is None:
                    continue
                radio.blockSignals(True)
                radio.setChecked(valor == modo)
                radio.blockSignals(False)

            self._pintar_estado(False, "Básico" if modo == "basico" else "Detallado")
        except Exception as e:
            logger.debug(f"No se pudieron restaurar las preferencias de auto-organización: {e}")
        finally:
            self._sincronizando_controles = False

    def _activar_auto_guardada(self):
        """Enciende la auto-organización con el modo e intervalo guardados."""
        modo = getattr(self, "_auto_modo_guardado", "basico")
        try:
            self._aplicar_auto_organizacion(True, modo=modo, anunciar=True)
        except Exception as e:
            logger.debug(f"No se pudo activar la auto-organización guardada: {e}")

    def _sincronizar_autoarranque(self, modo):
        """Reescribe el autoarranque del sistema con el modo actual.

        ``modo=None`` deja el autoarranque sin organización automática (la app
        arranca minimizada pero no ordena sola).
        """
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

    # Garantiza que los fallos dentro de la interfaz se muestren de forma
    # legible en lugar de morir en la consola (que en modo ventana no se ve).
    errores.instalar_manejador_global()

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
