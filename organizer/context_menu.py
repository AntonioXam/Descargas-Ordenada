#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integración con el menú contextual de Windows"""

import sys
import logging
from pathlib import Path
from typing import Tuple

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
            script_dir = Path(sys.argv[0]).parent.absolute()
            launcher = script_dir / "INICIAR_SIN_CONSOLA.bat"
            if launcher.exists():
                return str(launcher)
            return str(Path(sys.argv[0]).resolve())
    
    def registrar_menu_contextual(self, tipo="carpetas") -> Tuple[bool, str]:
        """Registra la aplicación en el menú contextual."""
        if sys.platform != "win32":
            return False, "Solo disponible en Windows"
        
        try:
            if tipo in ["carpetas", "ambos"]:
                self._registrar_carpetas()
            
            if tipo in ["archivos", "ambos"]:
                self._registrar_archivos()
            
            return True, f"Menú contextual registrado para {tipo}"
        except Exception as e:
            logger.error(f"Error registrando menú contextual: {e}")
            return False, f"Error: {e}"
    
    def _registrar_carpetas(self):
        """Registra el menú contextual para carpetas."""
        key_path = r"Directory\shell\DescargasOrdenadas"
        
        key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)
        winreg.SetValue(key, "", winreg.REG_SZ, "🍄 Organizar con DescargasOrdenadas")
        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, self.ruta_ejecutable)
        winreg.CloseKey(key)
        
        command_path = key_path + r"\command"
        key_command = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, command_path)
        comando = f'"{self.ruta_ejecutable}" --dir "%1"'
        winreg.SetValue(key_command, "", winreg.REG_SZ, comando)
        winreg.CloseKey(key_command)
    
    def _registrar_archivos(self):
        """Registra el menú contextual para archivos."""
        key_path = r"*\shell\DescargasOrdenadas"
        
        key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)
        winreg.SetValue(key, "", winreg.REG_SZ, "🍄 Organizar archivo")
        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, self.ruta_ejecutable)
        winreg.CloseKey(key)
        
        command_path = key_path + r"\command"
        key_command = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, command_path)
        comando = f'"{self.ruta_ejecutable}" --dir "%1"'
        winreg.SetValue(key_command, "", winreg.REG_SZ, comando)
        winreg.CloseKey(key_command)
    
    def desregistrar_menu_contextual(self) -> Tuple[bool, str]:
        """Elimina la integración con el menú contextual."""
        if sys.platform != "win32":
            return False, "Solo disponible en Windows"
        
        try:
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
        """Verifica si el menú contextual está registrado."""
        if sys.platform != "win32":
            return False
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\DescargasOrdenadas")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False
