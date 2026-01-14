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
echo    🍄 DESCARGAS ORDENADAS v3.1
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
echo [2/6] 📦 Instalando PySide6 (Interfaz gráfica)...
echo ════════════════════════════════════════════════════════════════
python -m pip install --upgrade PySide6
if %errorlevel% neq 0 (
    echo ⚠️  Error instalando PySide6
) else (
    echo ✅ PySide6 instalado correctamente
)

echo.
echo [3/6] 📦 Instalando Pillow (Procesamiento de imágenes)...
echo ════════════════════════════════════════════════════════════════
python -m pip install --upgrade Pillow
if %errorlevel% neq 0 (
    echo ⚠️  Error instalando Pillow
) else (
    echo ✅ Pillow instalado correctamente
)

echo.
echo [4/6] 📦 Instalando watchdog (Monitor de archivos)...
echo ════════════════════════════════════════════════════════════════
python -m pip install --upgrade watchdog
if %errorlevel% neq 0 (
    echo ⚠️  Error instalando watchdog
) else (
    echo ✅ watchdog instalado correctamente
)

echo.
echo [5/6] 📦 Instalando pywin32 (Windows APIs)...
echo ════════════════════════════════════════════════════════════════
python -m pip install --upgrade pywin32
if %errorlevel% neq 0 (
    echo ⚠️  Error instalando pywin32
) else (
    echo ✅ pywin32 instalado correctamente
)

echo.
echo [6/6] 📦 Instalando dependencias v3.1...
echo ════════════════════════════════════════════════════════════════

echo   • requests (actualizaciones automáticas)...
python -m pip install --upgrade requests
if %errorlevel% neq 0 (
    echo   ⚠️  Error instalando requests
) else (
    echo   ✅ requests instalado correctamente
)

echo   • plyer (notificaciones nativas)...
python -m pip install --upgrade plyer
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

python -c "import sys; print('🐍 Python:', sys.version.split()[0])"
python -c "try: import PySide6; print('✅ PySide6:', PySide6.__version__)\nexcept: print('❌ PySide6: No instalado')"
python -c "try: import PIL; print('✅ Pillow:', PIL.__version__)\nexcept: print('❌ Pillow: No instalado')"
python -c "try: import watchdog; print('✅ watchdog:', watchdog.__version__)\nexcept: print('❌ watchdog: No instalado')"
python -c "try: import win32com.client; print('✅ pywin32: Instalado')\nexcept: print('❌ pywin32: No instalado')"
python -c "try: import requests; print('✅ requests:', requests.__version__)\nexcept: print('❌ requests: No instalado')"
python -c "try: import plyer; print('✅ plyer:', plyer.__version__)\nexcept: print('❌ plyer: No instalado')"

echo.
echo ═══════════════════════════════════════════════════════════════
echo    ✅ INSTALACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════════
echo.
echo    🚀 Para iniciar la aplicación:
echo.
echo       1. Doble clic en: INICIAR_SIN_CONSOLA.bat
echo       2. O ejecuta: python INICIAR.py --gui
echo.
echo    📋 Para verificar que todo funciona:
echo       python PRUEBAS_v3.1.py
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

pause
