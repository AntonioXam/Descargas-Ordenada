#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DescargasOrdenadas - Organizador automático de descargas

Punto de entrada único para la aplicación de organización automática de archivos.
"""

import sys
import os
from pathlib import Path

# Asegurar que el directorio padre está en el path para importar organizer
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse
import logging
import importlib.util
import platform
import subprocess
import shutil
import time
import traceback

from organizer.version import obtener_version
from organizer.app_paths import obtener_archivo_version, obtener_base_recursos, obtener_directorio_configuracion
from organizer.single_instance import InstanciaUnica
from organizer import errores

# Lo antes posible: a partir de aquí ningún fallo acaba en una traza ilegible.
errores.instalar_manejador_global()

def obtener_python_ejecutable() -> str:
    """Obtiene un intérprete Python válido incluso cuando la app está empaquetada."""
    if not getattr(sys, "frozen", False):
        return sys.executable

    for candidato in ("python", "python3"):
        ruta = shutil.which(candidato)
        if ruta:
            return ruta

    return sys.executable


def instalar_dependencia(package_name):
    """Instala una dependencia automáticamente."""
    try:
        print(f"📦 Instalando {package_name}...")
        subprocess.check_call([
            obtener_python_ejecutable(), "-m", "pip", "install", package_name,
            "--quiet", "--disable-pip-version-check"
        ])
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Error al instalar {package_name}")
        return False

def obtener_dependencias_faltantes() -> list[tuple[str, str]]:
    """Devuelve la lista de dependencias Python que faltan en el sistema."""
    dependencias = [
        ("Pillow", "PIL"),
        ("PySide6", "PySide6"),
        ("watchdog", "watchdog"),
        ("requests", "requests"),
        ("plyer", "plyer"),
    ]
    if sys.platform == "win32":
        dependencias.append(("pywin32", "win32com.client"))

    faltantes = []
    for package_name, import_name in dependencias:
        try:
            importlib.import_module(import_name)
        except ImportError:
            faltantes.append((package_name, import_name))
    return faltantes

def reparar_dependencias() -> bool:
    """Repara las dependencias Python faltantes descargándolas desde PyPI."""
    faltantes = obtener_dependencias_faltantes()
    if not faltantes:
        print("✅ Todas las dependencias están instaladas")
        return True

    print("🩹 Reparando dependencias online...")
    fallos = []
    for package_name, _ in faltantes:
        if not instalar_dependencia(package_name):
            fallos.append(package_name)

    faltantes_despues = obtener_dependencias_faltantes()
    if faltantes_despues:
        nombres = ", ".join(package for package, _ in faltantes_despues)
        print(f"❌ No se pudieron reparar: {nombres}")
        return False

    print("✅ Dependencias reparadas correctamente")
    return True

def verificar_dependencias():
    """Verifica e instala dependencias automáticamente."""
    if getattr(sys, "frozen", False):
        return True

    required_packages = [
        ("pillow", "PIL"),
        ("PySide6", "PySide6"),
        ("watchdog", "watchdog")
    ]
    
    if sys.platform == "win32":
        required_packages.append(("pywin32", "win32api"))
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            importlib.import_module(import_name)
        except ImportError:
            missing_packages.append((package_name, import_name))
    
    if missing_packages:
        print("🔧 Instalando dependencias automáticamente...")
        
        for package_name, import_name in missing_packages:
            if package_name == "pywin32" and sys.platform == "win32":
                print("🪟 Instalando pywin32 para Windows...")
                instalar_dependencia(package_name)
            else:
                if not instalar_dependencia(package_name):
                    print(f"❌ Error: No se pudo instalar {package_name}")
                    return False
        
        print("✅ Dependencias instaladas correctamente")
        time.sleep(1)
    
    return True

def verificar_y_crear_acceso_directo():
    """Verifica si existe un acceso directo y lo crea si no existe."""
    if getattr(sys, "frozen", False):
        return
    if sys.platform != "win32":
        return  # Solo en Windows
    
    try:
        script_dir = Path(__file__).parent.absolute()
        shortcut_path = script_dir / "DescargasOrdenadas.lnk"
        
        # Si ya existe, no hacer nada
        if shortcut_path.exists():
            return
        
        # Intentar crear el acceso directo silenciosamente
        try:
            import win32com.client
            
            bat_file = script_dir / "INICIAR.bat"
            if not bat_file.exists():
                return
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(bat_file)
            shortcut.WorkingDirectory = str(script_dir)
            shortcut.Description = "DescargasOrdenadas v3.0 - Organizador Automático de Archivos"
            
            # Buscar icono
            ico_path = script_dir / "resources" / "favicon.ico"
            if ico_path.exists():
                shortcut.IconLocation = str(ico_path)
            
            shortcut.save()
            print("🔗 Acceso directo creado en la carpeta raíz")
            
        except Exception:
            # Si falla, no hacer nada (silencioso)
            pass
            
    except Exception:
        # Fallos silenciosos para no interrumpir el flujo principal
        pass

def flujo_organizar_carpeta(args) -> int:
    """Organiza una carpeta concreta (menú contextual) sin abrir la interfaz.

    - Si ya hay una instancia abierta, le delega el trabajo para aprovechar
      sus preferencias y no competir por los archivos.
    - Si no hay nadie, organiza directamente y termina.
    - Los problemas de permisos se avisan con claridad, nunca revientan.
    """
    carpeta_destino = Path(args.organizar_carpeta).expanduser()

    # Modo guardado por el usuario (básico/detallado) o el de la línea de órdenes
    preferencias = leer_preferencias_autoarranque()
    modo_efectivo = args.modo or preferencias["modo"]

    permitir_duplicada = (
        args.nueva_instancia
        or os.environ.get("DESCARGASORDENADAS_NUEVA_INSTANCIA") == "1"
    )

    if not permitir_duplicada:
        guardia = preparar_instancia_unica(permitir_duplicada)
        if not guardia.adquirir():
            # Ya hay una copia viva: que sea ella la que organice
            if guardia.enviar_organizar(str(carpeta_destino)):
                if not args_silencioso():
                    print(f"DescargasOrdenadas ya estaba abierto: organizando {carpeta_destino}")
                return 0
            if not args_silencioso():
                print("No se pudo avisar a la instancia abierta; se organiza por separado")

    ok, mensaje = comprobar_permisos_carpeta(carpeta_destino)
    if not ok:
        print(f"⚠️ {mensaje}")
        if not ok and "permisos" in mensaje.lower():
            _avisar_permisos_denegados(carpeta_destino)
        else:
            _avisar_usuario("No se pudo organizar la carpeta", mensaje)
        return 1

    if args.usar_como_base:
        from organizer.portable_config import obtener_config

        obtener_config().establecer("carpeta_base", str(carpeta_destino))
        if not args_silencioso():
            print(f"✅ Carpeta principal establecida: {carpeta_destino}")

    codigo = organizar_carpeta_cli(
        carpeta_destino, modo_efectivo, args.recursivo, args.dry_run
    )

    # El guardia (si lo teníamos) se libera al terminar
    if not permitir_duplicada:
        try:
            guardia.liberar()
        except Exception:
            pass
    return codigo


def configurar_logger():
    """Configura el sistema de logging."""
    logger = logging.getLogger('DescargasOrdenadas')
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def obtener_carpeta_descargas():
    """Obtiene la carpeta de descargas real del sistema.

    Respeta la carpeta guardada por el usuario en la configuración y, si no
    hay ninguna, detecta la del sistema (registro en Windows, XDG en Linux,
    ~/Downloads en macOS) con las mismas reglas que el organizador.
    """
    # ¿El usuario eligió una carpeta base en Ajustes o en el menú contextual?
    try:
        from organizer.portable_config import obtener_config

        guardada = obtener_config().obtener("carpeta_base", None)
        if guardada:
            ruta = Path(str(guardada)).expanduser()
            if ruta.is_dir():
                return ruta
    except Exception:
        pass

    try:
        from organizer.file_organizer import OrganizadorArchivos

        organizador = OrganizadorArchivos.__new__(OrganizadorArchivos)
        detectada = organizador._detectar_carpeta_descargas()
        if detectada:
            return detectada
    except Exception:
        pass

    downloads_path = Path.home() / "Downloads"
    if not downloads_path.exists():
        downloads_path = Path.home() / "Descargas"
    return downloads_path


def leer_preferencias_autoarranque() -> dict:
    """Devuelve el modo y el intervalo de auto-organización guardados."""
    preferencias = {"auto_organizacion": False, "modo": "basico", "intervalo": 3600}
    try:
        from organizer.portable_config import obtener_config
        config = obtener_config()
        preferencias["auto_organizacion"] = bool(config.obtener("auto_organizacion", False))
        modo_guardado = config.obtener("auto_modo", "basico")
        if modo_guardado in ("basico", "detallado"):
            preferencias["modo"] = modo_guardado
        try:
            intervalo = int(config.obtener("auto_intervalo", 3600) or 3600)
            preferencias["intervalo"] = max(30, intervalo)
        except (TypeError, ValueError):
            pass
    except Exception as e:
        logging.getLogger('DescargasOrdenadas').debug(
            f"No se pudieron leer las preferencias guardadas: {e}"
        )
    return preferencias


def preparar_instancia_unica(permitir_duplicada: bool):
    """Crea el control de instancia única de la aplicación."""
    return InstanciaUnica("DescargasOrdenadas")


def comprobar_permisos_carpeta(carpeta: Path) -> tuple[bool, str]:
    """Comprueba que la carpeta existe y se puede leer y escribir en ella.

    Devuelve (ok, mensaje). El mensaje es legible y explica qué falta, sin
    lanzar excepciones: es mejor avisar que fallar.
    """
    try:
        if not carpeta.exists():
            return False, f"La carpeta no existe: {carpeta}"
        if not carpeta.is_dir():
            return False, f"La ruta no es una carpeta: {carpeta}"
    except OSError as e:
        return False, f"No se puede acceder a la carpeta ({e}): {carpeta}"

    if not os.access(carpeta, os.R_OK):
        return False, (
            f"Sin permisos de lectura sobre:\n{carpeta}\n\n"
            "Abre Ajustes del sistema → Privacidad y seguridad → Archivos y carpetas "
            "y concede acceso a DescargasOrdenadas."
            if sys.platform == "darwin"
            else f"Sin permisos de lectura sobre:\n{carpeta}"
        )

    if not os.access(carpeta, os.W_OK):
        mensaje = f"Sin permisos de escritura sobre:\n{carpeta}"
        if sys.platform == "darwin":
            mensaje += "\n\nConcede acceso completo al disco en Privacidad y seguridad."
        elif sys.platform.startswith("linux"):
            mensaje += "\n\nRevisa el propietario de la carpeta o usa una carpeta de tu usuario."
        else:
            mensaje += "\n\nPrueba con una carpeta dentro de tu perfil de usuario."
        return False, mensaje

    return True, ""


def organizar_carpeta_cli(carpeta: Path, modo: str, recursivo: bool = False, dry_run: bool = False) -> int:
    """Organiza una carpeta concreta sin GUI. Devuelve el código de salida."""
    ok, mensaje = comprobar_permisos_carpeta(carpeta)
    if not ok:
        print(f"⚠️ {mensaje}")
        _avisar_usuario("No se pudo organizar la carpeta", mensaje)
        return 1

    if not (args_silencioso()):
        print(f"📂 Organizando: {carpeta}")

    try:
        from organizer.file_organizer import OrganizadorArchivos

        usar_subcarpetas = modo == "detallado"
        organizador = OrganizadorArchivos(
            carpeta_descargas=str(carpeta), usar_subcarpetas=usar_subcarpetas
        )
        resultados, errores = organizador.organizar(
            organizar_subcarpetas=recursivo, simular=dry_run
        )
        total = sum(len(files) for cat in resultados.values() for files in cat.values())

        if errores and total == 0:
            detalle = "\n".join(errores[:3])
            print(f"⚠️ No se pudo completar la organización:\n{detalle}")
            _avisar_usuario("No se pudo organizar la carpeta", detalle)
            return 1

        if not args_silencioso():
            print(f"✅ {total} archivos organizados")
            if errores:
                print(f"⚠️ {len(errores)} avisos (algún archivo no se pudo mover)")
        if total > 0:
            _avisar_usuario(
                "Carpeta organizada",
                f"{total} archivo{'s' if total != 1 else ''} en {carpeta.name}",
            )
        return 0
    except PermissionError as e:
        print(f"⚠️ Sin permisos para organizar {carpeta}: {e}")
        _avisar_usuario("Sin permisos", str(e))
        return 1
    except Exception as e:
        print(f"❌ Error organizando {carpeta}: {e}")
        _avisar_usuario("Error al organizar", str(e))
        return 1


def _avisar_usuario(titulo: str, mensaje: str):
    """Muestra una notificación nativa si es posible (nunca falla)."""
    try:
        from organizer.native_notifications import NotificadorNativo

        NotificadorNativo().mostrar(titulo, mensaje, tipo="info", duracion=5)
    except Exception:
        pass


def _avisar_permisos_denegados(carpeta: Path):
    """Aviso claro y específico cuando el sistema bloquea el acceso a la carpeta."""
    if sys.platform == "darwin":
        mensaje = (
            f"macOS está bloqueando el acceso a {carpeta}.\n\n"
            "Ve a Ajustes del sistema → Privacidad y seguridad → Archivos y carpetas "
            "y activa el acceso para DescargasOrdenadas."
        )
    elif sys.platform == "win32":
        mensaje = (
            f"Windows está bloqueando el acceso a {carpeta}.\n\n"
            "Prueba a ejecutar la aplicación como administrador o elige una carpeta "
            "dentro de tu perfil de usuario."
        )
    else:
        mensaje = (
            f"El sistema está bloqueando el acceso a {carpeta}.\n\n"
            "Revisa los permisos de la carpeta con: ls -ld "
            f"'{carpeta}'"
        )
    print(f"⚠️ {mensaje}")
    _avisar_usuario("Permisos necesarios", mensaje)


def args_silencioso() -> bool:
    """Indica si la ejecución actual debe evitar la salida por consola."""
    return os.environ.get("DESCARGASORDENADAS_SILENCIOSO") == "1"

def main():
    parser = argparse.ArgumentParser(description="Organiza automáticamente los archivos de descargas")
    parser.add_argument("--version", action="version", version=f"DescargasOrdenadas {obtener_version()}")
    parser.add_argument("--info", action="store_true", help="Mostrar información del sistema y de la instalación")
    parser.add_argument("--reparar-dependencias", action="store_true", help="Descargar e instalar dependencias faltantes")
    parser.add_argument("--gui", action="store_true", help="Abrir interfaz gráfica (por defecto)")
    parser.add_argument("--auto", action="store_true", help="Organizar una vez sin GUI")
    parser.add_argument("--autostart", action="store_true", help="Modo autostart del sistema")
    parser.add_argument("--minimizado", action="store_true", help="Iniciar minimizado")
    parser.add_argument("--sin-consola", action="store_true", help="Ocultar ventana de consola")
    parser.add_argument("--dir", type=str, help="Directorio a organizar")
    parser.add_argument("--dry-run", action="store_true", help="Mostrar qué se organizaría sin mover archivos")
    parser.add_argument("--modo", choices=["basico", "detallado"], default=None, help="Modo de organización (por defecto, el guardado en la configuración)")
    parser.add_argument("--recursivo", action="store_true", help="Organizar también archivos dentro de subcarpetas")
    parser.add_argument("--nueva-instancia", action="store_true", help="Permitir una segunda copia aunque ya haya una abierta")
    parser.add_argument(
        "--organizar-carpeta", type=str, metavar="RUTA",
        help="Organizar una carpeta concreta y salir (usado por el menú contextual)",
    )
    parser.add_argument(
        "--usar-como-base", action="store_true",
        help="Guardar la carpeta de --organizar-carpeta como carpeta principal",
    )
    
    args = parser.parse_args()

    if args.reparar_dependencias:
        sys.exit(0 if reparar_dependencias() else 1)

    if args.info:
        try:
            from organizer.file_organizer import OrganizadorArchivos
            organizador = OrganizadorArchivos()
            estado = organizador.obtener_estado_modulos()
        except Exception:
            estado = {}

        print("DescargasOrdenadas - Información del sistema")
        print("=" * 55)
        print(f"Versión: {obtener_version()}")
        print(f"Sistema: {platform.system()} {platform.release()}")
        print(f"Python: {platform.python_version()}")
        print(f"Modo: {'instalado (PyInstaller)' if getattr(sys, 'frozen', False) else 'desarrollo'}")
        print(f"Recursos: {obtener_base_recursos()}")
        print(f"Configuración: {obtener_directorio_configuracion()}")
        faltantes = obtener_dependencias_faltantes()
        if faltantes:
            print("Dependencias faltantes:")
            for package_name, _ in faltantes:
                print(f"  ❌ {package_name}")
            print("  💡 Usa: python organizer/INICIAR.py --reparar-dependencias")
        if estado:
            print("Módulos avanzados:")
            for nombre, disponible in estado.items():
                print(f"  {'✅' if disponible else '❌'} {nombre}")
        return
    
    # ------------------------------------------------- flujo menú contextual
    # Se atiende antes de cargar la interfaz: organizar una carpeta desde el
    # clic derecho no debe abrir ninguna ventana.
    if args.organizar_carpeta:
        return flujo_organizar_carpeta(args)

    # Ocultar consola ANTES de cualquier print si se solicita
    if args.sin_consola or args.autostart or args.minimizado:
        if sys.platform == "win32":
            try:
                import ctypes
                console_window = ctypes.windll.kernel32.GetConsoleWindow()
                if console_window:
                    ctypes.windll.user32.ShowWindow(console_window, 0)  # SW_HIDE
            except:
                pass
    
    # Solo mostrar prints si NO es modo silencioso
    if not (args.sin_consola or args.autostart or args.minimizado):
        try:
            version = obtener_archivo_version().read_text(encoding="utf-8").strip()
        except Exception:
            version = "5.1.0"
        print(f"DescargasOrdenadas v{version}")
        print("=" * 50)
    
    # Solo configurar logger con salida a consola si NO es modo silencioso
    if not (args.sin_consola or args.autostart or args.minimizado):
        logger = configurar_logger()
    else:
        # Configurar logger solo a archivo en modo silencioso
        logger = logging.getLogger('DescargasOrdenadas')
        logger.setLevel(logging.INFO)
        # Sin handler de consola en modo silencioso
    
    # Verificar dependencias
    if not verificar_dependencias():
        if not args.autostart:  # Solo mostrar input si NO es autostart
            input("\n❌ Presiona Enter para cerrar...")
        sys.exit(1)
    
    # Verificar y crear acceso directo automáticamente
    verificar_y_crear_acceso_directo()
    
    try:
        from organizer.file_organizer import OrganizadorArchivos
        try:
            from organizer.gui_avanzada import run_advanced_gui as run_gui
        except ImportError:
            from organizer.gui import run_app as run_gui
    except ImportError as e:
        logger.error(f"Error al importar módulos: {e}")
        if not args.autostart:  # Solo mostrar input si NO es autostart
            input("\n❌ Presiona Enter para cerrar...")
        sys.exit(1)
    
    # Determinar directorio
    if args.dir:
        directorio = Path(args.dir)
        if not directorio.exists():
            logger.error(f"El directorio no existe: {directorio}")
            sys.exit(1)
    else:
        directorio = obtener_carpeta_descargas()
    
    logger.info(f"📁 Directorio: {directorio}")
    
    # Preferencias guardadas (modo básico/detallado e intervalo)
    preferencias = leer_preferencias_autoarranque()
    modo_efectivo = args.modo or preferencias["modo"]

    # ¿La GUI disponible acepta el intervalo y el modo guardados?
    try:
        import inspect
        gui_acepta_preferencias = "intervalo_auto" in inspect.signature(run_gui).parameters
    except (TypeError, ValueError):
        gui_acepta_preferencias = False

    # ---------------------------------------------------------------- guardia
    # Control de instancia única: nunca debe haber dos copias abiertas. Si ya
    # hay una, en vez de lanzar otra se le pide que haga lo que haga falta
    # (mostrarse o organizar una carpeta del menú contextual).
    permitir_duplicada = args.nueva_instancia or os.environ.get("DESCARGASORDENADAS_NUEVA_INSTANCIA") == "1"
    guardia = None
    if not permitir_duplicada:
        guardia = preparar_instancia_unica(permitir_duplicada)
        if not guardia.adquirir():
            logger.info("ℹ️ Ya hay una instancia abierta; no se lanza una segunda copia")

            if not (args.minimizado or args.autostart):
                # Si el usuario la ha abierto a mano, sacamos la ventana existente
                if not guardia.avisar_instancia_existente():
                    print("ℹ️ DescargasOrdenadas ya está abierto (revisa la bandeja del sistema).")
            return

    # Modo de funcionamiento
    if args.auto:
        # Solo organizar una vez
        logger.info("📂 Organizando archivos...")
        usar_subcarpetas = modo_efectivo == "detallado"
        organizador = OrganizadorArchivos(carpeta_descargas=str(directorio), usar_subcarpetas=usar_subcarpetas)
        resultados, errores = organizador.organizar(
            organizar_subcarpetas=args.recursivo,
            simular=args.dry_run
        )
        modo = "simulación" if args.dry_run else "organización"
        total = sum(len(files) for cat in resultados.values() for files in cat.values())
        logger.info(f"✅ {total} archivos organizados")
        
    elif args.autostart:
        # Modo autostart: organizar + GUI minimizada con auto-organización
        logger.info("🚀 Modo autostart iniciado...")
        logger.info(
            f"⚙️  Configuración guardada: modo {modo_efectivo}, "
            f"intervalo {preferencias['intervalo']}s, "
            f"auto-organización {'activada' if preferencias['auto_organizacion'] else 'desactivada'}"
        )
        usar_subcarpetas = modo_efectivo == "detallado"
        organizador = OrganizadorArchivos(carpeta_descargas=str(directorio), usar_subcarpetas=usar_subcarpetas)
        resultados, errores = organizador.organizar(organizar_subcarpetas=args.recursivo)
        total = sum(len(files) for cat in resultados.values() for files in cat.values())
        logger.info(f"✅ {total} archivos organizados inicialmente")
        
        # Ocultar consola
        if sys.platform == "win32":
            try:
                import ctypes
                console_window = ctypes.windll.kernel32.GetConsoleWindow()
                if console_window:
                    ctypes.windll.user32.ShowWindow(console_window, 0)
            except:
                pass
        
        # Iniciar GUI minimizada respetando la configuración guardada
        try:
            if gui_acepta_preferencias:
                run_gui(
                    directorio=directorio,
                    minimizado=True,
                    auto_organizacion=preferencias["auto_organizacion"],
                    intervalo_auto=preferencias["intervalo"],
                    modo_auto=modo_efectivo,
                    guardia_instancia=guardia,
                )
            else:
                # Compatibilidad con la GUI sencilla (organizer/gui.py)
                run_gui(directorio=directorio, minimizado=True)
        except Exception as e:
            logger.error(f"Error iniciando GUI: {e}")
            
    else:
        # Modo normal: GUI
        logger.info("🖥️  Iniciando interfaz gráfica...")
        try:
            if gui_acepta_preferencias:
                run_gui(
                    directorio=directorio,
                    minimizado=args.minimizado,
                    auto_organizacion=preferencias["auto_organizacion"],
                    intervalo_auto=preferencias["intervalo"],
                    modo_auto=modo_efectivo,
                    guardia_instancia=guardia,
                )
            else:
                # Compatibilidad con la GUI sencilla (organizer/gui.py)
                run_gui(directorio=directorio, minimizado=args.minimizado)
        except Exception as e:
            logger.error(f"Error iniciando GUI: {e}")
            # No mostrar input() porque la GUI maneja su propio cierre
            sys.exit(1)

if __name__ == "__main__":
    try:
        # Los flujos de consola (organizar carpeta, auto, info) devuelven un
        # código de salida real para que scripts y menús contextuales puedan
        # saber si el trabajo se hizo o no.
        resultado = main()
        if isinstance(resultado, int):
            sys.exit(resultado)
    except KeyboardInterrupt:
        print("\n🛑 Aplicación cerrada por el usuario")
        # Salir silenciosamente en interrupciones de teclado
        sys.exit(0)
    except Exception as e:
        # El manejador global ya registró el rastro; aquí solo se decide si
        # conviene mantener la consola abierta para que el usuario lo lea.
        detalle = traceback.format_exc()
        errores.guardar_rastro(detalle)
        errores.mostrar_error(
            "No se pudo iniciar DescargasOrdenadas",
            str(e),
            detalle=detalle,
            sugerencia=(
                "El detalle completo está en:\n"
                f"{errores.ruta_registro_errores()}"
            ),
        )

        # En modo consola explícito se espera a que el usuario lea el mensaje;
        # en modo gráfico se sale sin bloquear.
        try:
            if len(sys.argv) == 1 or '--auto' not in sys.argv:
                sys.exit(1)
            input("Presiona Enter para cerrar...")
            sys.exit(1)
        except Exception:
            sys.exit(1)
