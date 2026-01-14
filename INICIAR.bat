@echo off
REM ===================================================================
REM 🍄 DescargasOrdenadas v3.1 - Launcher SIN CONSOLA
REM Creado por Champi 🍄
REM Este archivo inicia la aplicación sin ventana de consola
REM ===================================================================

REM Cambiar al directorio del script
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Verificar si pythonw.exe está disponible
where pythonw.exe > nul 2>&1
if %errorlevel% equ 0 (
    REM Usar pythonw.exe para ejecutar sin consola
    start "" pythonw.exe "%SCRIPT_DIR%INICIAR_SIN_CONSOLA.pyw" %*
) else (
    REM Si no existe pythonw, intentar con python.exe ocultando consola
    where python.exe > nul 2>&1
    if %errorlevel% equ 0 (
        start "" /MIN python.exe "%SCRIPT_DIR%INICIAR.py" --gui %*
    ) else (
        REM Crear archivo de error si Python no está instalado
        echo Python no está instalado > error_no_python.txt
        exit /b 1
    )
)

REM Salir inmediatamente sin mostrar mensajes
exit /b 0
