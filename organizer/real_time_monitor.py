#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Monitor en tiempo real para organización automática de archivos
"""

import time
import threading
from pathlib import Path
from typing import Callable, Optional, Set, Dict
import logging
from datetime import datetime
import sys

# Configurar logging
logger = logging.getLogger(__name__)

# Importaciones condicionales para watchdog
try:
    from watchdog.observers import Observer as WatchdogObserver
    from watchdog.events import FileSystemEventHandler as WatchdogFileSystemEventHandler
    WATCHDOG_AVAILABLE = True
    Observer = WatchdogObserver
    FileSystemEventHandler = WatchdogFileSystemEventHandler
except ImportError:
    logger.warning("Watchdog no está disponible. Monitoreo en tiempo real deshabilitado.")
    WATCHDOG_AVAILABLE = False
    
    # Crear clases mock para evitar errores
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

class EventosDescarga(FileSystemEventHandler):
    """
    Maneja eventos de descarga de archivos.
    """
    
    def __init__(self, organizador_callback: Callable, delay_segundos: int = 3):
        super().__init__()
        self.organizador_callback = organizador_callback
        self.delay_segundos = delay_segundos
        self.timers: Dict[Path, threading.Timer] = {}
        self.lock = threading.Lock()
    
    def on_created(self, event):
        if not event.is_directory:
            archivo = Path(event.src_path)
            self._programar_organizacion(archivo)
    
    def on_moved(self, event):
        if not event.is_directory:
            archivo = Path(event.dest_path)
            self._programar_organizacion(archivo)
    
    def on_modified(self, event):
        if not event.is_directory:
            archivo = Path(event.src_path)
            # Solo para archivos que no están siendo monitoreados aún
            if archivo not in self.timers:
                self._programar_organizacion(archivo)
    
    def _programar_organizacion(self, archivo: Path):
        """
        Programa la organización de un archivo después del delay especificado.
        Cancela cualquier timer previo para el mismo archivo.
        """
        with self.lock:
            # Cancelar timer existente si lo hay
            if archivo in self.timers:
                self.timers[archivo].cancel()
            
            # Crear nuevo timer
            timer = threading.Timer(self.delay_segundos, self._organizar_archivo, [archivo])
            self.timers[archivo] = timer
            timer.start()
            
            logger.debug(f"⏳ Programado para organizar en {self.delay_segundos}s: {archivo.name}")
    
    def _organizar_archivo(self, archivo: Path):
        """
        Organiza un archivo específico con sistema de reintentos mejorado.
        """
        max_reintentos = 3
        reintento = 0
        
        while reintento < max_reintentos:
            try:
                with self.lock:
                    # Remover de timers
                    if archivo in self.timers:
                        del self.timers[archivo]
                
                # Verificar que el archivo aún existe
                if not archivo.exists():
                    logger.debug(f"Archivo ya no existe: {archivo.name}")
                    return
                
                # Verificar si el archivo aún se está descargando
                if self._archivo_en_uso(archivo):
                    if reintento < max_reintentos - 1:
                        logger.debug(f"Archivo aún en uso, reintentando en {self.delay_segundos * 2} segundos: {archivo.name}")
                        # Aumentar el delay para archivos problemáticos
                        timer = threading.Timer(self.delay_segundos * 2, self._organizar_archivo, [archivo])
                        with self.lock:
                            self.timers[archivo] = timer
                        timer.start()
                        return
                    else:
                        logger.warning(f"Archivo sigue en uso después de {max_reintentos} intentos: {archivo.name}")
                        return
                
                # Verificar que el archivo tenga un tamaño razonable (no esté vacío)
                if archivo.stat().st_size == 0:
                    logger.debug(f"Archivo vacío, saltando: {archivo.name}")
                    return
                
                # Organizar el archivo
                logger.info(f"🔄 Organizando automáticamente: {archivo.name}")
                self.organizador_callback(archivo)
                return  # Éxito, salir del bucle
            
            except Exception as e:
                reintento += 1
                logger.warning(f"Error organizando {archivo} (intento {reintento}/{max_reintentos}): {e}")
                
                if reintento < max_reintentos:
                    # Esperar más tiempo antes del siguiente reintento
                    time.sleep(self.delay_segundos * reintento)
                else:
                    logger.error(f"❌ Falló organizar {archivo} después de {max_reintentos} intentos")
                    # Podrías agregar el archivo a una lista de "archivos problemáticos" aquí
    
    def _archivo_en_uso(self, archivo: Path) -> bool:
        """
        Detecta si un archivo está siendo usado (descarga en progreso).
        Usa múltiples métodos para mayor precisión.
        """
        try:
            # Método 1: Verificar si el archivo está creciendo
            try:
                tamaño_inicial = archivo.stat().st_size
                time.sleep(0.5)  # Esperar medio segundo
                tamaño_final = archivo.stat().st_size
                if tamaño_final > tamaño_inicial:
                    logger.debug(f"Archivo creciendo: {archivo.name}")
                    return True
            except (OSError, FileNotFoundError):
                return True  # Si no podemos acceder, probablemente está en uso
            
            # Método 2: Verificar nombres de archivos temporales comunes
            nombre_archivo = archivo.name.lower()
            if (nombre_archivo.endswith(('.tmp', '.temp', '.download', '.crdownload', '.part')) or
                nombre_archivo.startswith(('~', '.'))):
                logger.debug(f"Archivo temporal detectado: {archivo.name}")
                return True
            
            # Método 3: Intentar abrir en modo exclusivo (Windows)
            if sys.platform == "win32":
                try:
                    import msvcrt
                    with open(archivo, 'rb') as f:
                        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                    return False
                except (PermissionError, IOError, ImportError):
                    return True
            else:
                # En Unix/Linux, intentar abrir en modo lectura/escritura
                try:
                    with open(archivo, 'r+b') as f:
                        pass
                    return False
                except (PermissionError, IOError):
                    return True
            
            # Método 4: Verificar si el archivo es muy pequeño (puede estar empezando a descargarse)
            if archivo.stat().st_size < 1024:  # Menos de 1KB
                logger.debug(f"Archivo muy pequeño, esperando: {archivo.name}")
                return True
                
            return False
            
        except Exception as e:
            logger.debug(f"Error verificando archivo {archivo}: {e}")
            return True  # En caso de duda, asumir que está en uso
    
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
        if self.observer:
            return self.activo and self.observer.is_alive()
        return False
    
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