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
    assert ventana.stack.count() == 5, "Debe haber 5 vistas (Inicio, Historial, Actividad, Ajustes, Avanzado)"
    assert ventana.lista_lateral.count() == 5, "La barra lateral debe tener 5 entradas"

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


def test_actualizaciones_sin_api():
    """La comprobación debe funcionar aunque la API de GitHub esté limitada.

    Regresión: antes, un 403 de límite de peticiones se interpretaba como «ya
    tienes la última versión» y además bloqueaba el reintento durante 24 h.
    """
    try:
        import requests
        from unittest.mock import MagicMock, patch
        from organizer.actualizaciones_mejorado import GestorActualizacionesMejorado
    except ImportError:
        print("⏭️  Actualizaciones no probadas: dependencias ausentes")
        return

    get_real = requests.get

    def get_con_api_bloqueada(url, *args, **kwargs):
        if "api.github.com" in url:
            respuesta = MagicMock()
            respuesta.status_code = 403
            respuesta.text = '{"message":"API rate limit exceeded"}'
            respuesta.raise_for_status.side_effect = requests.exceptions.HTTPError("403")
            return respuesta
        return get_real(url, *args, **kwargs)

    gestor = GestorActualizacionesMejorado()
    gestor.VERSION_ACTUAL = "0.0.1"  # muy antigua: siempre hay algo más nuevo
    gestor.ultima_verificacion = None
    gestor._ultima_comprobacion_fallida = False

    with patch("organizer.actualizaciones_mejorado.requests.get",
               side_effect=get_con_api_bloqueada):
        hay, info = gestor.verificar_actualizaciones(forzar=True)

    assert hay and info, "No detectó la actualización con la API limitada"
    assert info.get("version"), "La actualización detectada no trae versión"
    assert not gestor.comprobacion_fallida(), (
        "Si se detectó la versión, la comprobación no debe marcarse como fallida"
    )

    # Sin red: debe indicar que no se pudo comprobar (no decir «estás al día»)
    def sin_red(*args, **kwargs):
        raise requests.exceptions.ConnectionError("sin internet")

    gestor2 = GestorActualizacionesMejorado()
    gestor2.VERSION_ACTUAL = "0.0.1"
    gestor2.ultima_verificacion = None
    gestor2._ultima_comprobacion_fallida = False
    with patch("organizer.actualizaciones_mejorado.requests.get", side_effect=sin_red):
        hay2, _ = gestor2.verificar_actualizaciones(forzar=True)
    assert not hay2, "Sin red no debe afirmar que hay actualización"
    assert gestor2.comprobacion_fallida(), (
        "Sin red debe marcarse como comprobación fallida, no como 'al día'"
    )

    # Migración del archivo antiguo: no debe bloquear el reintento
    import json
    import tempfile
    ruta = Path(tempfile.mkdtemp(prefix="do_act_")) / "actualizaciones.json"
    ruta.write_text(json.dumps({
        "ultima_verificacion": "2026-09-22T18:13:58.587543",
        "nueva_version": None,
        "version_actual": "5.0.0",
    }), encoding="utf-8")
    gestor3 = GestorActualizacionesMejorado()
    gestor3.config_path = ruta
    gestor3.ultima_verificacion = None
    gestor3._cargar_config()
    assert gestor3.ultima_verificacion is None, (
        "El formato antiguo debe permitir reintentar la comprobación"
    )

    print("✅ Actualizaciones robustas ante límites de GitHub y sin red")


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


def test_workflow_macos_valido():
    """La Acción rápida de Finder debe usar el formato que Automator acepta.

    Regresión: el flujo generado antes no incluía los metadatos de la acción
    (ActionBundlePath, BundleIdentifier, Class Name, UUID) y Automator fallaba
    con «la acción no se ha cargado»; además inputMethod debía ser 1 para que
    las carpetas llegasen al script.
    """
    if sys.platform != "darwin":
        print("⏭️  Workflow de macOS omitido: no estamos en macOS")
        return

    import plistlib

    from organizer.context_menu import GestorMenuContextual, NOMBRE_MENU

    gestor = GestorMenuContextual()
    raiz = Path.home() / "Library" / "Services" / f"{NOMBRE_MENU}.workflow"

    # Escribir un flujo temporal con el formato nuevo y validar su contenido
    generado = gestor._registrar_macos()
    assert generado[0], f"No se pudo generar la Acción rápida: {generado[1]}"

    documento = raiz / "Contents" / "document.wflow"
    assert documento.exists(), "No se creó el documento del flujo"

    datos = plistlib.loads(documento.read_bytes())
    acciones = datos.get("actions") or []
    assert acciones, "El flujo no contiene ninguna acción"
    accion = acciones[0].get("action", {})

    for clave in ("ActionBundlePath", "BundleIdentifier", "Class Name", "UUID"):
        assert accion.get(clave), f"Falta el metadato obligatorio '{clave}' en la acción"

    parametros = accion.get("ActionParameters", {})
    assert parametros.get("inputMethod") == 1, (
        "inputMethod debe ser 1 para que las carpetas lleguen al script"
    )
    assert "--organizar-carpeta" in parametros.get("COMMAND_STRING", ""), (
        "El script no ejecuta la organización"
    )

    # El flujo debe considerarse sano (no roto) y Automator debe poder cargarlo
    assert not gestor._workflow_macos_esta_roto(), "El flujo nuevo se detecta como roto"
    carga = subprocess.run(
        ["automator", str(raiz)], capture_output=True, text=True, timeout=60
    )
    assert "no se ha cargado" not in carga.stderr, (
        f"Automator no puede cargar el flujo:\n{carga.stderr}"
    )

    print("✅ Acción rápida de Finder con formato válido para Automator")


def test_previsualizacion():
    """El plan de organización no debe tocar nada y detallar los movimientos."""
    base = Path(tempfile.mkdtemp(prefix="do_plan_"))
    (base / "foto.jpg").write_text("x" * 100)
    (base / "doc.pdf").write_text("y" * 200)
    (base / "bajando.part").write_text("z" * 50)

    org = OrganizadorArchivos(carpeta_descargas=str(base), usar_subcarpetas=False)
    plan = org.planificar_organizacion()

    assert plan["total"] == 2, f"Debería planificar 2 archivos, no {plan['total']}"
    assert "PDFs" in plan["categorias"] and "Imágenes" in plan["categorias"]
    assert not plan["errores"], f"Errores inesperados: {plan['errores']}"

    # La carpeta debe quedar intacta: la previsualización no mueve nada
    assert (base / "foto.jpg").exists(), "La previsualización movió un archivo"
    assert (base / "doc.pdf").exists(), "La previsualización movió un archivo"
    assert (base / "bajando.part").exists(), "Se tocó una descarga en curso"

    print("✅ Previsualización sin tocar nada")
    shutil.rmtree(base, ignore_errors=True)


def test_historial_deshacer():
    """El historial registra la operación y puede deshacerla."""
    from organizer import portable_config
    from organizer.historial import HistorialOperaciones

    base = Path(tempfile.mkdtemp(prefix="do_hist_"))
    (base / "foto.jpg").write_text("x")
    (base / "doc.pdf").write_text("y")

    # Historial aislado para no tocar el del usuario
    config_temporal = Path(tempfile.mkdtemp(prefix="do_histcfg_"))
    historial = HistorialOperaciones.__new__(HistorialOperaciones)
    historial.nombre_app = "Pruebas"
    historial._ruta = config_temporal / "historial.json"
    historial._operaciones = []

    org = OrganizadorArchivos(carpeta_descargas=str(base), usar_subcarpetas=False)
    resultados, _ = org.organizar()
    operacion = historial.registrar(resultados, base, "basico")
    assert operacion and operacion["total"] == 2, "No se registró la operación"
    assert not (base / "foto.jpg").exists(), "No se organizó"

    resultado = historial.deshacer(operacion)
    assert resultado["devueltos"] == 2, f"No se deshizo bien: {resultado}"
    assert (base / "foto.jpg").exists(), "El archivo no volvió a su sitio"
    assert (base / "doc.pdf").exists(), "El archivo no volvió a su sitio"
    assert historial.ultima() is None, "La operación debería salir del historial"

    print("✅ Historial con deshacer funciona")
    shutil.rmtree(base, ignore_errors=True)
    shutil.rmtree(config_temporal, ignore_errors=True)


def test_programacion_horaria():
    """La programación diaria calcula bien la próxima ejecución."""
    from datetime import datetime
    from organizer import programacion

    assert programacion.parsear_hora("22:00") == (22, 0)
    assert programacion.parsear_hora("07:30") == (7, 30)
    assert programacion.parsear_hora("25:00") is None
    assert programacion.parsear_hora("texto") is None

    ahora = datetime(2026, 9, 23, 10, 0, 0)
    # A las 22:00 desde las 10:00 -> 12 horas
    assert programacion.segundos_hasta_la_hora("22:00", ahora) == 12 * 3600
    # A las 09:00 desde las 10:00 -> mañana, 23 horas
    assert programacion.segundos_hasta_la_hora("09:00", ahora) == 23 * 3600

    descripcion = programacion.descripcion("22:00")
    assert "22:00" in descripcion, descripcion

    print("✅ Programación diaria correcta")


def test_analisis_disco():
    """El análisis de disco calcula tamaños y sugiere limpieza."""
    from organizer.analisis_disco import AnalizadorDisco, formatear_bytes

    base = Path(tempfile.mkdtemp(prefix="do_disco_"))
    (base / "Imágenes").mkdir()
    (base / "Imágenes" / "foto.jpg").write_bytes(b"x" * 5000)
    (base / "temporal.tmp").write_bytes(b"x" * 1000)

    analizador = AnalizadorDisco(base)
    datos = analizador.analizar()

    assert not datos.get("error"), datos.get("error")
    assert datos["total"] == 6000, f"Total inesperado: {datos['total']}"
    assert datos["archivos"] == 2
    assert "Imágenes" in datos["categorias"]
    assert any(s["tipo"] == "temporal" for s in datos["sugerencias"]), (
        "No detectó el archivo temporal"
    )
    assert "Total:" in analizador.informe()
    assert formatear_bytes(1536).startswith("1.5 KB")

    print("✅ Análisis de disco funciona")
    shutil.rmtree(base, ignore_errors=True)


def test_efectos_nativos():
    """El módulo de efectos no debe fallar en ningún sistema."""
    from organizer import efectos

    # En un sistema gráfico debe responder; sin él, simplemente degrada
    assert isinstance(efectos.soportado(), bool)
    # Aplicarlo sobre un objeto vacío no debe lanzar excepción
    resultado = efectos.aplicar_efecto_ventana(object())
    assert resultado is False, "Sin ventana real no debe aplicar nada"

    # La detección de compositor en Linux debe responder sin lanzar
    assert isinstance(efectos.hay_compositor(), bool)

    # La variable de entorno desactiva la transparencia por completo
    os.environ[efectos.VARIABLE_DESACTIVAR] = "1"
    try:
        assert efectos.desactivado_por_entorno() is True
        assert efectos.soportado() is False, (
            "Con la transparencia desactivada, soportado() debe ser False"
        )
        assert efectos.aplicar_efecto_ventana(object()) is False
    finally:
        del os.environ[efectos.VARIABLE_DESACTIVAR]
    assert efectos.desactivado_por_entorno() is False

    print("✅ Efectos nativos degradan con elegancia")


def test_translucidez_legible():
    """Con material detrás, el fondo deja pasar la luz pero las tarjetas no.

    Regresión: antes el fondo se quedaba en alfa 0.86, así que del material solo
    se transparentaba un 14% y el efecto no se veía. Ahora el fondo baja a 0.70
    y los paneles se mantienen casi opacos para no perder legibilidad.
    """
    from organizer import estilos

    for tema in ("claro", "oscuro"):
        c = estilos.colores_translucidos(tema, 0.70)
        assert "rgba(" in c["fondo"], f"El fondo de {tema} debe ser translúcido"
        assert "rgba(" in c["panel"], f"El panel de {tema} debe llevar alfa"
        # El panel tiene que ser más opaco que el fondo, o el texto se pierde
        fondo_alfa = float(c["fondo"].rsplit(",", 1)[1].rstrip(")"))
        panel_alfa = float(c["panel"].rsplit(",", 1)[1].rstrip(")"))
        assert panel_alfa > fondo_alfa, (
            f"En {tema} el panel ({panel_alfa}) debe ser más opaco que el "
            f"fondo ({fondo_alfa})"
        )
        assert fondo_alfa <= 0.75, (
            f"En {tema} el fondo apenas deja ver el material (alfa {fondo_alfa})"
        )
        assert panel_alfa >= 0.9, (
            f"En {tema} las tarjetas quedan demasiado transparentes "
            f"(alfa {panel_alfa})"
        )

    # A opacidad 1.0 todo queda opaco: el aspecto de siempre
    opaco = estilos.colores_translucidos("claro", 1.0)
    alfa_opaco = float(opaco["fondo"].rsplit(",", 1)[1].rstrip(")"))
    assert alfa_opaco == 1.0, (
        f"A opacidad 1.0 el fondo debe ser opaco, no alfa {alfa_opaco}"
    )

    # Y la hoja de estilo sin transparencia no debe contener alfa en el fondo
    css_opaco = estilos.hoja_estilo("claro")
    assert "rgba(242, 242, 247, 0.7" not in css_opaco, (
        "Sin efecto nativo el fondo no debe ser translúcido"
    )

    print("✅ Con material detrás, fondo translúcido y tarjetas legibles")


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


def test_configuracion_no_escribible():
    """Sin permiso de escritura, la app avisa en vez de caerse.

    El fallo de permisos se simula sin privilegios: se usa una ruta cuyo padre
    es un archivo, así que ``mkdir`` falla siempre con ``NotADirectoryError``,
    que es un ``OSError`` como el que devolvería un permiso denegado.
    """
    from organizer.app_paths import crear_directorio, crear_directorio_con_respaldo
    from organizer.date_organizer import OrganizadorPorFecha
    from organizer.statistics import EstadisticasOrganizador

    base = Path(tempfile.mkdtemp(prefix="do_sinperm_"))
    bloqueado = base / "bloqueado"
    bloqueado.write_text("no soy una carpeta")

    # El helper no lanza: devuelve False y quien llama decide qué hacer.
    assert crear_directorio(bloqueado / "sub" / "carpeta") is False, \
        "crear_directorio debería devolver False en lugar de lanzar"

    # Con respaldo, siempre se obtiene una ruta usable.
    alternativa = crear_directorio_con_respaldo(bloqueado / "otra")
    assert alternativa.is_dir(), f"No se obtuvo una carpeta alternativa: {alternativa}"

    # Los módulos que antes reventaban al arrancar ahora degradan solos.
    estadisticas = EstadisticasOrganizador(bloqueado)
    assert estadisticas.carpeta_stats.is_dir(), estadisticas.carpeta_stats

    fechas = OrganizadorPorFecha(bloqueado)
    assert fechas.carpeta_config.is_dir(), fechas.carpeta_config

    print("✅ Sin permisos de escritura se avisa en vez de caerse")
    shutil.rmtree(base, ignore_errors=True)


def test_manejador_de_errores():
    """El manejador global registra el rastro y se instala sin fallar."""
    from organizer import errores

    rastro = "Traceback de prueba\n  linea 1"
    errores.guardar_rastro(rastro)
    registro = errores.ruta_registro_errores()
    assert registro.exists(), f"No se creó el registro de errores: {registro}"
    assert rastro in registro.read_text(encoding="utf-8"), \
        "El rastro no se guardó en el registro"

    # Instalarlo dos veces debe ser inocuo (es idempotente).
    errores.instalar_manejador_global()
    errores.instalar_manejador_global()
    assert sys.excepthook is errores._manejador_excepciones, \
        "El excepthook no quedó instalado"

    # Desde un hilo de trabajo no se puede abrir una ventana: debe caer a
    # consola en lugar de intentarlo y bloquearse.
    resultado = {}

    def en_hilo():
        resultado["ventana"] = errores._podemos_abrir_ventanas()
        errores.mostrar_error("Prueba", "Desde un hilo")

    import threading
    hilo = threading.Thread(target=en_hilo)
    hilo.start()
    hilo.join(timeout=15)
    assert not hilo.is_alive(), "mostrar_error se bloqueó desde un hilo"
    assert resultado["ventana"] is False, \
        "No debería intentar abrir ventanas fuera del hilo principal"

    print("✅ Manejador global de errores funciona")


def test_error_por_consola_sin_gui():
    """Sin interfaz gráfica, un error se explica por consola sin traza cruda."""
    codigo = (
        "import sys; sys.path.insert(0, r'%s');"
        "from organizer import errores;"
        "errores.mostrar_error('Titulo', 'Mensaje claro', detalle='detalle tecnico')"
        % str(project_root)
    )
    resultado = subprocess.run(
        [sys.executable, "-c", codigo],
        capture_output=True, text=True, timeout=60
    )
    assert resultado.returncode == 0, resultado.stderr
    assert "Titulo" in resultado.stderr and "Mensaje claro" in resultado.stderr, \
        f"El error no se explicó por consola:\n{resultado.stderr}"
    print("✅ Los errores se explican sin interfaz gráfica")


def test_sistema_de_permisos():
    """El motor de permisos comprueba, pide y degrada sin lanzar excepciones."""
    from organizer import permission_manager as pm

    base = Path(tempfile.mkdtemp(prefix="do_perm_"))
    gestor = pm.GestorPermisos(carpeta_descargas=base)

    # El catálogo tiene que estar bien formado
    assert pm.CATALOGO, "El catálogo de capacidades está vacío"
    ids = [c.id for c in pm.CATALOGO]
    assert len(ids) == len(set(ids)), f"Hay capacidades duplicadas: {ids}"
    assert "carpeta_descargas" in ids
    # Solo la carpeta es imprescindible: todo lo demás debe ser omitible
    obligatorias = [c.id for c in pm.CATALOGO if c.obligatoria]
    assert obligatorias == ["carpeta_descargas"], (
        f"Demasiadas capacidades obligatorias: {obligatorias}"
    )
    for capacidad in pm.CATALOGO:
        assert capacidad.nombre and capacidad.para_que, (
            f"La capacidad {capacidad.id} no se explica al usuario"
        )

    # Comprobar cualquier capacidad real no debe lanzar nunca
    for capacidad in pm.CATALOGO:
        if capacidad.id == "red":
            continue  # implica una llamada de red
        resultado = gestor.comprobar(capacidad.id)
        assert isinstance(resultado.estado, pm.EstadoPermiso), resultado
        assert resultado.estado.disponible in (True, False)

    # Una capacidad inventada sí es un error de programación
    try:
        gestor.comprobar("inventada")
        raise AssertionError("Debería haber lanzado KeyError")
    except KeyError:
        pass

    # Con una carpeta escribible, requerir deja seguir
    ok, mensaje = gestor.requerir("carpeta_descargas")
    assert ok, f"Debería permitir seguir: {mensaje}"
    assert not mensaje

    # Con una ruta que no es carpeta, requerir lo explica y no deja seguir
    bloqueada = base / "no_soy_carpeta"
    bloqueada.write_text("x")
    gestor_bloqueado = pm.GestorPermisos(carpeta_descargas=bloqueada)
    ok, mensaje = gestor_bloqueado.requerir("carpeta_descargas")
    assert not ok, "No debería permitir seguir con una ruta inválida"
    assert "carpeta" in mensaje.lower(), mensaje
    assert "Hace falta para" in mensaje, (
        f"El mensaje debe explicar para qué sirve el permiso:\n{mensaje}"
    )

    # El diagnóstico incluye todas las capacidades salvo la red
    resultados = gestor.diagnostico()
    assert len(resultados) == len(pm.CATALOGO) - 1, (
        f"Diagnóstico incompleto: {len(resultados)} de {len(pm.CATALOGO)}"
    )

    # Solicitar un permiso denegado deja el estado en PENDIENTE, sin reventar
    denegada = next(
        (r for r in resultados if r.estado is pm.EstadoPermiso.DENEGADO), None
    )
    if denegada is not None:
        tras_pedir = gestor.solicitar(denegada.capacidad.id)
        assert tras_pedir.estado is pm.EstadoPermiso.PENDIENTE, tras_pedir.estado

    # Sin ancla conocida debe dar instrucciones en lugar de abrir nada.
    # (Se usa una capacidad inventada a propósito para no abrir los ajustes
    # reales del sistema durante las pruebas.)
    abierto, texto = pm.abrir_ajustes_del_sistema("capacidad_sin_ancla")
    assert abierto is False, "No debería abrir nada sin ancla conocida"
    assert texto, "Debe devolver instrucciones legibles"

    print("✅ Sistema de permisos comprueba, pide y degrada correctamente")
    shutil.rmtree(base, ignore_errors=True)


def test_permisos_conectados():
    """Las operaciones privilegiadas pasan por el motor y fallan de forma visible."""
    from organizer.context_menu import GestorMenuContextual
    from organizer.native_notifications import NotificadorNativo

    gestor = GestorMenuContextual()

    # Windows: por defecto se registra solo para el usuario (sin administrador).
    import inspect
    firma = inspect.signature(gestor.registrar_menu_contextual)
    assert "todos_los_usuarios" in firma.parameters, (
        "Falta el parámetro para elegir el alcance del registro"
    )
    assert firma.parameters["todos_los_usuarios"].default is False, (
        "Por defecto no debe requerir privilegios de administrador"
    )

    # El refresco del Finder debe informar de los pasos que fallan, no callarse.
    fallos = gestor._refrescar_servicios_macos()
    assert isinstance(fallos, list), (
        f"Debe devolver la lista de fallos, no {type(fallos).__name__}"
    )
    if sys.platform != "darwin":
        assert fallos, "Fuera de macOS el refresco debe reportar que no pudo hacer nada"

    # Una notificación imposible de enviar debe dejar rastro consultable.
    notificador = NotificadorNativo()
    notificador.deshabilitar()
    assert notificador.ultimo_fallo() == "", "Deshabilitado no debe registrar fallo"

    notificador.habilitar()
    if not shutil.which("notify-send") and sys.platform.startswith("linux"):
        notificador.mostrar("Prueba", "Mensaje")
        assert notificador.ultimo_fallo(), (
            "Sin notify-send debe quedar registrado el motivo del fallo"
        )

    print("✅ Los permisos están conectados y los fallos dejan rastro")


def test_asistente_primer_arranque():
    """El asistente se muestra una vez, es omitible y no hace llamadas de red."""
    from organizer import permission_manager as pm, primer_arranque

    # --- memoria de «ya se ha mostrado» ---
    class ConfigFalsa:
        def __init__(self):
            self.datos = {}

        def obtener(self, clave, defecto=None):
            return self.datos.get(clave, defecto)

        def establecer(self, clave, valor):
            self.datos[clave] = valor

    config = ConfigFalsa()
    assert primer_arranque.debe_mostrarse(config) is True, "La primera vez debe mostrarse"
    primer_arranque.marcar_como_visto(config)
    assert primer_arranque.debe_mostrarse(config) is False, "No debe repetirse"
    primer_arranque.olvidar(config)
    assert primer_arranque.debe_mostrarse(config) is True, "Debe poder repetirse"

    # Sin configuración no se puede recordar nada: mejor no mostrarlo
    assert primer_arranque.debe_mostrarse(None) is False
    primer_arranque.marcar_como_visto(None)   # no debe lanzar
    primer_arranque.olvidar(None)             # no debe lanzar

    # --- la conexión a internet no se presenta como permiso a conceder ---
    red = pm.CAPACIDADES_POR_ID["red"]
    assert red.se_concede_en_ajustes is False, (
        "La conexión no se concede en Ajustes: se comprueba"
    )
    presentables = [c for c in pm.CATALOGO if c.se_concede_en_ajustes]
    assert "red" not in [c.id for c in presentables], (
        "El asistente no debe comprobar la red (retrasaría la ventana)"
    )
    assert presentables, "El asistente debe tener algo que presentar"

    print("✅ Asistente de primer arranque correcto")


def test_iconos_propios():
    """El set de iconos existe, se dibuja y responde al tema."""
    from organizer import iconos

    nombres = iconos.disponibles()
    assert nombres, "No hay iconos definidos"
    assert len(nombres) >= 20, f"El set es demasiado pobre: {len(nombres)} iconos"

    # Todos los que usa la interfaz deben existir
    necesarios = [
        "inicio", "historial", "actividad", "ajustes", "avanzado",
        "carpeta", "organizar", "deshacer", "refrescar", "escudo",
        "exito", "error", "info", "campana", "red",
    ]
    faltan = [n for n in necesarios if n not in nombres]
    assert not faltan, f"Faltan iconos que usa la interfaz: {faltan}"

    # Un nombre desconocido no debe reventar: cae al icono por defecto
    iconos.limpiar_cache()
    pixmap = iconos.pixmap("no_existe_este_icono", 20, tema="claro")
    assert not pixmap.isNull(), "Un icono desconocido debe devolver algo válido"

    # El color cambia con el tema
    assert iconos.color_texto("claro") != iconos.color_texto("oscuro"), (
        "El color del icono debe seguir al tema"
    )

    # Se dibuja al tamaño pedido, teniendo en cuenta la densidad de pantalla
    pm = iconos.pixmap("carpeta", 24, tema="claro")
    assert not pm.isNull(), "El icono de carpeta no se dibujó"
    assert pm.width() >= 24, f"Tamaño inesperado: {pm.width()}"

    # La caché no debe devolver objetos distintos para la misma petición
    iconos.limpiar_cache()
    primero = iconos.pixmap("inicio", 20, tema="claro")
    segundo = iconos.pixmap("inicio", 20, tema="claro")
    assert not primero.isNull() and not segundo.isNull()

    iconos.limpiar_cache()
    print("✅ Iconos propios correctos")


def test_tokens_de_diseno():
    """Los tokens de diseño existen y la hoja de estilo se genera a partir de ellos."""
    from organizer import estilos

    assert estilos.TOKENS, "No hay tokens de diseño"
    # Los tokens más usados por los componentes
    for clave in ("radio_tarjeta", "radio_campo", "radio_boton", "esp_m",
                  "esp_l", "esp_xl", "mov_transicion"):
        assert clave in estilos.TOKENS, f"Falta el token '{clave}'"
        assert isinstance(estilos.TOKENS[clave], int), f"'{clave}' debe ser entero"

    # La hoja de estilo se genera en los dos temas y con transparencia
    for tema in ("claro", "oscuro"):
        css = estilos.hoja_estilo(tema)
        assert css.strip(), f"Hoja vacía para el tema {tema}"
        assert "QPushButton" in css and "QListWidget" in css

    css_translucido = estilos.hoja_estilo("claro", opacidad=0.7)
    assert "rgba(" in css_translucido, (
        "Con transparencia los fondos deben expresarse en rgba"
    )
    # El fondo translúcido y las tarjetas casi opacas: es lo que hace que el
    # material se aprecie sin perder legibilidad.
    claro = estilos.colores_translucidos("claro", 0.70)
    assert "rgba(" in claro["fondo"], claro["fondo"]
    assert claro["panel"] != claro["fondo"], (
        "Las tarjetas deben ser más opacas que el fondo"
    )

    print("✅ Tokens de diseño correctos")


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
    test_actualizaciones_sin_api()
    test_instancia_unica()
    test_menu_contextual_multiplataforma()
    test_workflow_macos_valido()
    test_previsualizacion()
    test_historial_deshacer()
    test_programacion_horaria()
    test_analisis_disco()
    test_efectos_nativos()
    test_translucidez_legible()
    test_flujo_organizar_carpeta_cli()
    test_cli_diagnostico()
    test_configuracion_no_escribible()
    test_manejador_de_errores()
    test_error_por_consola_sin_gui()
    test_sistema_de_permisos()
    test_permisos_conectados()
    test_asistente_primer_arranque()
    test_iconos_propios()
    test_tokens_de_diseno()
    print("\n🎉 Todas las pruebas pasaron correctamente")


if __name__ == "__main__":
    main()
