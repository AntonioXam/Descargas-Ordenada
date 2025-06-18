#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Monitor en tiempo real para organización automática de archivos
"""

import time
import threading
from pathlib import Path
from typing import Callable, Optional, Set
import logging
from datetime import datetime

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    # Crear clases dummy para evitar errores
    class Observer:
        def __init__(self):
            pass
        def schedule(self, *args, **kwargs):
            pass
        def start(self):
            pass
        def stop(self):
            pass
        def join(self, timeout=None):
            pass
        def is_alive(self):
            return False
    
    class FileSystemEventHandler:
        def __init__(self):
            pass
        def on_created(self, event):
            pass
        def on_moved(self, event):
            pass
        def on_modified(self, event):
            pass
        def on_deleted(self, event):
            pass

logger = logging.getLogger(__name__)

class EventosDescarga(FileSystemEventHandler):
    """
    Maneja eventos del sistema de archivos para organización automática.
    """
    
    def __init__(self, organizador_callback: Callable, delay_segundos: int = 3):
        super().__init__()
        self.organizador_callback = organizador_callback
        self.delay_segundos = delay_segundos
        self.archivos_pendientes: Set[Path] = set()
        self.timers: dict = {}
        self.lock = threading.Lock()
    
    def on_created(self, event):
        """Se ejecuta cuando se crea un archivo."""
        if not event.is_directory:
            archivo = Path(event.src_path)
            self._programar_organizacion(archivo)
    
    def on_moved(self, event):
        """Se ejecuta cuando se mueve/renombra un archivo."""
        if not event.is_directory:
            archivo = Path(event.dest_path)
            self._programar_organizacion(archivo)
    
    def on_modified(self, event):
        """Se ejecuta cuando se modifica un archivo."""
        if not event.is_directory:
            archivo = Path(event.src_path)
            # Solo reprogramar si el archivo está creciendo (descarga en progreso)
            self._programar_organizacion(archivo)
    
    def _programar_organizacion(self, archivo: Path):
        """
        Programa la organización de un archivo después de un delay.
        Esto evita organizar archivos que aún se están descargando.
        """
        with self.lock:
            # Cancelar timer existente si lo hay
            if archivo in self.timers:
                self.timers[archivo].cancel()
            
            # Programar nuevo timer
            timer = threading.Timer(self.delay_segundos, self._organizar_archivo, [archivo])
            self.timers[archivo] = timer
            timer.start()
            
            logger.debug(f"Programado para organizar: {archivo.name}")
    
    def _organizar_archivo(self, archivo: Path):
        """
        Organiza un archivo específico.
        """
        try:
            with self.lock:
                # Remover de timers
                if archivo in self.timers:
                    del self.timers[archivo]
            
            # Verificar que el archivo aún existe y no está siendo usado
            if not archivo.exists():
                return
            
            # Intentar detectar si el archivo aún se está descargando
            if self._archivo_en_uso(archivo):
                logger.debug(f"Archivo aún en uso, reprogramando: {archivo.name}")
                self._programar_organizacion(archivo)
                return
            
            # Organizar el archivo
            logger.info(f"🔄 Organizando automáticamente: {archivo.name}")
            self.organizador_callback(archivo)
            
        except Exception as e:
            logger.error(f"Error organizando {archivo}: {e}")
    
    def _archivo_en_uso(self, archivo: Path) -> bool:
        """
        Detecta si un archivo está siendo usado (descarga en progreso).
        """
        try:
            # Método 1: Intentar abrir en modo exclusivo
            with open(archivo, 'r+b') as f:
                pass
            return False
        except (PermissionError, IOError):
            return True
        except Exception:
            return False
    
    def detener(self):
        """Detiene todos los timers pendientes."""
        with self.lock:
            for timer in self.timers.values():
                timer.cancel()
            self.timers.clear()

class MonitorTiempoReal:
    """
    Monitor principal para organización automática en tiempo real.
    """
    
    def __init__(self, carpeta_vigilar: Path, organizador_callback: Callable):
        self.carpeta_vigilar = carpeta_vigilar
        self.organizador_callback = organizador_callback
        self.observer: Optional[Observer] = None
        self.event_handler: Optional[EventosDescarga] = None
        self.activo = False
        
        if not WATCHDOG_AVAILABLE:
            logger.warning("Watchdog no disponible, monitoreo en tiempo real deshabilitado")
    
    def iniciar(self, delay_segundos: int = 3) -> bool:
        """
        Inicia el monitoreo en tiempo real.
        
        Args:
            delay_segundos: Segundos a esperar antes de organizar un archivo
            
        Returns:
            True si se inició correctamente, False si no
        """
        if not WATCHDOG_AVAILABLE:
            logger.error("No se puede iniciar: watchdog no está disponible")
            return False
        
        if self.activo:
            logger.warning("Monitor ya está activo")
            return True
        
        try:
            self.event_handler = EventosDescarga(self.organizador_callback, delay_segundos)
            self.observer = Observer()
            self.observer.schedule(
                self.event_handler,
                str(self.carpeta_vigilar),
                recursive=False
            )
            
            self.observer.start()
            self.activo = True
            
            logger.info(f"🔄 Monitor iniciado en: {self.carpeta_vigilar}")
            logger.info(f"⏱️  Delay de organización: {delay_segundos} segundos")
            
            return True
            
        except Exception as e:
            logger.error(f"Error iniciando monitor: {e}")
            return False
    
    def detener(self):
        """Detiene el monitoreo en tiempo real."""
        if not self.activo:
            return
        
        try:
            if self.event_handler:
                self.event_handler.detener()
            
            if self.observer:
                self.observer.stop()
                self.observer.join(timeout=5)
            
            self.activo = False
            logger.info("🛑 Monitor detenido")
            
        except Exception as e:
            logger.error(f"Error deteniendo monitor: {e}")
    
    def esta_activo(self) -> bool:
        """Retorna si el monitor está activo."""
        return self.activo and self.observer and self.observer.is_alive()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.detener()

def instalar_watchdog():
    """
    Función auxiliar para instalar watchdog si no está disponible.
    """
    try:
        import subprocess
        import sys
        
        logger.info("Instalando watchdog...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'watchdog'])
        
        global WATCHDOG_AVAILABLE
        WATCHDOG_AVAILABLE = True
        
        logger.info("✅ Watchdog instalado correctamente")
        return True
        
    except Exception as e:
        logger.error(f"Error instalando watchdog: {e}")
        return False 