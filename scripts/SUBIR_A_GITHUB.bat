@echo off
REM ═══════════════════════════════════════════════════════════════════
REM 📤 SUBIR A GITHUB - DescargasOrdenadas v3.2
REM ═══════════════════════════════════════════════════════════════════

echo.
echo ═══════════════════════════════════════════════════════════════════
echo    📤 SUBIR A GITHUB - DescargasOrdenadas v3.2
echo ═══════════════════════════════════════════════════════════════════
echo.

REM Verificar si Git está instalado
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git no está instalado.
    echo    Descarga desde: https://git-scm.com/downloads
    echo.
    pause
    exit /b 1
)

echo ✅ Git encontrado
echo.

REM Verificar si ya es un repositorio Git
if not exist ".git" (
    echo 📦 Inicializando repositorio Git...
    git init
    git branch -M main
    echo ✅ Repositorio inicializado
    echo.
) else (
    echo ℹ️  Repositorio Git ya existe
    echo.
)

REM Preguntar por el repositorio remoto
echo 🔗 Configuración del repositorio remoto
echo.
set /p USUARIO="👤 Tu usuario de GitHub: "
set /p REPO="📦 Nombre del repositorio [Descargas-Ordenada]: "

if "%REPO%"=="" set REPO=Descargas-Ordenada

echo.
echo 📋 URL del repositorio: https://github.com/%USUARIO%/%REPO%
echo.

REM Verificar/añadir remote
git remote -v | findstr origin >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔗 Añadiendo repositorio remoto...
    git remote add origin https://github.com/%USUARIO%/%REPO%.git
    echo ✅ Remoto añadido
) else (
    echo ℹ️  Remoto ya configurado, actualizando URL...
    git remote set-url origin https://github.com/%USUARIO%/%REPO%.git
    echo ✅ URL actualizada
)
echo.

REM Añadir todos los archivos
echo 📁 Añadiendo archivos al staging...
git add .
echo ✅ Archivos añadidos
echo.

REM Commit
set /p MENSAJE="💬 Mensaje del commit [v3.2.0 - Mejoras finales]: "
if "%MENSAJE%"=="" set MENSAJE=v3.2.0 - Mejoras finales

echo.
echo 📝 Creando commit...
git commit -m "%MENSAJE%"
if %errorlevel% neq 0 (
    echo ⚠️  No hay cambios para commitear o el commit falló
)
echo.

REM Push
echo 📤 Subiendo a GitHub...
echo.
git push -u origin main
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Si es tu primer push y pide credenciales:
    echo    1. Usa tu usuario de GitHub
    echo    2. Como contraseña, usa un Personal Access Token
    echo    3. Crea el token en: https://github.com/settings/tokens
    echo    4. Permisos necesarios: repo
    echo.
    echo ⚠️  Si el repositorio no existe en GitHub:
    echo    1. Ve a: https://github.com/new
    echo    2. Crea el repositorio: %REPO%
    echo    3. Vuelve a ejecutar este script
    echo.
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════════════
echo ✅ CÓDIGO SUBIDO A GITHUB CORRECTAMENTE
echo ═══════════════════════════════════════════════════════════════════
echo.
echo 📋 PRÓXIMO PASO: Crear una release
echo.
echo    1. Ve a: https://github.com/%USUARIO%/%REPO%/releases/new
echo    2. Tag: v3.2.0
echo    3. Title: v3.2.0 - Mejoras Finales
echo    4. Descripción:
echo.
echo        ## 🆕 Novedades v3.2
echo.
echo        - ⏱️ Intervalos personalizables (30 seg a 1 día)
echo        - ⬇️ Descarga automática de actualizaciones
echo        - 🚀 Botones mejorados de Startup
echo        - 🎨 Mejoras visuales
echo.
echo    5. Adjunta el .zip del proyecto (recomendado)
echo    6. Publica la release
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
pause
