# 🍄 DescargasOrdenadas - Funcionalidad de Bandeja del Sistema

## 📋 Descripción
Se ha implementado una funcionalidad completa de **bandeja del sistema (system tray)** que permite que la aplicación funcione de manera discreta en segundo plano, organizando archivos automáticamente.

## ✨ Características Implementadas

### 🎯 Comportamiento de Ventana
- **Minimizar (botón -)**: La ventana se oculta en la bandeja del sistema
- **Cerrar (botón X)**: Cierra la aplicación completamente
- **Click en bandeja**: Alterna entre mostrar/ocultar ventana
- **Doble click en bandeja**: Siempre muestra la ventana

### 🔧 Funcionalidades de Bandeja
- **Icono personalizado**: Muestra un icono verde con símbolo de carpeta
- **Menú contextual** con opciones:
  - 📂 Mostrar Ventana
  - 🔄 Organizar Ahora
  - ⚡ Auto-Organización (toggle)
  - 📁 Carpeta actual
  - ❌ Salir

### ⚡ Auto-Organización
- **Activación**: Desde el menú de la bandeja
- **Frecuencia**: Cada 30 segundos
- **Notificaciones**: Muestra cuando se organizan archivos
- **Estado visual**: Cambia el tooltip del icono

### 💻 Gestión de Consola (Windows)
- **Al minimizar**: Oculta la ventana de consola automáticamente
- **Al restaurar**: Muestra la consola nuevamente
- **Al cerrar**: Restaura la consola antes de salir

### 🔔 Notificaciones del Sistema
- **Minimizar**: "Aplicación minimizada a la bandeja del sistema"
- **Auto-organización**: Activación/desactivación y resultados
- **Organización**: Cantidad de archivos procesados

## 🚀 Uso

### Ejecutar con Bandeja del Sistema
```bash
# Ejecutar la GUI avanzada
python test_bandeja.py

# O directamente desde el organizador
python -m organizer.gui_avanzada
```

### Controles Principales
1. **Iniciar la aplicación**: Se ejecuta normalmente con ventana visible
2. **Minimizar**: Click en el botón minimizar → va a bandeja + oculta consola
3. **Restaurar**: Click en icono de bandeja → muestra ventana + consola
4. **Auto-organizar**: Click derecho en bandeja → "⚡ Auto-Organización"
5. **Cerrar**: Click en X o "❌ Salir" del menú de bandeja

### Funcionalidades Avanzadas
- **Organización manual**: Usar "🔄 Organizar Ahora" desde la bandeja
- **Monitoreo continuo**: Activar auto-organización para funcionamiento autónomo
- **Acceso rápido**: Doble click en bandeja para acceso inmediato

## 🖥️ Compatibilidad Multiplataforma

### Windows 
- ✅ Bandeja del sistema completa
- ✅ Ocultación de consola
- ✅ Notificaciones nativas
- ✅ Menú contextual

### Linux
- ✅ Bandeja del sistema (depende del entorno de escritorio)
- ⚠️ Consola manejada automáticamente por el sistema  
- ✅ Notificaciones nativas
- ✅ Menú contextual

### macOS
- ✅ Bandeja del sistema en menu bar
- ⚠️ Consola manejada automáticamente por el sistema
- ✅ Notificaciones nativas  
- ✅ Menú contextual

## 🎮 Ejemplo de Flujo de Trabajo

1. **Inicio**: `python test_bandeja.py`
2. **Configurar**: Ajustar opciones en la GUI
3. **Minimizar**: Click en minimizar → app va a bandeja
4. **Auto-organizar**: Click derecho → "⚡ Auto-Organización" 
5. **Trabajo en segundo plano**: La app organiza cada 30 segundos
6. **Verificar**: Las notificaciones muestran archivos organizados
7. **Acceder**: Click en bandeja cuando necesites la ventana
8. **Salir**: Click derecho → "❌ Salir"

## 🔍 Solución de Problemas

### Bandeja no disponible
Si el sistema no soporta bandeja del sistema:
- La app preguntará si cerrar completamente o minimizar a barra de tareas
- Se mostrará mensaje de advertencia en los logs

### Consola no se oculta
En sistemas que no son Windows:
- Es comportamiento normal, la consola se maneja automáticamente
- La funcionalidad principal sigue funcionando

### Auto-organización no funciona
- Verificar que esté activada desde el menú de bandeja  
- Revisar permisos de la carpeta de descargas
- Consultar los logs internos en la pestaña "Logs"

## 📝 Notas Técnicas

- **Timer**: QTimer de 30 segundos para auto-organización
- **Iconos**: Creación dinámica con QPainter para compatibilidad
- **Eventos**: Manejo de WindowStateChange para minimizar
- **Cleanup**: Cleanup automático al cerrar (timer, tray icon, etc.)
- **Threading**: Operaciones de E/O no bloquean la UI

---

🍄 **DescargasOrdenadas v3.0** - Organización inteligente con funcionalidad de bandeja del sistema completa 