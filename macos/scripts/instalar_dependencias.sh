#!/bin/bash

echo "🍄 DescargasOrdenadas v3.0 - Instalación de Dependencias"
echo "======================================================"

# Detectar el sistema operativo
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
    PYTHON_CMD="python3"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
    PYTHON_CMD="python3"
else
    OS="Desconocido"
    PYTHON_CMD="python"
fi

echo "🖥️  Sistema detectado: $OS"

# Verificar Python
echo "🔍 Verificando Python..."

if ! command -v $PYTHON_CMD &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python no está instalado"
        echo ""
        echo "💡 Para instalar Python:"
        
        if [[ "$OS" == "macOS" ]]; then
            echo "   Opción 1: brew install python"
            echo "   Opción 2: Descargar desde https://python.org"
        elif [[ "$OS" == "Linux" ]]; then
            echo "   Ubuntu/Debian: sudo apt install python3 python3-pip"
            echo "   Fedora/RHEL: sudo dnf install python3 python3-pip"
            echo "   Arch Linux: sudo pacman -S python python-pip"
        else
            echo "   Descargar desde https://python.org"
        fi
        
        echo ""
        exit 1
    else
        PYTHON_CMD="python"
    fi
fi

$PYTHON_CMD --version
echo "✅ Python encontrado"

# Verificar pip
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "❌ pip no está disponible"
    echo "💡 Instala pip para continuar"
    exit 1
fi

echo ""
echo "📦 Instalando dependencias necesarias..."

echo "🔧 Instalando Pillow (procesamiento de imágenes)..."
$PYTHON_CMD -m pip install pillow

echo "🖥️  Instalando PySide6 (interfaz gráfica)..."
$PYTHON_CMD -m pip install PySide6

echo ""
echo "🧪 Verificando instalación..."

# Verificar Pillow
if $PYTHON_CMD -c "import PIL; print('✅ Pillow:', PIL.__version__)" 2>/dev/null; then
    echo "Pillow instalado correctamente"
else
    echo "❌ Error con Pillow"
fi

# Verificar PySide6
if $PYTHON_CMD -c "import PySide6; print('✅ PySide6 instalado correctamente')" 2>/dev/null; then
    echo "PySide6 instalado correctamente"
else
    echo "❌ Error con PySide6"
fi

echo ""
echo "🎉 ¡Instalación de dependencias completada!"

if [[ "$OS" == "macOS" ]]; then
    echo "🚀 Ahora puedes ejecutar: ./DescargasOrdenadas.command"
else
    echo "🚀 Ahora puedes ejecutar: ./DescargasOrdenadas.sh"
fi

echo ""
read -p "Presiona Enter para continuar..." 