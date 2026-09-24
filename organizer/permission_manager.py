#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sistema de permisos proactivo de DescargasOrdenadas.

La aplicación nunca debe fallar porque le falte un permiso: debe **pedirlo
antes**. Este módulo centraliza todo lo que depende del sistema operativo para
que ninguna parte de la interfaz tenga que hablar directamente con él.

Tres ideas gobiernan el diseño:

1. **Primero, no necesitar el permiso.** Siempre que exista una ruta sin
   privilegios se usa esa (por ejemplo, el menú contextual de Windows se
   instala por usuario, no para todo el equipo). Así desaparece la elevación.
2. **Pedir antes de fallar.** :meth:`GestorPermisos.requerir` es la puerta
   única: comprueba, y si falta el permiso lo solicita y explica qué hacer.
3. **Degradar, nunca reventar.** Ninguna función de este módulo lanza
   excepciones hacia arriba. Un permiso que no se puede comprobar con
   fiabilidad se declara ``DESCONOCIDO``, no se inventa un resultado.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger('organizador.permisos')


# --------------------------------------------------------------------------
# Modelo
# --------------------------------------------------------------------------

class EstadoPermiso(Enum):
    """Situación de una capacidad concreta."""

    CONCEDIDO = "concedido"
    """Está disponible y funciona."""

    DENEGADO = "denegado"
    """Se ha comprobado y el sistema lo está bloqueando."""

    DESCONOCIDO = "desconocido"
    """No se puede comprobar con fiabilidad sin molestar al usuario."""

    NO_APLICA = "no_aplica"
    """Este sistema no necesita este permiso."""

    PENDIENTE = "pendiente"
    """Se ha solicitado y se espera a que el usuario actúe."""

    @property
    def disponible(self) -> bool:
        """True si la capacidad se puede usar (o no hace falta)."""
        return self in (EstadoPermiso.CONCEDIDO, EstadoPermiso.NO_APLICA)

    @property
    def etiqueta(self) -> str:
        return {
            EstadoPermiso.CONCEDIDO: "Concedido",
            EstadoPermiso.DENEGADO: "Bloqueado por el sistema",
            EstadoPermiso.DESCONOCIDO: "Sin comprobar",
            EstadoPermiso.NO_APLICA: "No hace falta",
            EstadoPermiso.PENDIENTE: "Esperando tu permiso",
        }[self]


@dataclass(frozen=True)
class Capacidad:
    """Describe un permiso y por qué la aplicación lo quiere."""

    id: str
    nombre: str
    para_que: str
    obligatoria: bool = False
    degradacion: str = ""
    se_concede_en_ajustes: bool = True
    """False para lo que no es un permiso del sistema que el usuario conceda.

    La conexión a internet es el caso claro: no se «concede», se comprueba. Por
    eso queda fuera del asistente de primer arranque, que solo presenta lo que
    el usuario puede ir a habilitar en los ajustes de su sistema. Además, su
    comprobación implica una llamada de red y retrasaría la ventana.
    """


@dataclass
class Resultado:
    """Resultado de comprobar una capacidad, listo para mostrar."""

    capacidad: Capacidad
    estado: EstadoPermiso
    detalle: str = ""
    accion: str = ""
    """Etiqueta del botón que resuelve la falta de permiso ('' si no hay)."""

    @property
    def disponible(self) -> bool:
        return self.estado.disponible


# --------------------------------------------------------------------------
# Catálogo de capacidades
# --------------------------------------------------------------------------

def _es_macos() -> bool:
    return sys.platform == "darwin"


def _es_windows() -> bool:
    return sys.platform == "win32"


def _es_linux() -> bool:
    return sys.platform.startswith("linux")


CATALOGO: tuple[Capacidad, ...] = (
    Capacidad(
        id="carpeta_descargas",
        nombre="Acceso a la carpeta",
        para_que=(
            "poder leer y organizar los archivos de la carpeta elegida"
        ),
        obligatoria=True,
        degradacion="Sin acceso a la carpeta no se puede organizar nada.",
    ),
    Capacidad(
        id="acceso_total_disco",
        nombre="Acceso total al disco",
        para_que=(
            "añadir «Organizar con DescargasOrdenadas» al menú del clic derecho "
            "del Finder"
        ),
        obligatoria=False,
        degradacion=(
            "Sin este permiso no se puede instalar la acción rápida del Finder; "
            "el resto de la aplicación funciona con normalidad."
        ),
    ),
    Capacidad(
        id="automatizacion_finder",
        nombre="Control del Finder",
        para_que=(
            "avisar al Finder de que la acción rápida ha cambiado, para que "
            "aparezca sin cerrar sesión"
        ),
        obligatoria=False,
        degradacion=(
            "La acción rápida puede tardar en aparecer en el Finder hasta que "
            "se reinicie la sesión."
        ),
    ),
    Capacidad(
        id="notificaciones",
        nombre="Notificaciones",
        para_que="avisarte cuando termine una organización automática",
        obligatoria=False,
        degradacion="No se recibirán avisos, pero la organización sigue igual.",
    ),
    Capacidad(
        id="red",
        nombre="Conexión a internet",
        para_que="buscar actualizaciones de la aplicación",
        obligatoria=False,
        degradacion="No se comprobarán las actualizaciones automáticamente.",
        se_concede_en_ajustes=False,
    ),
)

CAPACIDADES_POR_ID = {c.id: c for c in CATALOGO}


# --------------------------------------------------------------------------
# Comprobaciones por sistema
# --------------------------------------------------------------------------

def _sonda_escritura(carpeta: Path) -> tuple[bool, str]:
    """Comprueba de verdad si se puede escribir en una carpeta.

    Se crea y se borra un archivo temporal: es la única forma fiable de saberlo,
    porque los permisos de una carpeta pueden venir de la ruta, del usuario o de
    una política del sistema.
    """
    sonda = Path(carpeta) / ".descargasordenadas_sonda"
    try:
        sonda.write_text("prueba", encoding="utf-8")
    except OSError as e:
        return False, str(e)
    try:
        sonda.unlink()
    except OSError:
        # No poder borrar la sonda no invalida el permiso de escritura.
        pass
    return True, ""


def _comprobar_carpeta_descargas(carpeta: Path | None) -> tuple[EstadoPermiso, str, str]:
    if carpeta is None:
        return EstadoPermiso.DESCONOCIDO, "Todavía no se ha elegido carpeta.", ""

    try:
        if not carpeta.exists():
            return EstadoPermiso.DENEGADO, f"La carpeta no existe:\n{carpeta}", ""
        if not carpeta.is_dir():
            return EstadoPermiso.DENEGADO, f"La ruta no es una carpeta:\n{carpeta}", ""
    except OSError as e:
        return EstadoPermiso.DENEGADO, f"No se puede acceder a la carpeta ({e})", ""

    if not os.access(carpeta, os.R_OK):
        sugerencia = (
            "Abre Ajustes del sistema → Privacidad y seguridad → Archivos y "
            "carpetas y concede el acceso a DescargasOrdenadas."
            if _es_macos()
            else "Revisa los permisos de lectura de la carpeta."
        )
        return EstadoPermiso.DENEGADO, f"Sin permiso de lectura sobre:\n{carpeta}", sugerencia

    puede_escribir, motivo = _sonda_escritura(carpeta)
    if not puede_escribir:
        sugerencia = (
            "Prueba con una carpeta dentro de tu perfil de usuario o concede "
            "acceso completo al disco."
            if _es_macos()
            else "Prueba con una carpeta dentro de tu perfil de usuario."
        )
        return (
            EstadoPermiso.DENEGADO,
            f"Sin permiso de escritura sobre:\n{carpeta}\n({motivo})",
            sugerencia,
        )

    return EstadoPermiso.CONCEDIDO, str(carpeta), ""


def _comprobar_acceso_total_disco() -> tuple[EstadoPermiso, str, str]:
    """macOS: comprueba el Acceso total al disco escribiendo donde hace falta.

    En lugar de sondear un archivo protegido cualquiera, se prueba exactamente
    la carpeta que la aplicación necesita para la acción rápida del Finder. Si
    eso funciona, el permiso está concedido para lo que importa.
    """
    if not _es_macos():
        return EstadoPermiso.NO_APLICA, "", ""

    services = Path.home() / "Library" / "Services"
    try:
        services.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        return (
            EstadoPermiso.DENEGADO,
            f"No se puede escribir en ~/Library/Services ({e})",
            "Concede Acceso total al disco a DescargasOrdenadas.",
        )

    puede_escribir, motivo = _sonda_escritura(services)
    if not puede_escribir:
        return (
            EstadoPermiso.DENEGADO,
            f"macOS bloquea la escritura en ~/Library/Services ({motivo})",
            "Concede Acceso total al disco a DescargasOrdenadas.",
        )
    return EstadoPermiso.CONCEDIDO, "~/Library/Services es escribible.", ""


def _comprobar_automatizacion_finder() -> tuple[EstadoPermiso, str, str]:
    """macOS: comprueba si se puede enviar órdenes al Finder.

    Ojo: esta comprobación **puede hacer que macOS muestre su propio diálogo de
    permiso** la primera vez. Por eso solo se llama desde el asistente y desde
    el centro de permisos, nunca en cada arranque.

    Cuando macOS deniega el control del Finder, ``osascript`` devuelve el error
    -1743 («Not authorized to send Apple events»).
    """
    if not _es_macos():
        return EstadoPermiso.NO_APLICA, "", ""

    try:
        resultado = subprocess.run(
            ["osascript", "-e", 'tell application "Finder" to get name'],
            capture_output=True, text=True, timeout=10, check=False,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return EstadoPermiso.DESCONOCIDO, f"No se pudo comprobar ({e})", ""

    salida = (resultado.stderr or "") + (resultado.stdout or "")
    if resultado.returncode == 0:
        return EstadoPermiso.CONCEDIDO, "Se puede controlar el Finder.", ""
    if "-1743" in salida or "Not authorized" in salida:
        return (
            EstadoPermiso.DENEGADO,
            "macOS bloquea el control del Finder.",
            "Concede el control del Finder a DescargasOrdenadas.",
        )
    return EstadoPermiso.DESCONOCIDO, f"Respuesta inesperada: {salida.strip()[:120]}", ""


def _comprobar_notificaciones() -> tuple[EstadoPermiso, str, str]:
    """Comprueba que la aplicación pueda **enviar** avisos.

    Punto importante, y motivo de un fallo real: esta capacidad **no se puede
    verificar** desde dentro de la aplicación. Los tres sistemas permiten enviar
    la orden de notificar aunque el usuario las tenga silenciadas o desactivadas
    para esta aplicación, así que no hay forma de saber si se verán.

    Antes se declaraba ``DESCONOCIDO`` en macOS y Windows, pero la interfaz
    interpretaba ese estado como «falta el permiso» y mostraba un botón para
    concederlo: si el usuario ya lo había concedido, la aplicación le seguía
    diciendo que no. Ahora se informa de lo que sí se sabe —que se pueden enviar
    avisos— y el texto explica que quien decide mostrarlos es el sistema.
    """
    if _es_linux():
        if shutil.which("notify-send"):
            return (
                EstadoPermiso.CONCEDIDO,
                "Se pueden enviar avisos. Si no aparecen, revisa las "
                "notificaciones de tu escritorio.",
                "",
            )
        return (
            EstadoPermiso.DENEGADO,
            "No se encontró «notify-send» en el sistema.",
            "Instala libnotify para recibir avisos.",
        )

    if _es_macos():
        if shutil.which("osascript"):
            return (
                EstadoPermiso.CONCEDIDO,
                "Se pueden enviar avisos. macOS decide si se muestran: si no "
                "los ves, revisa Ajustes → Notificaciones → DescargasOrdenadas.",
                "",
            )
        return EstadoPermiso.DENEGADO, "No se encontró «osascript».", ""

    if _es_windows():
        if shutil.which("powershell"):
            return (
                EstadoPermiso.CONCEDIDO,
                "Se pueden enviar avisos. Windows decide si se muestran: si no "
                "los ves, revisa Configuración → Notificaciones.",
                "",
            )
        return EstadoPermiso.DENEGADO, "No se encontró PowerShell.", ""

    return EstadoPermiso.NO_APLICA, "", ""


def _comprobar_red() -> tuple[EstadoPermiso, str, str]:
    """Comprueba si hay conexión consultando la API de releases.

    Es una llamada de red, así que solo se ejecuta cuando se pide de forma
    explícita (centro de permisos o diagnóstico), nunca al arrancar.
    """
    try:
        import requests

        respuesta = requests.head(
            "https://api.github.com/repos/AntonioXam/Descargas-Ordenada/releases/latest",
            timeout=6,
        )
        # Un 403 por límite de peticiones también demuestra que hay conexión.
        if respuesta.status_code < 500:
            return EstadoPermiso.CONCEDIDO, f"Respuesta HTTP {respuesta.status_code}.", ""
        return (
            EstadoPermiso.DENEGADO,
            f"El servidor respondió {respuesta.status_code}.",
            "",
        )
    except Exception as e:
        return (
            EstadoPermiso.DENEGADO,
            f"No se pudo conectar ({type(e).__name__}).",
            "Comprueba tu conexión a internet o el cortafuegos.",
        )


_COMPROBADORES = {
    "acceso_total_disco": lambda ctx: _comprobar_acceso_total_disco(),
    "automatizacion_finder": lambda ctx: _comprobar_automatizacion_finder(),
    "notificaciones": lambda ctx: _comprobar_notificaciones(),
    "red": lambda ctx: _comprobar_red(),
}


# --------------------------------------------------------------------------
# Rutas a los ajustes del sistema
# --------------------------------------------------------------------------

# Paneles de macOS, en orden de preferencia: primero el identificador moderno
# (Ventura 13 y posteriores) y después el clásico, que sigue funcionando en
# versiones anteriores. Se prueban en orden hasta que uno abra algo.
#
# Detalle importante: «Notificaciones» **no** vive en Privacidad y seguridad,
# es un panel propio. Antes se usaba un ancla inventada (Privacy_Notifications)
# que no abría nada.
_PANELES_MACOS = {
    "acceso_total_disco": [
        "x-apple.systempreferences:com.apple.settings.PrivacySecurity.extension?Privacy_AllFiles",
        "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles",
    ],
    "automatizacion_finder": [
        "x-apple.systempreferences:com.apple.settings.PrivacySecurity.extension?Privacy_Automation",
        "x-apple.systempreferences:com.apple.preference.security?Privacy_Automation",
    ],
    "notificaciones": [
        "x-apple.systempreferences:com.apple.Notifications-Settings.extension",
        "x-apple.systempreferences:com.apple.preference.notifications",
    ],
}

# Ruta escrita, para cuando el enlace no funciona: el usuario siempre debe
# saber exactamente dónde ir.
_RUTA_MANUAL_MACOS = {
    "acceso_total_disco": (
        "Ajustes del sistema → Privacidad y seguridad → Acceso total al disco"
    ),
    "automatizacion_finder": (
        "Ajustes del sistema → Privacidad y seguridad → Automatización"
    ),
    "notificaciones": "Ajustes del sistema → Notificaciones → DescargasOrdenadas",
}

_AJUSTES_WINDOWS = {
    "notificaciones": "ms-settings:privacy-notifications",
    "acceso_total_disco": "ms-settings:privacy",
    "automatizacion_finder": "ms-settings:privacy",
    "red": "ms-settings:network",
}

# Ruta absoluta: al arrancar desde el Finder el PATH del proceso es mínimo y no
# conviene depender de que «open» aparezca en él.
_OPEN_MACOS = "/usr/bin/open"


def _abrir_url_macos(url: str) -> bool:
    """Intenta abrir una URL con el mecanismo del sistema. No lanza excepción."""
    try:
        resultado = subprocess.run(
            [_OPEN_MACOS, url], capture_output=True, text=True, timeout=10, check=False
        )
        if resultado.returncode != 0:
            logger.debug(
                "No se pudo abrir %s: %s", url, (resultado.stderr or "").strip()[:160]
            )
        return resultado.returncode == 0
    except Exception as e:
        logger.debug(f"No se pudo abrir {url}: {e}")
        return False


def abrir_ajustes_del_sistema(capacidad_id: str) -> tuple[bool, str]:
    """Abre el panel del sistema donde se concede el permiso indicado.

    Devuelve (abierto, mensaje). Si no se puede abrir automáticamente se
    devuelven las instrucciones para llegar a mano: es mejor dar indicaciones
    que decir que se ha abierto algo que en realidad no se ha abierto.
    """
    try:
        if _es_macos():
            for url in _PANELES_MACOS.get(capacidad_id, []):
                if _abrir_url_macos(url):
                    return True, (
                        "Se ha abierto en: "
                        f"{_RUTA_MANUAL_MACOS.get(capacidad_id, 'Ajustes del sistema')}"
                    )

            # Ningún enlace funcionó: se abre al menos Ajustes del sistema,
            # que sigue siendo más útil que no hacer nada, y se indica la ruta.
            if _abrir_url_macos("x-apple.systempreferences:com.apple.preference.security"):
                return True, (
                    "Se ha abierto Ajustes del sistema, pero no directamente en "
                    "la sección. Entra en:\n"
                    f"{_RUTA_MANUAL_MACOS.get(capacidad_id, 'la sección correspondiente')}"
                )

            return False, (
                "No se ha podido abrir Ajustes del sistema automáticamente.\n\n"
                "Ábrelo a mano en:\n"
                f"{_RUTA_MANUAL_MACOS.get(capacidad_id, 'Ajustes del sistema')}"
            )

        if _es_windows():
            destino = _AJUSTES_WINDOWS.get(capacidad_id, "ms-settings:privacy")
            os.startfile(destino)  # type: ignore[attr-defined]  # solo Windows
            return True, "Se ha abierto la configuración de Windows."

        return False, (
            "En Linux los permisos dependen de tu escritorio. Revisa la "
            "configuración de privacidad de tu entorno."
        )
    except Exception as e:
        logger.debug(f"No se pudieron abrir los ajustes: {e}")
        if _es_macos():
            return False, (
                "No se pudo abrir la configuración automáticamente.\n\n"
                "Ve a:\n"
                f"{_RUTA_MANUAL_MACOS.get(capacidad_id, 'Ajustes del sistema')}"
            )
        return False, "No se pudo abrir la configuración automáticamente."


# --------------------------------------------------------------------------
# Gestor
# --------------------------------------------------------------------------

@dataclass
class GestorPermisos:
    """Punto único de consulta y solicitud de permisos."""

    carpeta_descargas: Path | None = None
    _cache: dict = field(default_factory=dict, repr=False)

    # ------------------------------------------------------------ consulta

    def comprobar(self, capacidad_id: str) -> Resultado:
        """Comprueba el estado de una capacidad. Nunca lanza excepción."""
        capacidad = CAPACIDADES_POR_ID.get(capacidad_id)
        if capacidad is None:
            raise KeyError(f"Capacidad desconocida: {capacidad_id}")

        try:
            if capacidad_id == "carpeta_descargas":
                estado, detalle, accion = _comprobar_carpeta_descargas(
                    self.carpeta_descargas
                )
            else:
                comprobador = _COMPROBADORES.get(capacidad_id)
                if comprobador is None:
                    estado, detalle, accion = EstadoPermiso.NO_APLICA, "", ""
                else:
                    estado, detalle, accion = comprobador(self)
        except Exception as e:
            # Una comprobación que falla no es un permiso denegado: es que no
            # se pudo saber. Se declara desconocido en lugar de mentir.
            logger.debug(f"Fallo al comprobar «{capacidad_id}»: {e}")
            estado, detalle, accion = (
                EstadoPermiso.DESCONOCIDO, f"No se pudo comprobar ({e})", ""
            )

        if estado is EstadoPermiso.DENEGADO and not accion:
            accion = self._accion_sugerida(capacidad_id)

        self._cache[capacidad_id] = estado
        return Resultado(capacidad, estado, detalle, accion)

    def diagnostico(self, incluir_red: bool = False) -> list[Resultado]:
        """Devuelve el estado de todas las capacidades aplicables.

        Args:
            incluir_red: añade la comprobación de conexión, que implica una
                llamada de red y por eso no se hace por defecto.
        """
        resultados = []
        for capacidad in CATALOGO:
            if capacidad.id == "red" and not incluir_red:
                continue
            resultados.append(self.comprobar(capacidad.id))
        return resultados

    def pendientes(self) -> list[Resultado]:
        """Capacidades no disponibles que se pueden resolver pidiéndolas."""
        return [r for r in self.diagnostico() if not r.disponible and r.accion]

    # ----------------------------------------------------------- solicitud

    def _accion_sugerida(self, capacidad_id: str) -> str:
        """Qué puede hacer el usuario para desbloquear la capacidad."""
        if capacidad_id == "carpeta_descargas":
            return "Elegir otra carpeta"
        if capacidad_id in ("acceso_total_disco", "automatizacion_finder"):
            if _es_macos():
                return "Abrir Ajustes del sistema"
            if _es_windows():
                return "Abrir configuración de Windows"
            return "Ver cómo hacerlo"
        if capacidad_id == "notificaciones":
            if _es_macos():
                return "Abrir Ajustes de notificaciones"
            if _es_windows():
                return "Abrir configuración de notificaciones"
            return "Ver cómo hacerlo"
        if capacidad_id == "red":
            return "Reintentar"
        return ""

    def solicitar(self, capacidad_id: str) -> Resultado:
        """Pide el permiso de la forma más directa que permita el sistema.

        En macOS y Windows esto abre el panel correspondiente. En el caso del
        control del Finder, además, lanzar la orden hace que macOS muestre su
        propio diálogo. En todos los casos se devuelve ``PENDIENTE``: el
        permiso no se concede al instante y hay que volver a comprobarlo
        cuando el usuario haya actuado.
        """
        capacidad = CAPACIDADES_POR_ID.get(capacidad_id)
        if capacidad is None:
            raise KeyError(f"Capacidad desconocida: {capacidad_id}")

        actual = self.comprobar(capacidad_id)
        if actual.disponible:
            return actual

        mensaje = ""
        try:
            if capacidad_id == "automatizacion_finder" and _es_macos():
                # Aquí sí interesa provocar el diálogo del sistema: es la vía
                # por la que macOS concede el permiso.
                _comprobar_automatizacion_finder()
                mensaje = (
                    "macOS mostrará (o ha mostrado) un aviso pidiendo permiso "
                    "para controlar el Finder. Acéptalo."
                )
            else:
                abierto, mensaje = abrir_ajustes_del_sistema(capacidad_id)
                if not abierto and not mensaje:
                    mensaje = "Concede el permiso manualmente y vuelve a intentarlo."
        except Exception as e:
            logger.debug(f"No se pudo solicitar «{capacidad_id}»: {e}")
            mensaje = "No se pudo abrir la configuración automáticamente."

        return Resultado(capacidad, EstadoPermiso.PENDIENTE, mensaje, actual.accion)

    # -------------------------------------------------------------- puerta

    def requerir(self, capacidad_id: str) -> tuple[bool, str]:
        """Puerta única antes de una operación que necesita permiso.

        Devuelve ``(puede_seguir, mensaje)``. Si el permiso falta, **no**
        intenta abrir ventanas por su cuenta: devuelve el mensaje que la
        interfaz debe mostrar con el botón correspondiente. Así quien decide
        cómo se le explica al usuario es la interfaz, y esta clase sigue
        sirviendo igual en modo consola.
        """
        resultado = self.comprobar(capacidad_id)
        if resultado.disponible:
            return True, ""

        # El orden importa para que se lea como una explicación y no como una
        # lista de frases sueltas: primero qué pasa, luego para qué hacía falta
        # y por último qué se pierde.
        partes = []
        if resultado.detalle:
            partes.append(resultado.detalle)
        partes.append(f"Hace falta para {resultado.capacidad.para_que}.")
        if resultado.capacidad.degradacion:
            partes.append(resultado.capacidad.degradacion)
        return False, "\n\n".join(partes)


# --------------------------------------------------------------------------
# Instancia compartida
# --------------------------------------------------------------------------

_gestor: GestorPermisos | None = None


def obtener_gestor_permisos(carpeta_descargas: Path | None = None) -> GestorPermisos:
    """Devuelve el gestor compartido, actualizando la carpeta si se indica."""
    global _gestor
    if _gestor is None:
        _gestor = GestorPermisos(carpeta_descargas=carpeta_descargas)
    elif carpeta_descargas is not None:
        _gestor.carpeta_descargas = carpeta_descargas
    return _gestor
