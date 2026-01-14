@echo off
chcp 65001 > nul
title Instalar Dependencias - DescargasOrdenadas

echo 🍄 DescargasOrdenadas v3.0 - Instalación de Dependencias
echo ======================================================

echo 🔍 Verificando Python...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no está instalado o no está en PATH
    echo.
    echo 💡 Para instalar Python:
    echo    1. Ve a https://python.org/downloads/
    echo    2. Descarga la versión más reciente
    echo    3. Durante la instalación, marca "Add Python to PATH"
    echo    4. Ejecuta este script nuevamente
    echo.
    pause
    exit /b 1
)

python --version
echo ✅ Python encontrado

echo.
echo 📦 Instalando dependencias necesarias...

echo 🔧 Instalando Pillow (procesamiento de imágenes)...
pip install pillow

echo 🖥️  Instalando PySide6 (interfaz gráfica)...
pip install PySide6

echo 🪟 Instalando pywin32 (integración Windows)...
pip install pywin32

echo.
echo 🧪 Verificando instalación...

python -c "import PIL; print('✅ Pillow:', PIL.__version__)" 2>nul && (
    echo Pillow instalado correctamente
) || (
    echo ❌ Error con Pillow
)

python -c "import PySide6; print('✅ PySide6 instalado correctamente')" 2>nul && (
    echo PySide6 instalado correctamente  
) || (
    echo ❌ Error con PySide6
)

python -c "import win32api; print('✅ pywin32 instalado correctamente')" 2>nul && (
    echo pywin32 instalado correctamente
) || (
    echo ❌ Error con pywin32
)

echo.
echo 🎉 ¡Instalación de dependencias completada!
echo 🚀 Ahora puedes ejecutar: DescargasOrdenadas.bat
echo.
pause 