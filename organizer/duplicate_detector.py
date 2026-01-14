#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Detector de archivos duplicados basado en hash y tamaño
"""

import hashlib
import os
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
import logging
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

class DetectorDuplicados:
    """
    Detecta archivos duplicados usando hash MD5/SHA256 y tamaño.
    """
    
    def __init__(self, carpeta_descargas: Path):
        self.carpeta_descargas = carpeta_descargas
        self.carpeta_config = carpeta_descargas / ".config"
        self.carpeta_config.mkdir(exist_ok=True)
        self.archivo_cache = self.carpeta_config / "cache_duplicados.json"
        self.archivo_duplicados = self.carpeta_config / "duplicados_encontrados.json"
        self.cache_hashes: Dict[str, Dict[str, Any]] = {}
        self.duplicados_encontrados: List[Dict[str, Any]] = []
        self.algoritmo_hash = 'md5'  # 'md5' o 'sha256'
        self.usar_cache = True
        self._cargar_cache()
    
    def calcular_hash_archivo(self, archivo: Path) -> Optional[str]:
        """
        Calcula el hash de un archivo.
        
        Args:
            archivo: Ruta al archivo
            
        Returns:
            Hash del archivo o None si hay error
        """
        # Verificar cache primero
        ruta_str = str(archivo)
        if self.usar_cache and ruta_str in self.cache_hashes:
            info_cache = self.cache_hashes[ruta_str]
            try:
                # Verificar si el archivo ha cambiado
                stat = archivo.stat()
                if (info_cache['tamaño'] == stat.st_size and 
                    info_cache['modificado'] == stat.st_mtime):
                    return info_cache['hash']
            except:
                pass
        
        try:
            # Calcular hash
            if self.algoritmo_hash == 'md5':
                hasher = hashlib.md5()
            else:
                hasher = hashlib.sha256()
            
            with open(archivo, 'rb') as f:
                # Leer en chunks para archivos grandes
                while chunk := f.read(8192):
                    hasher.update(chunk)
            
            hash_resultado = hasher.hexdigest()
            
            # Guardar en cache
            if self.usar_cache:
                stat = archivo.stat()
                self.cache_hashes[ruta_str] = {
                    'hash': hash_resultado,
                    'tamaño': stat.st_size,
                    'modificado': stat.st_mtime,
                    'calculado': datetime.now().isoformat()
                }
            
            return hash_resultado
            
        except (IOError, PermissionError) as e:
            logger.warning(f"No se pudo calcular hash de {archivo}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error calculando hash de {archivo}: {e}")
            return None
    
    def _cargar_cache(self):
        """Carga el cache de hashes calculados anteriormente."""
        if not self.archivo_cache.exists():
            return
        
        try:
            with open(self.archivo_cache, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.cache_hashes = data.get('hashes', {})
            self.algoritmo_hash = data.get('algoritmo', 'md5')
            
            logger.info(f"📦 Cache cargado: {len(self.cache_hashes)} hashes")
            
        except Exception as e:
            logger.error(f"Error cargando cache de duplicados: {e}")
    
    def _guardar_cache(self):
        """Guarda el cache de hashes."""
        try:
            # Limpiar entradas obsoletas (archivos que ya no existen)
            cache_limpio = {}
            for ruta, info in self.cache_hashes.items():
                if Path(ruta).exists():
                    cache_limpio[ruta] = info
            
            data = {
                'algoritmo': self.algoritmo_hash,
                'ultima_actualizacion': datetime.now().isoformat(),
                'hashes': cache_limpio
            }
            
            with open(self.archivo_cache, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.cache_hashes = cache_limpio
            
        except Exception as e:
            logger.error(f"Error guardando cache de duplicados: {e}")
    
    def _guardar_duplicados(self):
        """Guarda la lista de duplicados encontrados."""
        try:
            data = {
                'fecha_escaneo': datetime.now().isoformat(),
                'algoritmo_usado': self.algoritmo_hash,
                'total_grupos': len(self.duplicados_encontrados),
                'duplicados': self.duplicados_encontrados
            }
            
            with open(self.archivo_duplicados, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Error guardando duplicados: {e}")
    
    def escanear_duplicados(self, incluir_subcarpetas: bool = True, 
                          tamaño_minimo: int = 1024) -> Dict[str, Any]:
        """
        Escanea la carpeta en busca de archivos duplicados.
        
        Args:
            incluir_subcarpetas: Si incluir subcarpetas en el escaneo
            tamaño_minimo: Tamaño mínimo en bytes para considerar archivo
            
        Returns:
            Diccionario con resultados del escaneo
        """
        logger.info("🔍 Iniciando escaneo de duplicados...")
        
        # Mapas para agrupar archivos
        archivos_por_tamaño: Dict[int, List[Path]] = defaultdict(list)
        archivos_por_hash: Dict[str, List[Path]] = defaultdict(list)
        
        # Contador de progreso
        archivos_escaneados = 0
        archivos_procesados = 0
        
        # Primera pasada: agrupar por tamaño
        patron = "**/*" if incluir_subcarpetas else "*"
        for archivo in self.carpeta_descargas.glob(patron):
            if not archivo.is_file():
                continue
            
            archivos_escaneados += 1
            
            try:
                tamaño = archivo.stat().st_size
                if tamaño >= tamaño_minimo:
                    archivos_por_tamaño[tamaño].append(archivo)
            except (OSError, IOError):
                continue
        
        logger.info(f"📊 Primera pasada: {archivos_escaneados} archivos encontrados")
        
        # Segunda pasada: calcular hashes solo para archivos con mismo tamaño
        grupos_duplicados = []
        
        for tamaño, archivos in archivos_por_tamaño.items():
            if len(archivos) < 2:
                continue  # Solo un archivo de este tamaño
            
            logger.info(f"🔍 Calculando hashes para {len(archivos)} archivos de {self._formatear_bytes(tamaño)}")
            
            # Calcular hashes para archivos con el mismo tamaño
            for archivo in archivos:
                hash_archivo = self.calcular_hash_archivo(archivo)
                if hash_archivo:
                    archivos_por_hash[hash_archivo].append(archivo)
                    archivos_procesados += 1
        
        # Identificar grupos de duplicados
        for hash_valor, archivos in archivos_por_hash.items():
            if len(archivos) > 1:
                # Encontramos duplicados
                grupo = {
                    'hash': hash_valor,
                    'tamaño': archivos[0].stat().st_size,
                    'cantidad': len(archivos),
                    'archivos': []
                }
                
                for archivo in archivos:
                    try:
                        stat = archivo.stat()
                        info_archivo = {
                            'ruta': str(archivo),
                            'nombre': archivo.name,
                            'tamaño': stat.st_size,
                            'modificado': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'carpeta': str(archivo.parent)
                        }
                        grupo['archivos'].append(info_archivo)
                    except:
                        continue
                
                if len(grupo['archivos']) > 1:
                    grupos_duplicados.append(grupo)
        
        # Ordenar por tamaño (duplicados más grandes primero)
        grupos_duplicados.sort(key=lambda g: g['tamaño'], reverse=True)
        
        self.duplicados_encontrados = grupos_duplicados
        self._guardar_duplicados()
        self._guardar_cache()
        
        # Calcular estadísticas
        total_duplicados = sum(g['cantidad'] - 1 for g in grupos_duplicados)  # -1 porque uno no es duplicado
        espacio_desperdiciado = sum(g['tamaño'] * (g['cantidad'] - 1) for g in grupos_duplicados)
        
        resultado = {
            'archivos_escaneados': archivos_escaneados,
            'archivos_procesados': archivos_procesados,
            'grupos_duplicados': len(grupos_duplicados),
            'total_duplicados': total_duplicados,
            'espacio_desperdiciado': espacio_desperdiciado,
            'espacio_desperdiciado_legible': self._formatear_bytes(espacio_desperdiciado),
            'duplicados': grupos_duplicados
        }
        
        logger.info(f"✅ Escaneo completado: {len(grupos_duplicados)} grupos, {total_duplicados} duplicados")
        logger.info(f"💾 Espacio desperdiciado: {self._formatear_bytes(espacio_desperdiciado)}")
        
        return resultado
    
    def eliminar_duplicados(self, estrategia: str = 'mas_nuevo', 
                          confirmar: bool = False) -> Dict[str, Any]:
        """
        Elimina archivos duplicados según una estrategia.
        
        Args:
            estrategia: 'mas_nuevo', 'mas_viejo', 'carpeta_principal', 'manual'
            confirmar: Si True, ejecuta la eliminación. Si False, solo simula.
            
        Returns:
            Diccionario con resultados de la eliminación
        """
        if not self.duplicados_encontrados:
            return {
                'exito': False,
                'mensaje': 'No hay duplicados para eliminar. Ejecuta escaneo primero.',
                'archivos_eliminados': 0
            }
        
        archivos_a_eliminar = []
        archivos_a_conservar = []
        
        for grupo in self.duplicados_encontrados:
            archivos = grupo['archivos']
            if len(archivos) < 2:
                continue
            
            # Seleccionar archivo a conservar según estrategia
            if estrategia == 'mas_nuevo':
                conservar = max(archivos, key=lambda a: a['modificado'])
            elif estrategia == 'mas_viejo':
                conservar = min(archivos, key=lambda a: a['modificado'])
            elif estrategia == 'carpeta_principal':
                # Conservar el que esté en la carpeta más cercana a la raíz
                conservar = min(archivos, key=lambda a: len(Path(a['ruta']).parts))
            else:
                # Estrategia manual - conservar el primero por defecto
                conservar = archivos[0]
            
            archivos_a_conservar.append(conservar)
            
            # Marcar el resto para eliminar
            for archivo in archivos:
                if archivo != conservar:
                    archivos_a_eliminar.append(archivo)
        
        # Ejecutar eliminación si se confirma
        eliminados = 0
        errores = []
        espacio_liberado = 0
        
        if confirmar:
            for archivo_info in archivos_a_eliminar:
                try:
                    archivo = Path(archivo_info['ruta'])
                    if archivo.exists():
                        espacio_liberado += archivo.stat().st_size
                        archivo.unlink()
                        eliminados += 1
                        logger.debug(f"Eliminado duplicado: {archivo}")
                except Exception as e:
                    error_msg = f"Error eliminando {archivo_info['nombre']}: {e}"
                    errores.append(error_msg)
                    logger.error(error_msg)
        
        resultado = {
            'exito': True,
            'estrategia_usada': estrategia,
            'archivos_analizados': len(archivos_a_eliminar) + len(archivos_a_conservar),
            'archivos_eliminados': eliminados if confirmar else len(archivos_a_eliminar),
            'archivos_conservados': len(archivos_a_conservar),
            'espacio_liberado': espacio_liberado if confirmar else sum(a['tamaño'] for a in archivos_a_eliminar),
            'espacio_liberado_legible': self._formatear_bytes(espacio_liberado if confirmar else sum(a['tamaño'] for a in archivos_a_eliminar)),
            'errores': errores,
            'fue_simulacion': not confirmar
        }
        
        if confirmar:
            logger.info(f"✅ Eliminación completada: {eliminados} archivos, {self._formatear_bytes(espacio_liberado)} liberados")
            # Limpiar lista de duplicados encontrados
            self.duplicados_encontrados = []
            self._guardar_duplicados()
        else:
            logger.info(f"📋 Simulación: se eliminarían {len(archivos_a_eliminar)} archivos")
        
        return resultado
    
    def obtener_duplicados_manual(self) -> List[Dict[str, Any]]:
        """
        Retorna la lista de duplicados para selección manual.
        
        Returns:
            Lista de grupos de duplicados para interfaz manual
        """
        return self.duplicados_encontrados
    
    def eliminar_archivo_especifico(self, ruta_archivo: str) -> bool:
        """
        Elimina un archivo específico de duplicados.
        
        Args:
            ruta_archivo: Ruta del archivo a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            archivo = Path(ruta_archivo)
            if archivo.exists():
                archivo.unlink()
                logger.info(f"🗑️ Archivo eliminado manualmente: {archivo.name}")
                return True
            else:
                logger.warning(f"Archivo no encontrado: {ruta_archivo}")
                return False
        except Exception as e:
            logger.error(f"Error eliminando archivo {ruta_archivo}: {e}")
            return False
    
    def _formatear_bytes(self, bytes_size: int) -> str:
        """Formatea bytes en formato legible."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"
    
    def limpiar_cache(self):
        """Limpia el cache de hashes."""
        self.cache_hashes = {}
        if self.archivo_cache.exists():
            self.archivo_cache.unlink()
        logger.info("🧹 Cache de duplicados limpiado")
    
    def configurar_algoritmo(self, algoritmo: str) -> bool:
        """
        Configura el algoritmo de hash a usar.
        
        Args:
            algoritmo: 'md5' o 'sha256'
            
        Returns:
            True si se configuró correctamente
        """
        if algoritmo not in ['md5', 'sha256']:
            logger.error(f"Algoritmo inválido: {algoritmo}. Válidos: md5, sha256")
            return False
        
        if algoritmo != self.algoritmo_hash:
            self.algoritmo_hash = algoritmo
            # Limpiar cache si cambió el algoritmo
            self.limpiar_cache()
            logger.info(f"🔧 Algoritmo de hash cambiado a: {algoritmo}")
        
        return True 