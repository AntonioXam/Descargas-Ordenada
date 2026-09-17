# 🍄 DescargasOrdenadas v3.2

**Organiza automáticamente tu carpeta de descargas** con inteligencia artificial, temas personalizables y actualización automática.

![Versión](https://img.shields.io/badge/versión-3.3.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Estado](https://img.shields.io/badge/estado-funcionando-brightgreen)

---

## 🚀 Inicio Rápido (3 pasos)

### 1️⃣ Instalar dependencias (solo la primera vez)
```bash
INSTALAR_DEPENDENCIAS.bat
```
**Nota:** Si no tienes internet, coloca la carpeta `dependencias/` con los archivos .whl y se instalarán desde ahí.

### 2️⃣ Iniciar la aplicación
```bash
INICIAR.bat
```

### 3️⃣ ¡Listo! 🎉
La aplicación se abre sin consola y aparece en la bandeja del sistema.

---

## 📦 Instalación Sin Internet

Si necesitas instalar en un PC sin internet:

1. **En un PC con internet:**
   ```bash
   cd scripts
   DESCARGAR_DEPENDENCIAS.bat
   ```
   Esto creará una carpeta `dependencias/` con todos los archivos .whl

2. **Copia toda la carpeta del proyecto** (incluyendo `dependencias/`) al PC sin internet

3. **En el PC sin internet:**
   ```bash
   INSTALAR_DEPENDENCIAS.bat
   ```
   Detectará automáticamente la carpeta `dependencias/` y instalará desde ahí

---

## ✨ Características Principales

### 🆕 Novedades v3.3
- 🔧 **Actualizaciones Corregidas** - Ahora apunta al repositorio correcto de GitHub
- 📌 **Versión Centralizada** - `VERSION.txt` es la única fuente de verdad
- 🧮 **Comparación de Versiones** - Compatible con formatos 3.3 y 3.3.0
- 🎨 **Footer Dinámico** - La GUI muestra siempre la versión real

### 🆕 Novedades v3.2
- ⏱️ **Intervalos Personalizables** - Elige cada cuánto revisar (30 seg a 1 día)
- 🚀 **Inicio Automático Mejorado** - Botones claros para activar/desactivar
- ⬇️ **Descarga Automática** - Actualiza con un click desde GitHub
- 🎨 **Interfaz Mejorada** - Textos más claros y legibles

### 🎯 Funcionalidades v3.1
- 🔔 **Notificaciones Nativas** - Alertas del sistema
- 🎨 **5 Temas** - Azul, Verde, Púrpura, Naranja, Gris
- 💾 **100% Portable** - Copia y funciona en cualquier PC
- 🖱️ **Menú Contextual** - Click derecho en carpetas
- 🔄 **Actualizaciones Automáticas** - Se descarga e instala sola desde GitHub (sin necesidad de cuenta)

### ⚡ Características Base
- 📁 **Organización Automática** - Cada X tiempo o manual
- 🤖 **IA Integrada** - Categorización inteligente
- 📅 **Por Fechas** - YYYY/MM-Mes, YYYY/MM, etc.
- 🔍 **Detector de Duplicados** - Encuentra y elimina
- 🪟 **Sin Consola** - Ejecuta sin ventana de comandos
- 🍄 **Bandeja del Sistema** - Minimiza y sigue funcionando

---

## 📁 Estructura del Proyecto

```
Descargas-Ordenada/
│
├── 🚀 INICIAR.bat                 ← EJECUTA ESTO
├── 🔧 INSTALAR_DEPENDENCIAS.bat  ← Solo primera vez
├── 📄 INICIAR.py                 ← Script principal
├── 📖 LEEME.txt                  ← Guía rápida
│
├── 📚 docs/                      ← Documentación completa
├── 🛠️ scripts/                   ← Scripts auxiliares
├── 🍄 organizer/                 ← Código de la aplicación
├── 📦 resources/                 ← Iconos y recursos
└── ⚙️ .config/                   ← Tu configuración
```

---

## 🎯 Uso Básico

### Organización Manual
1. Abre la aplicación (INICIAR.bat)
2. Click en **"✨ Organizar archivos nuevos"**
3. ¡Listo! Tus archivos están organizados

### Organización Automática
1. Abre la aplicación
2. Elige el intervalo (ej: "⚡ 1 minuto")
3. Activa **"📁 Modo BÁSICO"** o **"🔧 Modo DETALLADO"**
4. La aplicación organizará automáticamente cada X tiempo

### Inicio con Windows
1. Click en **"✅ Activar inicio automático"**
2. ¡Ya está! La app se inicia al encender el PC

---

## 🎨 Temas Disponibles

| Tema | Descripción |
|------|-------------|
| 🔵 **Azul Oscuro** | Moderno y profesional (predeterminado) |
| 🟢 **Verde Oscuro** | Natural y relajante |
| 🟣 **Púrpura** | Elegante y distintivo |
| 🟠 **Naranja** | Energético y cálido |
| ⚫ **Gris** | Clásico y minimalista |

---

## 📊 Requisitos

### Sistema
- Windows 10/11
- 100 MB de espacio libre
- Conexión a internet (para actualizaciones)

### Dependencias (se instalan automáticamente)
- Python 3.8+
- PySide6 ≥6.5.0
- Pillow ≥10.0.0
- watchdog ≥3.0.0
- pywin32 ≥300
- requests ≥2.31.0
- plyer ≥2.1.0

---

## ⚠️ Solución de Problemas

### La aplicación no inicia
```bash
# Reinstalar dependencias
INSTALAR_DEPENDENCIAS.bat

# Verificar instalación
cd scripts
python PRUEBAS_v3.1.py
```

### Los textos se ven cortados
- Amplía la ventana de la aplicación
- Resolución mínima recomendada: 1024x768

### Más ayuda
- Lee la guía completa: `docs\GUIA_COMPLETA_v3.1.txt`
- Consulta la documentación: `docs\README.md.backup`

---

## 🔄 Sistema de Actualizaciones Automáticas

### ¿Cómo funciona?

1. **Verificación Automática** - Al abrir la app, revisa si hay nuevas versiones en GitHub
2. **Descarga con 1 Click** - Pulsa "⬇️ Descargar e Instalar" y listo
3. **Instalación Automática** - Se descomprime en la misma carpeta, preservando tu configuración
4. **Reinicio Automático** - La app se cierra y se abre sola con la nueva versión

### Sin Necesidad de Cuenta

- ✅ **GitHub Público** - No necesitas tener cuenta ni permisos
- ✅ **Sin Tokens** - Funciona sin configuración
- ✅ **Comprobación de Versión** - Solo descarga si hay una versión más nueva
- ✅ **Backup Automático** - Crea respaldo antes de actualizar

### Buscar Actualizaciones Manualmente

Click en el botón **"🔍 Buscar Actualizaciones"** en la pestaña de Configuración.

---

## 📚 Documentación Completa

Toda la documentación está en la carpeta **`docs/`**:

- 📖 **COMO_USAR.md** - Guía de uso
- 📖 **BANDEJA_SISTEMA.md** - Cómo usar la bandeja del sistema
- 📖 **CREAR_PORTABLES.md** - Crear versión portable
- 📖 **INSTRUCCIONES_PORTABLE.md** - Modo portable
- 📖 **MEJORAS_IMPLEMENTADAS.md** - Historial de cambios

---

## 🤝 Contribuir

¿Encontraste un bug o tienes una idea? ¡Abre un issue en GitHub!

---

## 📄 Licencia

MIT License - Creado por Champi 🍄

---

## 🎉 ¡Disfruta!

**Mantén tu carpeta de descargas siempre organizada automáticamente** 🍄✨

**Versión:** 3.3.0  
**Fecha:** Septiembre 2026  
**Estado:** ✅ Funcional y estable
