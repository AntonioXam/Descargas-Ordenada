# 📝 Registro de Cambios

Todos los cambios notables de este proyecto se documentarán en este archivo.

---

## [4.0.0] - 2026-09-19

### 🎉 Versión estable multiplataforma
- CLI con diagnóstico, simulación y modos de organización
- Instaladores automáticos para Windows, macOS y Linux
- GUI responsive con scroll y tamaño de ventana persistente
- Autoarranque unificado en Windows, macOS y Linux

---

## [3.9.0] - 2026-09-19

### 🧭 Organización configurable desde terminal
- Nuevo `--modo basico` y `--modo detallado`
- Nuevo `--recursivo` para procesar también las subcarpetas

---

## [3.8.0] - 2026-09-19

### 🧪 Modo simulación
- Nuevo argumento `--dry-run` para ver qué se organizaría sin mover archivos
- No crea carpetas ni modifica la huella de archivos procesados

---

## [3.7.0] - 2026-09-19

### 🧭 Diagnóstico desde terminal
- Nuevo argumento `--version` para ver la versión exacta
- Nuevo argumento `--info` para ver sistema, Python, rutas y módulos avanzados

---

## [3.6.0] - 2026-09-17

### 📦 Instaladores por Sistema
- Windows: instalador `.exe` con Inno Setup
- macOS: instalador `.pkg` nativo con `productbuild`
- Linux: paquete `.deb` listo para instalar

### 🔐 Permisos y Dependencias
- Los instaladores piden permisos de administrador
- Todas las dependencias van incluidas dentro de la app
- No hace falta ejecutar `.bat` ni `.sh`

### 🛠️ Empaquetado
- Nuevo spec de PyInstaller multiplataforma
- Recursos, iconos y `VERSION.txt` se incluyen en el paquete
- Configuración compatible con app instalada en cada sistema

---

## [3.5.0] - 2026-09-17

### 🖥️ Interfaz Responsive
- Las pestañas ahora usan scroll automático en pantallas pequeñas
- Tamaño mínimo de ventana reducido para caber en más resoluciones
- La app recuerda el tamaño y el estado maximizado entre sesiones
- Todos los campos siguen accesibles aunque la ventana no esté maximizada

### 🚀 Autoarranque Multiplataforma
- macOS usa LaunchAgent y Linux usa systemd con los argumentos reales
- Se guarda la preferencia de inicio automático en la configuración
- Se muestra una notificación nativa al activarlo o desactivarlo
- La app arranca minimizada en la bandeja del sistema

### 🔄 Actualizaciones
- Si no hay Release publicado en GitHub, ahora usa los tags del repo como fallback

### 🐧 Linux
- Autoarranque corregido con el intérprete correcto y argumentos reales

---

## [3.4.0] - 2026-09-17

### 🍎 Soporte macOS Completo

#### 🐛 Corrección Crítica de Arranque
- **Corregido el bloqueo total en macOS** - `autostart.py` importaba `winreg` (exclusivo de Windows) sin condición y la GUI lo importa siempre, por lo que la aplicación **ni siquiera arrancaba** en Mac. Ahora el import es condicional

#### 🚀 Autoarranque en macOS
- **LaunchAgent corregido** - Usaba el argumento `--auto-organizar` (inexistente); ahora usa `--autostart --minimizado`, los argumentos reales de `INICIAR.py`
- **Rutas con espacios** - El XML del plist ahora escapa correctamente espacios y caracteres especiales
- **launchctl moderno** - Usa `bootstrap`/`bootout` (sintaxis actual de macOS) con fallback a `load`/`unload` para versiones antiguas

#### 🔄 Actualizaciones en macOS
- **Reinicio corregido** - Tras actualizar, usaba constantes exclusivas de Windows (`DETACHED_PROCESS`, `CREATE_NO_WINDOW`) que no existen en Mac/Linux y provocaban error. Ahora cada plataforma usa su mecanismo correcto (`start_new_session` en Unix)

### 🐧 Soporte Linux
- Autoarranque con systemd ya existía; los nuevos lanzadores de terminal lo hacen usable de principio a fin

### ⚙️ Lanzadores Multiplataforma
- `INSTALAR_DEPENDENCIAS.sh` - Instalador para Mac/Linux que crea un entorno virtual `.venv` (evita el Python "externally-managed" de macOS/Homebrew)
- `INICIAR.sh` - Lanzador de terminal que usa el `.venv` si existe
- `INICIAR.command` y `INSTALAR_DEPENDENCIAS.command` - Doble clic desde Finder en macOS

### ✅ Pruebas
- Nuevas pruebas de regresión multiplataforma: import de `autostart` en cualquier SO y existencia de lanzadores

---

## [3.3.0] - 2026-09-17
## [3.3.0] - 2026-09-17

### 🔧 Correcciones Críticas

#### 🔄 Sistema de Actualizaciones
- **Corregido el repositorio de GitHub** - Apuntaba a `AntonioIbanez1` (inexistente) y ahora apunta a `AntonioXam/Descargas-Ordenada`, por lo que la búsqueda de versiones vuelve a funcionar
- **Corregido el módulo antiguo** `actualizaciones.py` - Usaba una URL de ejemplo (`usuario/descargasordenadas`) y versión 3.1.0

### 📌 Versión Centralizada
- Nuevo módulo `organizer/version.py` - `VERSION.txt` es ahora la única fuente de verdad de la versión
- Todos los módulos (GUI, actualizaciones, arranque) leen la versión del mismo sitio
- Eliminadas las versiones duplicadas y desincronizadas (3.1.0, 3.2.0 y 1.0.0 en distintos archivos)

### 🧮 Mejoras Técnicas
- Comparación de versiones semánticas rellenando con ceros - `3.3` y `3.3.0` ahora se comparan correctamente
- El footer de la GUI muestra la versión dinámicamente en lugar de un texto fijo
- `__version__` del paquete `organizer` ahora se sincroniza con `VERSION.txt`

### 📚 Documentación
- Corregidas todas las URLs de GitHub en docs y scripts (antes apuntaban al usuario equivocado)

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
