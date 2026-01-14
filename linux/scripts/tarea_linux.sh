#!/bin/bash

# ===================================================================
# DescargasOrdenadas v3.0 - Configuración de Tarea Programada Linux
# Creado por Champi 🍄
# ===================================================================

echo ""
echo "🍄 DescargasOrdenadas v3.0 - Configuración de Tarea Programada"
echo "============================================================="
echo ""

# Obtener el directorio donde está este script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"
SHELL_SCRIPT="$APP_DIR/DescargasOrdenadas.sh"

echo "📁 Directorio de la aplicación: $APP_DIR"
echo "🚀 Script de inicio: $SHELL_SCRIPT"
echo ""

# Verificar que el script existe
if [ ! -f "$SHELL_SCRIPT" ]; then
    echo "❌ No se encontró DescargasOrdenadas.sh"
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
echo "1. Tarea al INICIO del sistema (systemd)"
echo "2. Tarea cada HORA (cron)"
echo "3. Tarea DIARIA (cron)"
echo "4. Tarea al INICIO de sesión (autostart)"
echo "5. ELIMINAR todas las tareas"
echo ""
read -p "Selecciona una opción (1-5): " opcion

case $opcion in
    1)
        echo ""
        echo "⏰ Configurando servicio systemd para inicio del sistema..."
        
        # Crear archivo de servicio systemd
        SERVICE_FILE="/etc/systemd/system/descargas-ordenadas.service"
        
        # Verificar permisos de sudo
        if ! sudo -v 2>/dev/null; then
            echo "❌ Se requieren permisos de administrador (sudo)"
            read -p "Presiona Enter para cerrar..." || true
            exit 1
        fi
        
        # Crear el archivo de servicio
        sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=DescargasOrdenadas - Organizador automático de archivos
After=network.target

[Service]
Type=oneshot
ExecStart=$SHELL_SCRIPT --inicio-sistema
User=$USER
WorkingDirectory=$APP_DIR
Environment=HOME=$HOME
Environment=PATH=$PATH

[Install]
WantedBy=multi-user.target
EOF
        
        # Recargar systemd y habilitar el servicio
        sudo systemctl daemon-reload
        sudo systemctl enable descargas-ordenadas.service
        
        if [ $? -eq 0 ]; then
            echo "✅ Servicio systemd creado exitosamente"
            echo "🚀 Se ejecutará automáticamente al iniciar el sistema"
            echo ""
            echo "💡 Comandos útiles:"
            echo "   Ver estado: sudo systemctl status descargas-ordenadas"
            echo "   Desactivar: sudo systemctl disable descargas-ordenadas"
            echo "   Eliminar: sudo rm $SERVICE_FILE && sudo systemctl daemon-reload"
        else
            echo "❌ Error al configurar el servicio systemd"
        fi
        ;;
        
    2)
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
        fi
        ;;
        
    3)
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
        fi
        ;;
        
    4)
        echo ""
        echo "⏰ Configurando autostart para inicio de sesión..."
        
        # Crear directorio autostart si no existe
        AUTOSTART_DIR="$HOME/.config/autostart"
        mkdir -p "$AUTOSTART_DIR"
        
        # Crear archivo .desktop
        DESKTOP_FILE="$AUTOSTART_DIR/descargas-ordenadas.desktop"
        
        cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=DescargasOrdenadas
Comment=Organizador automático de archivos al inicio
Exec=$SHELL_SCRIPT --inicio-sistema
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
        
        if [ $? -eq 0 ]; then
            echo "✅ Autostart configurado exitosamente"
            echo "🚀 Se ejecutará al iniciar sesión de usuario"
            echo ""
            echo "💡 Archivo creado en: $DESKTOP_FILE"
        else
            echo "❌ Error al configurar autostart"
        fi
        ;;
        
    5)
        echo ""
        echo "❌ Eliminando todas las tareas de DescargasOrdenadas..."
        
        # Eliminar servicio systemd
        sudo systemctl disable descargas-ordenadas.service 2>/dev/null
        sudo rm -f /etc/systemd/system/descargas-ordenadas.service
        sudo systemctl daemon-reload 2>/dev/null
        
        # Eliminar tareas cron
        crontab -l 2>/dev/null | grep -v "DescargasOrdenadas" | crontab - 2>/dev/null
        
        # Eliminar autostart
        rm -f "$HOME/.config/autostart/descargas-ordenadas.desktop"
        
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

# Verificar systemd
if systemctl is-enabled descargas-ordenadas.service >/dev/null 2>&1; then
    echo "✅ Servicio systemd: ACTIVO"
else
    echo "❌ Servicio systemd: NO ACTIVO"
fi

# Verificar cron
if crontab -l 2>/dev/null | grep -q "DescargasOrdenadas"; then
    echo "✅ Tareas cron: ACTIVAS"
    crontab -l 2>/dev/null | grep "DescargasOrdenadas" | sed 's/^/   /'
else
    echo "❌ Tareas cron: NO ACTIVAS"
fi

# Verificar autostart
if [ -f "$HOME/.config/autostart/descargas-ordenadas.desktop" ]; then
    echo "✅ Autostart: ACTIVO"
else
    echo "❌ Autostart: NO ACTIVO"
fi

echo ""
read -p "Presiona Enter para cerrar..." || true 