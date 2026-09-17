#!/usr/bin/env bash
# DescargasOrdenadas - Lanzador para macOS y Linux
set -e

cd "$(dirname "$0")"

# Usar el entorno virtual del proyecto si existe
if [ -f ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
elif [ -f ".venv/Scripts/python.exe" ]; then
    PYTHON=".venv/Scripts/python.exe"
else
    PYTHON="python3"
fi

if ! command -v "$PYTHON" >/dev/null 2>&1 && [ ! -x "$PYTHON" ]; then
    echo "❌ Python no encontrado. Ejecuta primero: ./INSTALAR_DEPENDENCIAS.sh"
    exit 1
fi

exec "$PYTHON" organizer/INICIAR.py "$@"
