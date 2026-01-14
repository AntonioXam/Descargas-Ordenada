@echo off
REM ═══════════════════════════════════════════════════════════════════════════════
REM 📦 CREAR RELEASE PÚBLICA - DescargasOrdenadas v3.2
REM ═══════════════════════════════════════════════════════════════════════════════
REM Este script crea una versión limpia para el repositorio público de GitHub
REM ═══════════════════════════════════════════════════════════════════════════════

title 📦 Crear Release Pública

color 0B
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo    📦 CREAR RELEASE PÚBLICA
echo    DescargasOrdenadas v3.2
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
echo    Este script copiará SOLO los archivos necesarios para el repo público:
echo.
echo    ✅ Archivos .bat (ejecutables)
echo    ✅ Código Python (organizer/)
echo    ✅ Recursos (resources/)
echo    ✅ Documentación básica (README.md, LEEME.txt)
echo    ✅ Configuración (requirements.txt, .gitignore)
echo.
echo    ❌ NO incluirá:
echo    ❌ docs/ (documentación de desarrollo)
echo    ❌ scripts/ (scripts auxiliares)
echo    ❌ Archivos .backup y temporales
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo.

pause

REM Cambiar al directorio raíz del proyecto
cd /d "%~dp0.."

echo.
echo [1/7] 🗑️  Limpiando carpeta release anterior...
echo ════════════════════════════════════════════════════════════════════════════════
if exist release (
    rmdir /S /Q release
    echo ✅ Carpeta anterior eliminada
) else (
    echo ℹ️  No había carpeta anterior
)

echo.
echo [2/7] 📁 Creando carpeta release...
echo ════════════════════════════════════════════════════════════════════════════════
mkdir release
echo ✅ Carpeta creada

echo.
echo [3/7] 📄 Copiando archivos principales...
echo ════════════════════════════════════════════════════════════════════════════════
copy INICIAR.bat release\ >nul
copy INSTALAR_DEPENDENCIAS.bat release\ >nul
copy INICIAR_SIN_CONSOLA.pyw release\ >nul
copy requirements.txt release\ >nul
copy README.md release\ >nul
copy LEEME.txt release\ >nul
copy .gitignore release\ >nul
echo ✅ 7 archivos copiados

echo.
echo [4/7] 🍄 Copiando carpeta organizer/...
echo ════════════════════════════════════════════════════════════════════════════════
xcopy /E /I /Q organizer release\organizer >nul
REM Eliminar archivos .backup de organizer
del /Q release\organizer\*.backup* 2>nul
del /Q release\organizer\*.bak 2>nul
echo ✅ Carpeta organizer copiada (sin backups)

echo.
echo [5/7] 📦 Copiando carpeta resources/...
echo ════════════════════════════════════════════════════════════════════════════════
xcopy /E /I /Q resources release\resources >nul
echo ✅ Carpeta resources copiada

echo.
echo [6/7] 🧹 Limpiando __pycache__ y temporales...
echo ════════════════════════════════════════════════════════════════════════════════
rmdir /S /Q release\organizer\__pycache__ 2>nul
del /Q release\*.log 2>nul
del /Q release\*.db 2>nul
echo ✅ Archivos temporales eliminados

echo.
echo [7/7] ✅ Verificando contenido...
echo ════════════════════════════════════════════════════════════════════════════════
echo.
echo    Archivos en release/:
dir /B release
echo.

echo ═══════════════════════════════════════════════════════════════════════════════
echo    ✅ RELEASE PÚBLICA CREADA EXITOSAMENTE
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
echo    📂 Ubicación: %CD%\release\
echo.
echo    📋 PRÓXIMOS PASOS:
echo.
echo    1. Revisar el contenido de la carpeta release\
echo.
echo    2. Si es la PRIMERA VEZ (repo público):
echo       cd release
echo       git init
echo       git add .
echo       git commit -m "v3.2.0 - Primera release pública"
echo       git branch -M main
echo       git remote add origin https://github.com/TU-USUARIO/Descargas-Ordenada.git
echo       git push -u origin main
echo.
echo    3. Si YA EXISTE el repo público:
echo       cd release
echo       git add .
echo       git commit -m "v3.2.0 - Actualización"
echo       git push
echo.
echo    4. Crear Release en GitHub:
echo       - Ve a: https://github.com/TU-USUARIO/Descargas-Ordenada/releases/new
echo       - Tag: v3.2.0
echo       - Title: v3.2.0 - Mejoras Finales
echo       - Adjunta: release.zip (comprime la carpeta release)
echo       - Publicar
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo.

pause
