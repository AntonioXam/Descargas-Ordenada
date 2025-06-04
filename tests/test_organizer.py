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

from organizer.file_organizer import OrganizadorArchivos, TIPOS_ARCHIVOS

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
        # Crear un archivo por cada categoría
        for categoria, extensiones in TIPOS_ARCHIVOS.items():
            # Tomar la primera extensión de cada categoría
            if extensiones:
                extension = extensiones[0]
                nombre_archivo = f"test_{categoria.lower()}{extension}"
                ruta_archivo = Path(self.temp_dir) / nombre_archivo
                
                # Crear archivo vacío
                with open(ruta_archivo, 'w') as f:
                    f.write(f"Archivo de prueba para {categoria}")
        
        # Crear un archivo con extensión desconocida
        ruta_desconocido = Path(self.temp_dir) / "desconocido.xyz"
        with open(ruta_desconocido, 'w') as f:
            f.write("Archivo con extensión desconocida")
        
        # Crear una carpeta de prueba
        carpeta_prueba = Path(self.temp_dir) / "carpeta_prueba"
        carpeta_prueba.mkdir()
    
    def test_deteccion_tipos(self):
        """Prueba la detección de tipos de archivos."""
        # Verificar la detección de tipos para cada categoría
        for categoria, extensiones in TIPOS_ARCHIVOS.items():
            if extensiones:
                extension = extensiones[0]
                archivo = Path(f"test{extension}")
                tipo_detectado = self.organizador._obtener_tipo_archivo(archivo)
                self.assertEqual(tipo_detectado, categoria)
        
        # Verificar tipo desconocido
        archivo_desconocido = Path("test.xyz")
        tipo_desconocido = self.organizador._obtener_tipo_archivo(archivo_desconocido)
        self.assertEqual(tipo_desconocido, "Otros")
    
    def test_organizacion(self):
        """Prueba la organización de archivos."""
        # Ejecutar organización
        resultados, errores = self.organizador.organizar()
        
        # Verificar que no hay errores
        self.assertEqual(len(errores), 0, f"Se produjeron errores: {errores}")
        
        # Verificar que se movieron archivos
        self.assertGreater(len(resultados), 0, "No se movió ningún archivo")
        
        # Verificar carpetas creadas
        for categoria in TIPOS_ARCHIVOS.keys():
            carpeta = Path(self.temp_dir) / categoria
            self.assertTrue(carpeta.exists(), f"No se creó la carpeta {categoria}")
        
        # Verificar carpeta "Otros"
        carpeta_otros = Path(self.temp_dir) / "Otros"
        self.assertTrue(carpeta_otros.exists(), "No se creó la carpeta Otros")
        
        # Verificar carpeta "Carpetas"
        carpeta_carpetas = Path(self.temp_dir) / "Carpetas"
        self.assertTrue(carpeta_carpetas.exists(), "No se creó la carpeta Carpetas")
        
        # Verificar que la carpeta de prueba se movió a "Carpetas"
        carpeta_movida = carpeta_carpetas / "carpeta_prueba"
        self.assertTrue(carpeta_movida.exists(), "No se movió la carpeta de prueba")
    
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
        for categoria, archivos in resultados.items():
            self.assertEqual(len(archivos), 0, f"Se movieron archivos en {categoria} en la segunda ejecución")
        
        # Verificar que la huella no cambió
        with open(archivo_huella, 'r', encoding='utf-8') as f:
            huella_nueva = json.load(f)
        
        self.assertEqual(huella_original, huella_nueva, "La huella cambió en la segunda ejecución")

if __name__ == '__main__':
    unittest.main() 