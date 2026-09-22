#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integración con el menú contextual de Windows"""

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

class GestorMenuContextual:
    """Gestor de integración con el menú contextual de Windows."""
    
    def __init__(self, nombre_app="DescargasOrdenadas"):
        self.nombre_app = nombre_app
        self.ruta_ejecutable = self._obtener_ruta_ejecutable()
    
    def _obtener_ruta_ejecutable(self) -> str:
        """Obtiene la ruta al ejecutable actual."""
        if getattr(sys, 'frozen', False):
            return sys.executable
        else:
            project_dir = Path(__file__).resolve().parent.parent
            launcher = project_dir / "INICIAR.bat"
            if launcher.exists():
                return str(launcher)
            return str(Path(sys.executable).resolve())
    
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
        except Exception as e:
            logger.error(f"Error registrando menú contextual: {e}")
            return False, f"Error: {e}"

    # --------------------------------------------------------------- macOS

    def _comando_macos(self) -> str:
        """Devuelve el comando que ejecuta la organización en una carpeta."""
        if getattr(sys, "frozen", False):
            return f'"{sys.executable}" --auto --dir "$f"'
        iniciar_py = Path(__file__).resolve().parent / "INICIAR.py"
        return f'"{sys.executable}" "{iniciar_py}" --auto --dir "$f"'

    def _registrar_macos(self) -> Tuple[bool, str]:
        """Crea una acción rápida de Finder (clic derecho → Acciones rápidas)."""
        import plistlib

        nombre_menu = "Organizar con DescargasOrdenadas"
        raiz = Path.home() / "Library" / "Services" / "Organizar con DescargasOrdenadas.workflow"
        contenido = raiz / "Contents"
        contenido.mkdir(parents=True, exist_ok=True)

        script = chr(10).join([
            "for f in \"$@\"; do",
            f"  {self._comando_macos()} &",
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
            "CFBundleName": "Organizar con DescargasOrdenadas",
            "CFBundleShortVersionString": "1.0",
            "CFBundleVersion": "1.0",
            "NSServices": [
                {
                    "NSBackgroundColorName": "background",
                    "NSMenuItem": {"default": nombre_menu},
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
        return True, "Acción rápida de Finder instalada"

    def _desregistrar_macos(self) -> Tuple[bool, str]:
        """Elimina la acción rápida de Finder."""
        import shutil as _shutil
        raiz = Path.home() / "Library" / "Services" / "Organizar con DescargasOrdenadas.workflow"
        if raiz.exists():
            _shutil.rmtree(raiz)
        subprocess.run(
            ["/System/Library/CoreServices/pbs", "-flush"],
            capture_output=True, check=False,
        )
        return True, "Acción rápida eliminada"

    def _verificar_macos(self) -> bool:
        raiz = Path.home() / "Library" / "Services" / "Organizar con DescargasOrdenadas.workflow"
        return (raiz / "Contents" / "Info.plist").exists()

    # --------------------------------------------------------------- Linux

    def _comando_linux(self) -> str:
        if getattr(sys, "frozen", False):
            return f'"{sys.executable}" --auto --dir'
        iniciar_py = Path(__file__).resolve().parent / "INICIAR.py"
        return f'"{sys.executable}" "{iniciar_py}" --auto --dir'

    def _ruta_desktop_linux(self) -> Path:
        base = os.getenv("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
        return Path(base) / "applications" / "descargasordenadas-carpeta.desktop"

    def _registrar_linux(self) -> Tuple[bool, str]:
        ruta = self._ruta_desktop_linux()
        ruta.parent.mkdir(parents=True, exist_ok=True)

        icono = obtener_recurso("icon.png")
        icono_ruta = str(icono) if icono.exists() else ""

        lineas = [
            "[Desktop Entry]",
            "Type=Application",
            "Name=Organizar con DescargasOrdenadas",
            "Comment=Organiza los archivos de esta carpeta",
            f"Exec={self._comando_linux()} %f",
            f"Icon={icono_ruta}",
            "MimeType=inode/directory;",
            "Terminal=false",
            "NoDisplay=true",
            "",
        ]
        ruta.write_text("\n".join(lineas), encoding="utf-8")

        # Script opcional para Nautilus (GNOME Files)
        try:
            scripts = Path.home() / ".local" / "share" / "nautilus" / "scripts"
            scripts.mkdir(parents=True, exist_ok=True)
            script = scripts / "Organizar con DescargasOrdenadas"
            cuerpo = chr(10).join([
                "#!/usr/bin/env bash",
                "# Organiza las carpetas seleccionadas con DescargasOrdenadas",
                'IFS="' + chr(10) + '"',
                "for f in $NAUTILUS_SCRIPT_SELECTED_FILE_PATHS; do",
                "  " + self._comando_linux() + " \"$f\" &",
                "done",
                "",
            ])
            script = scripts / "Organizar con DescargasOrdenadas"
            script.write_text(cuerpo + chr(10), encoding="utf-8")
            script.chmod(0o755)
        except Exception as e:
            logger.debug(f"No se pudo crear el script de Nautilus: {e}")

        # Refrescar la base de datos de aplicaciones si existe (solo Linux)
        if sys.platform.startswith("linux"):
            subprocess.run(["update-desktop-database", str(ruta.parent)],
                           capture_output=True, check=False)
        return True, "Menú contextual de Linux instalado"

    def _desregistrar_linux(self) -> Tuple[bool, str]:
        ruta = self._ruta_desktop_linux()
        if ruta.exists():
            ruta.unlink()
        script = Path.home() / ".local" / "share" / "nautilus" / "scripts" / "Organizar con DescargasOrdenadas"
        if script.exists():
            script.unlink()
        return True, "Integración de Linux eliminada"

    def _verificar_linux(self) -> bool:
        return self._ruta_desktop_linux().exists()

    def _registrar_carpetas(self):
        """Registra el menú contextual para carpetas."""
        key_path = r"Directory\shell\DescargasOrdenadas"
        icono = obtener_recurso("icon.ico")
        icono_ruta = str(icono) if icono.exists() else self.ruta_ejecutable
        
        key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)
        winreg.SetValue(key, "", winreg.REG_SZ, "Organizar con DescargasOrdenadas")
        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icono_ruta)
        winreg.CloseKey(key)
        
        command_path = key_path + r"\command"
        key_command = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, command_path)
        comando = f'"{self.ruta_ejecutable}" --auto --dir "%1"'
        winreg.SetValue(key_command, "", winreg.REG_SZ, comando)
        winreg.CloseKey(key_command)
    
    def _registrar_archivos(self):
        """Registra el menú contextual para archivos."""
        key_path = r"*\shell\DescargasOrdenadas"
        icono = obtener_recurso("icon.ico")
        icono_ruta = str(icono) if icono.exists() else self.ruta_ejecutable
        
        key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)
        winreg.SetValue(key, "", winreg.REG_SZ, "Organizar con DescargasOrdenadas")
        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icono_ruta)
        winreg.CloseKey(key)
        
        command_path = key_path + r"\command"
        key_command = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, command_path)
        comando = f'"{self.ruta_ejecutable}" --auto --dir "%1"'
        winreg.SetValue(key_command, "", winreg.REG_SZ, comando)
        winreg.CloseKey(key_command)
    
    def desregistrar_menu_contextual(self) -> Tuple[bool, str]:
        """Elimina la integración con el menú contextual."""
        try:
            if sys.platform == "darwin":
                return self._desregistrar_macos()
            if sys.platform != "win32":
                return self._desregistrar_linux()

            try:
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\DescargasOrdenadas\command")
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\DescargasOrdenadas")
            except FileNotFoundError:
                pass
            
            try:
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\DescargasOrdenadas\command")
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\DescargasOrdenadas")
            except FileNotFoundError:
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
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\DescargasOrdenadas")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False
