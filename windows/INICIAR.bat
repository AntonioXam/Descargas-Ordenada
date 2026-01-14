@echo off
chcp 65001 > nul
title DescargasOrdenadas v3.0 - Windows
color 0A

REM ===================================================================
REM DescargasOrdenadas v3.0 - Launcher Principal Windows
REM NO REQUIERE PYTHON PREINSTALADO - Lo instala automáticamente
REM Creado por Champi 🍄
REM ===================================================================

echo.
echo 🍄 DescargasOrdenadas v3.0 - Windows
echo ==================================
echo 💡 Launcher que NO requiere Python preinstalado
echo ⚡ Detectará e instalará todo automáticamente
echo.

REM Obtener directorio del proyecto (carpeta padre)
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."
set "CURRENT_DIR=%CD%"
cd /d "%PROJECT_DIR%"

echo 📁 Proyecto: %PROJECT_DIR%
echo.

REM Verificar si Python está disponible
echo 🔍 Verificando Python...
python --version > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python ya está instalado
    goto :ejecutar_app
)

REM Python no encontrado - ofrecer instalación automática
echo ❌ Python no está instalado en este sistema
echo.
echo 🤖 ¿Quieres que lo instale automáticamente?
echo.
echo 1. SÍ - Instalar Python automáticamente (recomendado)
echo 2. NO - Mostrar instrucciones manuales
echo 3. SALIR
echo.
set /p "opcion=Selecciona una opción (1-3): "

if "%opcion%"=="1" goto :instalar_python
if "%opcion%"=="2" goto :instrucciones_manuales  
if "%opcion%"=="3" goto :salir
echo ❌ Opción inválida
pause
goto :salir

:instalar_python
echo.
echo 🚀 Iniciando instalación automática de Python...
echo ⏳ Este proceso puede tardar varios minutos...
echo.

REM Crear directorio temporal
set "TEMP_DIR=%TEMP%\DescargasOrdenadas_Setup"
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

REM Detectar arquitectura del sistema
set "PYTHON_URL="
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe"
    echo 🖥️  Detectado: Windows 64-bit
) else (
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.6/python-3.11.6.exe"  
    echo 🖥️  Detectado: Windows 32-bit
)

set "PYTHON_INSTALLER=%TEMP_DIR%\python_installer.exe"

echo 📥 Descargando Python desde python.org...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'}"

if %errorlevel% neq 0 (
    echo ❌ Error al descargar Python
    echo 💡 Verifica tu conexión a internet
    goto :instrucciones_manuales
)

echo ✅ Descarga completada
echo 🔧 Instalando Python...
echo.
echo ⚠️  IMPORTANTE: Se instalará automáticamente con PATH configurado
echo.

REM Ejecutar instalador con opciones automáticas
"%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

if %errorlevel% equ 0 (
    echo ✅ Python instalado exitosamente
    echo 🔄 Refrescando variables de entorno...
    
    REM Refrescar PATH
    call refreshenv 2>nul || (
        echo 💡 Por favor reinicia la aplicación para aplicar cambios
        echo ⚠️  Ejecuta este script nuevamente
        pause
        goto :salir
    )
    
    echo 🧪 Verificando instalación...
    python --version
    if %errorlevel% equ 0 (
        echo ✅ Python instalado y configurado correctamente
        goto :ejecutar_app
    ) else (
        echo ⚠️  Python instalado pero PATH necesita reinicio
        echo 💡 Reinicia tu PC y ejecuta este script nuevamente
        pause
        goto :salir
    )
) else (
    echo ❌ Error durante la instalación
    goto :instrucciones_manuales
)

:instrucciones_manuales
echo.
echo 📖 INSTRUCCIONES MANUALES - Instalación de Python
echo ================================================
echo.
echo 1. Ve a: https://python.org/downloads/
echo 2. Descarga "Python 3.11 o superior para Windows"  
echo 3. Ejecuta el instalador
echo 4. ⚠️  MUY IMPORTANTE: Marca "Add Python to PATH"
echo 5. Completa la instalación
echo 6. Reinicia tu PC
echo 7. Ejecuta este script nuevamente
echo.
echo 💡 Alternativamente, desde Microsoft Store:
echo    - Busca "Python" en Microsoft Store
echo    - Instala "Python 3.11" o superior
echo.
pause
goto :salir

:ejecutar_app
echo.
echo 🚀 Iniciando DescargasOrdenadas...
echo ================================
echo.

REM Ejecutar la aplicación principal
python main.py %*

REM Capturar código de salida
set EXIT_CODE=%errorlevel%

echo.
if %EXIT_CODE% equ 0 (
    echo ✅ Aplicación ejecutada exitosamente
) else (
    echo ❌ La aplicación terminó con errores (Código: %EXIT_CODE%)
    
    REM Solo hacer pausa si no es ejecución silenciosa
    echo %* | findstr /C:"--tarea-programada\|--inicio-sistema" > nul
    if %errorlevel% neq 0 (
        echo.
        pause
    )
)

cd /d "%CURRENT_DIR%"
exit /b %EXIT_CODE%

:salir
cd /d "%CURRENT_DIR%"
echo.
echo 👋 ¡Hasta luego!
pause
exit /b 1 