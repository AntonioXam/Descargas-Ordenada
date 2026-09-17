#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shlex
import subprocess
import logging
from pathlib import Path
from typing import Optional, Tuple

# winreg solo existe en Windows; importarlo en macOS/Linux rompía la app al arrancar
if sys.platform == "win32":
    import winreg

logger = logging.getLogger('organizador.autostart')

class GestorAutoarranque:
    """Gestiona el autoarranque de la aplicación en diferentes sistemas operativos."""
    
    def __init__(self, nombre_app: str = "DescargasOrdenadas"):
        """
        Inicializa el gestor de autoarranque.
        
        Args:
            nombre_app: Nombre de la aplicación para identificarla en las tareas de inicio.
        """
        self.nombre_app = nombre_app
        self.ruta_ejecutable = self._obtener_ruta_ejecutable()
        
    def _obtener_ruta_ejecutable(self) -> str:
        """
        Obtiene la ruta al ejecutable actual (script o aplicación empaquetada).
        
        Returns:
            Ruta absoluta al ejecutable.
        """
        if getattr(sys, 'frozen', False):
            # Si estamos en una aplicación empaquetada
            return sys.executable
        else:
            # Si estamos en un script
            return str(Path(sys.argv[0]).resolve())
    
    def _configurar_windows(self, activar: bool) -> Tuple[bool, str]:
        """
        Configura el autoarranque en Windows usando el registro.
        
        Args:
            activar: True para activar, False para desactivar.
            
        Returns:
            Tupla con éxito (bool) y mensaje informativo (str).
        """
        try:
            # Usar el registro de Windows para el autoarranque
            registro = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            
            try:
                # Abrir la clave si existe
                key = winreg.OpenKey(registro, key_path, 0, winreg.KEY_ALL_ACCESS)
            except WindowsError:
                # Crear la clave si no existe
                key = winreg.CreateKey(registro, key_path)
            
            if activar:
                # Determinar la ruta del proyecto
                if getattr(sys, 'frozen', False):
                    # Si es un ejecutable empaquetado
                    comando = f'"{self.ruta_ejecutable}" --inicio-sistema --minimizado'
                else:
                    # Si es un script de Python, usar el .bat apropiado
                    proyecto_dir = Path(__file__).resolve().parent.parent
                    
                    # Buscar el lanzador .bat raíz de la distribución actual
                    bat_principal = proyecto_dir / "INICIAR.bat"
                    
                    if bat_principal.exists():
                        bat_file = bat_principal
                        comando = f'"{bat_file}" --autostart --minimizado'
                    else:
                        # Fallback al método anterior si no hay .bat
                        python_exe = sys.executable
                        if python_exe.endswith('python.exe'):
                            python_exe = python_exe.replace('python.exe', 'pythonw.exe')
                        iniciar_py = Path(__file__).resolve().parent / "INICIAR.py"
                        comando = f'"{python_exe}" "{iniciar_py}" --autostart --minimizado'
                        logger.warning("No se encontraron archivos .bat, usando Python directamente")
                
                logger.info(f"Configurando autoarranque con comando: {comando}")
                
                # Añadir al registro
                winreg.SetValueEx(key, self.nombre_app, 0, winreg.REG_SZ, comando)
                winreg.CloseKey(key)
                return True, "Autoarranque configurado correctamente en Windows (se iniciará minimizado usando .bat)."
            else:
                # Eliminar del registro
                try:
                    winreg.DeleteValue(key, self.nombre_app)
                except WindowsError:
                    # No hacer nada si la clave no existe
                    pass
                winreg.CloseKey(key)
                return True, "Autoarranque desactivado correctamente en Windows."
        except Exception as e:
            error_msg = f"Error al configurar autoarranque en Windows: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def _configurar_macos(self, activar: bool) -> Tuple[bool, str]:
        """
        Configura el autoarranque en macOS usando launchd.
        
        Args:
            activar: True para activar, False para desactivar.
            
        Returns:
            Tupla con éxito (bool) y mensaje informativo (str).
        """
        # Ruta al archivo plist
        ruta_plist = Path(os.path.expanduser('~')) / 'Library' / 'LaunchAgents' / f'com.{self.nombre_app}.plist'
        
        try:
            if activar:
                # Crear directorio si no existe
                ruta_plist.parent.mkdir(parents=True, exist_ok=True)
                
                # Comando de arranque: usar el mismo intérprete de Python y
                # los argumentos reales que soporta INICIAR.py
                if getattr(sys, 'frozen', False):
                    comando_args = [self.ruta_ejecutable, '--autostart', '--minimizado']
                else:
                    iniciar_py = Path(__file__).resolve().parent / 'INICIAR.py'
                    comando_args = [sys.executable, str(iniciar_py), '--autostart', '--minimizado']

                # Escapar rutas para XML (espacios, &, <, >)
                import xml.sax.saxutils as saxutils
                comando_xml = [saxutils.escape(arg) for arg in comando_args]
                args_xml = "\n".join(
                    f"        <string>{arg}</string>" for arg in comando_xml
                )

                # Contenido del archivo plist
                contenido_plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.{self.nombre_app}</string>
    <key>ProgramArguments</key>
    <array>
{args_xml}
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
'''
                # Escribir archivo plist
                with open(ruta_plist, 'w', encoding='utf-8') as f:
                    f.write(contenido_plist)
                
                # Cargar servicio: preferir la sintaxis moderna (bootstrap)
                # y hacer fallback a la clásica (load -w) en macOS antiguos
                uid = str(os.getuid())
                cargado = False
                try:
                    subprocess.check_call(
                        ['launchctl', 'bootstrap', f'gui/{uid}', str(ruta_plist)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    cargado = True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    try:
                        subprocess.check_call(
                            ['launchctl', 'load', '-w', str(ruta_plist)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                        )
                        cargado = True
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        pass

                if cargado:
                    return True, "Autoarranque configurado correctamente en macOS (LaunchAgent)."
                return False, "No se pudo cargar el LaunchAgent de macOS (launchctl)."
            else:
                # Descargar servicio si existe
                if ruta_plist.exists():
                    uid = str(os.getuid())
                    try:
                        subprocess.run(
                            ['launchctl', 'bootout', f'gui/{uid}', str(ruta_plist)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                        )
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        subprocess.run(
                            ['launchctl', 'unload', '-w', str(ruta_plist)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                        )
                    ruta_plist.unlink()
                return True, "Autoarranque desactivado correctamente en macOS."
        except Exception as e:
            error_msg = f"Error al configurar autoarranque en macOS: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def _configurar_linux(self, activar: bool) -> Tuple[bool, str]:
        """
        Configura el autoarranque en Linux usando systemd user service.
        
        Args:
            activar: True para activar, False para desactivar.
            
        Returns:
            Tupla con éxito (bool) y mensaje informativo (str).
        """
        # Ruta al archivo de servicio
        ruta_service = Path(os.path.expanduser('~')) / '.config' / 'systemd' / 'user' / f'{self.nombre_app.lower()}.service'
        
        try:
            if activar:
                # Crear directorio si no existe
                ruta_service.parent.mkdir(parents=True, exist_ok=True)

                if getattr(sys, 'frozen', False):
                    comando_args = [self.ruta_ejecutable, '--autostart', '--minimizado']
                    directorio_trabajo = str(Path(self.ruta_ejecutable).parent)
                else:
                    iniciar_py = Path(__file__).resolve().parent / 'INICIAR.py'
                    comando_args = [sys.executable, str(iniciar_py), '--autostart', '--minimizado']
                    directorio_trabajo = str(Path(__file__).resolve().parent.parent)

                exec_start = " ".join(shlex.quote(arg) for arg in comando_args)
                working_directory = shlex.quote(directorio_trabajo)
                
                # Contenido del archivo de servicio
                contenido_service = f'''[Unit]
Description={self.nombre_app} - Organizador de descargas
After=graphical-session.target

[Service]
Type=simple
ExecStart={exec_start}
WorkingDirectory={working_directory}
Restart=on-failure

[Install]
WantedBy=graphical-session.target
'''
                # Escribir archivo de servicio
                with open(ruta_service, 'w', encoding='utf-8') as f:
                    f.write(contenido_service)
                
                # Habilitar y arrancar servicio
                subprocess.check_call(['systemctl', '--user', 'daemon-reload'])
                subprocess.check_call(['systemctl', '--user', 'enable', ruta_service.name])
                subprocess.check_call(['systemctl', '--user', 'start', ruta_service.name])
                return True, "Autoarranque configurado correctamente en Linux (systemd user)."
            else:
                # Deshabilitar y detener servicio si existe
                if ruta_service.exists():
                    subprocess.check_call(['systemctl', '--user', 'stop', ruta_service.name])
                    subprocess.check_call(['systemctl', '--user', 'disable', ruta_service.name])
                    ruta_service.unlink()
                return True, "Autoarranque desactivado correctamente en Linux."
        except Exception as e:
            error_msg = f"Error al configurar autoarranque en Linux: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def configurar_autoarranque(self, activar: bool) -> Tuple[bool, str]:
        """
        Configura el autoarranque de la aplicación según el sistema operativo.
        
        Args:
            activar: True para activar, False para desactivar.
            
        Returns:
            Tupla con éxito (bool) y mensaje informativo (str).
        """
        if sys.platform == 'win32':
            # Windows
            return self._configurar_windows(activar)
        elif sys.platform == 'darwin':
            # macOS
            return self._configurar_macos(activar)
        else:
            # Linux y otros sistemas Unix
            return self._configurar_linux(activar)
    
    def verificar_autoarranque(self) -> bool:
        """
        Verifica si el autoarranque está configurado.
        
        Returns:
            True si está configurado, False en caso contrario.
        """
        try:
            if sys.platform == 'win32':
                # Windows - Verificar si existe en el registro
                registro = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                key = winreg.OpenKey(registro, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run")
                
                try:
                    value, _ = winreg.QueryValueEx(key, self.nombre_app)
                    winreg.CloseKey(key)
                    return True
                except WindowsError:
                    winreg.CloseKey(key)
                    return False
            
            elif sys.platform == 'darwin':
                # macOS - Verificar si existe el archivo plist
                ruta_plist = Path(os.path.expanduser('~')) / 'Library' / 'LaunchAgents' / f'com.{self.nombre_app}.plist'
                return ruta_plist.exists()
            
            else:
                # Linux - Verificar si existe el servicio y está activo
                ruta_service = Path(os.path.expanduser('~')) / '.config' / 'systemd' / 'user' / f'{self.nombre_app.lower()}.service'
                return ruta_service.exists() and subprocess.run(
                    ['systemctl', '--user', 'is-enabled', ruta_service.name],
                    capture_output=True
                ).returncode == 0
        
        except Exception as e:
            logger.error(f"Error al verificar autoarranque: {e}")
            return False 
