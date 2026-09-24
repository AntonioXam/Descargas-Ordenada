#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Organizador por fechas opcional con capacidad de revertir
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta
from collections import defaultdict

from .app_paths import crear_directorio, directorio_temporal_app

logger = logging.getLogger(__name__)

class OrganizadorPorFecha:
    """
    Organiza archivos por fecha de creación/modificación.
    Mantiene un registro para poder revertir la organización.
    """
    
    def __init__(self, carpeta_descargas: Path):
        self.carpeta_descargas = carpeta_descargas
        self.carpeta_config = carpeta_descargas / ".config"
        if not crear_directorio(self.carpeta_config):
            # Sin permiso de escritura en la carpeta de descargas, el registro
            # se guarda aparte para no impedir el arranque.
            self.carpeta_config = directorio_temporal_app() / "fechas"
            crear_directorio(self.carpeta_config)
        self.archivo_registro = self.carpeta_config / "organizacion_fechas.json"
        self.activo = False
        self.patron_fechas = "YYYY/MM-Mes"  # Patrón por defecto
        self.registro_movimientos: List[Dict[str, Any]] = []
        self._cargar_configuracion()
    
    def _cargar_configuracion(self):
        """Carga la configuración de organización por fechas."""
        if not self.archivo_registro.exists():
            return
        
        try:
            with open(self.archivo_registro, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.activo = data.get('activo', False)
            self.patron_fechas = data.get('patron_fechas', 'YYYY/MM-Mes')
            self.registro_movimientos = data.get('registro_movimientos', [])
            
            logger.info(f"📅 Configuración de fechas cargada - Activo: {self.activo}")
            
        except Exception as e:
            logger.error(f"Error cargando configuración de fechas: {e}")
    
    def _guardar_configuracion(self):
        """Guarda la configuración de organización por fechas."""
        try:
            data = {
                'activo': self.activo,
                'patron_fechas': self.patron_fechas,
                'ultima_actualizacion': datetime.now().isoformat(),
                'registro_movimientos': self.registro_movimientos[-1000:]  # Mantener últimos 1000
            }
            
            with open(self.archivo_registro, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Error guardando configuración de fechas: {e}")
    
    def activar(self, patron: str = "YYYY/MM-Mes") -> bool:
        """
        Activa la organización por fechas.
        
        Args:
            patron: Patrón de organización
                   - "YYYY/MM-Mes": 2024/12-Diciembre
                   - "YYYY/MM": 2024/12  
                   - "YYYY": 2024
                   - "MM-YYYY": 12-2024
                   - "Mes-YYYY": Diciembre-2024
        
        Returns:
            True si se activó correctamente
        """
        patrones_validos = ["YYYY/MM-Mes", "YYYY/MM", "YYYY", "MM-YYYY", "Mes-YYYY"]
        
        if patron not in patrones_validos:
            logger.error(f"Patrón inválido: {patron}. Válidos: {patrones_validos}")
            return False
        
        self.activo = True
        self.patron_fechas = patron
        self._guardar_configuracion()
        
        logger.info(f"✅ Organización por fechas activada con patrón: {patron}")
        return True
    
    def desactivar(self) -> bool:
        """
        Desactiva la organización por fechas.
        
        Returns:
            True si se desactivó correctamente
        """
        self.activo = False
        self._guardar_configuracion()
        
        logger.info("❌ Organización por fechas desactivada")
        return True
    
    def obtener_carpeta_fecha(self, archivo: Path, categoria: str, subcategoria: Optional[str] = None) -> Path:
        """
        Obtiene la carpeta de destino basada en la fecha del archivo.
        
        Args:
            archivo: Archivo a organizar
            categoria: Categoría del archivo
            subcategoria: Subcategoría del archivo
            
        Returns:
            Ruta de la carpeta de destino
        """
        if not self.activo:
            # Si no está activo, retornar estructura normal
            carpeta_destino = self.carpeta_descargas / categoria
            if subcategoria and subcategoria != "General":
                carpeta_destino = carpeta_destino / subcategoria
            return carpeta_destino
        
        try:
            # Obtener fecha del archivo (modificación por defecto)
            timestamp = archivo.stat().st_mtime
            fecha = datetime.fromtimestamp(timestamp)
            
            # Generar ruta según patrón
            carpeta_fecha = self._generar_carpeta_fecha(fecha)
            
            # Estructura: Downloads/Fechas/2024/12-Diciembre/Categoria/Subcategoria
            carpeta_destino = self.carpeta_descargas / "Fechas" / carpeta_fecha / categoria
            
            if subcategoria and subcategoria != "General":
                carpeta_destino = carpeta_destino / subcategoria
            
            return carpeta_destino
            
        except Exception as e:
            logger.error(f"Error obteniendo carpeta de fecha para {archivo}: {e}")
            # Fallback a estructura normal
            carpeta_destino = self.carpeta_descargas / categoria
            if subcategoria and subcategoria != "General":
                carpeta_destino = carpeta_destino / subcategoria
            return carpeta_destino
    
    def _generar_carpeta_fecha(self, fecha: datetime) -> Path:
        """Genera la ruta de carpeta según el patrón configurado."""
        meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        
        año = str(fecha.year)
        mes_num = f"{fecha.month:02d}"
        mes_nombre = meses[fecha.month - 1]
        
        if self.patron_fechas == "YYYY/MM-Mes":
            return Path(año) / f"{mes_num}-{mes_nombre}"
        elif self.patron_fechas == "YYYY/MM":
            return Path(año) / mes_num
        elif self.patron_fechas == "YYYY":
            return Path(año)
        elif self.patron_fechas == "MM-YYYY":
            return Path(f"{mes_num}-{año}")
        elif self.patron_fechas == "Mes-YYYY":
            return Path(f"{mes_nombre}-{año}")
        else:
            # Fallback
            return Path(año) / f"{mes_num}-{mes_nombre}"
    
    def registrar_movimiento(self, archivo_origen: Path, archivo_destino: Path, 
                           categoria: str, subcategoria: Optional[str] = None):
        """
        Registra un movimiento para poder revertirlo después.
        
        Args:
            archivo_origen: Ruta original del archivo
            archivo_destino: Ruta de destino del archivo
            categoria: Categoría asignada
            subcategoria: Subcategoría asignada
        """
        movimiento = {
            'timestamp': datetime.now().isoformat(),
            'origen': str(archivo_origen),
            'destino': str(archivo_destino),
            'categoria': categoria,
            'subcategoria': subcategoria,
            'patron_usado': self.patron_fechas,
            'activo_fecha': self.activo
        }
        
        self.registro_movimientos.append(movimiento)
        
        # Mantener solo los últimos 1000 movimientos
        if len(self.registro_movimientos) > 1000:
            self.registro_movimientos = self.registro_movimientos[-1000:]
        
        self._guardar_configuracion()
    
    def revertir_organizacion_fechas(self, confirmar: bool = False) -> Dict[str, Any]:
        """
        Revierte la organización por fechas, moviendo archivos de vuelta.
        
        Args:
            confirmar: Si True, ejecuta la reversión. Si False, solo simula.
            
        Returns:
            Diccionario con información de la reversión
        """
        if not self.registro_movimientos:
            return {
                'exito': False,
                'mensaje': 'No hay movimientos registrados para revertir',
                'archivos_afectados': 0
            }
        
        # Filtrar solo movimientos con organización por fechas
        movimientos_fecha = [
            m for m in self.registro_movimientos 
            if m.get('activo_fecha', False) and 'Fechas/' in m.get('destino', '')
        ]
        
        if not movimientos_fecha:
            return {
                'exito': False,
                'mensaje': 'No hay movimientos por fecha para revertir',
                'archivos_afectados': 0
            }
        
        archivos_revertidos = 0
        archivos_no_encontrados = 0
        errores = []
        
        logger.info(f"🔄 {'Simulando' if not confirmar else 'Ejecutando'} reversión de {len(movimientos_fecha)} movimientos...")
        
        for movimiento in reversed(movimientos_fecha):  # Revertir en orden inverso
            try:
                archivo_actual = Path(movimiento['destino'])
                carpeta_categoria = self.carpeta_descargas / movimiento['categoria']
                
                # Determinar destino según si había subcategoría
                if movimiento.get('subcategoria') and movimiento['subcategoria'] != "General":
                    archivo_destino = carpeta_categoria / movimiento['subcategoria'] / archivo_actual.name
                else:
                    archivo_destino = carpeta_categoria / archivo_actual.name
                
                if archivo_actual.exists():
                    if confirmar:
                        # Crear carpeta destino si no existe
                        archivo_destino.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Mover archivo
                        shutil.move(str(archivo_actual), str(archivo_destino))
                        logger.debug(f"Revertido: {archivo_actual.name} → {archivo_destino}")
                    
                    archivos_revertidos += 1
                else:
                    archivos_no_encontrados += 1
                    
            except Exception as e:
                error_msg = f"Error revirtiendo {movimiento.get('destino', 'archivo')}: {e}"
                errores.append(error_msg)
                logger.error(error_msg)
        
        if confirmar:
            # Limpiar carpetas vacías de fechas
            self._limpiar_carpetas_fechas_vacias()
            
            # Limpiar registro de movimientos revertidos
            self.registro_movimientos = [
                m for m in self.registro_movimientos 
                if not (m.get('activo_fecha', False) and 'Fechas/' in m.get('destino', ''))
            ]
            self._guardar_configuracion()
        
        resultado = {
            'exito': True,
            'archivos_revertidos': archivos_revertidos,
            'archivos_no_encontrados': archivos_no_encontrados,
            'errores': errores,
            'fue_simulacion': not confirmar
        }
        
        if confirmar:
            logger.info(f"✅ Reversión completada: {archivos_revertidos} archivos revertidos")
        else:
            logger.info(f"📋 Simulación: se revertirían {archivos_revertidos} archivos")
        
        return resultado
    
    def _limpiar_carpetas_fechas_vacias(self):
        """Limpia carpetas vacías dentro de la estructura de fechas."""
        carpeta_fechas = self.carpeta_descargas / "Fechas"
        
        if not carpeta_fechas.exists():
            return
        
        try:
            # Limpiar desde las carpetas más profundas hacia arriba
            for ruta in sorted(carpeta_fechas.rglob("*"), key=lambda p: len(p.parts), reverse=True):
                if ruta.is_dir() and not any(ruta.iterdir()):
                    ruta.rmdir()
                    logger.debug(f"Carpeta vacía eliminada: {ruta}")
            
            # Eliminar carpeta Fechas si está vacía
            if not any(carpeta_fechas.iterdir()):
                carpeta_fechas.rmdir()
                logger.info("📁 Carpeta 'Fechas' eliminada (estaba vacía)")
                
        except Exception as e:
            logger.error(f"Error limpiando carpetas de fechas: {e}")
    
    def obtener_estadisticas_fechas(self) -> Dict[str, Any]:
        """Obtiene estadísticas de organización por fechas."""
        movimientos_fecha = [
            m for m in self.registro_movimientos 
            if m.get('activo_fecha', False)
        ]
        
        if not movimientos_fecha:
            return {
                'total_archivos': 0,
                'archivos_por_mes': {},
                'patron_actual': self.patron_fechas,
                'activo': self.activo
            }
        
        # Agrupar por mes
        archivos_por_mes = defaultdict(int)
        for mov in movimientos_fecha:
            try:
                fecha = datetime.fromisoformat(mov['timestamp'])
                clave_mes = fecha.strftime('%Y-%m')
                archivos_por_mes[clave_mes] += 1
            except:
                pass
        
        return {
            'total_archivos': len(movimientos_fecha),
            'archivos_por_mes': dict(archivos_por_mes),
            'patron_actual': self.patron_fechas,
            'activo': self.activo,
            'primer_archivo': movimientos_fecha[0]['timestamp'] if movimientos_fecha else None,
            'ultimo_archivo': movimientos_fecha[-1]['timestamp'] if movimientos_fecha else None
        } 