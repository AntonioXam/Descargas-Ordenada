#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crea un acceso directo (.lnk) de DescargasOrdenadas para anclar a la barra de tareas.
"""

import sys
import os
from pathlib import Path
import subprocess

try:
    import win32com.client
except ImportError:
    print("❌ Se requiere pywin32. Instálalo con: pip install pywin32")
    sys.exit(1)


def crear_acceso_directo_appid(ruta_destino: Path, nombre: str) -> Path:
    """Crea un acceso directo .lnk que apunta a pythonw ejecutando el script principal."""
    project_dir = Path(__file__).parent.parent.resolve()
    script_path = project_dir / "organizer" / "INICIAR.py"
    ico_path = project_dir / "resources" / "icon.ico"
    if not ico_path.exists():
        ico_path = project_dir / "resources" / "icon.png"

    if not script_path.exists():
        print(f"❌ No se encontró {script_path}")
        sys.exit(1)

    # Buscar pythonw3 (sin consola) o python3 del sistema donde están las dependencias
    python_exe = None
    for candidato in ["pythonw3", "pythonw", "python3"]:
        try:
            result = subprocess.run(
                ["where", candidato],
                capture_output=True, text=True, check=True
            )
            for line in result.stdout.strip().splitlines():
                if "Microsoft\\WindowsApps" in line or "hermes" in line:
                    continue
                p = Path(line.strip())
                if p.exists():
                    python_exe = p
                    break
            if python_exe:
                break
        except Exception:
            continue

    if not python_exe:
        print("❌ No se encontró un pythonw/python3 adecuado")
        sys.exit(1)

    ruta_destino.mkdir(parents=True, exist_ok=True)
    lnk_path = ruta_destino / f"{nombre}.lnk"

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(str(lnk_path))
    shortcut.TargetPath = str(python_exe)
    shortcut.Arguments = f'"{script_path}" --gui'
    shortcut.WorkingDirectory = str(project_dir)
    shortcut.Description = "DescargasOrdenadas v3.2 - Organizador automático de descargas"
    shortcut.IconLocation = str(ico_path)
    shortcut.save()

    return lnk_path


def main():
    escritorio = Path.home() / "Desktop"
    menu_inicio = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"

    print("🍄 Creando accesos directos de DescargasOrdenadas...")

    lnk_escritorio = crear_acceso_directo_appid(escritorio, "DescargasOrdenadas")
    print(f"✅ Escritorio: {lnk_escritorio}")

    lnk_menu = crear_acceso_directo_appid(menu_inicio, "DescargasOrdenadas")
    print(f"✅ Menú Inicio: {lnk_menu}")

    print("\n📌 Para anclar a la barra de tareas:")
    print("   1. Haz clic derecho sobre el acceso directo del Escritorio")
    print("   2. Selecciona 'Anclar a la barra de tareas'")
    print("\n🚀 También puedes arrastrar el acceso directo directamente a la barra de tareas.")


if __name__ == "__main__":
    main()
