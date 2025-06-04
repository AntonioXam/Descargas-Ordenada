@echo off
setlocal enabledelayedexpansion

echo ==============================================
echo    Creador de Instalador DescargasOrdenadas
echo ==============================================
echo.

cd ..

REM Comprobar si existe Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo No se encontró Python. Por favor, instale Python antes de continuar.
    pause
    exit /b 1
)

REM Comprobar si existe PyInstaller
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo No se encontró PyInstaller. Instalando...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo Error al instalar PyInstaller.
        pause
        exit /b 1
    )
)

REM Compilar con PyInstaller
echo Compilando la aplicación con PyInstaller...
python -m PyInstaller --clean --onefile --windowed --noconsole --name DescargasOrdenadas --icon resources/app_icon.ico main.py
if %errorlevel% neq 0 (
    echo Error al compilar la aplicación con PyInstaller.
    pause
    exit /b 1
)

echo.
echo Aplicación compilada correctamente.
echo.

REM Verificar si existe el ejecutable compilado
if not exist "dist\DescargasOrdenadas.exe" (
    echo No se encontró el ejecutable compilado. La compilación falló.
    pause
    exit /b 1
)

REM Crear directorio para el instalador
if not exist "instalador" mkdir instalador

REM Copiar archivos necesarios
echo Copiando archivos para el instalador...
copy "dist\DescargasOrdenadas.exe" "instalador\"
if exist "LICENSE" copy "LICENSE" "instalador\"
if exist "README.md" copy "README.md" "instalador\"
copy "installer\setup.bat" "instalador\"
copy "installer\Instalar.bat" "instalador\"

echo.
echo Instalador creado correctamente en la carpeta "instalador".
echo Para distribuir, comprima la carpeta "instalador" en un archivo ZIP.
echo.

pause 