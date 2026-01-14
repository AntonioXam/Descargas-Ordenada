# 🔄 Sistema de Actualizaciones Automáticas

## ¿Cómo Funciona?

DescargasOrdenadas incluye un sistema de **actualizaciones automáticas desde GitHub** que no requiere ninguna configuración.

---

## 📋 Proceso Paso a Paso

### 1️⃣ Verificación Automática al Inicio

Cada vez que abres la aplicación:
- ✅ Se conecta a GitHub (repositorio público)
- ✅ Compara tu versión con la última disponible
- ✅ Si hay una nueva versión, te lo notifica

**¡No requiere cuenta de GitHub ni tokens!**

### 2️⃣ Notificación de Actualización

Si hay una versión nueva, verás un mensaje:

```
🎉 ¡Hay una nueva versión disponible!

📦 Versión: 3.3.0
📝 [Nombre del release]

[Descripción de las novedades]
```

**Opciones:**
- ⬇️ **Descargar e Instalar** - Actualización automática completa
- 🌐 **Abrir en Navegador** - Ver detalles en GitHub
- ❌ **Cancelar** - Actualizar más tarde

### 3️⃣ Descarga Automática

Si eliges "Descargar e Instalar":

1. **Descarga** el archivo .zip desde GitHub
   - Verás una barra de progreso
   - Se descarga en una carpeta temporal

2. **Crea un Backup** automático
   - Tu versión actual se guarda como respaldo
   - Por si necesitas volver atrás

3. **Instala** la nueva versión
   - Descomprime los archivos
   - Copia a la carpeta actual
   - **Preserva tu configuración** (.config/)

4. **Reinicia** automáticamente
   - Cierra la aplicación actual
   - Espera 2 segundos
   - Abre la nueva versión

### 4️⃣ Listo! 🎉

Tu aplicación está actualizada y funcionando con todas tus preferencias guardadas.

---

## 🔍 Buscar Actualizaciones Manualmente

Si quieres comprobar si hay actualizaciones en cualquier momento:

1. Abre la aplicación
2. Ve a la pestaña **"⚙️ Configuración"**
3. Haz scroll hasta **"🔄 Actualizaciones"**
4. Click en **"🔍 Buscar Actualizaciones"**

---

## 🔐 Seguridad y Privacidad

### ¿Es seguro?

- ✅ **Código Abierto** - Todo el código está en GitHub
- ✅ **GitHub Oficial** - Descarga directa desde GitHub.com
- ✅ **Sin Intermediarios** - No pasa por servidores externos
- ✅ **HTTPS** - Conexión cifrada
- ✅ **Verificación de Versión** - Compara números de versión

### ¿Qué datos se envían?

**NINGUNO.** La aplicación solo:
- ❓ **Pregunta** a GitHub: "¿Cuál es la última versión?"
- ⬇️ **Descarga** el archivo .zip público

**No se recopila información personal, estadísticas ni telemetría.**

---

## 💾 ¿Qué se Conserva?

Durante una actualización se preservan:

- ✅ **Tu configuración** (.config/)
- ✅ **Tema elegido**
- ✅ **Preferencias de notificaciones**
- ✅ **Carpeta de descargas seleccionada**
- ✅ **Reglas personalizadas** (si las has creado)

---

## 🛡️ Backup Automático

Cada vez que actualizas:

- 📁 Se crea una carpeta `DescargasOrdenadas_backup_YYYYMMDD_HHMMSS`
- 📁 Contiene tu versión anterior completa
- 📁 Puedes volver atrás copiando los archivos

**Ubicación:** Carpeta superior a donde está instalado el programa

---

## ⚙️ Configuración Avanzada

### Cambiar Frecuencia de Verificación

Por defecto, la aplicación verifica actualizaciones:
- ✅ Al iniciar (si han pasado más de 24 horas desde la última vez)
- ✅ Cuando pulsas manualmente "Buscar Actualizaciones"

No hay opciones para cambiar esto actualmente.

### Deshabilitar Actualizaciones

Si no quieres que verifique automáticamente:

1. Ve a `organizer/actualizaciones_mejorado.py`
2. Busca la línea `if not forzar and self.ultima_verificacion:`
3. Cambia la condición o desinstala `requests`:
   ```bash
   pip uninstall requests
   ```

**Nota:** No recomendado, te perderás mejoras y correcciones.

---

## 🐛 Solución de Problemas

### "Error verificando actualizaciones"

**Causas posibles:**
- ❌ Sin conexión a internet
- ❌ GitHub temporalmente no disponible
- ❌ Módulo `requests` no instalado

**Solución:**
```bash
# Reinstalar dependencias
INSTALAR_DEPENDENCIAS.bat

# O manualmente
pip install requests
```

### "Error descargando actualización"

**Causas posibles:**
- ❌ Conexión interrumpida
- ❌ Sin espacio en disco

**Solución:**
- Verifica tu conexión
- Libera espacio en disco
- Intenta de nuevo más tarde

### "Error instalando actualización"

**Causas posibles:**
- ❌ Archivos en uso por otro proceso
- ❌ Permisos insuficientes

**Solución:**
1. Cierra completamente la aplicación
2. Vuelve a abrirla
3. Intenta actualizar de nuevo

Si persiste:
1. Descarga manualmente desde: https://github.com/AntonioIbanez1/Descargas-Ordenada/releases
2. Extrae el .zip
3. Copia sobre tu instalación actual (preservando .config/)

---

## 📝 Notas para Desarrolladores

Si quieres publicar tu propia versión:

1. Modifica `organizer/actualizaciones_mejorado.py`:
   ```python
   GITHUB_USER = "tu-usuario"
   GITHUB_REPO = "tu-repositorio"
   ```

2. Actualiza `VERSION_ACTUAL`:
   ```python
   VERSION_ACTUAL = "3.2.0"  # Tu versión
   ```

3. Crea un release en GitHub:
   - Tag: `v3.2.0`
   - GitHub generará automáticamente el .zip

---

## 📞 Soporte

¿Problemas con las actualizaciones?

- 🐛 **GitHub Issues:** https://github.com/AntonioIbanez1/Descargas-Ordenada/issues
- 📧 **Email:** [tu email si quieres]
- 📖 **Documentación:** `docs/COMO_USAR.md`
