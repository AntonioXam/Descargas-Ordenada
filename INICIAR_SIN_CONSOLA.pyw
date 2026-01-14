#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🍄 DescargasOrdenadas v3.1 - Launcher Sin Consola
Este archivo .pyw inicia la aplicación sin ventana de consola
"""

import sys
import os
from pathlib import Path

# Asegurar que el directorio del script está en el path
script_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(script_dir))

# Importar y ejecutar el programa principal
from INICIAR import main

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # En caso de error, escribirlo a un archivo de log
        log_file = script_dir / "error_sin_consola.log"
        with open(log_file, 'w', encoding='utf-8') as f:
            import traceback
            f.write(f"Error al iniciar DescargasOrdenadas:\n")
            f.write(f"{e}\n\n")
            f.write(traceback.format_exc())
        sys.exit(1)
