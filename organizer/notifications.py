#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de notificaciones de escritorio multiplataforma
"""

import platform
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from plyer import notification as plyer_notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

logger = logging.getLogger(__name__)

class NotificadorEscritorio:
    """
    Gestor de notificaciones de escritorio multiplataforma.
    """
    
    def __init__(self):
        self.sistema = platform.system().lower()
        self.habilitado = True
        self.metodo_preferido = self._detectar_mejor_metodo()
        self.icono_app = None
        self._configurar_icono()
    
    def _detectar_mejor_metodo(self) -> str:
        """Detecta el mejor método de notificación disponible."""
        if PLYER_AVAILABLE:
            return 'plyer'
        elif self.sistema == 'windows':
            return 'windows_native'
        elif self.sistema == 'darwin':  # macOS
            return 'macos_native'
        elif self.sistema == 'linux':
            return 'linux_native'
        else:
            return 'none'
    
    def _configurar_icono(self):
        """Configura el icono para las notificaciones."""
        try:
            # Buscar icono de la aplicación
            posibles_iconos = [
                Path(__file__).parent.parent / "resources" / "icon.png",
                Path(__file__).parent.parent / "resources" / "icon.ico",
                Path(__file__).parent / "resources" / "icon.png",
                "/usr/share/pixmaps/descargasordenadas.png",
                "resources/icon.png"
            ]
            
            for icono in posibles_iconos:
                if icono.exists():
                    self.icono_app = str(icono)
                    logger.debug(f"Icono configurado: {self.icono_app}")
                    break
        except Exception as e:
            logger.debug(f"No se pudo configurar icono: {e}")
    
    def notificar(self, titulo: str, mensaje: str, tipo: str = "info", 
                  timeout: int = 5) -> bool:
        """
        Envía una notificación de escritorio.
        
        Args:
            titulo: Título de la notificación
            mensaje: Mensaje de la notificación
            tipo: Tipo de notificación ('info', 'success', 'warning', 'error')
            timeout: Tiempo en segundos antes de que desaparezca
            
        Returns:
            True si se envió correctamente
        """
        if not self.habilitado:
            return False
        
        try:
            if self.metodo_preferido == 'plyer':
                return self._notificar_plyer(titulo, mensaje, timeout)
            elif self.metodo_preferido == 'windows_native':
                return self._notificar_windows(titulo, mensaje, tipo)
            elif self.metodo_preferido == 'macos_native':
                return self._notificar_macos(titulo, mensaje)
            elif self.metodo_preferido == 'linux_native':
                return self._notificar_linux(titulo, mensaje, tipo, timeout)
            else:
                logger.debug("No hay método de notificación disponible")
                return False
                
        except Exception as e:
            logger.error(f"Error enviando notificación: {e}")
            return False
    
    def _notificar_plyer(self, titulo: str, mensaje: str, timeout: int) -> bool:
        """Envía notificación usando plyer (multiplataforma)."""
        try:
            plyer_notification.notify(
                title=titulo,
                message=mensaje,
                app_name="DescargasOrdenadas",
                app_icon=self.icono_app,
                timeout=timeout
            )
            return True
        except Exception as e:
            logger.error(f"Error con plyer: {e}")
            return False
    
    def _notificar_windows(self, titulo: str, mensaje: str, tipo: str) -> bool:
        """Envía notificación en Windows usando PowerShell."""
        try:
            # Mapeo de tipos a iconos de Windows
            iconos = {
                'info': 'Info',
                'success': 'Info', 
                'warning': 'Warning',
                'error': 'Error'
            }
            icono = iconos.get(tipo, 'Info')
            
            # Script PowerShell para mostrar notificación
            script = f'''
            Add-Type -AssemblyName System.Windows.Forms
            $notification = New-Object System.Windows.Forms.NotifyIcon
            $notification.Icon = [System.Drawing.SystemIcons]::{icono}
            $notification.BalloonTipTitle = "{titulo}"
            $notification.BalloonTipText = "{mensaje}"
            $notification.BalloonTipIcon = "{icono}"
            $notification.Visible = $true
            $notification.ShowBalloonTip(5000)
            Start-Sleep -Seconds 6
            $notification.Dispose()
            '''
            
            subprocess.run([
                'powershell', '-WindowStyle', 'Hidden', '-Command', script
            ], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            return True
            
        except Exception as e:
            logger.error(f"Error con notificación Windows: {e}")
            return False
    
    def _notificar_macos(self, titulo: str, mensaje: str) -> bool:
        """Envía notificación en macOS usando osascript."""
        try:
            script = f'''
            display notification "{mensaje}" with title "DescargasOrdenadas" subtitle "{titulo}"
            '''
            
            subprocess.run(['osascript', '-e', script], check=True)
            return True
            
        except Exception as e:
            logger.error(f"Error con notificación macOS: {e}")
            return False
    
    def _notificar_linux(self, titulo: str, mensaje: str, tipo: str, timeout: int) -> bool:
        """Envía notificación en Linux usando notify-send."""
        try:
            # Mapeo de tipos a iconos de Linux
            iconos = {
                'info': 'dialog-information',
                'success': 'dialog-information',
                'warning': 'dialog-warning', 
                'error': 'dialog-error'
            }
            icono = iconos.get(tipo, 'dialog-information')
            
            cmd = [
                'notify-send',
                '--app-name=DescargasOrdenadas',
                f'--expire-time={timeout * 1000}',  # notify-send usa milisegundos
                f'--icon={icono}',
                titulo,
                mensaje
            ]
            
            # Si tenemos icono personalizado, usarlo
            if self.icono_app:
                cmd[3] = f'--icon={self.icono_app}'
            
            subprocess.run(cmd, check=True)
            return True
            
        except FileNotFoundError:
            logger.warning("notify-send no encontrado en Linux")
            return False
        except Exception as e:
            logger.error(f"Error con notificación Linux: {e}")
            return False
    
    def notificar_organizacion(self, archivos_organizados: int, 
                             categorias_usadas: int) -> bool:
        """
        Notificación específica para organización completada.
        
        Args:
            archivos_organizados: Número de archivos organizados
            categorias_usadas: Número de categorías utilizadas
            
        Returns:
            True si se envió correctamente
        """
        if archivos_organizados == 0:
            return False
        
        titulo = "🎉 Organización Completada"
        
        if archivos_organizados == 1:
            mensaje = f"Se organizó 1 archivo en {categorias_usadas} categoría"
        else:
            mensaje = f"Se organizaron {archivos_organizados} archivos en {categorias_usadas} categorías"
        
        return self.notificar(titulo, mensaje, tipo="success")
    
    def notificar_archivo_nuevo(self, nombre_archivo: str, categoria: str) -> bool:
        """
        Notificación para archivo organizado automáticamente.
        
        Args:
            nombre_archivo: Nombre del archivo organizado
            categoria: Categoría donde se organizó
            
        Returns:
            True si se envió correctamente
        """
        titulo = "📂 Archivo Organizado"
        mensaje = f"{nombre_archivo} → {categoria}"
        
        return self.notificar(titulo, mensaje, tipo="info", timeout=3)
    
    def notificar_duplicados(self, duplicados_encontrados: int, 
                           espacio_liberado: str) -> bool:
        """
        Notificación para duplicados encontrados/eliminados.
        
        Args:
            duplicados_encontrados: Número de duplicados
            espacio_liberado: Espacio liberado (formato legible)
            
        Returns:
            True si se envió correctamente
        """
        titulo = "🔍 Duplicados Detectados"
        mensaje = f"Encontrados {duplicados_encontrados} duplicados\nEspacio liberado: {espacio_liberado}"
        
        return self.notificar(titulo, mensaje, tipo="warning")
    
    def notificar_error(self, error_mensaje: str) -> bool:
        """
        Notificación de error.
        
        Args:
            error_mensaje: Mensaje de error
            
        Returns:
            True si se envió correctamente
        """
        titulo = "❌ Error en DescargasOrdenadas"
        return self.notificar(titulo, error_mensaje, tipo="error")
    
    def notificar_monitor_iniciado(self, carpeta: str) -> bool:
        """
        Notificación cuando se inicia el monitor en tiempo real.
        
        Args:
            carpeta: Carpeta que se está monitoreando
            
        Returns:
            True si se envió correctamente
        """
        titulo = "🔄 Monitor Iniciado"
        mensaje = f"Monitoreando: {Path(carpeta).name}"
        
        return self.notificar(titulo, mensaje, tipo="info")
    
    def configurar(self, habilitado: bool = True, metodo: Optional[str] = None):
        """
        Configura el sistema de notificaciones.
        
        Args:
            habilitado: Si las notificaciones están habilitadas
            metodo: Método específico a usar ('plyer', 'native', 'none')
        """
        self.habilitado = habilitado
        
        if metodo and metodo != self.metodo_preferido:
            if metodo == 'plyer' and PLYER_AVAILABLE:
                self.metodo_preferido = 'plyer'
            elif metodo == 'native':
                if self.sistema == 'windows':
                    self.metodo_preferido = 'windows_native'
                elif self.sistema == 'darwin':
                    self.metodo_preferido = 'macos_native'
                elif self.sistema == 'linux':
                    self.metodo_preferido = 'linux_native'
            elif metodo == 'none':
                self.metodo_preferido = 'none'
        
        logger.info(f"🔔 Notificaciones configuradas - Habilitado: {habilitado}, Método: {self.metodo_preferido}")
    
    def probar_notificacion(self) -> bool:
        """
        Envía una notificación de prueba.
        
        Returns:
            True si la prueba fue exitosa
        """
        titulo = "🧪 Prueba de Notificación"
        mensaje = f"DescargasOrdenadas funciona correctamente\nMétodo: {self.metodo_preferido}"
        
        return self.notificar(titulo, mensaje, tipo="info")
    
    def obtener_estado(self) -> Dict[str, Any]:
        """Obtiene el estado actual del sistema de notificaciones."""
        return {
            'habilitado': self.habilitado,
            'metodo_preferido': self.metodo_preferido,
            'plyer_disponible': PLYER_AVAILABLE,
            'sistema': self.sistema,
            'icono_configurado': self.icono_app is not None
        }

# Instancia global del notificador
notificador = NotificadorEscritorio()

# Funciones de conveniencia
def notificar_organizacion(archivos: int, categorias: int) -> bool:
    """Función de conveniencia para notificar organización."""
    return notificador.notificar_organizacion(archivos, categorias)

def notificar_archivo_nuevo(archivo: str, categoria: str) -> bool:
    """Función de conveniencia para notificar archivo nuevo."""
    return notificador.notificar_archivo_nuevo(archivo, categoria)

def notificar_error(mensaje: str) -> bool:
    """Función de conveniencia para notificar error."""
    return notificador.notificar_error(mensaje) 