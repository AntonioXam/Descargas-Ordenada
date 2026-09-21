#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Control de instancia única para DescargasOrdenadas (Windows, macOS y Linux).

Evita que la aplicación se abra dos veces. Es el caso típico de que el
autoarranque ya la haya lanzado y el usuario vuelva a pulsar el icono: en lugar
de abrir una segunda copia, se muestra la ventana de la que ya está abierta.

Se usan dos capas independientes:

1. Bloqueo de archivo gestionado por el sistema operativo. No necesita Qt y el
   propio sistema lo libera al terminar el proceso, incluso si la aplicación se
   cierra a la fuerza o se queda colgada.
2. Canal local de Qt (QLocalServer / QLocalSocket) para pedirle a la instancia
   que ya está en marcha que saque su ventana al frente.
"""

import os
import re
import sys
import getpass
import logging
from pathlib import Path
from typing import Callable, Optional

from .app_paths import obtener_directorio_configuracion

logger = logging.getLogger('organizador.single_instance')

MENSAJE_MOSTRAR = "mostrar"


class BloqueoProceso:
    """Bloqueo entre procesos basado en un archivo, sin dependencias externas."""

    def __init__(self, nombre_app: str = "DescargasOrdenadas"):
        self.nombre_app = nombre_app
        self._archivo = None
        self._ruta = self._obtener_ruta()

    def _obtener_ruta(self) -> Path:
        try:
            carpeta = obtener_directorio_configuracion()
            carpeta.mkdir(parents=True, exist_ok=True)
            return carpeta / f"{self.nombre_app.lower()}.lock"
        except Exception:
            return Path.cwd() / f".{self.nombre_app.lower()}.lock"

    def adquirir(self) -> bool:
        """Intenta tomar el bloqueo. Devuelve True si lo hemos conseguido."""
        try:
            self._archivo = open(self._ruta, "a+")
        except OSError as e:
            # Si no podemos ni crear el archivo, preferimos dejar arrancar la app
            logger.debug(f"No se pudo abrir el archivo de bloqueo: {e}")
            return True

        try:
            if sys.platform == "win32":
                import msvcrt
                self._archivo.seek(0)
                msvcrt.locking(self._archivo.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self._archivo.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self._archivo.close()
            self._archivo = None
            return False
        except Exception as e:
            logger.debug(f"Bloqueo no disponible: {e}")
            self._archivo.close()
            self._archivo = None
            return True

        self._escribir_pid()
        return True

    def _escribir_pid(self):
        try:
            self._archivo.seek(0)
            self._archivo.truncate()
            self._archivo.write(str(os.getpid()))
            self._archivo.flush()
        except Exception:
            pass

    def liberar(self):
        """Suelta el bloqueo."""
        if not self._archivo:
            return
        try:
            if sys.platform == "win32":
                import msvcrt
                self._archivo.seek(0)
                msvcrt.locking(self._archivo.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self._archivo.fileno(), fcntl.LOCK_UN)
        except Exception:
            pass
        try:
            self._archivo.close()
        except Exception:
            pass
        self._archivo = None


class InstanciaUnica:
    """Coordina una única ejecución de la aplicación."""

    def __init__(self, nombre_app: str = "DescargasOrdenadas"):
        self.nombre_app = nombre_app
        self._bloqueo = BloqueoProceso(nombre_app)
        self._servidor = None
        self._callback: Optional[Callable[[], None]] = None
        self._bloqueo_conseguido = False

    # ---------------------------------------------------------------- bloqueo

    def adquirir(self) -> bool:
        """Intenta quedarse como instancia principal.

        Devuelve True si somos la primera instancia o si no se puede comprobar
        (en ese caso es preferible que la aplicación funcione).
        """
        self._bloqueo_conseguido = self._bloqueo.adquirir()
        return self._bloqueo_conseguido

    @property
    def somos_principal(self) -> bool:
        return self._bloqueo_conseguido

    # ------------------------------------------------- canal local (activar)

    def _nombre_canal(self) -> str:
        try:
            usuario = getpass.getuser() or "usuario"
        except Exception:
            usuario = "usuario"
        crudo = f"{self.nombre_app}-{usuario}"
        limpio = re.sub(r"[^A-Za-z0-9_.\-]", "_", crudo)
        return limpio[:100]

    def iniciar_servidor(self):
        """Escucha peticiones para mostrar la ventana. Requiere un QApplication."""
        if self._servidor is not None:
            return
        try:
            from PySide6.QtNetwork import QLocalServer
        except ImportError:
            logger.debug("PySide6.QtNetwork no disponible; sin canal de activación")
            return

        try:
            servidor = QLocalServer()
            servidor.setSocketOptions(QLocalServer.UserAccessOption)
            # Limpiamos restos de un cierre anterior que dejase el socket colgado
            QLocalServer.removeServer(self._nombre_canal())
            if not servidor.listen(self._nombre_canal()):
                logger.debug(f"No se pudo escuchar en el canal local: {servidor.errorString()}")
                return
            servidor.newConnection.connect(self._atender_conexion)
            self._servidor = servidor
        except Exception as e:
            logger.debug(f"Error creando el canal local: {e}")

    def conectar_activacion(self, callback: Callable[[], None]):
        """Registra la función que mostrará la ventana principal."""
        self._callback = callback

    def _atender_conexion(self):
        if self._servidor is None:
            return
        conexion = self._servidor.nextPendingConnection()
        if conexion is None:
            return
        conexion.readyRead.connect(lambda c=conexion: self._leer_peticion(c))
        conexion.disconnected.connect(conexion.deleteLater)

    def _leer_peticion(self, conexion):
        try:
            datos = bytes(conexion.readAll()).decode("utf-8", "ignore").strip()
        except Exception:
            datos = ""
        if datos == MENSAJE_MOSTRAR and self._callback:
            try:
                self._callback()
            except Exception as e:
                logger.debug(f"Error mostrando la ventana existente: {e}")

    def avisar_instancia_existente(self, mensaje: str = MENSAJE_MOSTRAR) -> bool:
        """Pide a la instancia que ya está abierta que muestre su ventana."""
        try:
            from PySide6.QtCore import QCoreApplication
            from PySide6.QtNetwork import QLocalSocket
        except ImportError:
            logger.debug("PySide6 no disponible; no se puede avisar a la otra instancia")
            return False

        app_temporal = None
        if QCoreApplication.instance() is None:
            try:
                app_temporal = QCoreApplication(sys.argv[:1])
            except Exception:
                app_temporal = None

        try:
            socket = QLocalSocket()
            socket.connectToServer(self._nombre_canal())
            if not socket.waitForConnected(400):
                return False
            socket.write(mensaje.encode("utf-8"))
            socket.flush()
            socket.waitForBytesWritten(400)
            socket.disconnectFromServer()
            return True
        except Exception as e:
            logger.debug(f"No se pudo avisar a la otra instancia: {e}")
            return False
        finally:
            del app_temporal

    # ----------------------------------------------------------------- cierre

    def liberar(self):
        """Libera canal y bloqueo."""
        if self._servidor is not None:
            try:
                self._servidor.close()
                from PySide6.QtNetwork import QLocalServer
                QLocalServer.removeServer(self._nombre_canal())
            except Exception:
                pass
            self._servidor = None
        self._bloqueo.liberar()
        self._bloqueo_conseguido = False
