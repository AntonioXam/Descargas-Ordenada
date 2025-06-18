#!/bin/bash

# ===================================================================
# DescargasOrdenadas v3.0 - Launcher Portable para macOS
# Creado por Champi 🍄
# ===================================================================

# Configurar UTF-8
export LANG=es_ES.UTF-8
export LC_ALL=es_ES.UTF-8

# Obtener el directorio donde está este script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_DIR="$(pwd)"

# Cambiar al directorio del script para asegurar rutas relativas
cd "$SCRIPT_DIR"

echo ""
echo "🍄 DescargasOrdenadas v3.0 - Portable para macOS"
echo "==============================================="
echo ""

echo "📁 Directorio de la aplicación: $SCRIPT_DIR"
echo ""

# Verificar si Python está disponible
echo "🔍 Verificando Python..."

if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python no está instalado"
    echo ""
    echo "💡 Para continuar necesitas instalar Python:"
    echo "   Opción 1: brew install python (recomendado)"
    echo "   Opción 2: Descargar desde https://python.org/downloads/"
    echo "   Opción 3: Instalar Xcode Command Line Tools"
    echo ""
    echo "📁 Esta es una versión portable que requiere Python instalado"
    echo ""
    read -p "Presiona Enter para cerrar..." || true
    cd "$CURRENT_DIR"
    exit 1
fi

# Usar python3 si está disponible, sino python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

$PYTHON_CMD --version
echo "✅ Python encontrado ($PYTHON_CMD)"
echo ""

# Verificar si pip está disponible
echo "🔍 Verificando pip..."
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "❌ pip no está disponible"
    echo "💡 Instala pip para continuar:"
    echo "   brew install python (si usas Homebrew)"
    echo "   O reinstala Python desde python.org"
    echo ""
    read -p "Presiona Enter para cerrar..." || true
    cd "$CURRENT_DIR"
    exit 1
fi

echo "✅ pip encontrado"
echo ""

# Verificar e instalar dependencias automáticamente
echo "🔧 Verificando dependencias..."
echo "⏳ Si faltan dependencias, se instalarán automáticamente..."
echo ""

# Ejecutar la aplicación - main.py manejará la instalación de dependencias
echo "🚀 Iniciando DescargasOrdenadas..."
echo ""
$PYTHON_CMD ../main.py "$@"

# Capturar el código de salida
EXIT_CODE=$?

# Restaurar directorio original
cd "$CURRENT_DIR"

# Si hubo error y no es una ejecución en modo silencioso, mantener terminal abierto
if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "❌ La aplicación terminó con errores (Código: $EXIT_CODE)"
    
    # Solo hacer pausa si no es una tarea programada o inicio automático
    if [[ "$*" != *"--tarea-programada"* ]] && [[ "$*" != *"--inicio-sistema"* ]]; then
        echo ""
        read -p "Presiona Enter para cerrar..." || true
    fi
fi

exit $EXIT_CODE 