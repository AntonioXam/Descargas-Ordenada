#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de actualizaciones automáticas con descarga desde GitHub
DescargasOrdenadas v3.1
"""

import sys
import logging
import json
import zipfile
import shutil
import subprocess
import os
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

from .version import obtener_version
from .app_paths import obtener_directorio_configuracion

logger = logging.getLogger('organizador.actualizaciones')

try:
    import requests
    REQUESTS_DISPONIBLE = True
except ImportError:
    REQUESTS_DISPONIBLE = False
    logger.warning("requests no disponible - actualizaciones deshabilitadas")

class GestorActualizacionesMejorado:
    """Gestor de actualizaciones con descarga automática desde GitHub."""
    
    VERSION_ACTUAL = obtener_version()
    GITHUB_USER = "AntonioXam"
    GITHUB_REPO = "Descargas-Ordenada"
    
    def __init__(self):
        self.config_path = self._obtener_ruta_config()
        self.ultima_verificacion = None
        self.nueva_version_disponible = None
        self._ultima_comprobacion_fallida = False
        self._api_latest = f"https://api.github.com/repos/{self.GITHUB_USER}/{self.GITHUB_REPO}/releases/latest"
        self._api_tags = f"https://api.github.com/repos/{self.GITHUB_USER}/{self.GITHUB_REPO}/tags"
        self._cargar_config()
    
    def _obtener_ruta_config(self) -> Path:
        """Obtiene la ruta del archivo de configuración."""
        config_dir = obtener_directorio_configuracion()
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "actualizaciones.json"
    
    def _cargar_config(self):
        """Carga la configuración de actualizaciones.

        Se recuerda cuál era la versión nueva detectada y cuándo se comprobó,
        para no consultar GitHub en cada arranque. La fecha solo cuenta si la
        comprobación terminó bien: si falló, se reintenta antes.
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    fecha_str = config.get('ultima_verificacion')
                    if fecha_str:
                        self.ultima_verificacion = datetime.fromisoformat(fecha_str)
                    self.nueva_version_disponible = config.get('nueva_version') or None
                    self._ultima_comprobacion_fallida = bool(
                        config.get('comprobacion_fallida', False)
                    )

                    # Migración: las versiones anteriores guardaban un fallo de
                    # red o un límite de GitHub como «comprobado, sin novedades»
                    # y eso bloqueaba cualquier reintento durante 24 h. Esos
                    # archivos no llevan la marca 'comprobacion_fallida', así que
                    # se descarta la comprobación para volver a mirar ya.
                    formato_antiguo = 'comprobacion_fallida' not in config
                    if formato_antiguo:
                        self.ultima_verificacion = None
                        self.nueva_version_disponible = None
                        self._ultima_comprobacion_fallida = False
                        logger.info(
                            "Se refresca la comprobación de actualizaciones "
                            "(formato anterior)"
                        )
        except Exception as e:
            logger.error(f"Error cargando config actualizaciones: {e}")

    def _guardar_config(self):
        """Guarda la configuración de actualizaciones."""
        try:
            config = {
                'ultima_verificacion': self.ultima_verificacion.isoformat() if self.ultima_verificacion else None,
                'nueva_version': self.nueva_version_disponible,
                'version_actual': self.VERSION_ACTUAL,
                'comprobacion_fallida': bool(getattr(self, '_ultima_comprobacion_fallida', False)),
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            logger.error(f"Error guardando config actualizaciones: {e}")
    
    def verificar_actualizaciones(self, forzar=False) -> Tuple[bool, Optional[Dict]]:
        """Comprueba si hay una versión más nueva publicada.

        Se apoya en la API pública de GitHub, que tiene un límite de peticiones
        por hora (60 por IP sin autenticar). Por eso se prueban varios canales
        en orden y, si todos fallan, se informa de que *no se pudo comprobar*
        en vez de decir «ya tienes la última versión» y no volver a intentarlo
        hasta el día siguiente.
        """
        if not REQUESTS_DISPONIBLE:
            return False, None

        # Comprobación reciente (24 h) salvo que se fuerce. Si la última vez no
        # se pudo comprobar de verdad, se reintenta aunque no haya pasado el día.
        if not forzar and self.ultima_verificacion and not self.comprobacion_fallida():
            if datetime.now() - self.ultima_verificacion < timedelta(hours=24):
                if self.nueva_version_disponible:
                    return True, self.nueva_version_disponible
                return False, None

        # 1) API de GitHub (datos completos: notas, assets…)
        data = self._leer_release_api()
        if data is not None:
            return self._procesar_release(data)

        # 2) Canal sin límite estricto: la página /releases/latest redirige a
        #    la última versión. Solo necesitamos el número para avisar; la
        #    descarga del instalador se busca aparte.
        version = self._leer_version_por_redirect()
        if version is not None:
            if self._es_version_nueva(version):
                self.nueva_version_disponible = {
                    'version': version,
                    'nombre': version,
                    'descripcion': '',
                    'url': f"https://github.com/{self.GITHUB_USER}/{self.GITHUB_REPO}/releases/latest",
                    'download_url': None,
                    'fecha': '',
                }
                self._marcar_verificacion()
                logger.info(f"Nueva versión disponible (canal directo): {version}")
                return True, self.nueva_version_disponible
            self.nueva_version_disponible = None
            self._marcar_verificacion()
            logger.info("Ya tienes la última versión (canal directo)")
            return False, None

        # 3) Tags como último recurso
        info = self._verificar_por_tags()
        if info:
            return True, info

        # Nada ha funcionado: no marcar como verificado para poder reintentar
        logger.warning(
            "No se pudo comprobar la actualización (posible límite de peticiones "
            "de GitHub). Se volverá a intentar más tarde."
        )
        return False, None

    def comprobacion_fallida(self) -> bool:
        """Indica si la última comprobación no pudo realizarse.

        Permite a la interfaz avisar de que no es lo mismo «no hay
        actualizaciones» que «no se pudo comprobar».
        """
        return bool(getattr(self, "_ultima_comprobacion_fallida", False))

    def _marcar_verificacion(self):
        """Registra que la comprobación se hizo correctamente."""
        self._ultima_comprobacion_fallida = False
        self.ultima_verificacion = datetime.now()
        self._guardar_config()

    def _leer_release_api(self) -> Optional[Dict]:
        """Lee la última release desde la API de GitHub.

        Devuelve None si no se puede (por ejemplo, límite de peticiones), de
        modo que se pueda probar otro canal.
        """
        try:
            logger.info(f"Verificando actualizaciones desde: {self._api_latest}")
            headers = {'Accept': 'application/vnd.github.v3+json'}
            response = requests.get(self._api_latest, headers=headers, timeout=10)

            if response.status_code == 403 and 'rate limit' in response.text.lower():
                logger.warning("La API de GitHub ha limitado las peticiones por ahora")
                self._ultima_comprobacion_fallida = True
                return None
            if response.status_code == 404:
                logger.info("No hay ninguna release publicada todavía")
                return {}

            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"No se pudo consultar la API de GitHub: {e}")
            self._ultima_comprobacion_fallida = True
            return None

    def _leer_version_por_redirect(self) -> Optional[str]:
        """Obtiene la última versión siguiendo la redirección de /releases/latest.

        Este canal no depende de la API y funciona aunque se hayan agotado las
        peticiones: GitHub redirige a /releases/tag/vX.Y.Z y basta con leer el
        destino.
        """
        url = f"https://github.com/{self.GITHUB_USER}/{self.GITHUB_REPO}/releases/latest"
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            # La URL final termina en /releases/tag/v5.0.1
            final = response.url.rstrip('/')
            if '/releases/tag/' in final:
                etiqueta = final.split('/releases/tag/')[-1]
                version = etiqueta.lstrip('vV')
                if version and version[0].isdigit():
                    logger.info(f"Versión detectada por canal directo: {version}")
                    return version
            logger.debug(f"No se pudo leer la versión del canal directo ({final})")
        except Exception as e:
            logger.debug(f"Canal directo no disponible: {e}")
        return None

    def _procesar_release(self, data: Dict) -> Tuple[bool, Optional[Dict]]:
        """Interpreta la respuesta de la API y prepara la info de actualización."""
        version_remota = str(data.get('tag_name', '')).lstrip('vV')

        # Sin tag no hay nada que comparar
        if not version_remota:
            self._marcar_verificacion()
            self.nueva_version_disponible = None
            return False, None

        self._marcar_verificacion()

        if not self._es_version_nueva(version_remota):
            self.nueva_version_disponible = None
            logger.info("Ya tienes la última versión")
            return False, None

        # Instalador nativo del sistema, si está adjunto en la release
        assets = data.get('assets', []) or []
        instalador = self._asset_instalador_para_este_sistema(assets)

        # Si no hay instalador nativo, se conserva el zip como respaldo
        zip_url = None
        for asset in assets:
            if str(asset.get('name', '')).endswith('.zip'):
                zip_url = asset.get('browser_download_url')
                break
        if not zip_url:
            zip_url = data.get('zipball_url')

        self.nueva_version_disponible = {
            'version': version_remota,
            'nombre': data.get('name', ''),
            'descripcion': data.get('body', ''),
            'url': data.get('html_url', ''),
            'download_url': instalador or zip_url,
            'tiene_instalador': bool(instalador),
            'fecha': data.get('published_at', ''),
        }
        self._guardar_config()
        logger.info(f"Nueva versión disponible: {version_remota}")
        return True, self.nueva_version_disponible

    def _verificar_por_tags(self) -> Optional[Dict]:
        """Último recurso: mira el tag más reciente del repositorio.

        También usa la API, así que si está limitada se intenta la página web
        de tags, que no impone límite.
        """
        version_remota = None
        try:
            headers = {'Accept': 'application/vnd.github.v3+json'}
            response = requests.get(self._api_tags, headers=headers, timeout=10)
            if response.status_code == 200:
                tags = response.json()
                if tags:
                    version_remota = str(tags[0].get('name', '')).lstrip('vV')
        except Exception as e:
            logger.debug(f"API de tags no disponible: {e}")

        # Alternativa sin límite: leer la primera etiqueta de la página web
        if not version_remota:
            version_remota = self._leer_ultimo_tag_web()

        if not version_remota or not self._es_version_nueva(version_remota):
            return None

        self.nueva_version_disponible = {
            'version': version_remota,
            'nombre': version_remota,
            'descripcion': '',
            'url': f"https://github.com/{self.GITHUB_USER}/{self.GITHUB_REPO}/releases",
            'download_url': None,
            'fecha': '',
        }
        self._marcar_verificacion()
        logger.info(f"Nueva versión disponible (tag): {version_remota}")
        return self.nueva_version_disponible

    def _leer_ultimo_tag_web(self) -> Optional[str]:
        """Lee la última etiqueta desde la página de tags (sin usar la API)."""
        import re

        url = f"https://github.com/{self.GITHUB_USER}/{self.GITHUB_REPO}/tags"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return None
            coincidencias = re.findall(r"/releases/tag/v?([0-9]+(?:\.[0-9]+)+)", response.text)
            if not coincidencias:
                return None
            # La primera que aparezca es la más reciente
            return coincidencias[0]
        except Exception as e:
            logger.debug(f"No se pudo leer la página de tags: {e}")
            return None

    def _es_version_nueva(self, version_remota: str) -> bool:
        """Compara versiones semánticas rellenando con ceros las partes que falten."""
        try:
            local = tuple(map(int, self.VERSION_ACTUAL.split('.')))
            remota = tuple(map(int, version_remota.split('.')))
            longitud = max(len(local), len(remota))
            local += (0,) * (longitud - len(local))
            remota += (0,) * (longitud - len(remota))
            return remota > local
        except Exception:
            return False
    
    def _asset_instalador_para_este_sistema(self, assets: list) -> Optional[str]:
        """Devuelve el instalador nativo (exe/pkg/deb) para el sistema actual."""
        es_windows = sys.platform == "win32"
        es_mac = sys.platform == "darwin"
        es_linux = sys.platform.startswith("linux")

        candidatos = []
        for asset in assets:
            nombre = (asset.get("name") or "").lower()
            url = asset.get("browser_download_url")
            if not url:
                continue
            if es_windows and nombre.endswith(".exe"):
                candidatos.append(url)
            elif es_mac and nombre.endswith(".pkg"):
                candidatos.append(url)
            elif es_linux and nombre.endswith(".deb"):
                candidatos.append(url)
        return candidatos[0] if candidatos else None

    def _url_instalador_nombre(self, version: str) -> str:
        """URL directa del instalador de una versión (sin pasar por la API).

        Los releases de este proyecto publican siempre los nombres
        ``DescargasOrdenadas-Setup-vX.Y.Z.exe`` (Windows),
        ``DescargasOrdenadas-vX.Y.Z.pkg`` (macOS) y
        ``DescargasOrdenadas-vX.Y.Z-amd64.deb`` (Linux). Al construir la URL
        directamente se puede descargar aunque la API esté limitada.
        """
        base = f"https://github.com/{self.GITHUB_USER}/{self.GITHUB_REPO}/releases/download/v{version}"
        if sys.platform == "win32":
            return f"{base}/DescargasOrdenadas-Setup-v{version}.exe"
        if sys.platform == "darwin":
            return f"{base}/DescargasOrdenadas-v{version}.pkg"
        return f"{base}/DescargasOrdenadas-v{version}-amd64.deb"

    def _url_instalador_desde_api(self, version: str) -> Optional[str]:
        """Busca el instalador del sistema en la release (requiere API)."""
        try:
            headers = {'Accept': 'application/vnd.github.v3+json'}
            response = requests.get(self._api_latest, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            return self._asset_instalador_para_este_sistema(data.get("assets", []))
        except Exception as e:
            logger.warning(f"No se pudo leer la release por la API: {e}")
            return None

    def _url_instalador_existe(self, url: str) -> bool:
        """Comprueba con una petición ligera que el instalador está publicado."""
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def descargar_instalador_nativo(self, info: Dict, callback_progreso=None) -> Tuple[bool, str]:
        """Descarga el instalador del sistema (.exe/.pkg/.deb) para actualizar."""
        if not REQUESTS_DISPONIBLE:
            return False, "requests no disponible"

        version = str(info.get('version', '')).lstrip('vV')

        # Primero se intenta la URL que ya traiga la info (viene de la API)
        url_descarga = info.get('download_url') if info.get('tiene_instalador') else None

        # Si no, se construye directamente (no depende de la API)
        if not url_descarga and version:
            candidata = self._url_instalador_nombre(version)
            if self._url_instalador_existe(candidata):
                url_descarga = candidata

        # Como último recurso, se consulta la API (puede estar limitada)
        if not url_descarga:
            url_descarga = self._url_instalador_desde_api(version)

        if not url_descarga:
            # Sin instalador nativo: se usa el zip del código como respaldo
            logger.warning("No se encontró instalador nativo; se usará el zip del código")
            return self.descargar_actualizacion(info, callback_progreso)

        try:
            if getattr(sys, 'frozen', False):
                base_dir = Path(sys.executable).parent
            else:
                base_dir = Path(__file__).parent.parent
            temp_dir = base_dir / ".temp_update"
            temp_dir.mkdir(exist_ok=True)

            version = info.get('version', 'latest')
            extension = ".pkg" if sys.platform == "darwin" else (".deb" if sys.platform.startswith("linux") else ".exe")
            destino = temp_dir / f"DescargasOrdenadas-v{version}{extension}"

            logger.info(f"Descargando instalador desde: {url_descarga}")
            response = requests.get(url_descarga, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            with open(destino, 'wb') as f:
                for chunk in response.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if callback_progreso and total_size:
                            callback_progreso(int(downloaded * 100 / total_size))

            return True, str(destino)
        except Exception as e:
            logger.error(f"Error descargando instalador: {e}")
            return False, f"Error descargando: {e}"

    def abrir_instalador(self, ruta: str) -> Tuple[bool, str]:
        """Lanza el instalador descargado con el mecanismo de cada sistema."""
        ruta = Path(ruta)
        if not ruta.exists():
            return False, f"No existe: {ruta}"
        try:
            if sys.platform == "darwin":
                # Abrir el .pkg (el instalador de macOS pide permisos y instala)
                subprocess.Popen(["open", str(ruta)])
                return True, "Instalador abierto. Sigue los pasos y vuelve a abrir la app."
            if sys.platform == "win32":
                os.startfile(str(ruta))  # type: ignore[attr-defined]
                return True, "Instalador abierto. Sigue los pasos del asistente."
            # Linux
            subprocess.Popen(["xdg-open", str(ruta.parent)])
            return True, f"Instalador en: {ruta}. Instálalo con: sudo apt install {ruta}"
        except Exception as e:
            return False, f"No se pudo abrir el instalador: {e}"

    # ------------------------------------------------------- actualización

    def _comando_reabrir(self, minimizado: bool = True) -> list:
        """Comando para volver a abrir la app (tras instalar la nueva versión)."""
        argumentos = ["--minimizado"] if minimizado else []
        if getattr(sys, "frozen", False):
            return [sys.executable, *argumentos]
        iniciar_py = Path(__file__).resolve().parent / "INICIAR.py"
        return [sys.executable, str(iniciar_py), *argumentos]

    def _script_actualizacion_windows(self, ruta_instalador: Path) -> Path:
        """Genera un .bat que espera el cierre, instala en silencio y reabre la app.

        Windows no permite reemplazar un .exe en uso, así que el único orden
        fiable es: cerrar → instalar encima → reabrir. El script se ejecuta
        desacoplado de la app para sobrevivir a su cierre.
        """
        base_dir = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent.parent
        script = base_dir / ".temp_actualizar.bat"
        log = base_dir / ".temp_actualizar.log"

        lineas = [
            "@echo off",
            "rem DescargasOrdenadas: actualiza sin dejar dos copias abiertas",
            "setlocal",
            f'set "INSTALADOR={ruta_instalador}"',
            f'set "LOG={log}"',
            "rem Esperar a que la aplicación termine (máximo 60 s)",
            "for /L %%i in (1,1,60) do (",
            '  tasklist /FI "IMAGENAME eq DescargasOrdenadas.exe" | find /I "DescargasOrdenadas.exe" >nul',
            "  if errorlevel 1 goto instalar",
            "  timeout /t 1 /nobreak >nul",
            ")",
            ":instalar",
            'echo [%date% %time%] Lanzando instalador >> "%LOG%"',
            f'"%INSTALADOR%" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS >> "%LOG%" 2>&1',
            'echo [%date% %time%] Instalador terminado >> "%LOG%"',
            "rem Reabrir la aplicación actualizada",
            'start "" "%ProgramFiles%\\DescargasOrdenadas\\DescargasOrdenadas.exe" --minimizado',
            'del "%~f0"',
            "endlocal",
        ]
        script.write_text("\r\n".join(lineas) + "\r\n", encoding="latin-1", errors="replace")
        return script

    def _script_actualizacion_unix(self, ruta_instalador: Path) -> Path:
        """Script para macOS/Linux: espera el cierre, instala y reabre.

        En macOS, el .pkg se instala con ``installer -pkg`` sobre /Applications;
        en Linux, el .deb se instala con el gestor del sistema pidiendo permisos
        de forma explícita (pkexec o sudo en una terminal).
        """
        base_dir = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent.parent
        script = base_dir / ".temp_actualizar.sh"
        log = base_dir / ".temp_actualizar.log"
        reabrir = " ".join(f'"{parte}"' for parte in self._comando_reabrir())

        if sys.platform == "darwin":
            instalacion = (
                f'installer -pkg "{ruta_instalador}" -target / >>"{log}" 2>&1'
            )
        else:
            instalacion = (
                f'if command -v pkexec >/dev/null 2>&1; then '
                f'pkexec apt-get install -y "{ruta_instalador}" >>"{log}" 2>&1; '
                f'else xdg-terminal-exec sudo apt-get install -y "{ruta_instalador}" >>"{log}" 2>&1; fi'
            )

        cuerpo = chr(10).join([
            "#!/usr/bin/env bash",
            "# DescargasOrdenadas: actualiza sin dejar dos copias abiertas",
            f'LOG="{log}"',
            'echo "[$(date)] Esperando a que la aplicación se cierre" >>"$LOG"',
            "for _ in $(seq 1 60); do",
            "  if ! pgrep -f DescargasOrdenadas >/dev/null 2>&1; then break; fi",
            "  sleep 1",
            "done",
            'echo "[$(date)] Instalando la nueva versión" >>"$LOG"',
            instalacion,
            'echo "[$(date)] Instalación terminada; reabriendo" >>"$LOG"',
            f"nohup {reabrir} >/dev/null 2>&1 &",
            'rm -f -- "$0"',
            "",
        ])
        script.write_text(cuerpo, encoding="utf-8")
        script.chmod(0o755)
        return script

    def actualizar_e_instalar(self, ruta_instalador: str, cerrar_app=None) -> Tuple[bool, str]:
        """Actualiza de forma segura: cierra la app, instala encima y reabre.

        Args:
            ruta_instalador: ruta del .exe/.pkg/.deb descargado.
            cerrar_app: función opcional que cierra la aplicación actual de
                forma ordenada (la GUI pasa la suya). Si no se indica, se usa
                ``sys.exit``.

        Returns:
            (exito, mensaje) con instrucciones claras para el usuario.
        """
        ruta = Path(ruta_instalador)
        if not ruta.exists():
            return False, f"No se encuentra el instalador descargado: {ruta}"

        if getattr(sys, "frozen", False) is False and sys.platform != "darwin":
            # En modo desarrollo no tiene sentido reemplazar la instalación
            pass

        try:
            if sys.platform == "win32":
                if ruta.suffix.lower() != ".exe":
                    return False, f"El instalador de Windows debe ser .exe y es: {ruta.name}"
                script = self._script_actualizacion_windows(ruta)
                subprocess.Popen(
                    ["cmd", "/c", str(script)],
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    close_fds=True,
                )
            else:
                if not ruta.name.endswith((".pkg", ".deb")):
                    return False, f"El instalador de este sistema debe ser .pkg o .deb y es: {ruta.name}"
                script = self._script_actualizacion_unix(ruta)
                subprocess.Popen(
                    ["/bin/bash", str(script)],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
        except Exception as e:
            logger.error(f"No se pudo preparar la actualización: {e}")
            return False, f"No se pudo preparar la actualización: {e}"

        # Cerrar la aplicación para que el instalador no encuentre archivos en uso
        QTimer_salida = None
        try:
            from PySide6.QtCore import QTimer as _QTimer

            QTimer_salida = _QTimer
        except Exception:
            pass

        def _cerrar():
            if cerrar_app is not None:
                try:
                    cerrar_app()
                    return
                except Exception as e:
                    logger.debug(f"El cierre ordenado falló: {e}")
            sys.exit(0)

        if QTimer_salida is not None:
            # Pequeña espera para que el mensaje se pueda leer y el script arranque
            QTimer_salida.singleShot(1200, _cerrar)
        else:
            _cerrar()

        return True, (
            "La aplicación se cerrará, el instalador se ejecutará en segundo plano "
            "y volverá a abrirse automáticamente al terminar."
        )

    def descargar_actualizacion(self, info: Dict, callback_progreso=None) -> Tuple[bool, str]:
        """
        Descarga la actualización desde GitHub.
        
        Args:
            info: Diccionario con información de la actualización
            callback_progreso: Función para reportar progreso (porcentaje)
        
        Returns:
            (exito, mensaje/ruta_archivo)
        """
        if not REQUESTS_DISPONIBLE:
            return False, "requests no disponible"
        
        download_url = info.get('download_url')
        if not download_url:
            return False, "URL de descarga no disponible"
        
        try:
            # Crear carpeta temporal
            if getattr(sys, 'frozen', False):
                base_dir = Path(sys.executable).parent
            else:
                base_dir = Path(__file__).parent.parent
            
            temp_dir = base_dir / ".temp_update"
            temp_dir.mkdir(exist_ok=True)
            
            # Nombre del archivo
            version = info.get('version', 'latest')
            zip_path = temp_dir / f"DescargasOrdenadas_v{version}.zip"
            
            logger.info(f"Descargando desde: {download_url}")
            
            # Descargar con progreso
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if callback_progreso and total_size > 0:
                            porcentaje = int((downloaded / total_size) * 100)
                            callback_progreso(porcentaje)
            
            logger.info(f"✅ Descarga completada: {zip_path}")
            return True, str(zip_path)
            
        except Exception as e:
            logger.error(f"Error descargando actualización: {e}")
            return False, f"Error: {e}"
    
    def instalar_actualizacion(self, zip_path: str) -> Tuple[bool, str]:
        """
        Descomprime e instala la actualización.
        
        Args:
            zip_path: Ruta al archivo .zip descargado
        
        Returns:
            (exito, mensaje)
        """
        try:
            zip_path = Path(zip_path)
            
            if not zip_path.exists():
                return False, f"Archivo no encontrado: {zip_path}"
            
            # Obtener directorio base
            if getattr(sys, 'frozen', False):
                base_dir = Path(sys.executable).parent
            else:
                base_dir = Path(__file__).parent.parent
            
            # Crear backup del proyecto actual
            backup_dir = base_dir.parent / f"DescargasOrdenadas_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"Creando backup en: {backup_dir}")
            
            try:
                shutil.copytree(base_dir, backup_dir, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git'))
            except Exception as e:
                logger.warning(f"Error creando backup: {e}")
            
            # Descomprimir actualización
            temp_extract = base_dir / ".temp_extract"
            temp_extract.mkdir(exist_ok=True)
            
            logger.info(f"Descomprimiendo: {zip_path}")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract)
            
            # Buscar la carpeta del proyecto dentro del zip
            # (GitHub zipball crea una carpeta con el nombre del repo)
            extracted_folders = [f for f in temp_extract.iterdir() if f.is_dir()]
            
            if not extracted_folders:
                return False, "No se encontró contenido en el archivo ZIP"
            
            source_folder = extracted_folders[0]
            
            # Copiar archivos al proyecto actual (excluyendo .config)
            logger.info(f"Copiando archivos desde: {source_folder}")
            
            archivos_copiados = 0
            for item in source_folder.rglob('*'):
                if item.is_file():
                    # Excluir ciertos archivos/carpetas
                    relative_path = item.relative_to(source_folder)
                    
                    if any(part.startswith('.') for part in relative_path.parts):
                        continue  # Skip archivos/carpetas ocultas
                    
                    if '.config' in relative_path.parts:
                        continue  # Preservar configuración
                    
                    # Copiar archivo
                    dest_path = base_dir / relative_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    shutil.copy2(item, dest_path)
                    archivos_copiados += 1
            
            # Limpiar archivos temporales
            shutil.rmtree(temp_extract, ignore_errors=True)
            zip_path.unlink(missing_ok=True)
            
            logger.info(f"✅ Actualización instalada: {archivos_copiados} archivos")
            
            return True, f"Actualización instalada correctamente\n\n" \
                        f"📁 Archivos actualizados: {archivos_copiados}\n" \
                        f"💾 Backup creado en: {backup_dir.name}\n\n" \
                        f"⚠️ IMPORTANTE: Reinicia la aplicación para aplicar los cambios"
            
        except Exception as e:
            logger.error(f"Error instalando actualización: {e}")
            return False, f"Error durante la instalación: {e}"
    
    def obtener_version_actual(self) -> str:
        """Obtiene la versión actual."""
        return self.VERSION_ACTUAL
    
    def obtener_info_actualizacion(self) -> Optional[Dict]:
        """Obtiene información de actualización disponible."""
        return self.nueva_version_disponible
    
    def reiniciar_aplicacion(self):
        """Reinicia la aplicación después de actualizar."""
        try:
            if sys.platform == "win32":
                # Las constantes DETACHED_PROCESS/CREATE_* solo existen en Windows
                if getattr(sys, 'frozen', False):
                    exe_path = sys.executable
                    subprocess.Popen([exe_path], creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
                else:
                    base_dir = Path(__file__).parent.parent
                    iniciar_bat = base_dir / "INICIAR.bat"

                    if iniciar_bat.exists():
                        temp_script = base_dir / ".temp_restart.bat"
                        with open(temp_script, 'w') as f:
                            f.write('@echo off\n')
                            f.write('timeout /t 2 /nobreak >nul\n')
                            f.write(f'cd /d "{base_dir}"\n')
                            f.write('start "" "INICIAR.bat"\n')
                            f.write('del "%~f0"\n')

                        subprocess.Popen([str(temp_script)], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    else:
                        # Fallback multiplataforma: relanzar con el mismo Python
                        iniciar_py = Path(__file__).parent / "INICIAR.py"
                        subprocess.Popen(
                            [sys.executable, str(iniciar_py), "--minimizado"],
                            stdin=subprocess.DEVNULL,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
            else:
                # macOS/Linux: start_new_session desvincula el proceso hijo
                # de la sesión actual para que sobreviva al cierre de la app
                if getattr(sys, 'frozen', False):
                    comando = [sys.executable, "--minimizado"]
                else:
                    iniciar_py = Path(__file__).parent / "INICIAR.py"
                    comando = [sys.executable, str(iniciar_py), "--minimizado"]

                subprocess.Popen(
                    comando,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            
            # Salir de la aplicación actual
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"Error reiniciando aplicación: {e}")
            return False
    
    def abrir_pagina_descarga(self):
        """Abre la página de descarga en el navegador."""
        if self.nueva_version_disponible:
            url = self.nueva_version_disponible.get('url')
            if url:
                try:
                    import webbrowser
                    webbrowser.open(url)
                    return True
                except Exception as e:
                    logger.error(f"Error abriendo navegador: {e}")
        return False

# Instancia global
_gestor_actualizaciones_global = None

def obtener_gestor_actualizaciones():
    """Obtiene la instancia global del gestor de actualizaciones."""
    global _gestor_actualizaciones_global
    if _gestor_actualizaciones_global is None:
        _gestor_actualizaciones_global = GestorActualizacionesMejorado()
    return _gestor_actualizaciones_global
