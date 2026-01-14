@echo off
REM ═══════════════════════════════════════════════════════════════
REM 🍄 DescargasOrdenadas v3.1 - Instalador Automático
REM ═══════════════════════════════════════════════════════════════
REM Instala TODAS las dependencias necesarias automáticamente
REM ═══════════════════════════════════════════════════════════════

title 🍄 DescargasOrdenadas - Instalador de Dependencias

color 0A
echo.
echo ═══════════════════════════════════════════════════════════════
echo    🍄 DESCARGAS ORDENADAS v3.2
echo    Instalador Automático de Dependencias
echo ═══════════════════════════════════════════════════════════════
echo.
echo    Este script instalará automáticamente:
echo.
echo    📦 DEPENDENCIAS PRINCIPALES:
echo       • PySide6           (Interfaz gráfica)
echo       • Pillow            (Imágenes)
echo       • watchdog          (Monitor archivos)
echo       • pywin32           (Windows APIs)
echo.
echo    📦 DEPENDENCIAS v3.1 (NUEVAS):
echo       • requests          (Actualizaciones)
echo       • plyer             (Notificaciones nativas)
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

pause

echo.
echo [1/6] 🔍 Verificando Python...
echo ════════════════════════════════════════════════════════════════

python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo ❌ ERROR: Python no está instalado o no está en el PATH
    echo.
    echo Por favor instala Python desde:
    echo https://www.python.org/downloads/
    echo.
    echo Asegúrate de marcar "Add Python to PATH" durante la instalación
    echo.
    pause
    exit /b 1
)

python --version
echo ✅ Python encontrado

echo.
echo 🔍 Verificando si hay dependencias locales...
if exist dependencias (
    echo ✅ Se encontró carpeta "dependencias" - Instalando desde ahí
    set INSTALL_FROM=--find-links=dependencias --no-index
) else (
    echo ℹ️  Instalando desde internet
    set INSTALL_FROM=
)

echo.
echo [2/6] 📦 Instalando PySide6 (Interfaz gráfica)...
echo ════════════════════════════════════════════════════════════════
python -m pip install %INSTALL_FROM% --upgrade PySide6
if %errorlevel% neq 0 (
    echo ⚠️  Error instalando PySide6
) else (
    echo ✅ PySide6 instalado correctamente
)

echo.
echo [3/6] 📦 Instalando Pillow (Procesamiento de imágenes)...
echo ════════════════════════════════════════════════════════════════
python -m pip install %INSTALL_FROM% --upgrade Pillow
if %errorlevel% neq 0 (
    echo ⚠️  Error instalando Pillow
) else (
    echo ✅ Pillow instalado correctamente
)

echo.
echo [4/6] 📦 Instalando watchdog (Monitor de archivos)...
echo ════════════════════════════════════════════════════════════════
python -m pip install %INSTALL_FROM% --upgrade watchdog
if %errorlevel% neq 0 (
    echo ⚠️  Error instalando watchdog
) else (
    echo ✅ watchdog instalado correctamente
)

echo.
echo [5/6] 📦 Instalando pywin32 (Windows APIs)...
echo ════════════════════════════════════════════════════════════════
python -m pip install %INSTALL_FROM% --upgrade pywin32
if %errorlevel% neq 0 (
    echo ⚠️  Error instalando pywin32
) else (
    echo ✅ pywin32 instalado correctamente
)

echo.
echo [6/6] 📦 Instalando dependencias v3.1...
echo ════════════════════════════════════════════════════════════════

echo   • requests (actualizaciones automáticas)...
python -m pip install %INSTALL_FROM% --upgrade requests
if %errorlevel% neq 0 (
    echo   ⚠️  Error instalando requests
) else (
    echo   ✅ requests instalado correctamente
)

echo   • plyer (notificaciones nativas)...
python -m pip install %INSTALL_FROM% --upgrade plyer
if %errorlevel% neq 0 (
    echo   ⚠️  Error instalando plyer
) else (
    echo   ✅ plyer instalado correctamente
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo    📊 VERIFICACIÓN FINAL
echo ═══════════════════════════════════════════════════════════════
echo.

python -c "import sys; print('Python:', sys.version.split()[0])"

echo Verificando PySide6...
python -c "import PySide6; print('  PySide6:', PySide6.__version__)" 2>nul || echo   PySide6: No instalado

echo Verificando Pillow...
python -c "import PIL; print('  Pillow:', PIL.__version__)" 2>nul || echo   Pillow: No instalado

echo Verificando watchdog...
python -c "import watchdog; print('  watchdog:', watchdog.__version__)" 2>nul || echo   watchdog: No instalado

echo Verificando pywin32...
python -c "import win32com.client; print('  pywin32: Instalado')" 2>nul || echo   pywin32: No instalado

echo Verificando requests...
python -c "import requests; print('  requests:', requests.__version__)" 2>nul || echo   requests: No instalado

echo Verificando plyer...
python -c "import plyer; print('  plyer:', plyer.__version__)" 2>nul || echo   plyer: No instalado

echo.
echo ═══════════════════════════════════════════════════════════════
echo    ✅ INSTALACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════════
echo.
echo    🚀 Para iniciar la aplicación:
echo.
echo       • Doble clic en: INICIAR.bat
echo.
echo    📋 Para verificar que todo funciona:
echo       • cd scripts
echo       • python PRUEBAS_v3.1.py
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

pause
