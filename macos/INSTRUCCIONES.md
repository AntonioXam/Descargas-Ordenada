# 🍎 DescargasOrdenadas v3.0 - macOS

## 📋 Archivos Disponibles

### 🚀 **INICIAR.sh** (Recomendado)
- **NO requiere Python preinstalado**
- Detecta e instala Python automáticamente
- Compatible con Intel y Apple Silicon (M1/M2)
- Instala con Homebrew o descarga oficial
- **¡Solo ejecuta este archivo y listo!**

### ⚙️ **DescargasOrdenadas.command**
- Requiere Python ya instalado
- Versión ligera para sistemas con Python
- Ideal para uso avanzado

### 📁 **scripts/**
- `tarea_macos.sh` - Configurar tareas programadas
- `instalar_dependencias.sh` - Instalar dependencias Python

---

## 🚀 Inicio Rápido

### Opción 1: Sin Python (Automático)
```bash
# Navega a la carpeta y ejecuta:
cd ruta/a/DescargasOrdenadas/macos
./INICIAR.sh

# O desde Finder:
# Doble-click en INICIAR.sh
```

### Opción 2: Con Python
```bash
# Si ya tienes Python instalado:
./DescargasOrdenadas.command
```

---

## 🔐 Permisos de Ejecución

**Dar permisos ejecutables (solo la primera vez):**
```bash
chmod +x INICIAR.sh
chmod +x DescargasOrdenadas.command
chmod +x scripts/tarea_macos.sh
chmod +x scripts/instalar_dependencias.sh
```

**O usa la utilidad automática:**
```bash
cd ..
python utils/hacer_ejecutables.py
```

---

## 📋 Funciones Disponibles

### 🔧 Configurar Tarea Programada
```bash
cd scripts
./tarea_macos.sh
```

**Opciones disponibles:**
- **LaunchDaemon:** Ejecutar al iniciar sistema (requiere sudo)
- **LaunchAgent:** Ejecutar al iniciar sesión usuario
- **Cron:** Usar crontab tradicional
- **Eliminar:** Quitar tarea programada

### 📦 Instalar Dependencias Manualmente
```bash
cd scripts
./instalar_dependencias.sh
```

---

## 🛠️ Solución de Problemas

### ❌ "Permission denied"
**Solución:**
```bash
chmod +x INICIAR.sh
./INICIAR.sh
```

### ❌ "Developer cannot be verified"
**Solución:**
1. Ve a **Preferencias del Sistema** → **Seguridad y Privacidad**
2. En la pestaña **General**, permite la aplicación
3. O ejecuta desde Terminal:
```bash
xattr -dr com.apple.quarantine INICIAR.sh
```

### ❌ "Python no encontrado"
**Solución:** Usa `INICIAR.sh` que instala Python automáticamente

### ❌ "Homebrew no instalado"
**Opciones:**
1. **Automático:** `INICIAR.sh` instala Homebrew
2. **Manual:** 
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### ❌ "No funciona la bandeja del sistema"
**Solución:**
1. Instala dependencias completas:
```bash
brew install python-tk
pip3 install pillow pyside6 pyobjc-framework-Cocoa
```

---

## 🍺 Instalación con Homebrew

### Instalar Python
```bash
brew install python
```

### Instalar dependencias
```bash
pip3 install pillow pyside6 pyobjc-framework-Cocoa
```

---

## 📖 Argumentos de Línea de Comandos

```bash
# Ejecución normal
./INICIAR.sh

# Para tareas programadas (sin interfaz)
./INICIAR.sh --tarea-programada

# Para inicio del sistema
./INICIAR.sh --inicio-sistema

# Mostrar ayuda
./INICIAR.sh --help
```

---

## 🔧 Arquitecturas Soportadas

### 🖥️ Intel Mac
- Python descargado de python.org
- Compatible con macOS 10.9+
- Homebrew x86_64

### 💻 Apple Silicon (M1/M2)
- Python nativo para Apple Silicon
- Compatible con macOS 11+
- Homebrew arm64

**El script detecta automáticamente tu arquitectura.**

---

## 💡 Consejos macOS

### 🎯 Ubicaciones Recomendadas
- `/Applications/DescargasOrdenadas/` - Instalación sistema
- `~/Applications/DescargasOrdenadas/` - Instalación usuario
- `~/Desktop/DescargasOrdenadas/` - Temporal

### 🔄 Agregar al PATH
```bash
# Agregar a ~/.zshrc o ~/.bash_profile:
echo 'export PATH="$PATH:/ruta/a/DescargasOrdenadas"' >> ~/.zshrc
```

### 📱 Crear Alias
```bash
# Agregar a ~/.zshrc:
echo 'alias descargas="/ruta/a/DescargasOrdenadas/macos/INICIAR.sh"' >> ~/.zshrc
```

### 🚀 Inicio Automático
```bash
# Configurar inicio automático:
cd scripts
./tarea_macos.sh
# Seleccionar opción "LaunchAgent"
```

### 🍎 Integración con Finder
1. Click derecho en `INICIAR.sh`
2. "Abrir con" → "Utilidad de Terminal" (por defecto)
3. O cambiar extensión a `.command` para doble-click

---

## 🔒 Seguridad y Permisos

### 🛡️ Gatekeeper
Si macOS bloquea la ejecución:
```bash
# Permitir aplicación específica:
sudo spctl --add /ruta/a/DescargasOrdenadas
```

### 🔐 Permisos de Carpetas
Para acceso a Downloads, Documents, etc.:
1. **Preferencias del Sistema** → **Seguridad y Privacidad**
2. **Privacidad** → **Acceso completo al disco**
3. Agregar Terminal o la aplicación

---

## 📞 Soporte

Si tienes problemas:
1. **Ejecuta:** `./INICIAR.sh` desde Terminal
2. **Revisa:** Los mensajes de error en Terminal
3. **Verifica:** Permisos de ejecución con `ls -la`
4. **Prueba:** Deshabilitar temporalmente Gatekeeper

¡El launcher `INICIAR.sh` está diseñado para funcionar en cualquier Mac sin configuración previa! 