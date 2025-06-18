#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de estadísticas y reportes para DescargasOrdenadas
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class EstadisticasOrganizador:
    """
    Recopila y genera estadísticas sobre la organización de archivos.
    """
    
    def __init__(self, carpeta_descargas: Path):
        self.carpeta_descargas = carpeta_descargas
        self.carpeta_stats = carpeta_descargas / ".config" / "stats"
        self.carpeta_stats.mkdir(parents=True, exist_ok=True)
        self.archivo_stats = self.carpeta_stats / "statistics.json"
        self.stats = self._cargar_estadisticas()
    
    def _cargar_estadisticas(self) -> Dict[str, Any]:
        """Carga las estadísticas existentes."""
        if self.archivo_stats.exists():
            try:
                with open(self.archivo_stats, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error cargando estadísticas: {e}")
        
        return {
            'total_archivos_organizados': 0,
            'espacio_total_organizado': 0,
            'sesiones_organizacion': [],
            'categorias_populares': {},
            'archivos_por_mes': {},
            'primera_ejecucion': datetime.now().isoformat(),
            'ultima_ejecucion': None,
            'tiempo_total_organizando': 0,
            'archivos_duplicados_encontrados': 0,
            'espacio_ahorrado_duplicados': 0
        }
    
    def guardar_estadisticas(self):
        """Guarda las estadísticas en disco."""
        try:
            with open(self.archivo_stats, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error guardando estadísticas: {e}")
    
    def registrar_sesion_organizacion(self, archivos_movidos: Dict[str, Dict[str, List[str]]], 
                                    tiempo_inicio: datetime, tiempo_fin: datetime):
        """
        Registra una sesión de organización.
        
        Args:
            archivos_movidos: Diccionario con archivos organizados
            tiempo_inicio: Momento de inicio
            tiempo_fin: Momento de finalización
        """
        sesion = {
            'fecha': tiempo_inicio.isoformat(),
            'duracion_segundos': (tiempo_fin - tiempo_inicio).total_seconds(),
            'archivos_procesados': 0,
            'espacio_procesado': 0,
            'categorias': {}
        }
        
        # Contar archivos y calcular espacio
        for categoria, subcategorias in archivos_movidos.items():
            if categoria not in sesion['categorias']:
                sesion['categorias'][categoria] = 0
            
            for subcategoria, archivos in subcategorias.items():
                sesion['categorias'][categoria] += len(archivos)
                sesion['archivos_procesados'] += len(archivos)
                
                # Intentar calcular tamaño de archivos
                for archivo in archivos:
                    try:
                        ruta_archivo = self.carpeta_descargas / categoria
                        if subcategoria != "General":
                            ruta_archivo = ruta_archivo / subcategoria
                        ruta_archivo = ruta_archivo / Path(archivo).name
                        
                        if ruta_archivo.exists():
                            sesion['espacio_procesado'] += ruta_archivo.stat().st_size
                    except Exception:
                        pass
        
        # Actualizar estadísticas globales
        self.stats['total_archivos_organizados'] += sesion['archivos_procesados']
        self.stats['espacio_total_organizado'] += sesion['espacio_procesado']
        self.stats['ultima_ejecucion'] = tiempo_fin.isoformat()
        self.stats['tiempo_total_organizando'] += sesion['duracion_segundos']
        
        # Actualizar categorías populares
        for categoria, cantidad in sesion['categorias'].items():
            if categoria not in self.stats['categorias_populares']:
                self.stats['categorias_populares'][categoria] = 0
            self.stats['categorias_populares'][categoria] += cantidad
        
        # Actualizar archivos por mes
        mes_clave = tiempo_inicio.strftime('%Y-%m')
        if mes_clave not in self.stats['archivos_por_mes']:
            self.stats['archivos_por_mes'][mes_clave] = 0
        self.stats['archivos_por_mes'][mes_clave] += sesion['archivos_procesados']
        
        # Agregar sesión
        self.stats['sesiones_organizacion'].append(sesion)
        
        # Mantener solo las últimas 100 sesiones
        if len(self.stats['sesiones_organizacion']) > 100:
            self.stats['sesiones_organizacion'] = self.stats['sesiones_organizacion'][-100:]
        
        self.guardar_estadisticas()
    
    def generar_reporte_completo(self) -> str:
        """Genera un reporte completo de estadísticas."""
        reporte = []
        reporte.append("=" * 60)
        reporte.append("   REPORTE DE ESTADÍSTICAS - DESCARGASORDENADAS")
        reporte.append("=" * 60)
        reporte.append("")
        
        # Estadísticas generales
        reporte.append("📊 ESTADÍSTICAS GENERALES:")
        reporte.append(f"   📁 Total de archivos organizados: {self.stats['total_archivos_organizados']:,}")
        reporte.append(f"   💾 Espacio total organizado: {self._formatear_bytes(self.stats['espacio_total_organizado'])}")
        reporte.append(f"   ⏱️  Tiempo total organizando: {self._formatear_tiempo(self.stats['tiempo_total_organizando'])}")
        reporte.append(f"   🗓️  Primera ejecución: {self._formatear_fecha(self.stats['primera_ejecucion'])}")
        if self.stats['ultima_ejecucion']:
            reporte.append(f"   🕐 Última ejecución: {self._formatear_fecha(self.stats['ultima_ejecucion'])}")
        reporte.append("")
        
        # Categorías más populares
        if self.stats['categorias_populares']:
            reporte.append("🏆 CATEGORÍAS MÁS POPULARES:")
            categorias_ordenadas = sorted(self.stats['categorias_populares'].items(), 
                                        key=lambda x: x[1], reverse=True)
            for categoria, cantidad in categorias_ordenadas[:10]:
                porcentaje = (cantidad / self.stats['total_archivos_organizados']) * 100
                reporte.append(f"   📂 {categoria:<20} {cantidad:>6,} archivos ({porcentaje:.1f}%)")
            reporte.append("")
        
        # Actividad por mes
        if self.stats['archivos_por_mes']:
            reporte.append("📅 ACTIVIDAD POR MES (últimos 6 meses):")
            meses_ordenados = sorted(self.stats['archivos_por_mes'].items(), reverse=True)
            for mes, cantidad in meses_ordenados[:6]:
                reporte.append(f"   📆 {mes}: {cantidad:,} archivos")
            reporte.append("")
        
        # Últimas sesiones
        if self.stats['sesiones_organizacion']:
            reporte.append("🕒 ÚLTIMAS SESIONES:")
            ultimas_sesiones = self.stats['sesiones_organizacion'][-5:]
            for sesion in reversed(ultimas_sesiones):
                fecha = self._formatear_fecha(sesion['fecha'])
                duracion = self._formatear_tiempo(sesion['duracion_segundos'])
                archivos = sesion['archivos_procesados']
                espacio = self._formatear_bytes(sesion['espacio_procesado'])
                reporte.append(f"   🗓️  {fecha}: {archivos} archivos, {espacio} en {duracion}")
            reporte.append("")
        
        # Recomendaciones
        reporte.append("💡 RECOMENDACIONES:")
        if self.stats['total_archivos_organizados'] > 1000:
            reporte.append("   ✅ ¡Excelente! Has organizado más de 1,000 archivos")
        if self.stats['espacio_total_organizado'] > 1024**3:  # 1 GB
            reporte.append("   💾 Has organizado más de 1 GB de archivos")
        
        # Calcular frecuencia de uso
        if self.stats['sesiones_organizacion']:
            primera = datetime.fromisoformat(self.stats['primera_ejecucion'])
            ultima = datetime.fromisoformat(self.stats['ultima_ejecucion']) if self.stats['ultima_ejecucion'] else datetime.now()
            dias_uso = (ultima - primera).days + 1
            frecuencia = len(self.stats['sesiones_organizacion']) / dias_uso
            
            if frecuencia < 0.1:
                reporte.append("   📅 Considera usar la organización automática más frecuentemente")
            elif frecuencia > 1:
                reporte.append("   🚀 ¡Eres un usuario muy activo!")
        
        reporte.append("")
        reporte.append("=" * 60)
        
        return "\n".join(reporte)
    
    def _formatear_bytes(self, bytes_size: int) -> str:
        """Formatea bytes en formato legible."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"
    
    def _formatear_tiempo(self, segundos: float) -> str:
        """Formatea segundos en formato legible."""
        if segundos < 60:
            return f"{segundos:.1f}s"
        elif segundos < 3600:
            return f"{segundos/60:.1f}m"
        else:
            return f"{segundos/3600:.1f}h"
    
    def _formatear_fecha(self, fecha_iso: str) -> str:
        """Formatea fecha ISO en formato legible."""
        try:
            fecha = datetime.fromisoformat(fecha_iso)
            return fecha.strftime("%d/%m/%Y %H:%M")
        except:
            return fecha_iso
    
    def obtener_resumen_rapido(self) -> Dict[str, Any]:
        """Obtiene un resumen rápido para mostrar en la GUI."""
        return {
            'total_archivos': self.stats['total_archivos_organizados'],
            'espacio_total': self._formatear_bytes(self.stats['espacio_total_organizado']),
            'categoria_favorita': max(self.stats['categorias_populares'].items(), 
                                    key=lambda x: x[1])[0] if self.stats['categorias_populares'] else 'N/A',
            'ultima_sesion': self._formatear_fecha(self.stats['ultima_ejecucion']) if self.stats['ultima_ejecucion'] else 'Nunca'
        } 