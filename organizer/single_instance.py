#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Control de instancia única para DescargasOrdenadas (Windows, macOS y Linux).

Garantiza que la aplicación nunca se abra dos veces, ni a mano ni por
autoarranque, y sirve además como canal para pedirle cosas a la copia que ya
está en marcha (por ejemplo, organizar una carpeta desde el menú contextual).

Capas independientes (si una falla, las demás siguen funcionando):

1. Bloqueo del sistema operativo sobre un archivo (``flock``/``msvcrt``). El
   propio sistema lo libera al terminar el proceso, incluso si se cierra a la
   fuerza.
2. Mutex con nombre en Windows, que además comparten los instaladores, para que
   el asistente de actualización nunca se ejecute con la app abierta.
3. Canal local de Qt (``QLocalServer``/``QLocalSocket``) para pedirle a la
   instancia viva que muestre su ventana o que organice una carpeta.

El protocolo del canal es JSON: ``{"accion": "mostrar"}`` o
``{"accion": "organizar", "carpeta": "/ruta"}``. Se mantiene la compatibilidad
con el mensaje de texto plano anterior ("mostrar").
"""

import os
import re
import sys
import json
import getpass
import logging
from pathlib import Path
from typing import Callable, Optional

from .app_paths import obtener_directorio_configuracion

logger = logging.getLogger('organizador.single_instance')

MENSAJE_MOSTRAR = "mostrar"
ACCION_ORGANIZAR = "organizar"
NOMBRE_MUTEX_WINDOWS = "Global\\DescargasOrdenadas_InstanciaUnica"


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

    def pid_bloqueante(self) -> Optional[int]:
        """Lee el PID del proceso que tiene el bloqueo (si se puede)."""
        try:
            with open(self._ruta, "r", encoding="utf-8") as f:
                return int(f.read().strip() or 0) or None
        except Exception:
            return None

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


class MutexWindows:
    """Mutex con nombre de Windows, compartido con el instalador (AppMutex)."""

    def __init__(self, nombre: str = NOMBRE_MUTEX_WINDOWS):
        self.nombre = nombre
        self._handle = None

    def adquirir(self) -> bool:
        if sys.platform != "win32":
            return True
        try:
            import ctypes
            from ctypes import wintypes

            kernel32 = ctypes.windll.kernel32
            handle = kernel32.CreateMutexW(None, True, self.nombre)
            if not handle:
                return True
            if kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
                kernel32.CloseHandle(handle)
                return False
            self._handle = handle
            return True
        except Exception as e:
            logger.debug(f"Mutex de Windows no disponible: {e}")
            return True

    def liberar(self):
        if self._handle is None:
            return
        try:
            import ctypes

            ctypes.windll.kernel32.ReleaseMutex(self._handle)
            ctypes.windll.kernel32.CloseHandle(self._handle)
        except Exception:
            pass
        self._handle = None


class InstanciaUnica:
    """Coordina una única ejecución de la aplicación."""

    def __init__(self, nombre_app: str = "DescargasOrdenadas"):
        self.nombre_app = nombre_app
        self._bloqueo = BloqueoProceso(nombre_app)
        self._mutex = MutexWindows()
        self._servidor = None
        self._callbacks: dict[str, Callable] = {}
        self._bloqueo_conseguido = False

    # ---------------------------------------------------------------- bloqueo

    def adquirir(self) -> bool:
        """Intenta quedarse como instancia principal.

        Devuelve True si somos la primera instancia o si no se puede comprobar
        (en ese caso es preferible que la aplicación funcione).
        """
        if not self._mutex.adquirir():
            logger.info("Ya existe una instancia (mutex de Windows activo)")
            self._bloqueo_conseguido = False
            return False

        self._bloqueo_conseguido = self._bloqueo.adquirir()
        if not self._bloqueo_conseguido:
            # Devolvemos el mutex: no somos la instancia principal
            self._mutex.liberar()
        return self._bloqueo_conseguido

    @property
    def somos_principal(self) -> bool:
        return self._bloqueo_conseguido

    @property
    def pid_existente(self) -> Optional[int]:
        """PID de la instancia que ya está en marcha (si se conoce)."""
        return self._bloqueo.pid_bloqueante()

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
        """Escucha peticiones. Requiere un QApplication en marcha."""
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
            # Limpiamos restos de un cierre anterior que dejasen el socket colgado
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
        self._callbacks[MENSAJE_MOSTRAR] = callback

    def conectar_accion(self, accion: str, callback: Callable[[dict], None]):
        """Registra una acción adicional (por ejemplo, organizar una carpeta)."""
        self._callbacks[accion] = callback

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
        if not datos:
            return

        accion = MENSAJE_MOSTRAR
        carga: dict = {}
        try:
            mensaje = json.loads(datos)
            if isinstance(mensaje, dict):
                accion = str(mensaje.get("accion") or MENSAJE_MOSTRAR)
                carga = mensaje
        except (ValueError, TypeError):
            # Compatibilidad con el protocolo antiguo de texto plano
            accion = MENSAJE_MOSTRAR if datos == MENSAJE_MOSTRAR else datos
            carga = {"accion": accion}

        callback = self._callbacks.get(accion)
        if callback is None:
            # Si piden organizar y no hay manejador, al menos mostramos la app
            callback = self._callbacks.get(MENSAJE_MOSTRAR)
            carga = {}
        if callback is None:
            return
        try:
            if carga:
                callback(carga)
            else:
                callback()
        except TypeError:
            try:
                callback()
            except Exception as e:
                logger.debug(f"Error ejecutando la acción '{accion}': {e}")
        except Exception as e:
            logger.debug(f"Error ejecutando la acción '{accion}': {e}")

    def enviar(self, mensaje: dict, espera_ms: int = 500) -> bool:
        """Envía una orden JSON a la instancia que ya está abierta."""
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
            if not socket.waitForConnected(espera_ms):
                return False
            socket.write(json.dumps(mensaje).encode("utf-8"))
            socket.flush()
            socket.waitForBytesWritten(espera_ms)
            socket.disconnectFromServer()
            return True
        except Exception as e:
            logger.debug(f"No se pudo enviar la orden a la otra instancia: {e}")
            return False
        finally:
            del app_temporal

    def avisar_instancia_existente(self, mensaje: str = MENSAJE_MOSTRAR) -> bool:
        """Pide a la instancia que ya está abierta que muestre su ventana."""
        return self.enviar({"accion": mensaje})

    def enviar_organizar(self, carpeta: str) -> bool:
        """Pide a la instancia abierta que organice una carpeta concreta."""
        return self.enviar({"accion": ACCION_ORGANIZAR, "carpeta": str(carpeta)})

    # ----------------------------------------------------------------- cierre

    def liberar(self):
        """Libera canal, bloqueo y mutex."""
        if self._servidor is not None:
            try:
                self._servidor.close()
                from PySide6.QtNetwork import QLocalServer
                QLocalServer.removeServer(self._nombre_canal())
            except Exception:
                pass
            self._servidor = None
        self._bloqueo.liberar()
        self._mutex.liberar()
        self._bloqueo_conseguido = False


def hay_instancia_activa(nombre_app: str = "DescargasOrdenadas") -> Optional[int]:
    """Comprueba si ya hay una instancia en marcha sin interferir con ella.

    Devuelve el PID de la instancia activa o None. Se usa, por ejemplo, antes
    de lanzar un instalador o para informar al usuario.
    """
    bloqueo = BloqueoProceso(nombre_app)
    if bloqueo.adquirir():
        # Nadie tenía el bloqueo: somos los únicos
        pid = None
        bloqueo.liberar()
        return pid
    return bloqueo.pid_bloqueante()
