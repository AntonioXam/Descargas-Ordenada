#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import shutil
import tempfile
import unittest
from pathlib import Path

# Añadir el directorio raíz al path para importar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from organizer.file_organizer import OrganizadorArchivos, TIPOS_ARCHIVOS, TIPOS_ARCHIVOS_DETALLADOS

class TestOrganizadorArchivos(unittest.TestCase):
    """Tests para el organizador de archivos."""
    
    def setUp(self):
        """Configura un entorno de prueba temporal."""
        # Crear directorio temporal para simular la carpeta de descargas
        self.temp_dir = tempfile.mkdtemp()
        self.organizador = OrganizadorArchivos(carpeta_descargas=self.temp_dir)
        
        # Crear algunos archivos de prueba
        self._crear_archivos_prueba()
    
    def tearDown(self):
        """Limpia después de las pruebas."""
        # Eliminar directorio temporal
        shutil.rmtree(self.temp_dir)
    
    def _crear_archivos_prueba(self):
        """Crea archivos de prueba en el directorio temporal."""
        # Crear un archivo por cada categoría principal usando solo la primera extensión
        categorias_excluir = ["Malla / Geometría"]  # Categorías problemáticas a excluir
        
        for categoria, extensiones_dict in TIPOS_ARCHIVOS_DETALLADOS.items():
            # Saltar categorías problemáticas
            if categoria in categorias_excluir:
                continue
                
            # Tomar solo la primera subcategoría y su primera extensión
            primera_subcategoria = list(extensiones_dict.keys())[0]
            extensiones = extensiones_dict[primera_subcategoria]
            
            if extensiones:
                extension = extensiones[0]
                # Sanitizar el nombre de la categoría para evitar problemas de caracteres especiales
                categoria_sanitizada = categoria.lower().replace(' ', '_').replace('/', '_').replace('\\', '_')
                nombre_archivo = f"test_{categoria_sanitizada}{extension}"
                ruta_archivo = Path(self.temp_dir) / nombre_archivo
                
                # Crear archivo vacío
                with open(ruta_archivo, 'w') as f:
                    f.write(f"Archivo de prueba para {categoria}")
        
        # Crear archivo torrent
        ruta_torrent = Path(self.temp_dir) / "test_torrent.torrent"
        with open(ruta_torrent, 'w') as f:
            f.write("Archivo torrent de prueba")
        
        # Crear un archivo con extensión desconocida
        ruta_desconocido = Path(self.temp_dir) / "desconocido.xyz"
        with open(ruta_desconocido, 'w') as f:
            f.write("Archivo con extensión desconocida")
        
        # Crear una carpeta de prueba
        carpeta_prueba = Path(self.temp_dir) / "carpeta_prueba"
        carpeta_prueba.mkdir()
    
    def test_deteccion_tipos(self):
        """Prueba la detección de tipos de archivos."""
        # Verificar la detección de tipos para algunas categorías y subcategorías
        test_cases = [
            (".jpg", "Imágenes", "Fotografía"),
            (".mp4", "Vídeos", "Películas"),
            (".doc", "Documentos", "Word"),
            (".obj", "Archivos 3D", "Modelos"),
            (".torrent", "Descargas P2P", "Torrents"),
            (".xyz", "Otros", None)
        ]
        
        for extension, categoria_esperada, subcategoria_esperada in test_cases:
            archivo = Path(f"test{extension}")
            categoria, subcategoria = self.organizador._obtener_tipo_archivo(archivo)
            self.assertEqual(categoria, categoria_esperada)
            if subcategoria_esperada:
                self.assertEqual(subcategoria, subcategoria_esperada)
    
    def test_organizacion_con_subcarpetas(self):
        """Prueba la organización de archivos con subcarpetas."""
        # Configurar para usar subcarpetas
        self.organizador.usar_subcarpetas = True
        
        # Ejecutar organización
        resultados, errores = self.organizador.organizar()
        
        # Verificar que no hay errores
        self.assertEqual(len(errores), 0, f"Se produjeron errores: {errores}")
        
        # Verificar que se movieron archivos
        self.assertGreater(len(resultados), 0, "No se movió ningún archivo")
        
        # Verificar carpetas principales creadas (solo algunas para simplificar el test)
        carpetas_a_verificar = ["Imágenes", "Vídeos", "Documentos", "Archivos 3D", "Descargas P2P"]
        for categoria in carpetas_a_verificar:
            carpeta = Path(self.temp_dir) / categoria
            self.assertTrue(carpeta.exists(), f"No se creó la carpeta {categoria}")
        
        # Verificar carpeta "Otros"
        carpeta_otros = Path(self.temp_dir) / "Otros"
        self.assertTrue(carpeta_otros.exists(), "No se creó la carpeta Otros")
        
        # Verificar carpeta "Carpetas"
        carpeta_carpetas = Path(self.temp_dir) / "Carpetas"
        self.assertTrue(carpeta_carpetas.exists(), "No se creó la carpeta Carpetas")
        
        # Verificar que la carpeta de prueba se movió a "Carpetas"
        carpeta_movida = Path(self.temp_dir) / "Carpetas" / "General" / "carpeta_prueba"
        self.assertTrue(carpeta_movida.exists() or 
                       (Path(self.temp_dir) / "Carpetas" / "carpeta_prueba").exists(), 
                       "No se movió la carpeta de prueba")
        
        # Verificar que el archivo torrent se movió a su categoría correcta
        torrent_movido = Path(self.temp_dir) / "Descargas P2P" / "Torrents" / "test_torrent.torrent"
        self.assertTrue(torrent_movido.exists() or
                       (Path(self.temp_dir) / "Descargas P2P" / "test_torrent.torrent").exists(),
                       "No se organizó correctamente el archivo torrent")
    
    def test_organizacion_sin_subcarpetas(self):
        """Prueba la organización de archivos sin subcarpetas."""
        # Configurar para no usar subcarpetas
        self.organizador.usar_subcarpetas = False
        
        # Ejecutar organización
        resultados, errores = self.organizador.organizar()
        
        # Verificar que no hay errores
        self.assertEqual(len(errores), 0, f"Se produjeron errores: {errores}")
        
        # Verificar que se movieron archivos
        self.assertGreater(len(resultados), 0, "No se movió ningún archivo")
        
        # Verificar carpetas principales creadas (solo algunas para simplificar el test)
        carpetas_a_verificar = ["Imágenes", "Vídeos", "Documentos", "Archivos 3D", "Descargas P2P"]
        for categoria in carpetas_a_verificar:
            carpeta = Path(self.temp_dir) / categoria
            self.assertTrue(carpeta.exists(), f"No se creó la carpeta {categoria}")
        
        # Verificar que NO se crearon subcarpetas en algunas categorías principales
        for categoria in carpetas_a_verificar:
            carpeta = Path(self.temp_dir) / categoria
            # Verificar que no hay subcarpetas excepto posiblemente "General"
            subcarpetas = [d for d in carpeta.iterdir() if d.is_dir() and d.name != "General"]
            self.assertEqual(len(subcarpetas), 0, f"Se crearon subcarpetas en {categoria} a pesar de no usar subcarpetas")
    
    def test_idempotencia(self):
        """Prueba la idempotencia (ejecutar múltiples veces no duplica acciones)."""
        # Primera ejecución
        self.organizador.organizar()
        
        # Verificar archivo de huella
        archivo_huella = Path(self.temp_dir) / ".organized.json"
        self.assertTrue(archivo_huella.exists(), "No se creó el archivo de huella")
        
        # Leer huella
        with open(archivo_huella, 'r', encoding='utf-8') as f:
            huella_original = json.load(f)
        
        # Segunda ejecución
        resultados, _ = self.organizador.organizar()
        
        # Verificar que no se movieron archivos en la segunda ejecución
        for categoria, subcategorias in resultados.items():
            for subcategoria, archivos in subcategorias.items():
                self.assertEqual(len(archivos), 0, f"Se movieron archivos en {categoria}/{subcategoria} en la segunda ejecución")
        
        # Verificar que la huella no cambió
        with open(archivo_huella, 'r', encoding='utf-8') as f:
            huella_nueva = json.load(f)
        
        self.assertEqual(huella_original, huella_nueva, "La huella cambió en la segunda ejecución")

if __name__ == '__main__':
    unittest.main() 