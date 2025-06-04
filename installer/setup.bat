@echo off
setlocal enabledelayedexpansion

REM Instalador para DescargasOrdenadas
title Instalador de DescargasOrdenadas

echo ==============================================
echo    Instalador de DescargasOrdenadas v1.0
echo ==============================================
echo.

REM Comprobar si se ejecuta como administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Este instalador necesita permisos de administrador.
    echo Por favor, ejecute este instalador como administrador.
    echo.
    pause
    exit /b 1
)

REM Preguntar dónde instalar
set "DEFAULT_INSTALL_DIR=%ProgramFiles%\DescargasOrdenadas"
set "INSTALL_DIR="

echo Directorio de instalación predeterminado: %DEFAULT_INSTALL_DIR%
set /p INSTALL_CUSTOM=Desea cambiar el directorio de instalación? (S/N): 

if /i "%INSTALL_CUSTOM%"=="S" (
    set /p INSTALL_DIR=Introduzca el directorio de instalación: 
) else (
    set "INSTALL_DIR=%DEFAULT_INSTALL_DIR%"
)

echo.
echo Instalando en: %INSTALL_DIR%
echo.

REM Crear directorio de instalación
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    if %errorlevel% neq 0 (
        echo Error al crear el directorio de instalación.
        pause
        exit /b 1
    )
)

REM Copiar archivos
echo Copiando archivos...
if exist "..\dist\DescargasOrdenadas.exe" (
    copy "..\dist\DescargasOrdenadas.exe" "%INSTALL_DIR%\"
    if %errorlevel% neq 0 (
        echo Error al copiar archivos.
        pause
        exit /b 1
    )
) else (
    echo No se encontró el archivo ejecutable. Por favor, compile la aplicación primero.
    pause
    exit /b 1
)

REM Copiar archivos adicionales si es necesario
if exist "..\LICENSE" (
    copy "..\LICENSE" "%INSTALL_DIR%\"
)

if exist "..\README.md" (
    copy "..\README.md" "%INSTALL_DIR%\"
)

echo Archivos copiados correctamente.
echo.

REM Crear acceso directo en el escritorio
echo Creando acceso directo en el escritorio...
set "DESKTOP=%USERPROFILE%\Desktop"

REM Crear archivo VBS para generar el acceso directo
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP%\DescargasOrdenadas.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\DescargasOrdenadas.exe" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "Organizador de la carpeta de descargas" >> CreateShortcut.vbs
echo oLink.IconLocation = "%INSTALL_DIR%\DescargasOrdenadas.exe, 0" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs

REM Crear menú de inicio
echo Creando acceso directo en el menú de inicio...
set "START_MENU=%ProgramData%\Microsoft\Windows\Start Menu\Programs"
mkdir "%START_MENU%\DescargasOrdenadas" 2>nul

echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateStartMenu.vbs
echo sLinkFile = "%START_MENU%\DescargasOrdenadas\DescargasOrdenadas.lnk" >> CreateStartMenu.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateStartMenu.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\DescargasOrdenadas.exe" >> CreateStartMenu.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> CreateStartMenu.vbs
echo oLink.Description = "Organizador de la carpeta de descargas" >> CreateStartMenu.vbs
echo oLink.IconLocation = "%INSTALL_DIR%\DescargasOrdenadas.exe, 0" >> CreateStartMenu.vbs
echo oLink.Save >> CreateStartMenu.vbs

echo sLinkFile = "%START_MENU%\DescargasOrdenadas\Desinstalar.lnk" >> CreateStartMenu.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateStartMenu.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\uninstall.bat" >> CreateStartMenu.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> CreateStartMenu.vbs
echo oLink.Description = "Desinstalar DescargasOrdenadas" >> CreateStartMenu.vbs
echo oLink.Save >> CreateStartMenu.vbs

cscript //nologo CreateStartMenu.vbs
del CreateStartMenu.vbs

REM Crear script de desinstalación
echo @echo off > "%INSTALL_DIR%\uninstall.bat"
echo echo Desinstalando DescargasOrdenadas... >> "%INSTALL_DIR%\uninstall.bat"
echo timeout /t 2 /nobreak > nul >> "%INSTALL_DIR%\uninstall.bat"
echo if exist "%DESKTOP%\DescargasOrdenadas.lnk" del "%DESKTOP%\DescargasOrdenadas.lnk" >> "%INSTALL_DIR%\uninstall.bat"
echo if exist "%START_MENU%\DescargasOrdenadas\DescargasOrdenadas.lnk" del "%START_MENU%\DescargasOrdenadas\DescargasOrdenadas.lnk" >> "%INSTALL_DIR%\uninstall.bat"
echo if exist "%START_MENU%\DescargasOrdenadas\Desinstalar.lnk" del "%START_MENU%\DescargasOrdenadas\Desinstalar.lnk" >> "%INSTALL_DIR%\uninstall.bat"
echo rmdir "%START_MENU%\DescargasOrdenadas" 2^>nul >> "%INSTALL_DIR%\uninstall.bat"
echo cd /d "%TEMP%" >> "%INSTALL_DIR%\uninstall.bat"
echo timeout /t 2 /nobreak > nul >> "%INSTALL_DIR%\uninstall.bat"
echo rmdir /s /q "%INSTALL_DIR%" >> "%INSTALL_DIR%\uninstall.bat"
echo echo Desinstalación completada. >> "%INSTALL_DIR%\uninstall.bat"
echo pause >> "%INSTALL_DIR%\uninstall.bat"

echo.
echo ¡Instalación completada!
echo.
echo DescargasOrdenadas ha sido instalado en: %INSTALL_DIR%
echo.
echo Puede encontrar accesos directos en:
echo - Escritorio
echo - Menú de inicio
echo.

pause 