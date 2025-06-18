# 🍄 DescargasOrdenadas v3.0

**Organizador inteligente de archivos descargados con detección automática de tipos, clasificación por fecha y monitoreo en tiempo real.**

[![Versión](https://img.shields.io/badge/versión-3.0-brightgreen.svg)](https://github.com/tu-usuario/DescargasOrdenadas)
[![Licencia](https://img.shields.io/badge/licencia-MIT-blue.svg)](LICENSE)
[![Plataforma](https://img.shields.io/badge/plataforma-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)

---

## 🚀 Inicio Rápido

### ⚡ Opción 1: Con Python (Recomendado)
```bash
# Desde cualquier sistema:
python EJECUTAR.py
```

### 🔧 Opción 2: Sin Python
Dirígete a la carpeta de tu sistema y ejecuta el launcher:
- **Windows:** `windows/INICIAR.bat`
- **macOS:** `macos/INICIAR.sh`
- **Linux:** `linux/INICIAR.sh`

¡Los launchers instalan Python automáticamente si no lo tienes!

---

## 📁 Estructura del Proyecto

```
DescargasOrdenadas/
├── 🚀 EJECUTAR.py              # ← LAUNCHER PRINCIPAL (Detecta tu sistema)
├── 📄 main.py                  # Aplicación principal
├── 📋 requirements.txt         # Dependencias Python
├── 📖 README.md               # Este archivo
├── 🪟 windows/                # Todo para Windows
│   ├── INICIAR.bat           # Launcher principal (NO requiere Python)
│   ├── DescargasOrdenadas.bat # Launcher básico (requiere Python)
│   ├── INSTRUCCIONES.md      # Guía específica Windows
│   └── scripts/              # Scripts específicos Windows
├── 🍎 macos/                 # Todo para macOS
│   ├── INICIAR.sh            # Launcher principal (NO requiere Python)
│   ├── DescargasOrdenadas.command  # Launcher básico (requiere Python)
│   ├── INSTRUCCIONES.md      # Guía específica macOS
│   └── scripts/              # Scripts específicos macOS
├── 🐧 linux/                 # Todo para Linux
│   ├── INICIAR.sh            # Launcher principal (NO requiere Python)
│   ├── DescargasOrdenadas.sh # Launcher básico (requiere Python)
│   ├── INSTRUCCIONES.md      # Guía específica Linux
│   └── scripts/              # Scripts específicos Linux
├── 🛠️ utils/                 # Utilidades generales
│   ├── hacer_ejecutables.py  # Configura permisos Unix
│   └── Configurar_TareaProgramada.py  # Config. tareas programadas
└── 📦 organizer/             # Módulos principales de la aplicación
    └── resources/            # Recursos (iconos, etc.)
```

---

## ✨ Características Principales

### 🔍 **Detección Inteligente**
- Identifica automáticamente tipos de archivo
- Clasifica por categorías (Documentos, Imágenes, Videos, etc.)
- Detecta duplicados y archivos similares

### 📅 **Organización Automática**
- Crea carpetas por fecha y tipo
- Estructura personalizable
- Mantiene historial de cambios

### 🖥️ **Interfaz Dual**
- **GUI:** Interfaz gráfica moderna con bandeja del sistema
- **CLI:** Modo consola para servidores y automatización

### 🔄 **Monitoreo en Tiempo Real**
- Vigila carpeta de Descargas continuamente
- Organiza archivos automáticamente al llegar
- Notificaciones del sistema

### 🛡️ **Seguridad**
- No modifica archivos originales
- Copias de seguridad automáticas
- Logs detallados de todas las operaciones

---

## 🎯 Uso por Sistema

### 🪟 Windows
```batch
# Método 1: Launcher principal
python EJECUTAR.py

# Método 2: Launcher Windows (sin Python)
cd windows
INICIAR.bat

# Método 3: Con Python instalado
cd windows
DescargasOrdenadas.bat
```

### 🍎 macOS
```bash
# Método 1: Launcher principal
python EJECUTAR.py

# Método 2: Launcher macOS (sin Python)
cd macos
./INICIAR.sh

# Método 3: Con Python instalado
cd macos
./DescargasOrdenadas.command
```

### 🐧 Linux
```bash
# Método 1: Launcher principal
python EJECUTAR.py

# Método 2: Launcher Linux (sin Python)
cd linux
./INICIAR.sh

# Método 3: Con Python instalado
cd linux
./DescargasOrdenadas.sh
```

---

## 🔧 Instalación y Configuración

### 📥 Descarga
```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/DescargasOrdenadas.git
cd DescargasOrdenadas

# O descargar ZIP y extraer
```

### ⚙️ Configuración Inicial
```bash
# Ejecutar configurador automático
python EJECUTAR.py

# O manualmente por sistema:
# Windows: windows/INICIAR.bat
# macOS:   macos/INICIAR.sh
# Linux:   linux/INICIAR.sh
```

### 🔐 Permisos (Unix)
```bash
# Hacer ejecutables los scripts
python utils/hacer_ejecutables.py

# O manualmente:
chmod +x macos/INICIAR.sh
chmod +x linux/INICIAR.sh
```

---

## 📋 Tareas Programadas

### 🚀 Configuración Automática
```bash
# Usar configurador universal
python utils/Configurar_TareaProgramada.py

# O por sistema:
# Windows: windows/scripts/tarea_windows.bat
# macOS:   macos/scripts/tarea_macos.sh
# Linux:   linux/scripts/tarea_linux.sh
```

### ⏰ Opciones Disponibles
- **Inicio del sistema:** Al arrancar el PC
- **Inicio de sesión:** Al iniciar sesión de usuario
- **Programada:** Cada hora, diariamente, etc.
- **Personalizada:** Horarios específicos

---

## 📖 Documentación Específica

### 📚 Guías Detalladas
- **Windows:** [`windows/INSTRUCCIONES.md`](windows/INSTRUCCIONES.md)
- **macOS:** [`macos/INSTRUCCIONES.md`](macos/INSTRUCCIONES.md)
- **Linux:** [`linux/INSTRUCCIONES.md`](linux/INSTRUCCIONES.md)

### 🛠️ Documentación Técnica
- **Bandeja del Sistema:** [`BANDEJA_SISTEMA.md`](BANDEJA_SISTEMA.md)
- **Crear Portables:** [`CREAR_PORTABLES.md`](CREAR_PORTABLES.md)
- **Leeme Primero:** [`LEEME_PRIMERO.md`](LEEME_PRIMERO.md)

---

## 💡 Casos de Uso

### 🏠 **Uso Personal**
- Organizar descargas automáticamente
- Mantener carpetas limpias
- Encontrar archivos rápidamente

### 🏢 **Uso Empresarial**
- Servidores de archivos organizados
- Flujos de trabajo automatizados
- Gestión de documentos

### 🖥️ **Administradores de Sistema**
- Despliegue masivo sin Python
- Configuración automatizada
- Monitoreo de directorios

---

## 🛠️ Requisitos Técnicos

### 📋 **Sistemas Soportados**
- **Windows:** 7, 8, 10, 11 (32/64-bit)
- **macOS:** 10.9+ (Intel y Apple Silicon)
- **Linux:** Todas las distribuciones principales

### 🐍 **Python (Opcional)**
- **Versión:** 3.7 o superior
- **Instalación:** Los launchers lo instalan automáticamente
- **Dependencias:** Se instalan automáticamente

### 📦 **Dependencias**
```txt
PySide6>=6.0.0        # Interfaz gráfica
Pillow>=8.0.0         # Procesamiento de imágenes
watchdog>=2.0.0       # Monitoreo de archivos
pywin32>=300          # Específico Windows
```

---

## 🚀 Desarrollo y Contribución

### 🔧 **Estructura del Código**
```
organizer/
├── core/              # Lógica principal
├── gui/               # Interfaz gráfica
├── utils/             # Utilidades
├── resources/         # Recursos
└── tests/             # Pruebas
```

### 📝 **Contribuir**
1. Fork del proyecto
2. Crear rama de características
3. Commit y push
4. Crear Pull Request

### 🐛 **Reportar Bugs**
- Usar GitHub Issues
- Incluir logs y capturas
- Especificar sistema operativo

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [`LICENSE`](LICENSE) para más detalles.

---

## 🙏 Agradecimientos

- **Comunidad Python** por las herramientas
- **Contribuidores** del proyecto
- **Usuarios** que reportan bugs y sugieren mejoras

---

## 📞 Soporte

### 🆘 **Obtener Ayuda**
```bash
# Mostrar ayuda
python EJECUTAR.py --help

# Revisar documentación específica
# Windows: windows/INSTRUCCIONES.md
# macOS:   macos/INSTRUCCIONES.md
# Linux:   linux/INSTRUCCIONES.md
```

### 🔍 **Solución de Problemas**
1. **Ejecutar launcher principal:** `python EJECUTAR.py`
2. **Usar launcher del sistema:** `windows/INICIAR.bat` (Windows)
3. **Revisar logs:** En la carpeta del proyecto
4. **Consultar documentación:** Carpeta del sistema correspondiente

---

**🍄 Creado por Champi - DescargasOrdenadas v3.0**

*¡Mantén tus descargas organizadas automáticamente en cualquier sistema!*
