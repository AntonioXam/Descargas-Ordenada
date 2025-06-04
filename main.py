#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import subprocess
import importlib.util

def check_dependencies():
    """Verifica e instala dependencias automáticamente si es necesario."""
    try:
        import PySide6
        import requests
    except ImportError:
        try:
            print("Instalando dependencias necesarias...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PySide6", "requests"])
            print("Dependencias instaladas correctamente.")
            # Reimportar después de instalar
            import PySide6
            import requests
        except Exception as e:
            from tkinter import messagebox
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Error de Instalación", 
                f"No se pudieron instalar las dependencias requeridas: {str(e)}\n"
                "Por favor, instale manualmente 'PySide6' y 'requests' con pip."
            )
            sys.exit(1)

if __name__ == "__main__":
    check_dependencies()
    
    # Importar después de verificar dependencias
    from organizer.gui import run_app
    run_app() 