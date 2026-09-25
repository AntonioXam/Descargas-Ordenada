# DescargasOrdenadas v7.0.1

**Organiza automáticamente tu carpeta de descargas** con una interfaz moderna tipo Apple, menú contextual en los tres sistemas y actualización integrada.

![Versión](https://img.shields.io/badge/versión-7.0.1-blue)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![Estado](https://img.shields.io/badge/estado-funcionando-brightgreen)

---

## 🚀 Inicio Rápido (3 pasos)

### 📦 Descargar instalador

1. Abre la página de [Releases](https://github.com/AntonioXam/Descargas-Ordenada/releases).
2. Descarga el instalador de tu sistema.
3. Ejecútalo y sigue el asistente.

El instalador ya incluye todas las dependencias, así que no tienes que instalar Python ni nada más.

### 💻 Windows

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

### 🍎 macOS / 🐧 Linux

### 1️⃣ Instalar dependencias (solo la primera vez)
```bash
./INSTALAR_DEPENDENCIAS.sh
```
Se creará un entorno virtual (`.venv`) con todas las dependencias, evitando conflictos con el Python del sistema.

### 2️⃣ Iniciar la aplicación
```bash
./INICIAR.sh
```
En macOS también puedes hacer **doble clic en `INICIAR.command`** desde Finder.

### 3️⃣ ¡Listo! 🎉
La aplicación se abre con su interfaz gráfica y puede minimizarse a la barra de menús.

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

## 🔐 Permisos: se piden antes, no se falla después

La aplicación nunca debería fallar porque le falte un permiso. La primera vez
que la abres, un asistente te explica qué necesita y **para qué**, y puedes
omitir lo que no quieras: funciona sin ninguno, con menos funciones.

| Permiso | Para qué sirve | ¿Hace falta? |
|---|---|---|
| Acceso a la carpeta | Leer y organizar los archivos | **Sí**, sin esto no hay nada que hacer |
| Acceso total al disco (macOS) | Añadir «Organizar con DescargasOrdenadas» al clic derecho del Finder | Opcional |
| Control del Finder (macOS) | Que la acción rápida aparezca sin reiniciar la sesión | Opcional |
| Notificaciones | Avisarte cuando termina una organización automática | Opcional |
| Conexión a internet | Buscar actualizaciones | Opcional |

En **Ajustes → Permisos** tienes el estado en vivo de todos ellos, con un botón
que abre el panel exacto donde se conceden. Si concedes uno fuera de la
aplicación, se detecta al volver a ella: no hay que reiniciar nada.

En **Windows no hace falta ser administrador**: el menú contextual se registra
solo para tu usuario, que no requiere permisos especiales.

La transparencia está **apagada por defecto**: en un Mac real dejaba restos del
fotograma anterior al cambiar de sección, así que se activa a propósito con
`DESCARGASORDENADAS_TRANSPARENCIA=1`. Para forzar que esté apagada, usa
`DESCARGASORDENADAS_SIN_TRANSPARENCIA=1`.

---

## ✨ Características Principales

### 🆕 Novedades v7.0
- **Identidad propia «mesa de clasificación»** - Se acabaron las tarjetas: listas alineadas, una línea fina como jerarquía y el carmesí de la seta como sello en la sección activa y en una sola acción por pantalla
- **Números que se alinean** - Recuentos, tamaños, intervalos y rutas van en monoespaciada con cifras tabulares
- **Raíl lateral** - La barra lateral pasa a ser un raíl con los nombres de las secciones y una barra carmesí marcando dónde estás
- **Más ancho de lectura** - El contenido baja de 980 a 760 px para que etiqueta y valor no queden a 750 px de distancia
- **Estado y títulos con jerarquía** - El estado de la app deja de competir en tamaño con el título de la sección
- **Correcciones** - El permiso de notificaciones ya no se pide cuando no consta que falte; la transparencia pasa a estar apagada por defecto (dejaba restos entre fotogramas en macOS); «Deshacer» deja de ser una acción de peligro

### 🆕 Novedades v6.0
- **Permisos que se piden, no que se sufren** - Asistente de primer arranque y centro de permisos con estado en vivo
- **Transparencia real (opcional)** - *Vibrancy* en macOS y efecto Mica en Windows 11, que antes estaban activados pero tapados por el fondo de Qt
- **Iconos propios** - 23 iconos SVG dibujados para la aplicación, en lugar de los genéricos del sistema
- **Adaptable de verdad** - La barra lateral pasa a flotante en ventanas estrechas y la ventana puede encogerse a 620×520 (antes no bajaba de 760×560)
- **Nada falla en silencio** - Los errores se explican en una ventana legible y quedan guardados en `errores.log`
- **Un solo sistema de estilos** - Se retiró el antiguo, con sus degradados y botones de otra época

### 🆕 Novedades v5.0
- **Diseño tipo Apple** - Barra lateral, tarjetas, tipografía del sistema y **tema automático** (sigue al del sistema operativo)
- **Menú contextual que funciona** - Clic derecho sobre una carpeta → organizar en segundo plano, sin abrir ventana
- **Una sola instancia, siempre** - Es imposible tener dos copias abiertas; si arrancas dos veces, se trae al frente la que ya está
- **Actualización sin restos** - «Descargar e Instalar» cierra la app, instala encima y la vuelve a abrir actualizada
- **Arranque seguro** - Linux con XDG autostart, macOS con LaunchAgent robusto, Windows con registro
- **Descargas en curso respetadas** - Los archivos `.part`, `.crdownload`, etc. no se mueven para no corromperlos
- **Permisos claros** - Si el sistema bloquea una carpeta, se explica qué hacer, sin errores crípticos

### 🆕 Novedades v3.3
- 🔧 **Actualizaciones Corregidas** - Ahora apunta al repositorio correcto de GitHub
- 📌 **Versión Centralizada** - `VERSION.txt` es la única fuente de verdad
- 🧮 **Comparación de Versiones** - Compatible con formatos 3.3 y 3.3.0
- 🎨 **Footer Dinámico** - La GUI muestra siempre la versión real

### 🆕 Novedades v3.4
- 🍎 **Soporte macOS** - Corregido el bloqueo de arranque (import de `winreg`) y autoarranque con LaunchAgent
- 🐧 **Soporte Linux** - Lanzadores de terminal y autoarranque con systemd
- ⚙️ **Entorno Virtual** - El instalador crea `.venv` automáticamente en Mac/Linux
- 🔄 **Reinicio Multiplataforma** - Las actualizaciones ya no fallan al reiniciar en Mac/Linux

### 🆕 Novedades v3.5
- 🖥️ **Interfaz Responsive** - Todas las pestañas se adaptan con scroll automático en pantallas pequeñas
- 🚀 **Autoarranque Mejorado** - Notificación nativa al activarlo y arranque minimizado en macOS, Linux y Windows
- 🔄 **Actualizaciones con Fallback** - Si no hay Release en GitHub, usa tags del repositorio
- 📦 **Portable** - Funciona sin instalar nada más que sus dependencias

### 🖥️ Pantallas Pequeñas
- La ventana se ajusta automáticamente a tu resolución
- Si un campo no cabe, aparece una barra de desplazamiento
- La app recuerda el tamaño de la ventana y si la dejaste maximizada
- Ya no necesitas ampliar la ventana a tamaños fijos

### 🆕 Novedades v3.6
- 📦 **Instaladores automáticos** - Windows `.exe`, macOS `.pkg` y Linux `.deb`
- 🔐 **Permisos del sistema** - Los instaladores piden permisos de administrador
- 🧩 **Todo incluido** - Las dependencias se empaquetan dentro del instalador
- 🚀 **Sin scripts** - Ya no hace falta abrir `.bat` ni `.sh`

### 🆕 Novedades v3.2
- ⏱️ **Intervalos Personalizables** - Elige cada cuánto revisar (30 seg a 1 día)
- 🚀 **Inicio Automático Mejorado** - Botones claros para activar/desactivar
- ⬇️ **Descarga Automática** - Actualiza con un click desde GitHub
- 🎨 **Interfaz Mejorada** - Textos más claros y legibles

### 🎯 Funcionalidades v3.1
- 🔔 **Notificaciones Nativas** - Alertas del sistema
- 🎨 **Temas claro y oscuro** - Con modo automático según el sistema
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
├── 📄 organizer/INICIAR.py        ← Script principal
│
├── 📚 docs/                      ← Documentación completa
├── 🛠️ scripts/                   ← Scripts auxiliares y pruebas
├── 🍄 organizer/                 ← Código de la aplicación
├── 📦 resources/                 ← Iconos y recursos
└── ⚙️ .config/                   ← Tu configuración
```

---

## 🎯 Uso Básico

### Comandos útiles
```bash
python organizer/INICIAR.py --version
python organizer/INICIAR.py --info
python organizer/INICIAR.py --reparar-dependencias
python organizer/INICIAR.py --auto
python organizer/INICIAR.py --auto --dry-run
python organizer/INICIAR.py --auto --modo basico
python organizer/INICIAR.py --auto --modo detallado --recursivo
```

- `--dry-run` muestra qué haría la app sin mover archivos.
- `--reparar-dependencias` descarga e instala las dependencias que falten.
- `--modo basico` usa carpetas principales.
- `--modo detallado` usa subcarpetas por tipo.
- `--recursivo` busca también dentro de subcarpetas.

### Organización Manual
1. Abre la aplicación (INICIAR.bat)
2. Pulsa **"Organizar ahora"**
3. ¡Listo! Tus archivos están organizados

### Organización Automática
1. Abre la aplicación
2. Elige el intervalo (ej: "1 minuto")
3. Activa **"Básico"** o **"Detallado"**
4. La aplicación organizará automáticamente cada X tiempo

### Inicio con el sistema
1. Marca **"Inicio automático"**
2. ¡Ya está! La app se inicia minimizada al encender Windows, macOS o Linux

---

## 🎨 Temas Disponibles

| Tema | Descripción |
|------|-------------|
| ☀️ **Claro** | Papel cálido con tinta oscura |
| 🌙 **Oscuro** | Fondo profundo con el mismo carmesí de marca |
| 🔄 **Automático** | Sigue el tema del sistema (predeterminado) |

---

## 📊 Requisitos

### Sistema
- Windows 10/11, macOS (11 o posterior) o Linux con escritorio
- 100 MB de espacio libre
- Conexión a internet (para actualizaciones)

### Dependencias (se instalan automáticamente)
- Python 3.9+
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
python scripts/PRUEBAS_FUNCIONALES.py
```

### Los textos se ven cortados
- Amplía la ventana de la aplicación
- Resolución mínima recomendada: 1024x768

### Más ayuda
- Lee la guía completa: `docs/COMO_USAR.md`
- Consulta las mejoras por versión: `CHANGELOG.md`

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

**Versión:** 7.0.1  
**Fecha:** Septiembre 2026  
**Estado:** ✅ Funcional y estable
