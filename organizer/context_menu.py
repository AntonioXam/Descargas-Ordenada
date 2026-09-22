#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integración con el menú contextual del sistema (Windows, macOS y Linux).

El objetivo: clic derecho sobre una carpeta → "Organizar con DescargasOrdenadas"
→ la carpeta se organiza en segundo plano, sin abrir ventanas.

Cada sistema usa el mecanismo que realmente respeta sus permisos:

- **Windows**: claves del registro en ``HKEY_CURRENT_USER\\Software\\Classes``
  (no requiere administrador, a diferencia de ``HKEY_CLASSES_ROOT``) y, si se
  puede, también en ``HKEY_CLASSES_ROOT`` para que afecte a todos los usuarios.
- **macOS**: Acción rápida de Finder en ``~/Library/Services``. Como los
  servicios se ejecutan en un entorno limitado, la primera vez macOS pedirá
  permiso para controlar Finder o acceder a la carpeta; el aviso lo explica.
- **Linux**: entrada ``.desktop`` para "Abrir con…" más un script de Nautilus.
  En Flatpak/Snap se instala en las carpetas del usuario (sin sudo).

En todos los casos el comando incluye ``--organizar-carpeta "$ruta"``, que
delega el trabajo en la instancia abierta si la hay.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import Tuple

from .app_paths import obtener_recurso

logger = logging.getLogger('organizador.context_menu')

if sys.platform == "win32":
    import winreg

NOMBRE_MENU = "Organizar con DescargasOrdenadas"


class GestorMenuContextual:
    """Gestor de integración con el menú contextual del sistema."""

    def __init__(self, nombre_app="DescargasOrdenadas"):
        self.nombre_app = nombre_app
        self.ruta_ejecutable = self._obtener_ruta_ejecutable()

    def _obtener_ruta_ejecutable(self) -> str:
        """Obtiene la ruta al ejecutable actual."""
        if getattr(sys, 'frozen', False):
            return sys.executable
        project_dir = Path(__file__).resolve().parent.parent
        launcher = project_dir / "INICIAR.bat"
        if launcher.exists():
            return str(launcher)
        return str(Path(sys.executable).resolve())

    def _comando_base(self) -> str:
        """Comando que organiza una carpeta y termina (sin abrir ventana)."""
        if getattr(sys, "frozen", False):
            return f'"{sys.executable}" --organizar-carpeta'
        iniciar_py = (Path(__file__).resolve().parent / "INICIAR.py").as_posix()
        return f'"{sys.executable}" "{iniciar_py}" --organizar-carpeta'

    def registrar_menu_contextual(self, tipo="carpetas") -> Tuple[bool, str]:
        """Registra la integración en el menú contextual del sistema."""
        try:
            if sys.platform == "win32":
                if tipo in ["carpetas", "ambos"]:
                    self._registrar_carpetas()
                if tipo in ["archivos", "ambos"]:
                    self._registrar_archivos()
                return True, f"Menú contextual registrado para {tipo}"

            if sys.platform == "darwin":
                return self._registrar_macos()

            return self._registrar_linux()
        except PermissionError as e:
            logger.error(f"Permisos insuficientes registrando el menú contextual: {e}")
            return False, (
                "El sistema ha denegado el permiso para instalar la integración.\n"
                "Concede acceso a la carpeta de servicios/registro e inténtalo de nuevo."
            )
        except Exception as e:
            logger.error(f"Error registrando menú contextual: {e}")
            return False, f"Error: {e}"

    # --------------------------------------------------------------- macOS

    def _registrar_macos(self) -> Tuple[bool, str]:
        """Crea una acción rápida de Finder (clic derecho → Acciones rápidas)."""
        import plistlib

        raiz = Path.home() / "Library" / "Services" / f"{NOMBRE_MENU}.workflow"
        try:
            contenido = raiz / "Contents"
            contenido.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            return False, (
                "macOS ha bloqueado la creación de la acción rápida.\n\n"
                "Ve a Ajustes del sistema → Privacidad y seguridad → Acceso total "
                "al disco y concede permiso a DescargasOrdenadas."
            )

        comando = self._comando_base()
        script = chr(10).join([
            "for f in \"$@\"; do",
            f"  {comando} \"$f\" >/dev/null 2>&1 &",
            "done",
        ])

        document_wflow = {
            "AMApplicationBuild": "521.1",
            "AMApplicationVersion": "2.10",
            "AMDocumentVersion": "2",
            "actions": [
                {
                    "action": {
                        "amAcceptsInput": False,
                        "alwaysRuns": True,
                        "name": "Run Shell Script",
                        "parameters": {
                            "COMMAND_STRING": script,
                            "CheckedForUserDefaultShell": True,
                            "inputMethod": 1,
                            "shell": "/bin/zsh",
                            "source": "",
                        },
                        "uuid": "descargas-ordenadas-0001",
                    },
                    "isViewVisible": 1,
                }
            ],
            "connectors": {},
            "workflowMetaData": {
                "applicationBundleIDsByPath": {},
                "applicationPaths": [],
                "inputTypeIdentifier": "com.apple.Automator.fileSystemObject",
                "outputTypeIdentifier": "com.apple.Automator.nothing",
                "presentationMode": 11,
                "processesInput": 0,
                "serviceApplicationBundleID": "com.apple.finder",
                "serviceApplicationPath": "/System/Library/CoreServices/Finder.app",
                "serviceInputTypeIdentifier": "com.apple.Automator.fileSystemObject",
                "serviceOutputTypeIdentifier": "com.apple.Automator.nothing",
                "serviceProcessesInput": 0,
                "systemImageName": "NSActionTemplate",
                "useAutomaticInputType": 0,
                "workflowTypeIdentifier": "com.apple.Automator.servicesMenu",
            },
        }
        (contenido / "document.wflow").write_bytes(
            plistlib.dumps(document_wflow, fmt=plistlib.FMT_XML)
        )

        info_plist = {
            "CFBundleIdentifier": "com.antonioxam.DescargasOrdenadas.quickaction",
            "CFBundleName": NOMBRE_MENU,
            "CFBundleShortVersionString": "1.0",
            "CFBundleVersion": "1.0",
            "NSServices": [
                {
                    "NSBackgroundColorName": "background",
                    "NSMenuItem": {"default": NOMBRE_MENU},
                    "NSMessage": "runWorkflowAsService",
                    "NSRequiredContext": {"NSApplicationIdentifier": "com.apple.finder"},
                    "NSSendFileTypes": ["public.folder", "public.directory"],
                }
            ],
        }
        (contenido / "Info.plist").write_bytes(
            plistlib.dumps(info_plist, fmt=plistlib.FMT_XML)
        )

        # Pedir a macOS que reescanee los servicios
        subprocess.run(
            ["/System/Library/CoreServices/pbs", "-flush"],
            capture_output=True, timeout=10, check=False,
        )
        # Algunas versiones de macOS solo recargan los servicios por usuario
        subprocess.run(
            ["/System/Library/CoreServices/pbs", "-flush", "-user", os.environ.get("USER", "")],
            capture_output=True, timeout=10, check=False,
        )

        return True, (
            "Acción rápida instalada.\n\n"
            "En Finder: clic derecho sobre una carpeta → Acciones rápidas → "
            f"{NOMBRE_MENU}.\n\n"
            "La primera vez macOS pedirá permiso para acceder a la carpeta: acéptalo."
        )

    def _desregistrar_macos(self) -> Tuple[bool, str]:
        """Elimina la acción rápida de Finder."""
        import shutil as _shutil

        raiz = Path.home() / "Library" / "Services" / f"{NOMBRE_MENU}.workflow"
        if raiz.exists():
            _shutil.rmtree(raiz, ignore_errors=True)
        subprocess.run(
            ["/System/Library/CoreServices/pbs", "-flush"],
            capture_output=True, check=False,
        )
        return True, "Acción rápida eliminada"

    def _verificar_macos(self) -> bool:
        raiz = Path.home() / "Library" / "Services" / f"{NOMBRE_MENU}.workflow"
        return (raiz / "Contents" / "Info.plist").exists()

    # --------------------------------------------------------------- Linux

    def _ruta_desktop_linux(self) -> Path:
        base = os.getenv("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
        return Path(base) / "applications" / "descargasordenadas-carpeta.desktop"

    def _registrar_linux(self) -> Tuple[bool, str]:
        ruta = self._ruta_desktop_linux()
        try:
            ruta.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            return False, (
                f"No se puede escribir en {ruta.parent}.\n\n"
                "Revisa los permisos de tu carpeta de usuario."
            )

        icono = obtener_recurso("icon.png")
        icono_ruta = str(icono) if icono.exists() else ""

        lineas = [
            "[Desktop Entry]",
            "Type=Application",
            "Name=Organizar con DescargasOrdenadas",
            "Comment=Organiza los archivos de esta carpeta sin abrir ventanas",
            f"Exec={self._comando_base()} %f",
            f"Icon={icono_ruta}",
            "MimeType=inode/directory;",
            "Terminal=false",
            "NoDisplay=true",
            "Categories=Utility;FileTools;",
            "",
        ]
        ruta.write_text("\n".join(lineas), encoding="utf-8")
        try:
            ruta.chmod(0o755)
        except OSError:
            pass

        # Script opcional para Nautilus (GNOME Files)
        try:
            scripts = Path.home() / ".local" / "share" / "nautilus" / "scripts"
            scripts.mkdir(parents=True, exist_ok=True)
            script = scripts / NOMBRE_MENU
            if getattr(sys, "frozen", False):
                comando_script = f'"{sys.executable}" --organizar-carpeta "$f"'
            else:
                iniciar_py = (Path(__file__).resolve().parent / "INICIAR.py").as_posix()
                comando_script = f'"{sys.executable}" "{iniciar_py}" --organizar-carpeta "$f"'
            cuerpo = chr(10).join([
                "#!/usr/bin/env bash",
                "# Organiza las carpetas seleccionadas con DescargasOrdenadas",
                "# (se ejecuta sin abrir la ventana; delega en la app si está abierta)",
                'IFS="' + chr(10) + '"',
                "for f in $NAUTILUS_SCRIPT_SELECTED_FILE_PATHS; do",
                f"  {comando_script} >/dev/null 2>&1 &",
                "done",
                "",
            ])
            script.write_text(cuerpo + chr(10), encoding="utf-8")
            script.chmod(0o755)
        except PermissionError as e:
            logger.debug(f"No se pudo crear el script de Nautilus: {e}")

        # Refrescar la base de datos de aplicaciones si existe
        subprocess.run(
            ["update-desktop-database", str(ruta.parent)],
            capture_output=True, check=False,
        )
        return True, (
            "Integración instalada.\n\n"
            "En el explorador de archivos: clic derecho sobre una carpeta → "
            "Abrir con… → Organizar con DescargasOrdenadas\n"
            "En Nautilus también aparece dentro de Scripts."
        )

    def _desregistrar_linux(self) -> Tuple[bool, str]:
        ruta = self._ruta_desktop_linux()
        if ruta.exists():
            ruta.unlink()
        script = Path.home() / ".local" / "share" / "nautilus" / "scripts" / NOMBRE_MENU
        if script.exists():
            script.unlink()
        return True, "Integración de Linux eliminada"

    def _verificar_linux(self) -> bool:
        return self._ruta_desktop_linux().exists() or (
            Path.home() / ".local" / "share" / "nautilus" / "scripts" / NOMBRE_MENU
        ).exists()

    # ------------------------------------------------------------- Windows

    def _icono_windows(self) -> str:
        icono = obtener_recurso("icon.ico")
        return str(icono) if icono.exists() else self.ruta_ejecutable

    def _escribir_clave_windows(self, raiz, key_path: str):
        """Escribe la clave del menú contextual bajo la raíz indicada."""
        comando = f'{self.ruta_ejecutable} --organizar-carpeta "%1"'

        key = winreg.CreateKey(raiz, key_path)
        try:
            winreg.SetValue(key, "", winreg.REG_SZ, NOMBRE_MENU)
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, self._icono_windows())
        finally:
            winreg.CloseKey(key)

        key_command = winreg.CreateKey(raiz, key_path + r"\command")
        try:
            winreg.SetValue(key_command, "", winreg.REG_SZ, comando)
        finally:
            winreg.CloseKey(key_command)

    def _registrar_carpetas(self):
        """Registra el menú contextual en carpetas y en el fondo de carpeta.

        HKEY_CURRENT_USER no requiere permisos de administrador; además, si se
        puede, se escribe en HKEY_CLASSES_ROOT para todos los usuarios.
        """
        rutas = [
            r"Directory\shell\DescargasOrdenadas",
            r"Directory\Background\shell\DescargasOrdenadas",
        ]
        for key_path in rutas:
            self._escribir_clave_windows(winreg.HKEY_CURRENT_USER, r"Software\Classes\\" + key_path)
            try:
                self._escribir_clave_windows(winreg.HKEY_CLASSES_ROOT, key_path)
            except PermissionError:
                logger.debug("Sin permisos de administrador: solo se registra por usuario")

    def _registrar_archivos(self):
        """Registra el menú contextual para archivos (abre la carpeta contenedora)."""
        self._escribir_clave_windows(
            winreg.HKEY_CURRENT_USER, r"Software\Classes\*\shell\DescargasOrdenadas"
        )
        try:
            self._escribir_clave_windows(winreg.HKEY_CLASSES_ROOT, r"*\shell\DescargasOrdenadas")
        except PermissionError:
            logger.debug("Sin permisos de administrador: solo se registra por usuario")

    def desregistrar_menu_contextual(self) -> Tuple[bool, str]:
        """Elimina la integración con el menú contextual."""
        try:
            if sys.platform == "darwin":
                return self._desregistrar_macos()
            if sys.platform != "win32":
                return self._desregistrar_linux()

            claves = [
                r"Directory\shell\DescargasOrdenadas",
                r"Directory\Background\shell\DescargasOrdenadas",
                r"*\shell\DescargasOrdenadas",
            ]
            for raiz in (winreg.HKEY_CURRENT_USER, winreg.HKEY_CLASSES_ROOT):
                prefijo = r"Software\Classes\\" if raiz == winreg.HKEY_CURRENT_USER else ""
                for clave in claves:
                    for sufijo in (r"\command", ""):
                        try:
                            winreg.DeleteKey(raiz, prefijo + clave + sufijo)
                        except (FileNotFoundError, PermissionError, OSError):
                            pass

            return True, "Menú contextual eliminado"
        except Exception as e:
            logger.error(f"Error eliminando menú contextual: {e}")
            return False, f"Error: {e}"

    def verificar_registro(self) -> bool:
        """Verifica si la integración está instalada en este sistema."""
        if sys.platform == "darwin":
            return self._verificar_macos()
        if sys.platform != "win32":
            return self._verificar_linux()

        claves = [
            (winreg.HKEY_CURRENT_USER, r"Software\Classes\Directory\shell\DescargasOrdenadas"),
            (winreg.HKEY_CLASSES_ROOT, r"Directory\shell\DescargasOrdenadas"),
        ]
        for raiz, clave in claves:
            try:
                key = winreg.OpenKey(raiz, clave)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                continue
            except Exception:
                continue
        return False
