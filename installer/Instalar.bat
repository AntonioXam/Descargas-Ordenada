@echo off

REM Ejecutar el instalador con privilegios de administrador
echo Ejecutando el instalador de DescargasOrdenadas...

REM Generar un archivo VBS para ejecutar el script con privilegios de administrador
echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
echo UAC.ShellExecute "%~dp0setup.bat", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
cscript //nologo "%temp%\getadmin.vbs"
del "%temp%\getadmin.vbs"

exit 