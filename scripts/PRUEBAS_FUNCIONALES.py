#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pruebas funcionales automáticas para DescargasOrdenadas.
Ejecutar desde la raíz del proyecto: python scripts/PRUEBAS_FUNCIONALES.py
"""

import sys
import tempfile
import shutil
from pathlib import Path

# Añadir raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from organizer.file_organizer import OrganizadorArchivos
from organizer.duplicate_detector import DetectorDuplicados


def crear_escenario(base: Path):
    """Crea archivos y carpetas de prueba."""
    (base / "foto.jpg").write_text("imagen")
    (base / "doc.pdf").write_text("pdf")
    (base / "factura.xlsx").write_text("excel")
    (base / "cancion.mp3").write_text("audio")
    (base / "script.py").write_text("print('hola')")
    (base / "zip.zip").write_text("zip")
    (base / "desconocido.xyz").write_text("?")
    carpeta = base / "carpeta_suelta"
    carpeta.mkdir()
    (carpeta / "dentro.txt").write_text("hola")


def test_organizacion_basica():
    base = Path(tempfile.mkdtemp(prefix="do_test_"))
    crear_escenario(base)
    org = OrganizadorArchivos(carpeta_descargas=str(base), usar_subcarpetas=True)
    resultados, errores = org.organizar()
    assert not errores, f"Errores: {errores}"
    categorias = set(resultados.keys())
    esperadas = {"Imágenes", "PDFs", "Hojas de cálculo", "Audio", "Código Fuente", "Comprimidos", "Otros", "Carpetas"}
    faltan = esperadas - categorias
    assert not faltan, f"Faltan categorías: {faltan}"
    print("✅ Organización básica funciona")
    shutil.rmtree(base, ignore_errors=True)


def test_proteccion_carpeta_programa():
    try:
        OrganizadorArchivos(carpeta_descargas=str(project_root), usar_subcarpetas=True)
        raise AssertionError("Debería haber fallado al organizar la carpeta del programa")
    except PermissionError:
        print("✅ Protección contra autoorganización funciona")


def test_duplicados_pequeños():
    base = Path(tempfile.mkdtemp(prefix="do_dup_test_"))
    (base / "a.txt").write_text("duplicado")
    (base / "b.txt").write_text("duplicado")
    det = DetectorDuplicados(base)
    res = det.escanear_duplicados(tamaño_minimo=1)
    assert res["grupos_duplicados"] >= 1, "No detectó duplicados pequeños"
    print("✅ Detector de duplicados pequeños funciona")
    shutil.rmtree(base, ignore_errors=True)


def main():
    print("🍄 Ejecutando pruebas funcionales...")
    test_organizacion_basica()
    test_proteccion_carpeta_programa()
    test_duplicados_pequeños()
    print("\n🎉 Todas las pruebas pasaron correctamente")


if __name__ == "__main__":
    main()
