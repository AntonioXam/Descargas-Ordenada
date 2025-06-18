# 🐧 DescargasOrdenadas v3.0 - Linux

## 📋 Archivos Disponibles

### 🚀 **INICIAR.sh** (Recomendado)
- **NO requiere Python preinstalado**
- Detecta automáticamente tu distribución
- Soporta Ubuntu, Debian, Fedora, Arch, openSUSE, Alpine, etc.
- Instala Python usando tu gestor de paquetes
- **¡Solo ejecuta este archivo y listo!**

### ⚙️ **DescargasOrdenadas.sh**
- Requiere Python ya instalado
- Versión ligera para sistemas con Python
- Ideal para uso avanzado

### 📁 **scripts/**
- `tarea_linux.sh` - Configurar tareas programadas
- `instalar_dependencias.sh` - Instalar dependencias Python

---

## 🚀 Inicio Rápido

### Opción 1: Sin Python (Automático)
```bash
# Navega a la carpeta y ejecuta:
cd ruta/a/DescargasOrdenadas/linux
./INICIAR.sh

# O con ruta completa:
/ruta/completa/DescargasOrdenadas/linux/INICIAR.sh
```

### Opción 2: Con Python
```bash
# Si ya tienes Python instalado:
./DescargasOrdenadas.sh
```

---

## 🔐 Permisos de Ejecución

**Dar permisos ejecutables (solo la primera vez):**
```bash
chmod +x INICIAR.sh
chmod +x DescargasOrdenadas.sh
chmod +x scripts/tarea_linux.sh
chmod +x scripts/instalar_dependencias.sh
```

**O usa la utilidad automática:**
```bash
cd ..
python utils/hacer_ejecutables.py
```

---

## 🐧 Distribuciones Soportadas

| Distribución | Gestor de Paquetes | Comando |
|--------------|-------------------|---------|
| **Ubuntu/Debian** | apt | `sudo apt install python3` |
| **Fedora/CentOS** | dnf/yum | `sudo dnf install python3` |
| **Arch/Manjaro** | pacman | `sudo pacman -S python` |
| **openSUSE** | zypper | `sudo zypper install python3` |
| **Alpine** | apk | `sudo apk add python3` |
| **Gentoo** | emerge | `sudo emerge dev-lang/python` |

**El script detecta automáticamente tu distribución.**

---

## 📋 Funciones Disponibles

### 🔧 Configurar Tarea Programada
```bash
cd scripts
./tarea_linux.sh
```

**Opciones disponibles:**
- **Systemd:** Servicio del sistema (recomendado)
- **Autostart:** Ejecutar al iniciar sesión (Desktop)
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

### ❌ "Python no encontrado"
**Solución:** Usa `INICIAR.sh` que instala Python automáticamente

### ❌ "sudo: command not found"
**En distribuciones minimalistas:**
```bash
# Instalar sudo (como root):
apt install sudo        # Debian/Ubuntu
dnf install sudo        # Fedora
pacman -S sudo          # Arch
```

### ❌ "No funciona la bandeja del sistema"
**Solución:**
```bash
# Instalar dependencias GUI:
sudo apt install python3-tk python3-pil.imagetk  # Ubuntu/Debian
sudo dnf install python3-tkinter                  # Fedora
sudo pacman -S tk                                  # Arch
```

### ❌ "Distribución no reconocida"
**Solución manual:**
```bash
# Instala Python según tu distribución:
# Luego ejecuta:
./DescargasOrdenadas.sh
```

---

## 📦 Instalación Manual por Distribución

### 📘 Ubuntu/Debian/Mint
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-tk
pip3 install pillow pyside6
```

### 📗 Fedora/CentOS/RHEL
```bash
sudo dnf install python3 python3-pip python3-tkinter
pip3 install pillow pyside6
```

### 📙 Arch Linux/Manjaro
```bash
sudo pacman -S python python-pip tk
pip install pillow pyside6
```

### 📕 openSUSE
```bash
sudo zypper install python3 python3-pip python3-tk
pip3 install pillow pyside6
```

### 📔 Alpine Linux
```bash
sudo apk add python3 py3-pip tk
pip3 install pillow pyside6
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

## 🔧 Entornos de Escritorio

### 🖥️ GNOME
- Bandeja del sistema con extensión
- Autostart en `~/.config/autostart/`

### 🎨 KDE Plasma
- Bandeja del sistema nativa
- Autostart en `~/.config/autostart/`

### 🪟 XFCE
- Panel con área de notificación
- Autostart en `~/.config/autostart/`

### 🌊 LXDE/LXQt
- Panel con bandeja del sistema
- Autostart en `~/.config/autostart/`

### 🔲 i3/Awesome/Tiling WM
- Configuración manual de bandeja
- Usar `systray` o `stalonetray`

---

## 💡 Consejos Linux

### 🎯 Ubicaciones Recomendadas
- `/opt/DescargasOrdenadas/` - Instalación sistema
- `~/Applications/DescargasOrdenadas/` - Instalación usuario
- `~/.local/share/DescargasOrdenadas/` - Datos locales

### 🔄 Agregar al PATH
```bash
# Agregar a ~/.bashrc o ~/.zshrc:
echo 'export PATH="$PATH:/ruta/a/DescargasOrdenadas"' >> ~/.bashrc
source ~/.bashrc
```

### 📱 Crear Alias
```bash
# Agregar a ~/.bashrc:
echo 'alias descargas="/ruta/a/DescargasOrdenadas/linux/INICIAR.sh"' >> ~/.bashrc
```

### 🚀 Inicio Automático
```bash
# Configurar inicio automático:
cd scripts
./tarea_linux.sh
# Seleccionar opción "Autostart"
```

### 🗂️ Crear Acceso Directo
```bash
# Crear .desktop file:
cat > ~/.local/share/applications/descargasordenadas.desktop << EOF
[Desktop Entry]
Name=DescargasOrdenadas
Exec=/ruta/a/DescargasOrdenadas/linux/INICIAR.sh
Icon=/ruta/a/DescargasOrdenadas/organizer/resources/icon.png
Type=Application
Categories=Utility;FileManager;
EOF
```

---

## 🔒 Permisos y Seguridad

### 🛡️ SELinux (Fedora/CentOS)
Si SELinux bloquea:
```bash
# Ver contexto actual:
ls -Z INICIAR.sh

# Permitir ejecución:
sudo chcon -t bin_t INICIAR.sh
```

### 🔐 AppArmor (Ubuntu)
Si AppArmor bloquea:
```bash
# Ver logs:
sudo dmesg | grep -i apparmor

# O deshabilitar para Python:
sudo aa-complain /usr/bin/python3
```

### 🔑 Sudo sin Contraseña (Opcional)
Para instalación automática:
```bash
# Agregar a /etc/sudoers:
tu_usuario ALL=(ALL) NOPASSWD: /usr/bin/apt, /usr/bin/dnf, /usr/bin/pacman
```

---

## 🖥️ Servidor sin GUI

Para servidores sin entorno gráfico:
```bash
# Ejecutar en modo comando:
./INICIAR.sh --no-gui

# O modificar main.py para modo servidor
```

---

## 📞 Soporte

Si tienes problemas:
1. **Ejecuta:** `./INICIAR.sh` desde terminal
2. **Revisa:** Los mensajes de error
3. **Verifica:** Permisos con `ls -la`
4. **Comprueba:** Tu distribución con `cat /etc/os-release`
5. **Instala:** Las dependencias GUI si es necesario

¡El launcher `INICIAR.sh` está diseñado para funcionar en cualquier distribución Linux sin configuración previa! 