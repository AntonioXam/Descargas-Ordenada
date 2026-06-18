@echo off
REM ===================================================================
REM 🍄 DescargasOrdenadas v3.2 - Crear acceso directo en barra de tareas
REM Ejecutar como administrador si quieres para todos los usuarios
REM ===================================================================

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

python3 scripts/crear_acceso_directo.py

if %errorlevel% neq 0 (
    echo.
    echo ⚠️ No se pudo crear el acceso directo con python3.
    echo Intentando con python...
    python scripts/crear_acceso_directo.py
)

pause
