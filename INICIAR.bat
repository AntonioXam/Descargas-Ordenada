@echo off
REM ===================================================================
REM 🍄 DescargasOrdenadas v3.2 - Launcher
REM Creado por Champi 🍄
REM ===================================================================

REM Cambiar al directorio del script
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Preferir python3 del sistema (donde están instaladas las dependencias)
where python3.exe > nul 2>&1
if %errorlevel% equ 0 (
    REM Usar pythonw3 si existe para no mostrar consola; si no, python3
    where pythonw3.exe > nul 2>&1
    if %errorlevel% equ 0 (
        start "" pythonw3.exe "%SCRIPT_DIR%organizer\INICIAR.py" --gui %*
    ) else (
        start "" python3.exe "%SCRIPT_DIR%organizer\INICIAR.py" --gui %*
    )
    goto :fin
)

REM Fallback a pythonw.exe / python.exe
where pythonw.exe > nul 2>&1
if %errorlevel% equ 0 (
    start "" pythonw.exe "%SCRIPT_DIR%organizer\INICIAR.py" --gui %*
    goto :fin
)

where python.exe > nul 2>&1
if %errorlevel% equ 0 (
    start "" python.exe "%SCRIPT_DIR%organizer\INICIAR.py" --gui %*
    goto :fin
)

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

:fin
REM Salir inmediatamente
exit /b 0
