@echo off
REM ═══════════════════════════════════════════════════════════════
REM 📦 DESCARGAR DEPENDENCIAS - DescargasOrdenadas v3.2
REM ═══════════════════════════════════════════════════════════════
REM Este script descarga todas las dependencias en formato .whl
REM para instalación offline
REM ═══════════════════════════════════════════════════════════════

title 📦 Descargar Dependencias

color 0B
echo.
echo ═══════════════════════════════════════════════════════════════
echo    📦 DESCARGAR DEPENDENCIAS
echo    DescargasOrdenadas v3.2
echo ═══════════════════════════════════════════════════════════════
echo.
echo    Este script descargará todas las dependencias necesarias
echo    en formato .whl para instalación sin internet.
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

pause

REM Cambiar al directorio raíz del proyecto
cd /d "%~dp0.."

echo.
echo [1/2] 🔍 Verificando Python...
echo ════════════════════════════════════════════════════════════════

python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo ❌ ERROR: Python no está instalado
    echo.
    pause
    exit /b 1
)

python --version
echo ✅ Python encontrado

echo.
echo [2/2] 📦 Descargando dependencias...
echo ════════════════════════════════════════════════════════════════
echo.
echo    Descargando a: dependencias\
echo.

REM Crear carpeta si no existe
if not exist dependencias mkdir dependencias

REM Descargar todas las dependencias con sus subdependencias
python -m pip download -d dependencias PySide6 Pillow watchdog pywin32 requests plyer

if %errorlevel% neq 0 (
    color 0C
    echo.
    echo ❌ ERROR: Fallo al descargar algunas dependencias
    echo.
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo    ✅ DESCARGA COMPLETADA
echo ═══════════════════════════════════════════════════════════════
echo.
echo    📂 Dependencias guardadas en: dependencias\
echo.
echo    Ahora puedes:
echo    1. Copiar la carpeta "dependencias" a otros PCs
echo    2. Usar INSTALAR_DEPENDENCIAS.bat instalará desde ahí
echo       si no hay internet
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

pause
