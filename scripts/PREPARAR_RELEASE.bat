@echo off
chcp 65001 >nul
title Preparar Release para GitHub

echo.
echo ═══════════════════════════════════════════════════════════
echo 📦 PREPARAR RELEASE PARA GITHUB
echo ═══════════════════════════════════════════════════════════
echo.

:: Leer versión actual
set /p VERSION=<VERSION.txt
echo 📌 Versión actual: v%VERSION%
echo.

:: Confirmar
set /p CONFIRMAR="¿Deseas crear el release v%VERSION%? (S/N): "
if /i not "%CONFIRMAR%"=="S" (
    echo ❌ Cancelado
    pause
    exit /b
)

echo.
echo 📋 Pasos para crear el release en GitHub:
echo.
echo 1️⃣  Sube todos los cambios a GitHub:
echo    git add .
echo    git commit -m "Release v%VERSION%"
echo    git push
echo.
echo 2️⃣  Ve a: https://github.com/AntonioXam/Descargas-Ordenada/releases/new
echo.
echo 3️⃣  Completa los campos:
echo    • Tag version: v%VERSION%
echo    • Release title: DescargasOrdenadas v%VERSION%
echo    • Description: Escribe las novedades de esta versión
echo.
echo 4️⃣  Marca como "Set as the latest release"
echo.
echo 5️⃣  Haz click en "Publish release"
echo.
echo ✅ GitHub generará automáticamente el archivo .zip
echo    Los usuarios podrán descargarlo desde la aplicación
echo.

pause
