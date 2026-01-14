#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para la funcionalidad de bandeja del sistema
"""

import sys
import os

# Agregar el directorio del organizador al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from organizer.gui_avanzada import run_advanced_gui

if __name__ == "__main__":
    print("🍄 Iniciando GUI Avanzada con Bandeja del Sistema...")
    print("📋 Funcionalidades:")
    print("   • Minimizar a bandeja del sistema")
    print("   • Cerrar completamente con X")
    print("   • Auto-organización opcional")
    print("   • Menú contextual en bandeja")
    print("   • Notificaciones del sistema")
    print()
    
    try:
        run_advanced_gui()
    except KeyboardInterrupt:
        print("\n🚪 Aplicación cerrada por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc() 