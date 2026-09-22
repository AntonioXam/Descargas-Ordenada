@echo off
REM ===================================================================
REM DescargasOrdenadas - Lanzador de Windows
REM ===================================================================
setlocal

REM Cambiar al directorio del script
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Elegir el intérprete: primero el entorno virtual, luego pythonw (sin
REM consola), y por último python del sistema.
set "PYTHON="
if exist "%SCRIPT_DIR%.venv\Scripts\pythonw.exe" set "PYTHON=%SCRIPT_DIR%.venv\Scripts\pythonw.exe"
if not defined PYTHON (
    where pythonw3.exe > nul 2>&1 && set "PYTHON=pythonw3.exe"
)
if not defined PYTHON (
    where pythonw.exe > nul 2>&1 && set "PYTHON=pythonw.exe"
)
if not defined PYTHON (
    where python3.exe > nul 2>&1 && set "PYTHON=python3.exe"
)
if not defined PYTHON (
    where python.exe > nul 2>&1 && set "PYTHON=python.exe"
)

if not defined PYTHON (
    echo ERROR: Python no esta instalado
    echo.
    echo Instalalo desde:
    echo https://www.python.org/downloads/
    echo.
    echo Marca la casilla "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

REM Detectar si es una orden del menu contextual (no debe abrir nada visible)
set "MODO_SILENCIOSO="
echo %* | find /I "--organizar-carpeta" >nul && set "MODO_SILENCIOSO=1"

if defined MODO_SILENCIOSO (
    REM Organizar una carpeta en segundo plano: sin consola y sin esperar
    start "" /B "%PYTHON%" "%SCRIPT_DIR%organizer\INICIAR.py" %*
    exit /b 0
)

REM Arranque normal de la interfaz
start "" "%PYTHON%" "%SCRIPT_DIR%organizer\INICIAR.py" --gui %*
exit /b 0
