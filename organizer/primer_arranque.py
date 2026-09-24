#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Asistente de primer arranque: pide los permisos una sola vez, bien explicados.

En lugar de descubrir los permisos a base de errores, la primera vez que se
abre la aplicación se presenta en una sola ventana qué necesita y para qué,
en lenguaje llano. Todo es omitible: la aplicación arranca igual sin ningún
permiso concedido, simplemente con menos funciones.
"""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from . import permission_manager as permisos

logger = logging.getLogger('organizador.primer_arranque')

CLAVE_CONFIG = "primer_arranque_visto"


class DialogoPrimerArranque(QDialog):
    """Ventana de bienvenida que explica y solicita los permisos."""

    def __init__(self, gestor_permisos: permisos.GestorPermisos, parent=None):
        super().__init__(parent)
        self.permisos = gestor_permisos
        self._filas = {}

        self.setWindowTitle("Bienvenido a DescargasOrdenadas")
        self.setMinimumWidth(560)
        self.setModal(True)

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)

        # ---------------------------------------------------------- cabecera
        cabecera = QWidget()
        cabecera_layout = QVBoxLayout(cabecera)
        cabecera_layout.setContentsMargins(28, 24, 28, 8)
        cabecera_layout.setSpacing(6)

        titulo = QLabel("Bienvenido a DescargasOrdenadas")
        titulo.setProperty("rol", "titulo")
        cabecera_layout.addWidget(titulo)

        intro = QLabel(
            "Para ordenar tu carpeta de descargas, la aplicación necesita "
            "algunos accesos del sistema. Se piden una sola vez y puedes "
            "omitir los que no quieras: se puede usar sin ninguno, con menos "
            "funciones."
        )
        intro.setProperty("rol", "secundaria")
        intro.setWordWrap(True)
        cabecera_layout.addWidget(intro)

        raiz.addWidget(cabecera)

        # ------------------------------------------------------------ lista
        contenido = QWidget()
        contenido_layout = QVBoxLayout(contenido)
        contenido_layout.setContentsMargins(28, 8, 28, 8)
        contenido_layout.setSpacing(10)

        # Solo se presentan los permisos que el usuario puede ir a conceder en
        # los ajustes de su sistema. La conexión a internet, por ejemplo, no se
        # «concede»: se comprueba, y además retrasaría la apertura de la ventana.
        for capacidad in permisos.CATALOGO:
            if not capacidad.se_concede_en_ajustes:
                continue
            contenido_layout.addWidget(self._crear_fila(capacidad))
        contenido_layout.addStretch()

        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setFrameShape(QFrame.NoFrame)
        area.setWidget(contenido)
        raiz.addWidget(area, 1)

        # ----------------------------------------------------------- botones
        pie = QWidget()
        pie_layout = QHBoxLayout(pie)
        pie_layout.setContentsMargins(28, 10, 28, 22)
        pie_layout.setSpacing(10)

        self.lbl_pie = QLabel("")
        self.lbl_pie.setProperty("rol", "secundaria")
        self.lbl_pie.setWordWrap(True)
        pie_layout.addWidget(self.lbl_pie, 1)

        btn_continuar = QPushButton("Empezar a usar la aplicación")
        btn_continuar.setProperty("rol", "primario")
        btn_continuar.clicked.connect(self.accept)
        pie_layout.addWidget(btn_continuar)

        raiz.addWidget(pie)

        self._actualizar_estado()

    # ------------------------------------------------------------------ UI

    def _crear_fila(self, capacidad: permisos.Capacidad) -> QWidget:
        """Crea la fila de una capacidad con su explicación y su botón.

        Las filas se separan con una línea fina, como una lista. Sin ella, con
        el estilo plano del rediseño, los cuatro permisos se leían como un
        bloque continuo sin principio ni fin.
        """
        marco = QFrame()
        marco.setProperty("rol", "fila")
        layout = QHBoxLayout(marco)
        layout.setContentsMargins(0, 14, 0, 14)
        layout.setSpacing(12)

        textos = QVBoxLayout()
        textos.setSpacing(3)

        nombre = QLabel(capacidad.nombre)
        nombre.setProperty("rol", "etiqueta")
        textos.addWidget(nombre)

        explicacion = QLabel(
            f"Sirve para {capacidad.para_que}."
            if not capacidad.obligatoria
            else f"Es necesaria para {capacidad.para_que}."
        )
        explicacion.setProperty("rol", "secundaria")
        explicacion.setWordWrap(True)
        textos.addWidget(explicacion)

        detalle = QLabel("")
        detalle.setProperty("rol", "discreta")
        detalle.setWordWrap(True)
        textos.addWidget(detalle)

        layout.addLayout(textos, 1)

        boton = QPushButton("Conceder")
        boton.setToolTip(f"Sirve para {capacidad.para_que}")
        boton.clicked.connect(
            lambda _=False, c=capacidad.id: self._pedir_permiso(c)
        )
        layout.addWidget(boton, 0, Qt.AlignTop)

        self._filas[capacidad.id] = (boton, detalle)
        return marco

    # ------------------------------------------------------------ lógica

    def _pedir_permiso(self, capacidad_id: str):
        """Solicita el permiso y deja la fila a la espera."""
        try:
            resultado = self.permisos.solicitar(capacidad_id)
        except KeyError:
            return

        detalle = self._filas.get(capacidad_id, (None, None))[1]
        if detalle is not None and resultado.detalle:
            detalle.setText(resultado.detalle)

        self._actualizar_estado()

    def _actualizar_estado(self):
        """Repinta cada fila según su estado actual."""
        pendientes = 0
        for capacidad_id, (boton, detalle) in self._filas.items():
            try:
                resultado = self.permisos.comprobar(capacidad_id)
            except KeyError:
                continue

            if resultado.disponible:
                boton.setEnabled(False)
                boton.setText("Listo" if resultado.estado.disponible else "No hace falta")
                if not detalle.text():
                    detalle.setText(
                        "Ya disponible."
                        if resultado.estado is permisos.EstadoPermiso.CONCEDIDO
                        else "Este sistema no lo necesita."
                    )
            else:
                pendientes += 1
                boton.setEnabled(True)
                boton.setText("Conceder")

        if pendientes:
            self.lbl_pie.setText(
                f"{pendientes} permiso{'s' if pendientes != 1 else ''} sin "
                "conceder. Puedes continuar y concederlos más adelante desde "
                "Ajustes."
            )
        else:
            self.lbl_pie.setText("Todo listo. Puedes empezar a organizar.")


def debe_mostrarse(config_portable) -> bool:
    """Indica si toca mostrar el asistente (solo la primera vez)."""
    if config_portable is None:
        return False
    try:
        return not bool(config_portable.obtener(CLAVE_CONFIG, False))
    except Exception:
        return False


def marcar_como_visto(config_portable) -> None:
    """Guarda que el asistente ya se ha mostrado."""
    if config_portable is None:
        return
    try:
        config_portable.establecer(CLAVE_CONFIG, True)
    except Exception as e:
        logger.debug(f"No se pudo recordar el primer arranque: {e}")


def olvidar(config_portable) -> None:
    """Permite que el asistente vuelva a mostrarse (desde Ajustes)."""
    if config_portable is None:
        return
    try:
        config_portable.establecer(CLAVE_CONFIG, False)
    except Exception as e:
        logger.debug(f"No se pudo reiniciar el primer arranque: {e}")
