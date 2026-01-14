#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de categorización con IA básica usando análisis de texto y patrones
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
import logging
from datetime import datetime
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class CategorizadorIA:
    """
    Categorizador que usa técnicas básicas de IA/ML para mejorar la clasificación.
    """
    
    def __init__(self, carpeta_descargas: Path):
        self.carpeta_descargas = carpeta_descargas
        self.carpeta_config = carpeta_descargas / ".config"
        self.carpeta_config.mkdir(exist_ok=True)
        self.archivo_modelo = self.carpeta_config / "modelo_ia.json"
        self.archivo_patrones = self.carpeta_config / "patrones_aprendidos.json"
        
        # Datos del modelo
        self.patrones_nombre: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.palabras_clave: Dict[str, Set[str]] = defaultdict(set)
        self.confianza_minima = 0.6
        self.historial_decisiones: List[Dict[str, Any]] = []
        
        # Cargar modelo existente
        self._cargar_modelo()
        self._inicializar_patrones_base()
    
    def _cargar_modelo(self):
        """Carga el modelo de IA desde disco."""
        if not self.archivo_modelo.exists():
            return
        
        try:
            with open(self.archivo_modelo, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convertir patrones cargados
            for categoria, palabras in data.get('patrones_nombre', {}).items():
                for palabra, peso in palabras.items():
                    self.patrones_nombre[categoria][palabra] = peso
            
            # Cargar palabras clave
            for categoria, palabras in data.get('palabras_clave', {}).items():
                self.palabras_clave[categoria] = set(palabras)
            
            self.confianza_minima = data.get('confianza_minima', 0.6)
            self.historial_decisiones = data.get('historial_decisiones', [])
            
            logger.info(f"🤖 Modelo de IA cargado: {len(self.patrones_nombre)} categorías")
            
        except Exception as e:
            logger.error(f"Error cargando modelo de IA: {e}")
    
    def _guardar_modelo(self):
        """Guarda el modelo de IA en disco."""
        try:
            # Convertir defaultdict a dict normal para JSON
            patrones_dict = {}
            for categoria, palabras in self.patrones_nombre.items():
                patrones_dict[categoria] = dict(palabras)
            
            palabras_clave_dict = {}
            for categoria, palabras in self.palabras_clave.items():
                palabras_clave_dict[categoria] = list(palabras)
            
            data = {
                'version': '1.0',
                'ultima_actualizacion': datetime.now().isoformat(),
                'patrones_nombre': patrones_dict,
                'palabras_clave': palabras_clave_dict,
                'confianza_minima': self.confianza_minima,
                'historial_decisiones': self.historial_decisiones[-500:]  # Últimas 500
            }
            
            with open(self.archivo_modelo, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Error guardando modelo de IA: {e}")
    
    def _inicializar_patrones_base(self):
        """Inicializa patrones base si no existen."""
        if self.patrones_nombre:
            return  # Ya hay patrones cargados
        
        # Patrones semilla para entrenar el modelo
        patrones_semilla = {
            'Imágenes': {
                'foto': 0.8, 'image': 0.7, 'picture': 0.7, 'screenshot': 0.9,
                'captura': 0.9, 'wallpaper': 0.8, 'background': 0.6, 'avatar': 0.7
            },
            'Vídeos': {
                'video': 0.9, 'movie': 0.8, 'film': 0.8, 'clip': 0.7,
                'trailer': 0.8, 'episodio': 0.8, 'serie': 0.7, 'season': 0.7
            },
            'Audio': {
                'music': 0.8, 'song': 0.8, 'audio': 0.7, 'sound': 0.6,
                'musica': 0.8, 'cancion': 0.8, 'track': 0.7, 'album': 0.8
            },
            'Documentos': {
                'document': 0.7, 'doc': 0.6, 'manual': 0.8, 'guide': 0.7,
                'instruction': 0.8, 'tutorial': 0.7, 'readme': 0.8, 'info': 0.6
            },
            'Trabajo': {
                'work': 0.7, 'project': 0.8, 'report': 0.8, 'presentation': 0.8,
                'proyecto': 0.8, 'informe': 0.8, 'presentacion': 0.8, 'meeting': 0.7
            },
            'Educación': {
                'course': 0.8, 'lesson': 0.8, 'study': 0.7, 'homework': 0.8,
                'curso': 0.8, 'leccion': 0.8, 'estudio': 0.7, 'tarea': 0.8
            },
            'Juegos': {
                'game': 0.8, 'gaming': 0.7, 'juego': 0.8, 'mod': 0.7,
                'save': 0.6, 'cheat': 0.7, 'trainer': 0.7, 'crack': 0.8
            }
        }
        
        for categoria, palabras in patrones_semilla.items():
            for palabra, peso in palabras.items():
                self.patrones_nombre[categoria][palabra] = peso
                self.palabras_clave[categoria].add(palabra)
        
        self._guardar_modelo()
        logger.info("🌱 Patrones base de IA inicializados")
    
    def analizar_nombre_archivo(self, archivo: Path) -> Optional[Tuple[str, float]]:
        """
        Analiza el nombre de archivo usando IA para determinar categoría.
        
        Args:
            archivo: Archivo a analizar
            
        Returns:
            Tupla con (categoría, confianza) o None si no hay coincidencia
        """
        nombre_completo = archivo.name.lower()
        nombre_sin_ext = archivo.stem.lower()
        
        # Preprocesar nombre - limpiar y dividir en palabras
        texto_limpio = self._limpiar_texto(nombre_completo)
        palabras = self._extraer_palabras(texto_limpio)
        
        # Calcular puntuación para cada categoría
        puntuaciones = {}
        
        for categoria in self.patrones_nombre.keys():
            puntuacion = self._calcular_puntuacion_categoria(palabras, categoria)
            if puntuacion > 0:
                puntuaciones[categoria] = puntuacion
        
        if not puntuaciones:
            return None
        
        # Obtener categoría con mayor puntuación
        mejor_categoria = max(puntuaciones, key=puntuaciones.get)
        confianza = puntuaciones[mejor_categoria]
        
        # Solo retornar si supera el umbral de confianza
        if confianza >= self.confianza_minima:
            logger.debug(f"IA categoriza '{archivo.name}' como '{mejor_categoria}' (confianza: {confianza:.2f})")
            return (mejor_categoria, confianza)
        
        return None
    
    def _limpiar_texto(self, texto: str) -> str:
        """Limpia el texto para análisis."""
        # Remover caracteres especiales y números
        texto = re.sub(r'[^\w\s-]', ' ', texto)
        # Remover números de versión, fechas, etc.
        texto = re.sub(r'\b\d+[\d\.-]*\b', ' ', texto)
        # Remover palabras muy cortas
        palabras = [p for p in texto.split() if len(p) > 2]
        return ' '.join(palabras)
    
    def _extraer_palabras(self, texto: str) -> List[str]:
        """Extrae palabras significativas del texto."""
        # Dividir por espacios, guiones, underscores
        palabras = re.split(r'[\s_-]+', texto.lower())
        
        # Filtrar palabras muy cortas o comunes
        palabras_filtradas = []
        palabras_comunes = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'man', 'oil', 'sit', 'usa', 'car', 'few', 'lot', 'run', 'sea', 'set', 'too', 'big', 'end', 'far', 'off', 'own', 'say', 'she', 'try', 'use'}
        
        for palabra in palabras:
            if len(palabra) > 2 and palabra not in palabras_comunes:
                palabras_filtradas.append(palabra)
        
        return palabras_filtradas
    
    def _calcular_puntuacion_categoria(self, palabras: List[str], categoria: str) -> float:
        """Calcula la puntuación de una categoría para las palabras dadas."""
        if categoria not in self.patrones_nombre:
            return 0.0
        
        puntuacion_total = 0.0
        palabras_encontradas = 0
        
        patrones_categoria = self.patrones_nombre[categoria]
        
        for palabra in palabras:
            # Coincidencia exacta
            if palabra in patrones_categoria:
                puntuacion_total += patrones_categoria[palabra]
                palabras_encontradas += 1
            else:
                # Coincidencia parcial (substring)
                for patron, peso in patrones_categoria.items():
                    if patron in palabra or palabra in patron:
                        puntuacion_total += peso * 0.5  # Peso reducido para coincidencias parciales
                        palabras_encontradas += 0.5
                        break
        
        # Normalizar por número de palabras
        if palabras_encontradas > 0:
            puntuacion_normalizada = puntuacion_total / max(len(palabras), 1)
            return min(puntuacion_normalizada, 1.0)  # Máximo 1.0
        
        return 0.0
    
    def entrenar_con_decision(self, archivo: Path, categoria_asignada: str, 
                            subcategoria: Optional[str] = None, fue_correcta: bool = True):
        """
        Entrena el modelo con una decisión de categorización.
        
        Args:
            archivo: Archivo que fue categorizado
            categoria_asignada: Categoría que se le asignó
            subcategoria: Subcategoría asignada
            fue_correcta: Si la decisión fue correcta (feedback del usuario)
        """
        nombre_limpio = self._limpiar_texto(archivo.name.lower())
        palabras = self._extraer_palabras(nombre_limpio)
        
        # Factor de aprendizaje
        factor = 0.1 if fue_correcta else -0.05
        
        # Actualizar pesos
        for palabra in palabras:
            if fue_correcta:
                # Reforzar asociación con categoría correcta
                self.patrones_nombre[categoria_asignada][palabra] += factor
                self.palabras_clave[categoria_asignada].add(palabra)
                
                # Limitar peso máximo
                if self.patrones_nombre[categoria_asignada][palabra] > 1.0:
                    self.patrones_nombre[categoria_asignada][palabra] = 1.0
            else:
                # Debilitar asociación incorrecta
                if palabra in self.patrones_nombre[categoria_asignada]:
                    self.patrones_nombre[categoria_asignada][palabra] += factor
                    
                    # Eliminar si el peso es muy bajo
                    if self.patrones_nombre[categoria_asignada][palabra] < 0.1:
                        del self.patrones_nombre[categoria_asignada][palabra]
                        self.palabras_clave[categoria_asignada].discard(palabra)
        
        # Registrar decisión para análisis
        decision = {
            'timestamp': datetime.now().isoformat(),
            'archivo': archivo.name,
            'categoria': categoria_asignada,
            'subcategoria': subcategoria,
            'fue_correcta': fue_correcta,
            'palabras_analizadas': palabras
        }
        
        self.historial_decisiones.append(decision)
        self._guardar_modelo()
        
        logger.debug(f"IA entrenada: {archivo.name} → {categoria_asignada} ({'✓' if fue_correcta else '✗'})")
    
    def analizar_patrones_usuario(self) -> Dict[str, Any]:
        """
        Analiza los patrones de uso del usuario para mejorar el modelo.
        
        Returns:
            Diccionario con análisis de patrones
        """
        if not self.historial_decisiones:
            return {'mensaje': 'No hay suficiente historial para análisis'}
        
        # Análisis de categorías más usadas
        categorias_counter = Counter()
        decisiones_correctas = 0
        
        for decision in self.historial_decisiones:
            categorias_counter[decision['categoria']] += 1
            if decision['fue_correcta']:
                decisiones_correctas += 1
        
        total_decisiones = len(self.historial_decisiones)
        precision_ia = (decisiones_correctas / total_decisiones) * 100 if total_decisiones > 0 else 0
        
        # Palabras más influyentes por categoría
        palabras_influyentes = {}
        for categoria, patrones in self.patrones_nombre.items():
            if patrones:
                palabras_top = sorted(patrones.items(), key=lambda x: x[1], reverse=True)[:5]
                palabras_influyentes[categoria] = palabras_top
        
        analisis = {
            'total_decisiones': total_decisiones,
            'precision_ia': round(precision_ia, 1),
            'categorias_mas_usadas': categorias_counter.most_common(5),
            'palabras_influyentes': palabras_influyentes,
            'confianza_actual': self.confianza_minima,
            'categorias_aprendidas': len(self.patrones_nombre)
        }
        
        return analisis
    
    def ajustar_confianza(self, nueva_confianza: float):
        """
        Ajusta el umbral de confianza mínima.
        
        Args:
            nueva_confianza: Nuevo umbral entre 0.0 y 1.0
        """
        if 0.0 <= nueva_confianza <= 1.0:
            self.confianza_minima = nueva_confianza
            self._guardar_modelo()
            logger.info(f"🎯 Confianza de IA ajustada a: {nueva_confianza}")
        else:
            logger.error("Confianza debe estar entre 0.0 y 1.0")
    
    def limpiar_modelo(self):
        """Limpia el modelo de IA y reinicia el aprendizaje."""
        self.patrones_nombre.clear()
        self.palabras_clave.clear()
        self.historial_decisiones.clear()
        
        # Reinicializar patrones base
        self._inicializar_patrones_base()
        
        logger.info("🧹 Modelo de IA reiniciado")
    
    def exportar_modelo(self, archivo_destino: Path) -> bool:
        """
        Exporta el modelo entrenado para compartir o respaldo.
        
        Args:
            archivo_destino: Ruta donde guardar el modelo
            
        Returns:
            True si se exportó correctamente
        """
        try:
            import shutil
            shutil.copy2(self.archivo_modelo, archivo_destino)
            logger.info(f"📤 Modelo exportado a: {archivo_destino}")
            return True
        except Exception as e:
            logger.error(f"Error exportando modelo: {e}")
            return False
    
    def importar_modelo(self, archivo_origen: Path) -> bool:
        """
        Importa un modelo entrenado.
        
        Args:
            archivo_origen: Ruta del modelo a importar
            
        Returns:
            True si se importó correctamente
        """
        try:
            import shutil
            shutil.copy2(archivo_origen, self.archivo_modelo)
            self._cargar_modelo()
            logger.info(f"📥 Modelo importado desde: {archivo_origen}")
            return True
        except Exception as e:
            logger.error(f"Error importando modelo: {e}")
            return False 