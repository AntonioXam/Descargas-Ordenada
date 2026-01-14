# 📝 Registro de Cambios

Todos los cambios notables de este proyecto se documentarán en este archivo.

---

## [3.2.0] - 2026-01-14

### ✨ Nuevas Funcionalidades

#### ⏱️ Intervalos Personalizables
- Selector de tiempo para auto-organización con opciones:
  - ⚡ 30 segundos
  - 🕐 1 minuto
  - 🕐 5 minutos
  - 🕐 10 minutos
  - 🕐 30 minutos
  - 🕐 1 hora
  - 📅 1 día
- El intervalo seleccionado se muestra en tiempo real en el estado y logs

#### 🚀 Gestión de Inicio Mejorada
- Botón dedicado **"Agregar al Inicio"** para activar arranque automático
- Botón dedicado **"Quitar del Inicio"** para desactivar arranque automático
- Se eliminó el checkbox confuso de "Iniciar con el sistema"
- Mensajes claros de confirmación

#### 🔄 Actualizaciones Completamente Automáticas
- **Descarga automática** desde GitHub (repositorio público)
- **Instalación automática** en la misma carpeta
- **Reinicio automático** de la aplicación tras actualizar
- **Backup automático** antes de actualizar
- **Preservación de configuración** (.config/)
- **Verificación de versión** - Solo descarga si hay versión nueva
- **Sin necesidad de cuenta GitHub** - Acceso público
- **Barra de progreso** durante la descarga

### 🎨 Mejoras de Interfaz

#### Ventana Principal
- Tamaño inicial: 1200x850 (antes 1000x700)
- Tamaño mínimo: 1100x800
- Todos los campos visibles sin scroll
- Footer con versión "v3.2.0" en pequeño (abajo derecha)

#### Títulos
- **Antes:** "DescargasOrdenadas v3.0 - Funcionalidades Completas"
- **Ahora:** "🍄 DescargasOrdenadas - Organizador Automático"
- Versión solo en el footer (discreta)
- Headers genéricos sin número de versión

#### Textos Dinámicos
- Estado de auto-organización muestra el intervalo real
- Tooltip de bandeja del sistema actualizado con intervalo
- Logs con información precisa del tiempo configurado

### 🧹 Limpieza del Proyecto

#### Documentación Eliminada (25 archivos)
Se eliminó documentación redundante y temporal:
- Todos los `RESUMEN_*.txt`
- Todos los `GUIA_*.txt` duplicados
- Archivos de estado temporal
- Instrucciones de desarrollo

#### Scripts Eliminados (9 archivos)
Se eliminaron scripts de desarrollo temporal:
- Scripts de configuración manual de GitHub
- Scripts de pruebas de desarrollo
- Scripts de integración de versiones

#### Documentación Conservada
Solo se mantiene documentación útil para usuarios:
- ✅ `README.md` (principal)
- ✅ `docs/COMO_USAR.md`
- ✅ `docs/BANDEJA_SISTEMA.md`
- ✅ `docs/CREAR_PORTABLES.md`
- ✅ `docs/INSTRUCCIONES_PORTABLE.md`
- ✅ `docs/MEJORAS_IMPLEMENTADAS.md`
- ✅ `docs/ACTUALIZACIONES.md` (nuevo)
- ✅ `docs/PUBLICAR_EN_GITHUB.md` (nuevo)

### 🔧 Cambios Técnicos

#### Sistema de Actualizaciones
- Versión actual: `3.2.0`
- GitHub User: `AntonioIbanez1`
- GitHub Repo: `Descargas-Ordenada`
- API URL pública sin autenticación
- Función `reiniciar_aplicacion()` mejorada
- Script batch temporal para reinicio en Windows

#### Configuración
- Nuevo archivo `VERSION.txt` con la versión actual
- Script `scripts/PREPARAR_RELEASE.bat` para crear releases
- Módulo `actualizaciones_mejorado.py` actualizado a v3.2.0

### 📄 Archivos Nuevos
- `VERSION.txt`
- `CHANGELOG.md`
- `docs/ACTUALIZACIONES.md`
- `docs/PUBLICAR_EN_GITHUB.md`
- `scripts/PREPARAR_RELEASE.bat`

### 🐛 Correcciones
- Arreglado: Intervalo de auto-organización siempre mostraba "30 seg"
- Arreglado: Versión hardcodeada en múltiples lugares
- Arreglado: Ventana pequeña que cortaba campos
- Arreglado: Confusión entre checkbox y botones de inicio

### 🗑️ Archivos Eliminados
- 25 archivos de documentación temporal
- 9 scripts de desarrollo
- `INICIAR_SIN_CONSOLA.pyw` (consolidado en INICIAR.bat)

---

## [3.1.0] - 2026-01-13

### ✨ Nuevas Funcionalidades

#### 🔔 Notificaciones Nativas
- Integración con el sistema de notificaciones de Windows
- Librería `plyer` para notificaciones multiplataforma
- Checkbox para activar/desactivar
- Fallback a notificaciones Qt si plyer no está disponible

#### 🎨 Sistema de Temas
- 5 temas personalizables:
  - 🔵 Azul Oscuro (predeterminado)
  - 🟢 Verde Oscuro
  - 🟣 Púrpura
  - 🟠 Naranja
  - ⚫ Gris
- Selector de tema en tiempo real
- Configuración guardada entre sesiones

#### 💾 Configuración Portable
- Sistema de configuración JSON portable
- Archivo `.config/descargasordenadas_config.json`
- Guarda:
  - Tema seleccionado
  - Notificaciones activas
  - Última carpeta seleccionada
  - Tamaño y posición de ventana
  - Última verificación de actualizaciones

#### 🖱️ Menú Contextual de Windows
- Opción "Organizar con DescargasOrdenadas" al hacer click derecho en carpetas
- Registro en el registro de Windows
- Checkbox para activar/desactivar
- Funciona con `pywin32`

#### 🔄 Sistema de Actualizaciones
- Verificación automática desde GitHub
- Descarga manual desde la interfaz
- Comprobación de versión semántica
- Notificación de nuevas versiones disponibles

### 🔧 Mejoras Técnicas
- Módulos separados para cada funcionalidad
- Imports con try-except para dependencias opcionales
- Logging mejorado
- Manejo de errores robusto

---

## [3.0.0] - 2026-01-12

### ✨ Versión Base

- 📁 Organización automática de archivos
- 🤖 Categorización con IA
- 📅 Organización por fechas
- 🔍 Detector de duplicados
- 🪟 Ejecución sin consola
- 🍄 Icono en bandeja del sistema
- 📋 Sistema de logs
- 🎨 Interfaz gráfica con PySide6
- 📊 Vista de estadísticas
- ⚙️ Configuración avanzada

---

## Formato

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

### Tipos de Cambios
- **✨ Nuevas Funcionalidades** - Para funciones nuevas
- **🎨 Mejoras de Interfaz** - Cambios visuales
- **🐛 Correcciones** - Arreglos de bugs
- **🔧 Cambios Técnicos** - Refactorización, optimización
- **🗑️ Eliminado** - Funciones/archivos eliminados
- **📄 Documentación** - Solo cambios en documentación
- **🔒 Seguridad** - Vulnerabilidades corregidas
