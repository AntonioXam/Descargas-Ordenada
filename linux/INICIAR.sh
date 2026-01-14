#!/bin/bash

# ===================================================================
# DescargasOrdenadas v3.0 - Launcher Principal Linux
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
echo "🍄 DescargasOrdenadas v3.0 - Linux"
echo "================================="
echo "💡 Launcher que NO requiere Python preinstalado"
echo "⚡ Detectará e instalará todo automáticamente"
echo ""

echo "📁 Proyecto: $PROJECT_DIR"
echo ""

# Función para detectar distribución
detectar_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        echo "$DISTRIB_ID" | tr '[:upper:]' '[:lower:]'
    else
        echo "unknown"
    fi
}

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

# Función para instalar Python automáticamente
instalar_python_auto() {
    DISTRO=$(detectar_distro)
    echo "🐧 Detectado: $DISTRO"
    echo "📦 Instalando Python automáticamente..."
    
    case $DISTRO in
        ubuntu|debian|mint|elementary|zorin|pop)
            echo "🔧 Usando apt (Debian/Ubuntu)..."
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv python3-tk
            ;;
            
        fedora|centos|rhel|rocky|alma)
            echo "🔧 Usando dnf/yum (RedHat/Fedora)..."
            if command -v dnf &> /dev/null; then
                sudo dnf install -y python3 python3-pip python3-tkinter
            else
                sudo yum install -y python3 python3-pip tkinter
            fi
            ;;
            
        arch|manjaro|endeavour)
            echo "🔧 Usando pacman (Arch)..."
            sudo pacman -S --noconfirm python python-pip tk
            ;;
            
        opensuse*|suse)
            echo "🔧 Usando zypper (openSUSE)..."
            sudo zypper install -y python3 python3-pip python3-tk
            ;;
            
        alpine)
            echo "🔧 Usando apk (Alpine)..."
            sudo apk add python3 py3-pip tk
            ;;
            
        gentoo)
            echo "🔧 Usando emerge (Gentoo)..."
            sudo emerge dev-lang/python dev-python/pip dev-lang/tk
            ;;
            
        *)
            echo "❌ Distribución no reconocida: $DISTRO"
            return 1
            ;;
    esac
    
    # Verificar instalación
    if verificar_python; then
        echo "✅ Python instalado exitosamente"
        return 0
    else
        echo "❌ Error al instalar Python"
        return 1
    fi
}

# Función para mostrar instrucciones manuales
mostrar_instrucciones() {
    DISTRO=$(detectar_distro)
    
    echo ""
    echo "📖 INSTRUCCIONES MANUALES - Instalación de Python"
    echo "================================================"
    echo ""
    
    case $DISTRO in
        ubuntu|debian|mint|elementary|zorin|pop)
            echo "🐧 Para $DISTRO (Debian/Ubuntu):"
            echo "sudo apt update"
            echo "sudo apt install python3 python3-pip python3-venv python3-tk"
            ;;
            
        fedora|centos|rhel|rocky|alma)
            echo "🐧 Para $DISTRO (RedHat/Fedora):"
            if command -v dnf &> /dev/null; then
                echo "sudo dnf install python3 python3-pip python3-tkinter"
            else
                echo "sudo yum install python3 python3-pip tkinter"
            fi
            ;;
            
        arch|manjaro|endeavour)
            echo "🐧 Para $DISTRO (Arch):"
            echo "sudo pacman -S python python-pip tk"
            ;;
            
        opensuse*|suse)
            echo "🐧 Para $DISTRO (openSUSE):"
            echo "sudo zypper install python3 python3-pip python3-tk"
            ;;
            
        alpine)
            echo "🐧 Para $DISTRO (Alpine):"
            echo "sudo apk add python3 py3-pip tk"
            ;;
            
        gentoo)
            echo "🐧 Para $DISTRO (Gentoo):"
            echo "sudo emerge dev-lang/python dev-python/pip dev-lang/tk"
            ;;
            
        *)
            echo "🐧 Para distribuciones genéricas:"
            echo "- Usa tu gestor de paquetes para instalar 'python3' y 'python3-pip'"
            echo "- También instala 'python3-tk' o 'tkinter' para la interfaz gráfica"
            ;;
    esac
    
    echo ""
    echo "💡 Alternativamente:"
    echo "1. Descarga desde: https://python.org/downloads/"
    echo "2. Compila desde código fuente"
    echo "3. Usa pyenv: curl https://pyenv.run | bash"
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
echo "1. Automático (recomendado)"
echo "2. Mostrar instrucciones manuales"
echo "3. Salir"
echo ""
read -p "Selecciona una opción (1-3): " opcion

case $opcion in
    1)
        echo ""
        if instalar_python_auto; then
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
            echo "❌ No se pudo instalar automáticamente"
            mostrar_instrucciones
        fi
        ;;
        
    2)
        mostrar_instrucciones
        ;;
        
    3)
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