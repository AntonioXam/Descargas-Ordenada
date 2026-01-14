@echo off
REM ===================================================================
REM 🍄 DescargasOrdenadas v3.2 - Launcher
REM Creado por Champi 🍄
REM ===================================================================

REM Cambiar al directorio del script
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Verificar si pythonw.exe está disponible (para ejecutar sin consola)
where pythonw.exe > nul 2>&1
if %errorlevel% equ 0 (
    REM Usar pythonw.exe para ejecutar sin consola
    start "" pythonw.exe "%SCRIPT_DIR%organizer\INICIAR.py" --gui %*
) else (
    REM Si no existe pythonw, usar python.exe normal
    where python.exe > nul 2>&1
    if %errorlevel% equ 0 (
        start "" python.exe "%SCRIPT_DIR%organizer\INICIAR.py" --gui %*
    ) else (
        REM Mostrar error si Python no está instalado
        echo ❌ ERROR: Python no está instalado
        echo.
        echo Por favor instala Python desde:
        echo https://www.python.org/downloads/
        echo.
        echo Asegúrate de marcar "Add Python to PATH"
        echo.
        pause
        exit /b 1
    )
)

REM Salir inmediatamente
exit /b 0
