# 🍄 DescargasOrdenadas v3.2

**Organiza automáticamente tu carpeta de descargas** con inteligencia artificial, temas personalizables, actualización automática y modo 100% portable.

![Estado](https://img.shields.io/badge/estado-funcionando-brightgreen)
![Versión](https://img.shields.io/badge/versión-3.2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Licencia](https://img.shields.io/badge/licencia-MIT-green)

---

## 🚀 Inicio Rápido

### ¿Primera vez?

```bash
# 1. Instalar dependencias (solo la primera vez)
INSTALAR_DEPENDENCIAS.bat

# 2. Iniciar la aplicación
INICIAR.bat
```

**¡Eso es todo!** La aplicación se abre sin consola y aparece en la bandeja del sistema.

---

## ✨ Características v3.2

### 🆕 Novedades v3.2

- **⏱️ Intervalos Personalizables** - Elige entre 30 seg, 1 min, 5 min, 10 min, 30 min, 1 hora, 6 horas, 12 horas o 1 día
- **⬇️ Descarga Automática** - Descarga e instala actualizaciones automáticamente desde GitHub
- **🚀 Gestión Startup Mejorada** - Botones claros para añadir/quitar del inicio de Windows
- **🎨 Estilos Mejorados** - Interfaz más pulida y moderna

### 🎉 Características v3.1

- **🔔 Notificaciones Nativas** - Alertas del sistema cuando se organizan archivos
- **🎨 5 Temas Personalizables** - Azul, Verde, Púrpura, Naranja, Gris
- **💾 Configuración Portable** - Copia la carpeta a otro PC y mantiene tu configuración
- **🖱️ Menú Contextual** - Click derecho en carpetas → "Organizar con DescargasOrdenadas"
- **🔄 Actualizaciones Automáticas** - Verifica nuevas versiones automáticamente

### ⚡ Características Principales

- ✅ **Organización Automática** - Personaliza el intervalo (30 seg a 1 día)
- ✅ **Inteligencia Artificial** - Categorización inteligente de archivos
- ✅ **Organización por Fechas** - YYYY/MM-Mes, YYYY/MM, etc.
- ✅ **Detector de Duplicados** - Encuentra y elimina duplicados
- ✅ **Sin Consola** - Ejecuta sin ventana de comandos
- ✅ **Bandeja del Sistema** - Minimiza y sigue funcionando
- ✅ **Inicio Automático** - Inicia con Windows
- ✅ **100% Portable** - Copia y funciona en cualquier PC

---

## 📦 Instalación

### Windows

```bash
# Automático (recomendado)
INSTALAR_DEPENDENCIAS.bat

# Manual
pip install PySide6 Pillow watchdog pywin32 requests plyer
```

### Verificar Instalación

```bash
python PRUEBAS_v3.1.py
```

Debe mostrar: ✅ 11/11 pruebas exitosas

---

## 🎯 Uso

### Iniciar la Aplicación

**Opción 1: Doble clic**
```
INICIAR.bat
```

**Opción 2: Python**
```bash
python INICIAR.py --gui
```

**Opción 3: Sin consola**
```bash
pythonw INICIAR_SIN_CONSOLA.pyw
```

### Acceder a Controles v3.1

1. Abre la aplicación
2. Ve a: **Pestaña Principal**
3. Baja hasta: **Sección "Configuración"**

Verás:
- ☑ **🔔 Notificaciones nativas del sistema**
- **🎨 Tema visual:** [Selector con 5 opciones]
- ☑ **🖱️ Menú contextual (Click derecho)**
- **[🔄 Buscar Actualizaciones]**

---

## 🎨 Temas Disponibles

| Tema | Descripción |
|------|-------------|
| 🔵 **Azul Oscuro** | Tema por defecto, moderno y profesional |
| 🟢 **Verde Oscuro** | Natural y relajante |
| 🟣 **Púrpura** | Elegante y distintivo |
| 🟠 **Naranja** | Energético y cálido |
| ⚫ **Gris** | Clásico y minimalista |

El tema se aplica **instantáneamente** y se guarda automáticamente.

---

## 📁 Estructura del Proyecto

```
Descargas-Ordenada/
│
├── INICIAR.bat                    ← Iniciar aplicación (SIN consola)
├── INICIAR.py                     ← Script principal
├── INICIAR_SIN_CONSOLA.pyw        ← Alternativa Python sin consola
│
├── INSTALAR_DEPENDENCIAS.bat      ← Instalador automático
├── INSTALAR.py                    ← Instalador inteligente
├── PRUEBAS_v3.1.py                ← Script de verificación
│
├── organizer/
│   ├── file_organizer.py          ← Organizador principal
│   ├── gui_avanzada.py            ← Interfaz gráfica
│   ├── autostart.py               ← Inicio automático
│   │
│   ├── native_notifications.py    ← 🆕 Notificaciones v3.1
│   ├── portable_config.py         ← 🆕 Configuración v3.1
│   ├── temas.py                   ← 🆕 Temas v3.1
│   ├── context_menu.py            ← 🆕 Menú contextual v3.1
│   └── actualizaciones.py         ← 🆕 Actualizaciones v3.1
│
├── .config/                       ← Configuración portable
│   ├── descargasordenadas_config.json
│   └── actualizaciones.json
│
└── README.md                      ← Este archivo
```

---

## 🔧 Configuración Portable

### ¿Qué se guarda?

- ✅ Tema seleccionado
- ✅ Notificaciones activadas/desactivadas
- ✅ Tamaño y posición de ventana
- ✅ Última carpeta usada
- ✅ Configuración de IA
- ✅ Todas tus preferencias

### Ubicación

```
.config/descargasordenadas_config.json
```

### Migrar a Otro PC

1. Copia **toda la carpeta** del proyecto (incluyendo `.config/`)
2. Ejecuta: `INSTALAR_DEPENDENCIAS.bat` en el PC nuevo
3. Ejecuta: `INICIAR.bat`
4. ¡Tu configuración ya está ahí! ✨

---

## 🖱️ Menú Contextual de Windows

### Activar

1. Abre la aplicación
2. Ve a: Configuración
3. Marca: ☑ **🖱️ Menú contextual**

### Usar

1. Click derecho en **cualquier carpeta**
2. Selecciona: **"🍄 Organizar con DescargasOrdenadas"**
3. ¡La carpeta se organiza automáticamente!

---

## 🔄 Actualizaciones

### Verificación Automática

- La aplicación verifica actualizaciones **cada 24 horas**
- Si hay nueva versión, te muestra un diálogo

### Verificación Manual

1. Abre la aplicación
2. Ve a: Configuración
3. Click en: **[🔄 Buscar Actualizaciones]**

---

## 📊 Dependencias

### Críticas (Requeridas)

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| PySide6 | ≥6.5.0 | Interfaz gráfica |
| Pillow | ≥10.0.0 | Procesamiento de imágenes |
| watchdog | ≥3.0.0 | Monitor de archivos |
| pywin32 | ≥300 | APIs de Windows |

### Opcionales (Recomendadas)

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| requests | ≥2.31.0 | Actualizaciones automáticas |
| plyer | ≥2.1.0 | Notificaciones nativas |

---

## 🧪 Pruebas

### Ejecutar Todas las Pruebas

```bash
python PRUEBAS_v3.1.py
```

### Resultado Esperado

```
✅ Pruebas exitosas: 11/11 (100%)

Módulos principales: 4/4
Módulos v3.1: 5/5
Dependencias: 2/2
```

---

## ⚠️ Solución de Problemas

### La aplicación no se abre

```bash
# 1. Verificar dependencias
python PRUEBAS_v3.1.py

# 2. Reinstalar dependencias
INSTALAR_DEPENDENCIAS.bat

# 3. Probar inicio manual
python INICIAR.py --gui
```

### No veo los controles v3.1

```bash
# 1. Cerrar la aplicación completamente
# 2. Verificar módulos
python -c "from organizer.temas import obtener_gestor_temas; print('OK')"

# 3. Reiniciar
INICIAR.bat
```

### Las notificaciones no funcionan

```bash
# Instalar plyer
pip install plyer

# Reiniciar aplicación
INICIAR.bat
```

### Error al iniciar

Si ves: `'OrganizadorAvanzado' object has no attribute '_toggle_notificaciones'`

**Solución:**
```bash
# Ejecutar script de reparación
python FORZAR_INTEGRACION_GUI.py

# Reiniciar
INICIAR.bat
```

---

## 📚 Documentación Completa

- **INICIO_RAPIDO.txt** - Guía de inicio rápido
- **GUIA_COMPLETA_v3.1.txt** - Documentación detallada
- **COMPLETADO_v3.1.txt** - Resumen técnico
- **COMO_USAR_v3.1.txt** - Instrucciones de uso

---

## 🎯 Casos de Uso

### Organización Básica

```python
# La aplicación organiza automáticamente:
archivo.pdf → Documentos/PDFs/
imagen.png → Imágenes/PNG/
video.mp4 → Videos/MP4/
musica.mp3 → Música/MP3/
```

### Organización por Fechas

```python
# Con patrón YYYY/MM-Mes:
archivo.pdf → Fechas/2026/01-Enero/Documentos/PDFs/
```

### Organización con IA

```python
# La IA detecta patrones:
"informe_2025.pdf" → Documentos/Trabajo/
"vacaciones.jpg" → Imágenes/Personal/
```

---

## 🛠️ Desarrollo

### Requisitos de Desarrollo

```bash
pip install -r requirements.txt
```

### Estructura de Módulos v3.1

```python
# Notificaciones
from organizer.native_notifications import obtener_notificador

# Configuración
from organizer.portable_config import obtener_config

# Temas
from organizer.temas import obtener_gestor_temas

# Menú contextual
from organizer.context_menu import GestorMenuContextual

# Actualizaciones
from organizer.actualizaciones import obtener_gestor_actualizaciones
```

---

## 🤝 Contribuir

¿Encontraste un bug o tienes una idea? ¡Abre un issue!

---

## 📄 Licencia

MIT License - Creado por Champi 🍄

---

## 🎉 Agradecimientos

Gracias por usar DescargasOrdenadas v3.1

**¡Mantén tu carpeta de descargas siempre organizada!** 🍄✨

---

## 📞 Soporte

- **Documentación:** `GUIA_COMPLETA_v3.1.txt`
- **Inicio Rápido:** `INICIO_RAPIDO.txt`
- **Pruebas:** `python PRUEBAS_v3.1.py`

---

**Versión:** 3.1.0  
**Fecha:** 14 de Enero de 2026  
**Estado:** ✅ Funcional y Portable  

🍄 **¡Disfruta de tu aplicación completamente portable!** 🍄
