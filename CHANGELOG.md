# 📝 Registro de Cambios

Todos los cambios notables de este proyecto se documentarán en este archivo.

---

## [5.0.3] - 2026-09-22

### 🖱️ Menú contextual de macOS arreglado (daba error en Finder)
- **Causa**: la Acción rápida que se instalaba en `~/Library/Services` no tenía
  los metadatos que Automator necesita (identificador del bundle, clase de la
  acción, UUID…), así que Finder respondía «Automator no ha podido ejecutar el
  flujo de trabajo: la acción no se ha cargado»
- Además, la entrada se configuraba para no recibir las carpetas seleccionadas,
  por lo que, incluso cargando, el script se ejecutaba sin saber qué organizar
- Ahora se genera el flujo con el **formato exacto de los flujos del sistema**
  (verificado contra `Run Shell Script` de `/System/Library/Automator`), de modo
  que Finder lo carga y las rutas llegan al script como argumentos
- **Reparación automática**: si la Acción rápida quedó dañada de una versión
  anterior, la aplicación la detecta al abrirse y la regenera sola; no hay que
  desinstalar ni tocar nada
- También se refresca la caché de servicios (`pbs -flush` y recarga de Finder)
  para que aparezca sin cerrar sesión
- Nueva prueba funcional que valida el flujo con `automator` de verdad

---

## [5.0.2] - 2026-09-22

### 🐛 Actualizaciones que no se detectaban (decía «5.0.0» estando la 5.0.1)
- **Causa**: la comprobación dependía en exclusiva de la API de GitHub, que sin
  autenticar permite 60 peticiones por hora. Al agotarse, GitHub responde 403 y
  la aplicación lo interpretaba como «ya tienes la última versión»… y además
  guardaba la fecha como si hubiera comprobado bien, así que **no reintentaba
  hasta 24 horas después**
- Ahora se prueban **tres canales** en orden:
  1. La API de GitHub (datos completos: notas y archivos adjuntos)
  2. La redirección de `/releases/latest`, que **no tiene límite** y basta para
     saber la versión publicada
  3. La página de etiquetas del repositorio, también sin límite
- Si todos fallan, se avisa con claridad de que **no se pudo comprobar** (ya no
  se dice «estás actualizado» cuando en realidad no se ha mirado) y se reintenta
  más tarde, sin esperar 24 h
- La descarga del instalador ya no depende de la API: se construye la URL
  directa del archivo del sistema (`.exe` / `.pkg` / `.deb`) y se verifica que
  existe antes de descargarlo
- **Migración automática**: los equipos con el archivo de estado antiguo (que
  quedó bloqueado) vuelven a comprobar la actualización en el siguiente arranque
- Nueva prueba funcional que simula el límite de GitHub y la falta de red

---

## [5.0.1] - 2026-09-22

### 🐛 Controles de auto-organización siempre coherentes
- Corregido el fallo por el que el modo Básico/Detallado y la hora se quedaban
  «pinzados»: los radios de Qt no se pueden desmarcar cuando están en grupo, así
  que apagar el interruptor dejaba el estado a medias y el siguiente cambio no
  se aplicaba
- Ahora **todo** (encender, apagar, cambiar de modo y cambiar la hora) pasa por un
  único punto que actualiza a la vez el interruptor, los radios, el
  temporizador, la tarjeta de estado y lo que se guarda para el próximo arranque
- Cambiar «Revisar cada» con la auto-organización encendida aplica el intervalo
  **al momento** y reinicia la cuenta (antes el temporizador seguía con la hora
  anterior)
- Cambiar de modo con la auto-organización **apagada** ya no la enciende sola:
  solo se recuerda la elección para cuando la actives
- Al encender se usa exactamente el modo y la hora que dejaste seleccionados
- Nueva prueba funcional de regresión que cubre todos estos casos

---

## [5.0.0] - 2026-09-22

### 🎨 Diseño nuevo tipo Apple
- La interfaz pasa de pestañas superiores a **barra lateral** con secciones Inicio,
  Actividad, Ajustes y Avanzado
- Nuevo sistema de estilos centralizado (`organizer/estilos.py`): paleta clara y
  oscura de macOS, tipografía nativa de cada sistema, tarjetas, esquinas
  redondeadas, separadores finos y transiciones suaves
- **Tema automático**: sigue el tema claro/oscuro del sistema (Windows, macOS y
  Linux) y se puede forzar Claro u Oscuro en Ajustes
- Cabecera con la carpeta actual y botón principal; animación corta al cambiar de
  sección; los interruptores tienen el tamaño correcto en cualquier resolución

### 🧭 Una sola instancia, siempre
- Bloqueo por archivo + **mutex con nombre en Windows** compartido con el
  instalador: es imposible tener dos copias abiertas
- El canal entre instancias ahora habla JSON y admite órdenes: mostrar la ventana
  u organizar una carpeta
- Si arrancas la app dos veces, la segunda no abre nada: trae al frente la que ya
  está abierta (o le pide el trabajo)

### 🖱️ Menú contextual que por fin funciona
- Nuevo `--organizar-carpeta RUTA`: organiza esa carpeta **sin abrir ventana**
- Si la app ya está abierta, el menú contextual **delega** en ella; si no, lo hace
  por su cuenta y termina
- Windows: se registra en `HKEY_CURRENT_USER` (sin permisos de administrador) y
  también en carpetas y en el fondo de carpeta
- macOS: Acción rápida de Finder, con aviso de los permisos que macOS pida
- Linux: entrada `.desktop` para «Abrir con…» y script de Nautilus, todo en la
  carpeta del usuario (compatible con Flatpak/Snap)
- Los problemas de permisos se avisan de forma clara, nunca revientan

### ⬇️ Actualizar sin dejar copias sueltas
- «Descargar e Instalar» ahora hace el ciclo completo: descarga el instalador
  nativo, **cierra la app**, instala encima y **vuelve a abrirla** actualizada
- Windows: asistente en modo silencioso con `/CLOSEAPPLICATIONS` y mutex
  compartido; macOS: `installer -pkg`; Linux: instalación con permisos explícitos
- Se elimina el riesgo de dos instancias durante la actualización

### 📂 Organización más segura
- Detección de la carpeta de descargas real: registro de Windows, XDG en Linux y
  ~/Downloads en macOS, con creación automática si no existe
- **No se tocan las descargas a medias**: `.part`, `.crdownload`, `.tmp`… se quedan
  donde están para no corromperlas
- Avisos de permisos legibles con pasos concretos según el sistema
- «Cambiar carpeta» ahora permite organizarla una vez o **usarla como carpeta
  principal**, y esa elección se recuerda entre reinicios

### 🚀 Arranque con el sistema
- Linux: se usa el estándar **XDG autostart** (funciona en GNOME, KDE, XFCE…),
  con systemd de usuario como complemento opcional
- macOS: LaunchAgent más robusto (recarga limpia, límite de sesión Aqua, registro
  de errores en /tmp)

### 🪟 Instalador Windows
- `AppMutex` compartido con la aplicación: el asistente nunca se ejecuta con la
  app abierta
- `CloseApplications` / `RestartApplications` para cerrar y reabrir sin duplicados
- Registro de instalación activado para diagnosticar problemas

### 🧪 Pruebas
- 13 pruebas funcionales: organización, descargas en curso, permisos, estilos,
  barra lateral, tema automático, instancia única, menú contextual y CLI

---

## [4.8.0] - 2026-09-22

### 🐛 Automático fiable al arrancar
- La organización automática se activa justo al abrir si estaba activada (sin el retardo que fallaba)
- La tarjeta de estado muestra el estado real desde el primer segundo
- Corregido el modo guardado por defecto (Básico) y el intervalo (1 hora)

### ⬇️ Actualización "Descargar e Instalar" arreglada
- Ahora descarga el instalador nativo de tu sistema (.exe / .pkg / .deb) y lo abre
- Ya no intenta instalar un ZIP del código (fuente del error)

### 🖱️ Menú contextual (Windows)
- Comando corregido para que organice la carpeta seleccionada con `--auto`
- Verificado el registro en macOS (Acción rápida) y Linux (Nautilus / Abrir con)

---

## [4.7.0] - 2026-09-22

### 🎛️ Automático tal como lo dejaste
- Nuevo interruptor encendido/apagado para la organización automática (y para arrancar con el sistema)
- Por defecto: Básico y 1 hora; la elección se restaura al abrir la app sin tocar nada
- Añadida la opción de apagar la organización automática cuando quieras

### 🖱️ Menú contextual
- Corregido el script de Nautilus (Linux) que lanzaba la ordenación sin la carpeta
- Verificado en macOS (Acción rápida de Finder) y Linux (script y "Abrir con")

### 📂 Cambiar carpeta
- Al elegir otra carpeta, se organiza en segundo plano con aviso de progreso
- La carpeta de trabajo vuelve a ser la anterior al terminar

---

## [4.6.1] - 2026-09-21

### 🐛 Corrección de crash al arrancar (macOS)
- El icono de la bandeja se dibuja cerrando siempre el QPainter (try/finally)
- Si el dibujo falla, se usa un icono estándar de carpeta en lugar de romper el arranque
- Afectaba a la 4.5.0/4.6.0 instalada: QPainter sin cerrar podía corromper memoria (SIGSEGV)

---

## [4.6.0] - 2026-09-21

### 🎨 Interfaz afinada
- Solo quedan los temas Minimal claro y Minimal oscuro; los antiguos se retiran (migran al oscuro)
- Pestaña de Ajustes separada de Actividad; las herramientas avanzadas (IA, Fechas, Duplicados, Estadísticas) se agrupan en Avanzado

### 🖱️ Menú contextual en los tres sistemas
- macOS: acción rápida de Finder (clic derecho → Acciones rápidas → Organizar con DescargasOrdenadas)
- Linux: entrada "Abrir con…" para carpetas y script para Nautilus
- Windows: el comando ahora organiza la carpeta seleccionada (antes solo la abría)

---

## [4.5.0] - 2026-09-21

### 🗂️ Carpetas y menú contextual
- La reorganización completa ahora también lleva las carpetas sueltas a Carpetas/
- El menú contextual de Windows apunta a la carpeta elegida y usa el icono de la app
- Icono de bandeja nuevo: carpeta con flecha de ordenación (sin círculo verde ni champiñón)
- Textos de la ventana y de la bandeja más sobrios

---

## [4.4.0] - 2026-09-21

### 🎨 Rediseño minimalista
- Nueva pantalla de inicio con lo esencial: automático (Básico/Detallado), cada cuánto y arrancar con el sistema
- Temas Minimal Claro y Minimal Oscuro, planos y discretos (paleta tipo Apple)
- Ventana más compacta por defecto y pestañas en formato píldora
- Ajustes y actividad reunidos en una sola pestaña; sin colores llamativos

---

## [4.3.0] - 2026-09-21

### 🧭 Una sola instancia
- Nuevo control de instancia única en Windows, macOS y Linux
- Si la app ya está abierta, el segundo arranque la muestra en lugar de duplicarla
- El bloqueo se libera solo, incluso si la app se cierra a la fuerza

### ⚙️ Autoarranque con memoria
- El modo BÁSICO/DETALLADO y el intervalo se guardan y se restauran al arrancar
- El autoarranque del sistema se reescribe con el modo elegido
- Al apagar la auto-organización, el autoarranque deja de auto-organizar

### 🛠️ Otros
- `--nueva-instancia` para forzar una segunda copia si alguien la necesita
- Empaquetado: incluidos PySide6.QtNetwork y el módulo de instancia única

---

## [4.2.0] - 2026-09-19

### 🔁 Reparación en app instalada
- `--reparar-dependencias` ahora busca Python del sistema en modo instalado
- Evita intentar usar `pip` dentro del binario empaquetado

---

## [4.1.0] - 2026-09-19

### 🧰 Dependencias online
- Nuevo `--reparar-dependencias` para descargar e instalar dependencias faltantes
- `--info` ahora muestra las dependencias que faltan
- Instaladores adjuntados automáticamente al release

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
