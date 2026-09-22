#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pruebas funcionales automáticas para DescargasOrdenadas.
Ejecutar desde la raíz del proyecto: python scripts/PRUEBAS_FUNCIONALES.py
"""

import sys
import tempfile
import os
import subprocess
import shutil
import time
from pathlib import Path

# Añadir raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from organizer.file_organizer import OrganizadorArchivos
from organizer.duplicate_detector import DetectorDuplicados
from organizer.portable_config import ConfigPortable
from organizer.version import obtener_version
from organizer import estilos
from organizer.single_instance import InstanciaUnica, hay_instancia_activa
import organizer.autostart  # noqa: F401 - regresión: debe importar en cualquier SO


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


def test_no_toca_descargas_en_curso():
    """Los archivos a medio descargar (.part, .crdownload) no deben moverse."""
    base = Path(tempfile.mkdtemp(prefix="do_parcial_"))
    (base / "video.mp4.part").write_text("a medias")
    (base / "paquete.crdownload").write_text("a medias")
    (base / "completo.pdf").write_text("listo")
    org = OrganizadorArchivos(carpeta_descargas=str(base), usar_subcarpetas=False)
    resultados, errores = org.organizar()
    assert not errores, f"Errores: {errores}"
    assert (base / "video.mp4.part").exists(), "Se movió una descarga en curso (.part)"
    assert (base / "paquete.crdownload").exists(), "Se movió una descarga en curso (.crdownload)"
    assert (base / "PDFs" / "completo.pdf").exists(), "No se organizó el archivo completo"
    print("✅ Las descargas en curso se respetan")
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


def test_lanzadores_multiplataforma():
    """Verifica que existan lanzadores para macOS/Linux y sean ejecutables."""
    esperados = ["INICIAR.sh", "INSTALAR_DEPENDENCIAS.sh", "INICIAR.command", "INSTALAR_DEPENDENCIAS.command"]
    for nombre in esperados:
        ruta = project_root / nombre
        assert ruta.exists(), f"Falta el lanzador: {nombre}"
        assert os.access(ruta, os.X_OK), f"El lanzador {nombre} no es ejecutable"
    print("✅ Lanzadores multiplataforma presentes y ejecutables")


def test_configuracion_autoarranque():
    """Verifica que las claves base existan en la configuración por defecto."""
    config = ConfigPortable.__new__(ConfigPortable)
    valores = config._obtener_config_por_defecto()
    assert "autoarranque" in valores, "Falta la clave de autoarranque"
    assert valores["autoarranque"] is False, "El autoarranque debe estar desactivado por defecto"
    assert valores["tema"] == "auto", "El tema por defecto debe seguir al sistema"
    assert "carpeta_base" in valores, "Falta la clave de carpeta principal"
    print("✅ Configuración por defecto correcta")


def test_estilos_multiplataforma():
    """La hoja de estilo se genera en claro, oscuro y automático, sin fallar."""
    for nombre in ("claro", "oscuro", "auto"):
        hoja = estilos.hoja_estilo(nombre)
        assert "QPushButton" in hoja and "QListWidget[rol=\"lateral\"]" in hoja, f"Hoja incompleta: {nombre}"
    colores = estilos.hoja_estilo_switch("oscuro")
    assert colores["on"] and colores["off"] and colores["thumb"]
    assert estilos.familias_sistema(), "Sin familias tipográficas"
    print("✅ Sistema de estilos tipo Apple operativo")


class _ConfigAislada:
    """Sustituye temporalmente la configuración global para no tocar la real."""

    def __init__(self):
        from organizer import portable_config

        self._modulo = portable_config
        self._original = portable_config._config_global
        self.temporal = portable_config.ConfigPortable.__new__(portable_config.ConfigPortable)
        self.temporal.nombre_app = "DescargasOrdenadasPruebas"
        self.temporal._config = self.temporal._obtener_config_por_defecto()
        carpeta = Path(tempfile.mkdtemp(prefix="do_cfg_"))
        self.temporal._config_path = carpeta / "pruebas.json"
        self.temporal._config_path.write_text("{}", encoding="utf-8")

    def __enter__(self):
        self._modulo._config_global = self.temporal
        return self.temporal

    def __exit__(self, *args):
        self._modulo._config_global = self._original
        # La carpeta temporal se deja: el sistema la limpia sola y así ningún
        # guardado posterior del test falla por "no such file or directory".
        return False


def test_gui_responsive():
    """La ventana es adaptable: barra lateral + vistas con scroll."""
    try:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PySide6.QtWidgets import QApplication, QScrollArea
        from organizer.gui_avanzada import OrganizadorAvanzado
    except ImportError:
        print("⏭️  GUI no probada: PySide6 no disponible")
        return

    app = QApplication.instance() or QApplication([])
    with _ConfigAislada():
        ventana = OrganizadorAvanzado()
    ventana.resize(800, 600)

    assert ventana.minimumSize().width() <= 800, "El ancho mínimo es demasiado grande"
    assert ventana.minimumSize().height() <= 600, "El alto mínimo es demasiado grande"
    assert ventana.stack.count() == 4, "Debe haber 4 vistas (Inicio, Actividad, Ajustes, Avanzado)"
    assert ventana.lista_lateral.count() == 4, "La barra lateral debe tener 4 entradas"

    for indice in range(ventana.stack.count()):
        contenedor = ventana.stack.widget(indice)
        assert isinstance(contenedor, QScrollArea), f"La vista {indice} no tiene scroll"
        assert contenedor.widgetResizable(), f"La vista {indice} no es redimensionable"

    # Interruptores con altura correcta (no aplastados por el layout)
    assert ventana.chk_subcarpetas.sizeHint().height() >= 24

    # Cambio de tema sin excepciones
    ventana._cambiar_tema(1)
    ventana._cambiar_tema(0)

    print("✅ GUI adaptable con barra lateral y scroll")


def test_tema_segun_sistema():
    """El tema automático se resuelve siempre a claro u oscuro."""
    from organizer.gui_avanzada import OrganizadorAvanzado
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    with _ConfigAislada():
        ventana = OrganizadorAvanzado()
    ventana._tema = "auto"
    assert ventana._tema_efectivo() in ("claro", "oscuro")
    ventana._tema = "claro"
    assert ventana._tema_efectivo() == "claro"
    print("✅ Tema automático según el sistema")


def test_controles_auto_organizacion():
    """Switch, modo e intervalo deben mantenerse coherentes en todo momento.

    Cubre la regresión de los radios exclusivos: al tocar el modo o la hora
    con la auto-organización apagada, esta no debe encenderse sola, y al
    cambiar cualquiera de los dos estando encendida debe aplicarse ya.
    """
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from organizer.gui_avanzada import OrganizadorAvanzado

    app = QApplication.instance() or QApplication([])
    with _ConfigAislada():
        ventana = OrganizadorAvanzado()

    def intervalos():
        return [ventana.combo_intervalo_auto.itemData(i)
                for i in range(ventana.combo_intervalo_auto.count())]

    # --- apagada: tocar modo y hora no debe encenderla ------------------
    ventana._aplicar_auto_organizacion(False)
    ventana.chk_auto_basico.setChecked(True)
    ventana.chk_auto_detallado.setChecked(True)
    ventana.chk_auto_basico.setChecked(True)
    assert not ventana.chk_auto_principal.isChecked(), "Tocar el modo encendió la auto-organización"
    assert not ventana.timer_auto.isActive(), "El temporizador arrancó sin pedirlo"

    indice_10 = intervalos().index(600)
    ventana.combo_intervalo_auto.setCurrentIndex(indice_10)
    assert not ventana.chk_auto_principal.isChecked(), "Cambiar la hora encendió la auto-organización"
    assert ventana.config_portable.obtener("auto_intervalo") == 600

    # --- encendida: el cambio de hora se aplica al temporizador ---------
    ventana.chk_auto_principal.setChecked(True)
    assert ventana.timer_auto.isActive(), "Al encender debe arrancar el temporizador"
    assert ventana.timer_auto.interval() == 600 * 1000, "El intervalo no se aplicó al encender"
    assert "10 minutos" in ventana.lbl_estado_detalle.text(), (
        f"La tarjeta no refleja la hora: {ventana.lbl_estado_detalle.text()}"
    )

    ventana.combo_intervalo_auto.setCurrentIndex(intervalos().index(300))
    assert ventana.timer_auto.interval() == 300 * 1000, "El cambio de hora no se aplicó en caliente"

    # --- encendida: el cambio de modo se aplica -------------------------
    ventana.chk_auto_detallado.setChecked(True)
    assert ventana.config_portable.obtener("auto_modo") == "detallado"
    assert ventana._modo_seleccionado() == "detallado"
    assert "Detallado" in ventana.lbl_estado.text()
    assert not ventana.chk_auto_basico.isChecked(), "Los modos deben ser exclusivos"

    # --- apagar no debe perder el modo ni la hora elegidos --------------
    ventana.chk_auto_principal.setChecked(False)
    assert not ventana.timer_auto.isActive(), "Al apagar debe detenerse el temporizador"
    assert ventana.config_portable.obtener("auto_modo") == "detallado"
    assert ventana.config_portable.obtener("auto_intervalo") == 300
    assert ventana.config_portable.obtener("auto_organizacion") is False

    # --- volver a encender usa lo elegido ------------------------------
    ventana.chk_auto_principal.setChecked(True)
    assert ventana.timer_auto.isActive()
    assert ventana.timer_auto.interval() == 300 * 1000
    assert ventana.chk_auto_detallado.isChecked(), "Debe recordar el modo detallado"

    print("✅ Controles de auto-organización coherentes (modo, hora y switch)")


def test_instancia_unica():
    """El bloqueo impide dos copias y el canal JSON envía órdenes."""
    nombre = f"PruebaUnica{os.getpid()}"
    primera = InstanciaUnica(nombre)
    assert primera.adquirir(), "La primera instancia debe adquirir el bloqueo"
    try:
        segunda = InstanciaUnica(nombre)
        assert not segunda.adquirir(), "La segunda instancia no debe adquirir el bloqueo"
        assert hay_instancia_activa(nombre) is not None, "Debería detectar la instancia activa"
    finally:
        primera.liberar()
    assert hay_instancia_activa(nombre) is None, "Tras liberar, no debe haber instancia activa"
    print("✅ Control de instancia única funciona")


def test_menu_contextual_multiplataforma():
    """El gestor genera comandos con --organizar-carpeta en los tres sistemas."""
    from organizer.context_menu import GestorMenuContextual
    gestor = GestorMenuContextual()
    comando = gestor._comando_base()
    assert "--organizar-carpeta" in comando, f"Comando sin acción de organizar: {comando}"
    assert sys.executable in comando or "python" in comando.lower()
    # El estado de registro debe consultarse sin lanzar excepciones
    gestor.verificar_registro()
    print("✅ Menú contextual preparado para los tres sistemas")


def test_flujo_organizar_carpeta_cli():
    """La CLI organiza una carpeta concreta y avisa si no tiene permisos."""
    base = Path(tempfile.mkdtemp(prefix="do_cli_"))
    (base / "foto.png").write_text("png")
    resultado = subprocess.run(
        [sys.executable, str(project_root / "organizer" / "INICIAR.py"),
         "--organizar-carpeta", str(base), "--modo", "basico"],
        capture_output=True, text=True, timeout=90
    )
    assert (base / "Imágenes" / "foto.png").exists(), (
        f"No se organizó la carpeta por CLI:\n{resultado.stdout}\n{resultado.stderr}"
    )

    inexistente = subprocess.run(
        [sys.executable, str(project_root / "organizer" / "INICIAR.py"),
         "--organizar-carpeta", str(base / "no_existe")],
        capture_output=True, text=True, timeout=90
    )
    assert inexistente.returncode != 0, "Debe devolver error con una carpeta inexistente"
    assert "no existe" in inexistente.stdout.lower(), inexistente.stdout
    print("✅ Flujo de menú contextual por CLI funciona")
    shutil.rmtree(base, ignore_errors=True)


def test_cli_diagnostico():
    """Comprueba que la CLI muestra versión e información del sistema."""
    python = sys.executable
    version = subprocess.run(
        [python, str(project_root / "organizer" / "INICIAR.py"), "--version"],
        check=True, capture_output=True, text=True
    )
    assert obtener_version() in version.stdout.strip(), version.stdout.strip()

    info = subprocess.run(
        [python, str(project_root / "organizer" / "INICIAR.py"), "--info"],
        check=True, capture_output=True, text=True
    )
    assert "Información del sistema" in info.stdout, info.stdout
    assert "Sistema:" in info.stdout, info.stdout
    print("✅ CLI de diagnóstico funciona")


def main():
    print("🍄 Ejecutando pruebas funcionales...")
    test_organizacion_basica()
    test_no_toca_descargas_en_curso()
    test_proteccion_carpeta_programa()
    test_duplicados_pequeños()
    test_lanzadores_multiplataforma()
    test_configuracion_autoarranque()
    test_estilos_multiplataforma()
    test_gui_responsive()
    test_tema_segun_sistema()
    test_controles_auto_organizacion()
    test_instancia_unica()
    test_menu_contextual_multiplataforma()
    test_flujo_organizar_carpeta_cli()
    test_cli_diagnostico()
    print("\n🎉 Todas las pruebas pasaron correctamente")


if __name__ == "__main__":
    main()
