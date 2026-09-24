#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sistema de notificaciones nativas para DescargasOrdenadas v3.1"""

import logging
import sys
import subprocess

from .app_paths import obtener_recurso

logger = logging.getLogger('organizador.native_notifications')

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False


def _usar_metodo_nativo() -> bool:
    """En macOS y Linux el método del sistema es más fiable que plyer.

    En macOS plyer depende de pyobjus (no siempre instalado) y en Linux
    requiere que exista un demonio de notificaciones; en ambos casos el
    comando nativo da mejor resultado y no ensucia la salida de errores.
    """
    return sys.platform == "darwin" or sys.platform.startswith("linux")


class NotificadorNativo:
    """Gestor de notificaciones nativas multiplataforma."""
    
    def __init__(self, app_name="DescargasOrdenadas", icono_path=None):
        self.app_name = app_name
        self.icono_path = icono_path
        self.habilitado = True
        # Motivo del último fallo al notificar ('' si el último intento fue bien).
        self._ultimo_fallo = ""
        
        if not self.icono_path:
            iconos = [
                obtener_recurso("favicon.ico"),
                obtener_recurso("icon.png"),
            ]
            for icono in iconos:
                if icono.exists():
                    self.icono_path = str(icono)
                    break
    
    def mostrar(self, titulo, mensaje, tipo="info", duracion=5):
        """Muestra una notificación nativa."""
        if not self.habilitado:
            return

        self._ultimo_fallo = ""

        if _usar_metodo_nativo():
            self._notificar_sistema(titulo, mensaje)
            return

        if not PLYER_AVAILABLE:
            self._notificar_sistema(titulo, mensaje)
            return

        try:
            notification.notify(
                title=f"{self.app_name} - {titulo}",
                message=mensaje,
                app_name=self.app_name,
                app_icon=self.icono_path if self.icono_path else None,
                timeout=duracion
            )
        except Exception as e:
            logger.debug(f"plyer no pudo notificar: {e}")
            # plyer falló (p.ej. en macOS no tiene implementación): usar el método nativo
            self._notificar_sistema(titulo, mensaje)

    def ultimo_fallo(self) -> str:
        """Motivo del último fallo al notificar, o '' si fue bien."""
        return self._ultimo_fallo
    
    def _notificar_sistema(self, titulo, mensaje) -> bool:
        """Método nativo del sistema, sin depender de plyer.

        Devuelve si se pudo enviar. Un fallo aquí no debe pasar inadvertido: si
        las notificaciones no funcionan, el usuario tiene que poder saberlo (el
        centro de permisos lo muestra), en lugar de no recibir avisos sin
        explicación.
        """
        try:
            if sys.platform == "darwin":
                # Escapar comillas para el AppleScript
                titulo_escapado = titulo.replace('"', '\\"')
                mensaje_escapado = mensaje.replace('"', '\\"')
                script = (
                    f'display notification "{mensaje_escapado}" '
                    f'with title "DescargasOrdenadas" subtitle "{titulo_escapado}"'
                )
                subprocess.run(
                    ['osascript', '-e', script], check=True, capture_output=True
                )
                self._ultimo_fallo = ""
                return True

            if sys.platform.startswith("linux"):
                subprocess.run(
                    ['notify-send', 'DescargasOrdenadas', titulo, mensaje],
                    check=True, capture_output=True
                )
                self._ultimo_fallo = ""
                return True

            if sys.platform == "win32":
                # Sin Windows 10/11 a mano, el aviso nativo se envía con
                # PowerShell; antes este caso no existía y el respaldo no hacía
                # nada en Windows.
                script = (
                    "Add-Type -AssemblyName System.Windows.Forms;"
                    "$n = New-Object System.Windows.Forms.NotifyIcon;"
                    "$n.Icon = [System.Drawing.SystemIcons]::Information;"
                    f'$n.BalloonTipTitle = "{titulo}";'
                    f'$n.BalloonTipText = "{mensaje}";'
                    "$n.Visible = $true; $n.ShowBalloonTip(5000);"
                    "Start-Sleep -Seconds 6; $n.Dispose()"
                )
                subprocess.run(
                    ['powershell', '-WindowStyle', 'Hidden', '-Command', script],
                    check=True, capture_output=True,
                )
                return True
        except FileNotFoundError as e:
            self._ultimo_fallo = f"no se encontró el comando de notificaciones ({e})"
        except subprocess.CalledProcessError as e:
            detalle = (e.stderr or b"").decode(errors="replace").strip()[:200]
            self._ultimo_fallo = f"el comando falló ({detalle or e.returncode})"
        except Exception as e:
            self._ultimo_fallo = str(e)

        logger.warning(f"No se pudo mostrar la notificación: {self._ultimo_fallo}")
        return False
    
    def notificar_organizacion(self, cantidad_archivos, categorias):
        """Notificación de organización de archivos."""
        if cantidad_archivos == 0:
            return
        
        mensaje = f"{cantidad_archivos} archivo{'s' if cantidad_archivos > 1 else ''} organizados"
        if categorias:
            cats = ", ".join(list(categorias)[:3])
            if len(categorias) > 3:
                cats += f" y {len(categorias) - 3} más"
            mensaje += f"\n📂 {cats}"
        
        self.mostrar("Organización Completada", mensaje, tipo="success")
    
    def notificar_duplicados(self, cantidad, espacio_liberado):
        """Notificación de duplicados eliminados."""
        if cantidad == 0:
            return
        
        espacio_mb = espacio_liberado / (1024 * 1024)
        if espacio_mb < 1:
            espacio_str = f"{espacio_liberado / 1024:.1f} KB"
        else:
            espacio_str = f"{espacio_mb:.1f} MB"
        
        mensaje = f"{cantidad} duplicados eliminados\n💾 {espacio_str} liberados"
        self.mostrar("Duplicados Eliminados", mensaje, tipo="success")
    
    def notificar_error(self, mensaje_error):
        """Notificación de error."""
        self.mostrar("Error", mensaje_error, tipo="error", duracion=10)
    
    def notificar_inicio(self):
        """Notificación de inicio."""
        self.mostrar("Aplicación Iniciada", "Organizador automático activo", tipo="info", duracion=3)
    
    def habilitar(self):
        """Habilita las notificaciones."""
        self.habilitado = True
    
    def deshabilitar(self):
        """Deshabilita las notificaciones."""
        self.habilitado = False
    
    def esta_habilitado(self):
        """Verifica si están habilitadas."""
        return self.habilitado

# Instancia global
_notificador_global = None

def obtener_notificador():
    """Obtiene la instancia global del notificador."""
    global _notificador_global
    if _notificador_global is None:
        _notificador_global = NotificadorNativo()
    return _notificador_global

def notificar(titulo, mensaje, tipo="info", duracion=5):
    """Función de conveniencia."""
    obtener_notificador().mostrar(titulo, mensaje, tipo, duracion)

def notificar_organizacion(cantidad_archivos, categorias):
    """Función de conveniencia."""
    obtener_notificador().notificar_organizacion(cantidad_archivos, categorias)

def notificar_duplicados(cantidad, espacio_liberado):
    """Función de conveniencia."""
    obtener_notificador().notificar_duplicados(cantidad, espacio_liberado)
