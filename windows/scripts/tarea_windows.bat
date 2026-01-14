@echo off
chcp 65001 > nul
title Configurar Tarea Programada - DescargasOrdenadas
color 0B

echo 🍄 DescargasOrdenadas v3.0 - Configuración de Tarea Programada
echo ============================================================
echo.

REM Obtener la ruta actual
set "SCRIPT_DIR=%~dp0"
set "APP_DIR=%SCRIPT_DIR%.."
set "BAT_FILE=%APP_DIR%\DescargasOrdenadas.bat"

echo 📁 Directorio de la aplicación: %APP_DIR%
echo 🚀 Archivo de inicio: %BAT_FILE%
echo.

REM Verificar que el archivo bat existe
if not exist "%BAT_FILE%" (
    echo ❌ No se encontró DescargasOrdenadas.bat
    echo 💡 Asegúrate de ejecutar este script desde la carpeta correcta
    pause
    exit /b 1
)

REM Verificar que Python está disponible
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no está disponible en PATH
    echo 💡 Asegúrate de tener Python instalado y agregado al PATH
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

echo ⚙️  Opciones de configuración disponibles:
echo.
echo 1. Tarea al INICIO del sistema (recomendado)
echo 2. Tarea cada HORA
echo 3. Tarea DIARIA
echo 4. ELIMINAR tarea existente
echo.
set /p "opcion=Selecciona una opción (1-4): "

if "%opcion%"=="1" goto inicio_sistema
if "%opcion%"=="2" goto cada_hora
if "%opcion%"=="3" goto diaria
if "%opcion%"=="4" goto eliminar
echo ❌ Opción inválida
pause
exit /b 1

:inicio_sistema
echo.
echo ⏰ Configurando tarea para ejecutar al INICIO del sistema...
schtasks /create /tn "DescargasOrdenadas_InicioSistema" /tr "\"%BAT_FILE%\" --inicio-sistema" /sc onlogon /rl highest /f

if %errorlevel% equ 0 (
    echo ✅ Tarea de inicio creada exitosamente
    echo 🚀 Se ejecutará automáticamente al iniciar sesión
    echo.
    echo 💡 Para desactivar: schtasks /delete /tn "DescargasOrdenadas_InicioSistema" /f
) else (
    echo ❌ Error al crear la tarea de inicio
    echo 💡 Asegúrate de ejecutar como administrador
)
goto fin

:cada_hora
echo.
echo ⏰ Configurando tarea para ejecutar cada HORA...
schtasks /create /tn "DescargasOrdenadas_Automatico" /tr "\"%BAT_FILE%\" --tarea-programada" /sc hourly /mo 1 /st 00:00 /f

if %errorlevel% equ 0 (
    echo ✅ Tarea horaria creada exitosamente
    echo 🕐 Se ejecutará cada hora automáticamente
    echo.
    echo 💡 Para desactivar: schtasks /delete /tn "DescargasOrdenadas_Automatico" /f
) else (
    echo ❌ Error al crear la tarea horaria
    echo 💡 Asegúrate de ejecutar como administrador
)
goto fin

:diaria
echo.
echo ⏰ Configurando tarea para ejecutar DIARIAMENTE...
schtasks /create /tn "DescargasOrdenadas_Diario" /tr "\"%BAT_FILE%\" --tarea-programada" /sc daily /st 09:00 /f

if %errorlevel% equ 0 (
    echo ✅ Tarea diaria creada exitosamente
    echo 📅 Se ejecutará todos los días a las 09:00
    echo.
    echo 💡 Para desactivar: schtasks /delete /tn "DescargasOrdenadas_Diario" /f
) else (
    echo ❌ Error al crear la tarea diaria
    echo 💡 Asegúrate de ejecutar como administrador
)
goto fin

:eliminar
echo.
echo ❌ Eliminando todas las tareas de DescargasOrdenadas...

schtasks /delete /tn "DescargasOrdenadas_InicioSistema" /f >nul 2>&1
schtasks /delete /tn "DescargasOrdenadas_Automatico" /f >nul 2>&1
schtasks /delete /tn "DescargasOrdenadas_Diario" /f >nul 2>&1

echo ✅ Todas las tareas han sido eliminadas
goto fin

:fin
echo.
echo 📋 Estado actual de las tareas:
echo.
schtasks /query /tn "DescargasOrdenadas_InicioSistema" 2>nul && echo "✅ Tarea de inicio: ACTIVA" || echo "❌ Tarea de inicio: NO ACTIVA"
schtasks /query /tn "DescargasOrdenadas_Automatico" 2>nul && echo "✅ Tarea horaria: ACTIVA" || echo "❌ Tarea horaria: NO ACTIVA"
schtasks /query /tn "DescargasOrdenadas_Diario" 2>nul && echo "✅ Tarea diaria: ACTIVA" || echo "❌ Tarea diaria: NO ACTIVA"

echo.
pause 