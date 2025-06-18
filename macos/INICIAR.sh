#!/bin/bash

# ===================================================================
# DescargasOrdenadas v3.0 - Launcher Principal macOS
# NO REQUIERE PYTHON PREINSTALADO - Lo instala automáticamente
# Creado por Champi 🍄
# ===================================================================

# Configurar UTF-8
export LANG=es_ES.UTF-8
export LC_ALL=es_ES.UTF-8

# Obtener directorio del proyecto (carpeta padre)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CURRENT_DIR="$(pwd)"
cd "$PROJECT_DIR"

echo ""
echo "🍄 DescargasOrdenadas v3.0 - macOS"
echo "================================="
echo "💡 Launcher que NO requiere Python preinstalado"
echo "⚡ Detectará e instalará todo automáticamente"
echo ""

echo "📁 Proyecto: $PROJECT_DIR"
echo ""

# Función para verificar si Python está disponible
verificar_python() {
    if command -v python3 &> /dev/null; then
        echo "✅ Python3 encontrado: $(python3 --version)"
        return 0
    elif command -v python &> /dev/null; then
        echo "✅ Python encontrado: $(python --version)"
        return 0
    else
        return 1
    fi
}

# Función para instalar Python con Homebrew
instalar_con_homebrew() {
    echo "🍺 Intentando instalar Python con Homebrew..."
    
    # Verificar si Homebrew está instalado
    if ! command -v brew &> /dev/null; then
        echo "📥 Instalando Homebrew primero..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Agregar Homebrew al PATH
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [[ -f "/usr/local/bin/brew" ]]; then
            echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.bash_profile
            eval "$(/usr/local/bin/brew shellenv)"
        fi
    fi
    
    # Instalar Python
    echo "📦 Instalando Python..."
    brew install python
    
    if [ $? -eq 0 ]; then
        echo "✅ Python instalado exitosamente con Homebrew"
        return 0
    else
        echo "❌ Error al instalar Python con Homebrew"
        return 1
    fi
}

# Función para descargar e instalar Python manualmente
instalar_manual() {
    echo "📥 Descargando Python desde python.org..."
    
    # Detectar arquitectura
    ARCH=$(uname -m)
    if [[ "$ARCH" == "arm64" ]]; then
        PYTHON_URL="https://www.python.org/ftp/python/3.11.6/python-3.11.6-macos11.pkg"
        echo "🖥️  Detectado: Apple Silicon (M1/M2)"
    else
        PYTHON_URL="https://www.python.org/ftp/python/3.11.6/python-3.11.6-macosx10.9.pkg"
        echo "🖥️  Detectado: Intel Mac"
    fi
    
    TEMP_DIR="/tmp/DescargasOrdenadas_Setup"
    mkdir -p "$TEMP_DIR"
    PYTHON_INSTALLER="$TEMP_DIR/python_installer.pkg"
    
    # Descargar instalador
    curl -L "$PYTHON_URL" -o "$PYTHON_INSTALLER"
    
    if [ $? -eq 0 ]; then
        echo "✅ Descarga completada"
        echo "🔧 Instalando Python (se abrirá el instalador)..."
        echo ""
        echo "⚠️  Se abrirá el instalador gráfico. Sigue las instrucciones."
        echo ""
        read -p "Presiona Enter para continuar..."
        
        # Instalar paquete
        sudo installer -pkg "$PYTHON_INSTALLER" -target /
        
        if [ $? -eq 0 ]; then
            echo "✅ Python instalado exitosamente"
            # Actualizar PATH
            export PATH="/Library/Frameworks/Python.framework/Versions/3.11/bin:$PATH"
            return 0
        else
            echo "❌ Error durante la instalación"
            return 1
        fi
    else
        echo "❌ Error al descargar Python"
        return 1
    fi
}

# Función para mostrar instrucciones manuales
mostrar_instrucciones() {
    echo ""
    echo "📖 INSTRUCCIONES MANUALES - Instalación de Python"
    echo "================================================"
    echo ""
    echo "OPCIÓN 1 - Homebrew (Recomendado para desarrolladores):"
    echo "1. Instala Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo "2. Instala Python: brew install python"
    echo ""
    echo "OPCIÓN 2 - Instalador oficial:"
    echo "1. Ve a: https://python.org/downloads/"
    echo "2. Descarga 'Python 3.11 o superior para macOS'"
    echo "3. Ejecuta el archivo .pkg descargado"
    echo "4. Sigue las instrucciones del instalador"
    echo ""
    echo "OPCIÓN 3 - Xcode Command Line Tools:"
    echo "1. Ejecuta: xcode-select --install"
    echo "2. Esto instalará Python básico del sistema"
    echo ""
    read -p "Presiona Enter para cerrar..." || true
}

# Verificar Python
echo "🔍 Verificando Python..."
if verificar_python; then
    # Python ya está disponible
    python_cmd=""
    if command -v python3 &> /dev/null; then
        python_cmd="python3"
    else
        python_cmd="python"
    fi
    
    echo "🚀 Iniciando DescargasOrdenadas..."
    echo "================================"
    echo ""
    
    # Ejecutar la aplicación principal
    $python_cmd main.py "$@"
    exit_code=$?
    
    cd "$CURRENT_DIR"
    
    if [ $exit_code -eq 0 ]; then
        echo "✅ Aplicación ejecutada exitosamente"
    else
        echo "❌ La aplicación terminó con errores (Código: $exit_code)"
        
        # Solo hacer pausa si no es ejecución silenciosa
        if [[ "$*" != *"--tarea-programada"* ]] && [[ "$*" != *"--inicio-sistema"* ]]; then
            read -p "Presiona Enter para cerrar..." || true
        fi
    fi
    
    exit $exit_code
fi

# Python no encontrado - ofrecer instalación
echo "❌ Python no está instalado en este sistema"
echo ""
echo "🤖 ¿Cómo quieres instalarlo?"
echo ""
echo "1. Automático con Homebrew (recomendado)"
echo "2. Descargar instalador oficial"
echo "3. Mostrar instrucciones manuales"
echo "4. Salir"
echo ""
read -p "Selecciona una opción (1-4): " opcion

case $opcion in
    1)
        echo ""
        if instalar_con_homebrew; then
            echo "🔄 Verificando instalación..."
            if verificar_python; then
                echo "✅ ¡Listo! Ejecutando aplicación..."
                echo ""
                
                python_cmd=""
                if command -v python3 &> /dev/null; then
                    python_cmd="python3"
                else
                    python_cmd="python"
                fi
                
                $python_cmd main.py "$@"
                exit $?
            else
                echo "❌ Python instalado pero no disponible"
                echo "💡 Reinicia la terminal y ejecuta este script nuevamente"
            fi
        else
            mostrar_instrucciones
        fi
        ;;
        
    2)
        echo ""
        if instalar_manual; then
            echo "🔄 Verificando instalación..."
            if verificar_python; then
                echo "✅ ¡Listo! Ejecutando aplicación..."
                echo ""
                
                python_cmd=""
                if command -v python3 &> /dev/null; then
                    python_cmd="python3"
                else
                    python_cmd="python"
                fi
                
                $python_cmd main.py "$@"
                exit $?
            else
                echo "❌ Python instalado pero no disponible"
                echo "💡 Reinicia la terminal y ejecuta este script nuevamente"
            fi
        else
            mostrar_instrucciones
        fi
        ;;
        
    3)
        mostrar_instrucciones
        ;;
        
    4)
        echo ""
        echo "👋 ¡Hasta luego!"
        cd "$CURRENT_DIR"
        exit 1
        ;;
        
    *)
        echo "❌ Opción inválida"
        mostrar_instrucciones
        ;;
esac

cd "$CURRENT_DIR"
exit 1 