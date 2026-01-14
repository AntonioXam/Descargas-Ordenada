# 🚀 Guía: Publicar en GitHub

Esta guía te explica cómo subir el proyecto a GitHub para que el sistema de actualizaciones funcione.

---

## 📋 Requisitos Previos

- ✅ Tener una cuenta de GitHub (gratis)
- ✅ Tener Git instalado ([descargar aquí](https://git-scm.com/))
- ✅ El proyecto listo y funcionando

---

## 🆕 Primera Vez - Crear Repositorio

### 1️⃣ Crear Repositorio en GitHub

1. Ve a [GitHub](https://github.com/)
2. Click en el botón **"+"** (arriba derecha) → **"New repository"**
3. Completa:
   - **Repository name:** `Descargas-Ordenada`
   - **Description:** Organizador automático de descargas
   - **Visibility:** ✅ Public (para que las actualizaciones funcionen)
   - ❌ **NO** marques "Add a README file" (ya lo tienes)
4. Click **"Create repository"**

### 2️⃣ Configurar Git Local (solo primera vez)

Abre una terminal (CMD) en la carpeta del proyecto:

```bash
# Configurar tu identidad (solo la primera vez en tu PC)
git config --global user.name "Tu Nombre"
git config --global user.email "tuemail@ejemplo.com"

# Inicializar repositorio
git init

# Agregar todos los archivos
git add .

# Hacer el primer commit
git commit -m "Initial commit - DescargasOrdenadas v3.2.0"

# Conectar con GitHub (cambia TU-USUARIO por tu nombre de usuario)
git remote add origin https://github.com/TU-USUARIO/Descargas-Ordenada.git

# Subir a GitHub
git branch -M main
git push -u origin main
```

### 3️⃣ Crear el Primer Release

1. Ve a tu repositorio en GitHub
2. Click en **"Releases"** (lateral derecho)
3. Click **"Create a new release"**
4. Completa:
   - **Choose a tag:** v3.2.0 (escribir y click "Create new tag: v3.2.0 on publish")
   - **Release title:** DescargasOrdenadas v3.2.0
   - **Description:** 
     ```
     ## 🎉 Primera Release Pública
     
     ### ✨ Características:
     - 📁 Organización automática de descargas
     - 🤖 Categorización con IA
     - 🔄 Actualizaciones automáticas
     - 🎨 5 temas personalizables
     - 🔔 Notificaciones nativas
     - 💾 100% portable
     
     ### 📥 Instalación:
     1. Descarga el código (Download ZIP)
     2. Extrae en una carpeta
     3. Ejecuta `INSTALAR_DEPENDENCIAS.bat`
     4. Ejecuta `INICIAR.bat`
     ```
5. ✅ Marca **"Set as the latest release"**
6. Click **"Publish release"**

**¡Listo!** GitHub generó automáticamente el archivo .zip que usarán las actualizaciones.

---

## 🔄 Actualizaciones Futuras

Cada vez que hagas cambios y quieras publicar una nueva versión:

### 1️⃣ Actualizar la Versión

```bash
# Edita VERSION.txt
echo 3.3.0 > VERSION.txt

# Edita organizer/actualizaciones_mejorado.py
# Cambia: VERSION_ACTUAL = "3.3.0"

# Edita README.md
# Cambia el badge de versión
```

### 2️⃣ Subir Cambios a GitHub

```bash
# Agregar cambios
git add .

# Crear commit
git commit -m "Release v3.3.0 - Descripción de cambios"

# Subir a GitHub
git push
```

### 3️⃣ Crear Nueva Release

1. Ve a [tu repositorio]/releases
2. Click **"Draft a new release"**
3. Tag: `v3.3.0`
4. Title: `DescargasOrdenadas v3.3.0`
5. Description: Lista de novedades
6. ✅ **Set as the latest release**
7. **Publish release**

### 4️⃣ Probar Actualización

1. Abre tu versión anterior de la app (v3.2.0)
2. Click **"Buscar Actualizaciones"**
3. Debería detectar v3.3.0
4. Click **"Descargar e Instalar"**
5. ¡Verifica que funcione!

---

## 🔧 Configurar el Proyecto

Si creaste tu propio fork o copia, actualiza las referencias:

### Archivo: `organizer/actualizaciones_mejorado.py`

```python
# Líneas 30-32
GITHUB_USER = "TU-USUARIO-GITHUB"     # ← Cambia esto
GITHUB_REPO = "Descargas-Ordenada"    # ← Y esto si cambiaste el nombre
```

### Archivo: `README.md`

Actualiza los enlaces a tu repositorio.

---

## 📝 Buenas Prácticas

### Versionado Semántico

Usa números de versión `MAJOR.MINOR.PATCH`:

- **MAJOR (3.x.x):** Cambios incompatibles (nueva versión mayor)
- **MINOR (x.2.x):** Nuevas funcionalidades compatibles
- **PATCH (x.x.1):** Corrección de bugs

Ejemplos:
- `3.2.0` → `3.2.1`: Arreglaste un bug
- `3.2.0` → `3.3.0`: Agregaste una nueva función
- `3.2.0` → `4.0.0`: Cambio completo de arquitectura

### Mensajes de Commit Claros

```bash
# ✅ Buenos
git commit -m "Fix: Corrige error al organizar PDFs"
git commit -m "Feature: Agrega soporte para archivos .webp"
git commit -m "Docs: Actualiza README con instalación offline"

# ❌ Malos
git commit -m "cambios"
git commit -m "fix"
git commit -m "update"
```

### Descripción de Releases

Siempre incluye:
- ✨ **Novedades** (Features)
- 🐛 **Correcciones** (Fixes)
- ⚠️ **Cambios Importantes** (Breaking Changes)
- 📥 **Instrucciones** de instalación

---

## 🚫 Qué NO Subir a GitHub

Ya está configurado en `.gitignore`:

- ❌ `__pycache__/` y `*.pyc`
- ❌ `.config/` (configuración del usuario)
- ❌ `dependencias/*.whl` (archivos grandes)
- ❌ Logs y archivos temporales
- ❌ `.vscode/`, `.idea/` (configs de editores)

**¿Por qué?**
- Mantiene el repositorio ligero
- Evita conflictos entre usuarios
- Los .whl se pueden descargar

---

## 🔐 Repositorio Público vs Privado

### Público (Recomendado)
- ✅ Actualizaciones funcionan sin autenticación
- ✅ Cualquiera puede usar el programa
- ✅ Mayor visibilidad
- ❌ El código es visible

### Privado
- ✅ Código oculto
- ❌ Requiere token de GitHub para actualizaciones
- ❌ Más complejo de configurar
- ❌ No recomendado para este proyecto

**Para este proyecto, usa repositorio PÚBLICO.**

---

## 🐛 Solución de Problemas

### "Permission denied (publickey)"

Configura HTTPS en vez de SSH:

```bash
git remote set-url origin https://github.com/TU-USUARIO/Descargas-Ordenada.git
```

### "Failed to push"

Si da error al hacer push:

```bash
# Crear token de acceso personal
# GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
# Generate new token → Marcar "repo" → Generate

# Usar token como contraseña al hacer push
git push
Username: TU-USUARIO
Password: [pega tu token]
```

### "The file will have its original line endings"

Es solo una advertencia, ignórala o configura:

```bash
git config --global core.autocrlf true
```

---

## 📞 Ayuda Adicional

- 📖 **Guía oficial de Git:** https://git-scm.com/book/es/v2
- 📖 **GitHub Docs:** https://docs.github.com/es
- 🎓 **Tutorial interactivo:** https://learngitbranching.js.org/?locale=es_ES

---

## ✅ Checklist Final

Antes de publicar:

- [ ] Código probado y funcionando
- [ ] README.md actualizado
- [ ] Versión incrementada en 3 lugares:
  - [ ] `VERSION.txt`
  - [ ] `organizer/actualizaciones_mejorado.py`
  - [ ] `README.md` (badge)
- [ ] `.gitignore` configurado
- [ ] Commit descriptivo creado
- [ ] Push a GitHub exitoso
- [ ] Release creada en GitHub
- [ ] Actualización probada desde versión anterior

---

¡Todo listo para que tu proyecto esté disponible para el mundo! 🚀
