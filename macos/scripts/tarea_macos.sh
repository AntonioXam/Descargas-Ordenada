#!/bin/bash

# ===================================================================
# DescargasOrdenadas v3.0 - Configuración de Tarea Programada macOS
# Creado por Champi 🍄
# ===================================================================

echo ""
echo "🍄 DescargasOrdenadas v3.0 - Configuración de Tarea Programada"
echo "============================================================="
echo ""

# Obtener el directorio donde está este script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"
SHELL_SCRIPT="$APP_DIR/DescargasOrdenadas.command"

echo "📁 Directorio de la aplicación: $APP_DIR"
echo "🚀 Script de inicio: $SHELL_SCRIPT"
echo ""

# Verificar que el script existe
if [ ! -f "$SHELL_SCRIPT" ]; then
    echo "❌ No se encontró DescargasOrdenadas.command"
    echo "💡 Asegúrate de ejecutar este script desde la carpeta correcta"
    read -p "Presiona Enter para cerrar..." || true
    exit 1
fi

# Verificar que Python está disponible
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python no está disponible"
    echo "💡 Instala Python para continuar"
    read -p "Presiona Enter para cerrar..." || true
    exit 1
fi

echo "✅ Python encontrado"
echo ""

echo "⚙️  Opciones de configuración disponibles:"
echo ""
echo "1. Tarea al INICIO del sistema (LaunchDaemon)"
echo "2. Tarea al INICIO de sesión (LaunchAgent)"
echo "3. Tarea cada HORA (cron)"
echo "4. Tarea DIARIA (cron)"
echo "5. ELIMINAR todas las tareas"
echo ""
read -p "Selecciona una opción (1-5): " opcion

case $opcion in
    1)
        echo ""
        echo "⏰ Configurando LaunchDaemon para inicio del sistema..."
        
        # Crear plist para LaunchDaemon (requiere sudo)
        DAEMON_PLIST="/Library/LaunchDaemons/com.champi.descargasordenadas.plist"
        
        # Verificar permisos de sudo
        echo "🔐 Se requieren permisos de administrador..."
        if ! sudo -v; then
            echo "❌ No se pudieron obtener permisos de administrador"
            read -p "Presiona Enter para cerrar..." || true
            exit 1
        fi
        
        # Crear el archivo plist
        sudo tee "$DAEMON_PLIST" > /dev/null << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.champi.descargasordenadas</string>
    <key>ProgramArguments</key>
    <array>
        <string>$SHELL_SCRIPT</string>
        <string>--inicio-sistema</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>WorkingDirectory</key>
    <string>$APP_DIR</string>
    <key>StandardOutPath</key>
    <string>/tmp/descargasordenadas.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/descargasordenadas.error.log</string>
</dict>
</plist>
EOF
        
        # Cargar el daemon
        sudo launchctl load "$DAEMON_PLIST" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            echo "✅ LaunchDaemon creado exitosamente"
            echo "🚀 Se ejecutará automáticamente al iniciar el sistema"
            echo ""
            echo "💡 Comandos útiles:"
            echo "   Ver estado: sudo launchctl list | grep descargasordenadas"
            echo "   Descargar: sudo launchctl unload $DAEMON_PLIST"
            echo "   Eliminar: sudo rm $DAEMON_PLIST"
        else
            echo "❌ Error al configurar el LaunchDaemon"
        fi
        ;;
        
    2)
        echo ""
        echo "⏰ Configurando LaunchAgent para inicio de sesión..."
        
        # Crear directorio si no existe
        AGENT_DIR="$HOME/Library/LaunchAgents"
        mkdir -p "$AGENT_DIR"
        
        # Crear plist para LaunchAgent
        AGENT_PLIST="$AGENT_DIR/com.champi.descargasordenadas.plist"
        
        cat > "$AGENT_PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.champi.descargasordenadas</string>
    <key>ProgramArguments</key>
    <array>
        <string>$SHELL_SCRIPT</string>
        <string>--inicio-sistema</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>WorkingDirectory</key>
    <string>$APP_DIR</string>
    <key>StandardOutPath</key>
    <string>/tmp/descargasordenadas.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/descargasordenadas.error.log</string>
</dict>
</plist>
EOF
        
        # Cargar el agent
        launchctl load "$AGENT_PLIST" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            echo "✅ LaunchAgent creado exitosamente"
            echo "🚀 Se ejecutará al iniciar sesión de usuario"
            echo ""
            echo "💡 Comandos útiles:"
            echo "   Ver estado: launchctl list | grep descargasordenadas"
            echo "   Descargar: launchctl unload $AGENT_PLIST"
            echo "   Eliminar: rm $AGENT_PLIST"
        else
            echo "❌ Error al configurar el LaunchAgent"
        fi
        ;;
        
    3)
        echo ""
        echo "⏰ Configurando tarea cron para ejecutar cada HORA..."
        
        # Agregar tarea cron
        (crontab -l 2>/dev/null; echo "0 * * * * $SHELL_SCRIPT --tarea-programada >/dev/null 2>&1") | crontab -
        
        if [ $? -eq 0 ]; then
            echo "✅ Tarea cron horaria creada exitosamente"
            echo "🕐 Se ejecutará cada hora en punto"
            echo ""
            echo "💡 Para ver: crontab -l | grep DescargasOrdenadas"
        else
            echo "❌ Error al crear la tarea cron"
            echo "💡 En macOS puede requerir permisos especiales para cron"
        fi
        ;;
        
    4)
        echo ""
        echo "⏰ Configurando tarea cron para ejecutar DIARIAMENTE..."
        
        # Agregar tarea cron diaria
        (crontab -l 2>/dev/null; echo "0 9 * * * $SHELL_SCRIPT --tarea-programada >/dev/null 2>&1") | crontab -
        
        if [ $? -eq 0 ]; then
            echo "✅ Tarea cron diaria creada exitosamente"
            echo "📅 Se ejecutará todos los días a las 09:00"
            echo ""
            echo "💡 Para ver: crontab -l | grep DescargasOrdenadas"
        else
            echo "❌ Error al crear la tarea cron diaria"
            echo "💡 En macOS puede requerir permisos especiales para cron"
        fi
        ;;
        
    5)
        echo ""
        echo "❌ Eliminando todas las tareas de DescargasOrdenadas..."
        
        # Eliminar LaunchDaemon
        sudo launchctl unload /Library/LaunchDaemons/com.champi.descargasordenadas.plist 2>/dev/null
        sudo rm -f /Library/LaunchDaemons/com.champi.descargasordenadas.plist
        
        # Eliminar LaunchAgent
        launchctl unload "$HOME/Library/LaunchAgents/com.champi.descargasordenadas.plist" 2>/dev/null
        rm -f "$HOME/Library/LaunchAgents/com.champi.descargasordenadas.plist"
        
        # Eliminar tareas cron
        crontab -l 2>/dev/null | grep -v "DescargasOrdenadas" | crontab - 2>/dev/null
        
        echo "✅ Todas las tareas han sido eliminadas"
        ;;
        
    *)
        echo "❌ Opción inválida"
        read -p "Presiona Enter para cerrar..." || true
        exit 1
        ;;
esac

echo ""
echo "📋 Estado actual de las tareas:"
echo ""

# Verificar LaunchDaemon
if sudo launchctl list 2>/dev/null | grep -q "descargasordenadas"; then
    echo "✅ LaunchDaemon: ACTIVO"
else
    echo "❌ LaunchDaemon: NO ACTIVO"
fi

# Verificar LaunchAgent
if launchctl list 2>/dev/null | grep -q "descargasordenadas"; then
    echo "✅ LaunchAgent: ACTIVO"
else
    echo "❌ LaunchAgent: NO ACTIVO"
fi

# Verificar cron
if crontab -l 2>/dev/null | grep -q "DescargasOrdenadas"; then
    echo "✅ Tareas cron: ACTIVAS"
    crontab -l 2>/dev/null | grep "DescargasOrdenadas" | sed 's/^/   /'
else
    echo "❌ Tareas cron: NO ACTIVAS"
fi

echo ""
echo "💡 Nota: Los logs se guardan en /tmp/descargasordenadas.log"
echo ""
read -p "Presiona Enter para cerrar..." || true 