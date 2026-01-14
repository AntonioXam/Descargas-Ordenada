# 🚀 ¿Cómo Usar DescargasOrdenadas v3.0?

## 🎯 Método Más Simple (Recomendado)

### ✨ Si tienes Python:
```bash
python EJECUTAR.py
```
**¡Eso es todo!** El script detecta tu sistema y ejecuta todo automáticamente.

### 🔧 Si NO tienes Python:
1. **Windows:** Doble-click en `windows/INICIAR.bat`
2. **macOS:** Ejecuta `macos/INICIAR.sh` 
3. **Linux:** Ejecuta `linux/INICIAR.sh`

Los launchers instalan Python automáticamente.

---

## 📁 ¿Qué Hay en Cada Carpeta?

### 🪟 `windows/`
- `INICIAR.bat` ← **USAR ESTE** (no requiere Python)
- `DescargasOrdenadas.bat` ← Solo si ya tienes Python
- `INSTRUCCIONES.md` ← Guía completa Windows
- `scripts/` ← Herramientas avanzadas

### 🍎 `macos/`
- `INICIAR.sh` ← **USAR ESTE** (no requiere Python)
- `DescargasOrdenadas.command` ← Solo si ya tienes Python
- `INSTRUCCIONES.md` ← Guía completa macOS
- `scripts/` ← Herramientas avanzadas

### 🐧 `linux/`
- `INICIAR.sh` ← **USAR ESTE** (no requiere Python)
- `DescargasOrdenadas.sh` ← Solo si ya tienes Python
- `INSTRUCCIONES.md` ← Guía completa Linux
- `scripts/` ← Herramientas avanzadas

### 🛠️ `utils/`
- `hacer_ejecutables.py` ← Da permisos a scripts Unix
- `Configurar_TareaProgramada.py` ← Config tareas automáticas

---

## 🔥 Para Impacientes

### ⚡ Quiero que funcione YA:
```bash
# Método universal (cualquier sistema):
python EJECUTAR.py
```

### 🎮 Quiero configurarlo todo automático:
```bash
# Primero ejecutar la app:
python EJECUTAR.py

# Luego configurar tarea programada:
python utils/Configurar_TareaProgramada.py
```

### 🚀 Quiero que se ejecute solo al iniciar mi PC:
- **Windows:** Ejecuta `windows/scripts/tarea_windows.bat` → Opción "Sistema"
- **macOS:** Ejecuta `macos/scripts/tarea_macos.sh` → Opción "LaunchDaemon"  
- **Linux:** Ejecuta `linux/scripts/tarea_linux.sh` → Opción "Systemd"

---

## 🤔 ¿Cuál Archivo Ejecutar?

### 📊 Tabla de Decisión Rápida

| Tu Situación | Archivo a Ejecutar |
|--------------|-------------------|
| **Cualquier sistema + Python** | `python EJECUTAR.py` |
| **Windows sin Python** | `windows/INICIAR.bat` |
| **macOS sin Python** | `macos/INICIAR.sh` |
| **Linux sin Python** | `linux/INICIAR.sh` |
| **Quiero configurar todo** | `python utils/Configurar_TareaProgramada.py` |

---

## 💡 Consejos Importantes

### ✅ **Funciona Siempre:**
- `python EJECUTAR.py` - Detecta tu sistema automáticamente
- Los launchers `INICIAR.*` instalan Python si no lo tienes

### 🔐 **Permisos en macOS/Linux:**
```bash
# Dar permisos una sola vez:
chmod +x macos/INICIAR.sh
chmod +x linux/INICIAR.sh

# O automáticamente:
python utils/hacer_ejecutables.py
```

### ⚠️ **Si Algo No Funciona:**
1. **Lee las instrucciones específicas** de tu sistema:
   - Windows: `windows/INSTRUCCIONES.md`
   - macOS: `macos/INSTRUCCIONES.md`
   - Linux: `linux/INSTRUCCIONES.md`

2. **Ejecuta como administrador/sudo** si es necesario

3. **Verifica antivirus** - puede bloquear los scripts

---

## 🎉 Resumen Ultra Rápido

1. **¿Tienes Python?** → `python EJECUTAR.py`
2. **¿No tienes Python?** → Ve a carpeta de tu sistema → Ejecuta `INICIAR.*`
3. **¿Quieres que sea automático?** → Ejecuta script de tareas programadas de tu sistema
4. **¿Problemas?** → Lee `INSTRUCCIONES.md` de tu sistema

**¡Tan simple como eso!** 🍄 