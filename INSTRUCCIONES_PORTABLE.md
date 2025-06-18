# 🍄 DescargasOrdenadas v3.0 - Instrucciones Portable

## 🚀 Inicio Rápido - ¡En 30 Segundos!

### ✅ ¿TIENES Python Instalado?

| Tengo Python | Comando a Ejecutar |
|--------------|-------------------|
| ✅ **SÍ tengo Python** | `python Ejecutar_DescargasOrdenadas.py` |
| ❌ **NO tengo Python** | Ver sección "🛠️ Sin Python Instalado" abajo |

### 🎯 Launcher Universal (Si tienes Python)
```bash
python Ejecutar_DescargasOrdenadas.py
```

## 🛠️ Sin Python Instalado - Launchers Nativos

### ¡No hay problema! Usa estos launchers que NO requieren Python:

| Sistema | Launcher Nativo | ¿Qué Hace? |
|---------|-----------------|------------|
| 🪟 **Windows** | `INICIAR_Windows.bat` | Detecta, descarga e instala Python automáticamente |
| 🍎 **macOS** | `./INICIAR_macOS.sh` | Instala con Homebrew o descarga desde python.org |
| 🐧 **Linux** | `./INICIAR_Linux.sh` | Detecta tu distro e instala con apt/dnf/pacman |

### 🌟 Características de los Launchers Nativos:

- **🔥 NO requieren Python** preinstalado
- **🤖 Instalación automática** del sistema correcto
- **🔍 Detección inteligente** de arquitectura (64/32-bit, Intel/ARM)
- **📦 Gestores de paquetes** nativos (apt, brew, dnf, etc.)
- **⚡ Una sola ejecución** - instala y ejecuta automáticamente

## ✅ ¿Todo Funciona Automáticamente?

**¡SÍ!** Cualquier launcher detecta y configura automáticamente:

1. ✅ **Sistema operativo** - Windows, macOS o Linux
2. ✅ **Arquitectura** - 64-bit, 32-bit, Intel, ARM (M1/M2)
3. ✅ **Python** - Verifica, descarga e instala si falta
4. ✅ **Dependencias** - PySide6, Pillow, pywin32
5. ✅ **Permisos** - Configura archivos ejecutables
6. ✅ **Rutas** - Funciona desde cualquier carpeta

## 🎯 Configurar Inicio Automático

Una vez que Python esté instalado:

```bash
python Configurar_TareaProgramada.py
```

### Opciones disponibles:

| Sistema | Opciones Disponibles |
|---------|---------------------|
| 🪟 **Windows** | • Inicio del sistema<br>• Cada hora<br>• Diario |
| 🍎 **macOS** | • LaunchDaemon (sistema)<br>• LaunchAgent (usuario)<br>• Tareas cron |
| 🐧 **Linux** | • systemd (sistema)<br>• autostart (usuario)<br>• Tareas cron |

## 📦 Hacer Completamente Portable

### Paso 1: Preparar en tu Sistema
1. **Ejecuta el launcher nativo** correspondiente a tu sistema:
   - Windows: `INICIAR_Windows.bat`  
   - macOS: `./INICIAR_macOS.sh`
   - Linux: `./INICIAR_Linux.sh`

2. **Verifica que funciona** correctamente

### Paso 2: Comprimir y Compartir
1. **Comprime toda la carpeta** `Descargas-Ordenada/`
2. **Envía el archivo** a cualquier sistema
3. **Extrae y ejecuta** el launcher nativo correspondiente

### Paso 3: En el Sistema Destino
**NO necesita Python preinstalado** - El launcher se encarga de todo:
1. Detecta si Python está instalado
2. Si no está, lo descarga e instala automáticamente
3. Configura PATH y dependencias
4. Ejecuta la aplicación

## 🎮 Modos de Uso

### Interfaz Gráfica (Normal)
```bash
# Con Python ya instalado:
python Ejecutar_DescargasOrdenadas.py

# Sin Python (launchers nativos):
# Windows: INICIAR_Windows.bat
# macOS: ./INICIAR_macOS.sh  
# Linux: ./INICIAR_Linux.sh
```

### Solo Organizar (Sin Ventanas)
```bash
python Ejecutar_DescargasOrdenadas.py --auto-organizar
```

### Reorganizar TODO
```bash
python Ejecutar_DescargasOrdenadas.py --reorganizar
```

### Carpeta Específica
```bash
python Ejecutar_DescargasOrdenadas.py --dir "C:\Mi\Carpeta"
```

### Minimizado en Bandeja
```bash
python Ejecutar_DescargasOrdenadas.py --minimizado
```

### Al Inicio del Sistema
```bash
python Ejecutar_DescargasOrdenadas.py --inicio-sistema
```

## 🔧 Solución de Problemas

### ❌ "Python no encontrado"

| Sistema | Solución Automática | Solución Manual |
|---------|---------------------|-----------------|
| 🪟 **Windows** | `INICIAR_Windows.bat` | [Descargar Python](https://python.org) |
| 🍎 **macOS** | `./INICIAR_macOS.sh` | `brew install python` |
| 🐧 **Linux** | `./INICIAR_Linux.sh` | `sudo apt install python3` |

### ❌ "Error en launcher nativo"
**Windows**:
- Ejecutar como Administrador si es necesario
- Verificar conexión a internet para descargas

**macOS**:  
- Dar permisos con `chmod +x INICIAR_macOS.sh`
- Para Homebrew: `xcode-select --install` primero

**Linux**:
- Dar permisos con `chmod +x INICIAR_Linux.sh`  
- Verificar `sudo` disponible para instalación

### ❌ "Permisos denegados" (macOS/Linux)
```bash
chmod +x INICIAR_macOS.sh INICIAR_Linux.sh
# O usar el configurador automático:
python hacer_ejecutables.py
```

## 🎯 ¿Qué Hace Exactamente?

### Organización Automática
- 📁 **40+ categorías** de archivos
- 🗂️ **Subcategorías inteligentes**
- 🔍 **500+ tipos de archivo** reconocidos
- 🧠 **IA para categorización**
- 🔄 **Detección de duplicados**

### Funciones Avanzadas
- 📊 **Estadísticas detalladas**
- 📅 **Organización por fechas**
- ⚙️ **Reglas personalizadas**
- 🔔 **Notificaciones del sistema**
- 📝 **Logs completos**

## 📂 ¿Dónde Organiza?

**Por defecto**: Carpeta de Descargas del sistema
- Windows: `C:\Users\[Usuario]\Downloads`
- macOS: `/Users/[Usuario]/Downloads`
- Linux: `/home/[usuario]/Downloads`

**Personalizado**: Cualquier carpeta que especifiques con `--dir`

## 🔒 ¿Es Seguro?

✅ **100% local** - No envía datos a internet (excepto para instalar Python/dependencias)  
✅ **Código abierto** - Puedes revisar todo  
✅ **Sin instalación invasiva** - No modifica registro del sistema  
✅ **Reversible** - Puedes deshacer cambios  
✅ **Logs completos** - Sabes qué se movió dónde  

## 🌟 Características Únicas

### Verdaderamente Portable
- ✅ **Sin instalación** requerida en sistemas destino
- ✅ **Sin registro** del sistema
- ✅ **Sin dependencias** del SO
- ✅ **Funciona desde USB** o cualquier carpeta
- ✅ **Launchers nativos** para sistemas sin Python

### Detección Inteligente
- 🔍 **Detecta el SO** y arquitectura automáticamente
- 🐍 **Verifica Python** y versión
- 📦 **Instala dependencias** si faltan
- 🔧 **Configura permisos** automáticamente

### Instalación Automática Avanzada
- 📥 **Descarga Python** según SO y arquitectura
- 🍺 **Homebrew** automático en macOS
- 🐧 **Detecta distribución** Linux (Ubuntu, Fedora, Arch, etc.)
- ⏳ **Muestra progreso** de instalación
- ✅ **Verifica instalación** correcta

## 💡 Consejos Pro

### Para Usuarios Sin Conocimientos Técnicos
1. **Descarga y extrae** el proyecto
2. **Ejecuta el launcher** de tu sistema:
   - Windows: Doble clic en `INICIAR_Windows.bat`
   - macOS: Terminal → `./INICIAR_macOS.sh`
   - Linux: Terminal → `./INICIAR_Linux.sh`
3. **Sigue las instrucciones** en pantalla
4. **¡Listo!** - Todo se configura automáticamente

### Para Usuarios Avanzados
- Modifica `organizer/custom_rules.py` para reglas personalizadas
- Usa `--reorganizar` para rehacer toda la organización
- Los duplicados se manejan automáticamente
- Logs en carpeta temporal del sistema

### Para Administradores
- Los launchers nativos facilitan despliegue masivo
- Servicios systemd/LaunchDaemons para automatización
- Sin dependencias de Python preinstalado en estaciones

## 🎉 ¡Listo Para Usar!

El proyecto está **completamente configurado** con dos niveles:

### Nivel 1: Con Python Ya Instalado
```bash
python Ejecutar_DescargasOrdenadas.py
```

### Nivel 2: Sin Python (Launchers Nativos)
- **Windows**: `INICIAR_Windows.bat`
- **macOS**: `./INICIAR_macOS.sh`  
- **Linux**: `./INICIAR_Linux.sh`

**🎯 Resultado**: Funciona en cualquier sistema, con o sin Python preinstalado

---

## 🆘 ¿Necesitas Ayuda?

1. **Lee este archivo** - Tiene todas las respuestas
2. **Usa launchers nativos** si no tienes Python
3. **Revisa los logs** - Muestran qué pasó exactamente
4. **Prueba el modo debug** - `python main.py --help`

---

**🍄 Creado con ❤️ por Champi**

*¡Disfruta de tus descargas siempre organizadas, con o sin Python!* 🎯 