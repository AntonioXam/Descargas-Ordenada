@echo off
title DescargasOrdenadas v3.0 - Portable
color 0A

REM ===================================================================
REM DescargasOrdenadas v3.0 - Launcher Portable para Windows
REM Creado por Champi 🍄
REM ===================================================================

echo.
echo 🍄 DescargasOrdenadas v3.0 - Portable para Windows
echo ================================================
echo.

REM Obtener la ruta del directorio donde está este script
set "SCRIPT_DIR=%~dp0"
set "CURRENT_DIR=%CD%"

REM Cambiar al directorio del script para asegurar rutas relativas
cd /d "%SCRIPT_DIR%"

echo 📁 Directorio de la aplicación: %SCRIPT_DIR%
echo.

REM Verificar si Python está disponible
echo 🔍 Verificando Python...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no está instalado o no está en PATH
    echo.
    echo 💡 Para continuar necesitas instalar Python:
    echo    1. Ve a https://python.org/downloads/
    echo    2. Descarga la versión más reciente 
    echo    3. Durante la instalación, marca "Add Python to PATH"
    echo    4. Reinicia y ejecuta este script nuevamente
    echo.
    echo 📁 Esta es una versión portable que requiere Python instalado
    echo.
    pause
    cd /d "%CURRENT_DIR%"
    exit /b 1
)

python --version
echo ✅ Python encontrado
echo.

REM Verificar si pip está disponible
echo 🔍 Verificando pip...
python -m pip --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip no está disponible
    echo 💡 Instala pip para continuar
    pause
    cd /d "%CURRENT_DIR%"
    exit /b 1
)

echo ✅ pip encontrado
echo.

REM Verificar e instalar dependencias automáticamente
echo 🔧 Verificando dependencias...
echo ⏳ Si faltan dependencias, se instalarán automáticamente...
echo.

REM Ejecutar la aplicación - main.py manejará la instalación de dependencias
echo 🚀 Iniciando DescargasOrdenadas...
echo.
python ..\main.py %*

REM Capturar el código de salida
set EXIT_CODE=%errorlevel%

REM Restaurar directorio original
cd /d "%CURRENT_DIR%"

REM Si la aplicación terminó con error y no es una ejecución en modo silencioso, mostrar mensaje
if %EXIT_CODE% neq 0 (
    echo.
    echo ❌ La aplicación terminó con errores (Código: %EXIT_CODE%)
    
    REM Solo hacer pausa si no es una tarea programada o inicio automático
    if not "%*"=="" (
        if not "%*"=="*--tarea-programada*" (
            if not "%*"=="*--inicio-sistema*" (
                echo.
                pause
            )
        )
    ) else (
        echo.
        pause
    )
)

exit /b %EXIT_CODE% 