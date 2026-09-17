#!/usr/bin/env bash
# DescargasOrdenadas - Instalador de dependencias para macOS y Linux
set -e

cd "$(dirname "$0")"

echo "🍄 DescargasOrdenadas - Instalando dependencias"
echo "================================================"
echo

# Comprobar Python 3
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python 3 no está instalado."
    echo "   • macOS:  brew install python  (o descarga desde https://python.org)"
    echo "   • Linux:  sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python detectado: $PYTHON_VERSION"
echo

# Crear entorno virtual (evita el Python 'externally-managed' de macOS/Homebrew)
if [ ! -d ".venv" ]; then
    echo "📦 Creando entorno virtual en .venv ..."
    python3 -m venv .venv
fi

# Activar entorno virtual
if [ -f ".venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    # shellcheck disable=SC1091
    source .venv/Scripts/activate
fi

echo "⬇️  Instalando dependencias ..."
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

echo
echo "✅ Dependencias instaladas correctamente."
echo "🚀 Ejecuta la aplicación con: ./INICIAR.sh"
