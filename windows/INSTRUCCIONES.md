# 🪟 DescargasOrdenadas v3.0 - Windows

## 📋 Archivos Disponibles

### 🚀 **INICIAR.bat** (Recomendado)
- **NO requiere Python preinstalado**
- Detecta e instala Python automáticamente
- Configura todo el entorno necesario
- **¡Solo ejecuta este archivo y listo!**

### ⚙️ **DescargasOrdenadas.bat**
- Requiere Python ya instalado
- Versión ligera para sistemas con Python
- Ideal para uso avanzado

### 📁 **scripts/**
- `tarea_windows.bat` - Configurar tareas programadas
- `instalar_dependencias.bat` - Instalar dependencias Python

---

## 🚀 Inicio Rápido

### Opción 1: Sin Python (Automático)
```batch
# Simplemente ejecuta:
INICIAR.bat
```

### Opción 2: Con Python
```batch
# Si ya tienes Python instalado:
DescargasOrdenadas.bat
```

---

## 📋 Funciones Disponibles

### 🔧 Configurar Tarea Programada
```batch
cd scripts
tarea_windows.bat
```

**Opciones disponibles:**
- **Sistema:** Ejecutar al iniciar Windows (requiere admin)
- **Cada Hora:** Ejecutar cada 60 minutos
- **Diario:** Ejecutar una vez al día
- **Eliminar:** Quitar tarea programada

### 📦 Instalar Dependencias Manualmente
```batch
cd scripts
instalar_dependencias.bat
```

---

## 🛠️ Solución de Problemas

### ❌ "Python no encontrado"
**Solución:** Usa `INICIAR.bat` que instala Python automáticamente

### ❌ "Error de permisos"
**Solución:** 
1. Ejecuta como Administrador
2. Click derecho → "Ejecutar como administrador"

### ❌ "Windows Defender bloquea"
**Solución:**
1. Permite la aplicación en Windows Defender
2. Agrega la carpeta a exclusiones

### ❌ "No funciona la bandeja del sistema"
**Causas comunes:**
- Falta instalar dependencias
- Python no tiene permisos
- Antivirus bloquea la ejecución

**Solución:**
```batch
# Ejecuta como administrador:
INICIAR.bat
```

---

## 📖 Argumentos de Línea de Comandos

```batch
# Ejecución normal
INICIAR.bat

# Para tareas programadas (sin interfaz)
INICIAR.bat --tarea-programada

# Para inicio del sistema
INICIAR.bat --inicio-sistema

# Mostrar ayuda
INICIAR.bat --help
```

---

## 🔒 Permisos de Administrador

Algunas funciones requieren permisos de administrador:
- ✅ Configurar tareas del sistema
- ✅ Instalar Python automáticamente
- ✅ Acceso completo a carpetas del sistema

**Para ejecutar como administrador:**
1. Click derecho en `INICIAR.bat`
2. Seleccionar "Ejecutar como administrador"

---

## 💡 Consejos Windows

### 🎯 Ubicaciones Recomendadas
- `C:\DescargasOrdenadas\` - Instalación sistema
- `%USERPROFILE%\DescargasOrdenadas\` - Instalación usuario

### 🔄 Agregar al PATH
```batch
# Para ejecutar desde cualquier lugar:
setx PATH "%PATH%;C:\ruta\a\DescargasOrdenadas"
```

### 📱 Crear Acceso Directo
1. Click derecho en `INICIAR.bat`
2. "Crear acceso directo"
3. Mover al Escritorio o Menú Inicio

### 🚀 Inicio Automático
```batch
# Configurar inicio automático:
cd scripts
tarea_windows.bat
# Seleccionar opción "Sistema"
```

---

## 📞 Soporte

Si tienes problemas:
1. **Ejecuta:** `INICIAR.bat` como administrador
2. **Revisa:** El archivo de log generado
3. **Verifica:** Que Windows Defender no bloquee
4. **Prueba:** Desactivar temporalmente el antivirus

¡El launcher `INICIAR.bat` está diseñado para funcionar en cualquier Windows sin configuración previa! 