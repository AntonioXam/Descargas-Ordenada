#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para demostrar el funcionamiento completo del organizador.
Crea archivos de ejemplo y los organiza.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

def crear_archivos_de_prueba(carpeta_test):
    """Crea archivos de ejemplo para probar la organización."""
    carpeta_test = Path(carpeta_test)
    carpeta_test.mkdir(exist_ok=True)
    
    # Archivos de ejemplo con diferentes extensiones
    archivos_ejemplo = [
        # Imágenes
        "foto_vacaciones.jpg",
        "captura_pantalla.png", 
        "logo_empresa.svg",
        "icono_app.ico",
        "diseño_photoshop.psd",
        
        # Videos
        "pelicula_completa.mp4",
        "clip_divertido.webm",
        "tutorial_programacion.avi",
        "grabacion_pantalla.mov",
        
        # Audio
        "cancion_favorita.mp3",
        "podcast_interesante.m4a",
        "efecto_sonido.wav",
        "audiolibro_capitulo1.m4b",
        
        # Documentos
        "informe_trabajo.pdf",
        "documento_importante.docx",
        "notas_reunión.txt",
        "presentacion_ventas.pptx",
        "hoja_calculos.xlsx",
        
        # Código
        "script_python.py",
        "pagina_web.html",
        "estilos.css",
        "aplicacion.js",
        "configuracion.json",
        
        # Comprimidos
        "backup_fotos.zip",
        "archivos_importantes.rar",
        "proyecto_completo.7z",
        
        # Ejecutables
        "instalador_programa.exe",
        "aplicacion_portatil.msi",
        "script_automatizacion.bat",
        
        # Ebooks
        "libro_programacion.epub",
        "manual_usuario.pdf",
        "comic_digital.cbr",
        
        # 3D y CAD
        "modelo_3d.obj",
        "diseño_mecanico.dwg",
        "textura_material.mtl",
        
        # Fuentes
        "tipografia_moderna.ttf",
        "fuente_web.woff2",
        
        # Datos
        "base_datos.sqlite",
        "configuracion_sistema.xml",
        "datos_experimento.csv",
        
        # Backups
        "respaldo_documentos.bak",
        "copia_seguridad.backup",
        
        # Otros formatos menos comunes
        "archivo_desconocido.xyz",
        "datos_especiales.custom",
        
        # Subtítulos
        "pelicula_subtitulos.srt",
        "video_traducido.vtt",
        
        # Videojuegos
        "juego_retro.rom",
        "partida_guardada.sav",
        
        # P2P
        "descarga_torrent.torrent",
        "enlace_magnet.magnet",
        
        # Configuración
        "ajustes_aplicacion.ini",
        "preferencias_usuario.conf",
    ]
    
    print(f"📁 Creando {len(archivos_ejemplo)} archivos de prueba en: {carpeta_test}")
    
    # Crear archivos vacíos
    for archivo in archivos_ejemplo:
        archivo_path = carpeta_test / archivo
        archivo_path.touch()
        print(f"   ✅ {archivo}")
    
    # Crear algunas carpetas también
    carpetas_ejemplo = ["Carpeta_Vieja", "Documentos_Antiguos", "Backup_2023"]
    for carpeta in carpetas_ejemplo:
        carpeta_path = carpeta_test / carpeta
        carpeta_path.mkdir(exist_ok=True)
        # Crear algunos archivos dentro
        (carpeta_path / "archivo_interno.txt").touch()
        print(f"   📂 {carpeta}/")
    
    print(f"\n✅ Archivos de prueba creados exitosamente!")
    return carpeta_test

def probar_organizacion(carpeta_test):
    """Prueba la organización con los archivos de ejemplo."""
    print(f"\n🔄 Iniciando prueba de organización...")
    
    try:
        # Importar el organizador
        from organizer.file_organizer import OrganizadorArchivos
        
        # Crear organizador
        organizador = OrganizadorArchivos(carpeta_descargas=str(carpeta_test), usar_subcarpetas=True)
        
        print(f"📊 Archivos encontrados antes de organizar:")
        archivos_antes = list(carpeta_test.glob("*"))
        for item in archivos_antes:
            if item.is_file():
                print(f"   📄 {item.name}")
            else:
                print(f"   📂 {item.name}/")
        
        # Organizar
        print(f"\n🚀 Ejecutando organización...")
        resultados, errores = organizador.organizar(organizar_subcarpetas=True)
        
        # Mostrar resultados
        total_archivos = sum(len(files) for cat in resultados.values() for files in cat.values())
        print(f"\n✅ Organización completada!")
        print(f"📈 Total de archivos organizados: {total_archivos}")
        
        if errores:
            print(f"⚠️  Errores encontrados: {len(errores)}")
            for error in errores[:3]:  # Mostrar solo los primeros 3
                print(f"   ❌ {error}")
        
        # Mostrar resumen por categorías
        print(f"\n📊 Resumen de organización:")
        for categoria, subcategorias in resultados.items():
            total_cat = sum(len(files) for files in subcategorias.values())
            print(f"  📂 {categoria}: {total_cat} archivos")
            for subcat, files in subcategorias.items():
                if files and len(subcategorias) > 1:
                    print(f"    📁 {subcat}: {len(files)} archivos")
                    for archivo in files[:2]:  # Mostrar solo los primeros 2 archivos
                        print(f"      📄 {archivo}")
                    if len(files) > 2:
                        print(f"      ... y {len(files) - 2} más")
        
        # Verificar estructura final
        print(f"\n📁 Estructura final de carpetas:")
        for item in sorted(carpeta_test.iterdir()):
            if item.is_dir() and not item.name.startswith('.'):
                archivos_en_carpeta = len(list(item.rglob("*")))
                print(f"  📂 {item.name}/ ({archivos_en_carpeta} elementos)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal del script de prueba."""
    print("=" * 60)
    print("   PRUEBA DEL ORGANIZADOR DE DESCARGAS")
    print("=" * 60)
    print()
    
    # Crear carpeta temporal para la prueba
    carpeta_test = Path(tempfile.mkdtemp(prefix="test_descargasordenadas_"))
    
    try:
        # Crear archivos de ejemplo
        crear_archivos_de_prueba(carpeta_test)
        
        # Probar organización
        exito = probar_organizacion(carpeta_test)
        
        if exito:
            print(f"\n🎉 ¡Prueba completada exitosamente!")
            print(f"📁 Puedes revisar los resultados en: {carpeta_test}")
            
            respuesta = input(f"\n¿Quieres mantener los archivos de prueba? (s/N): ").lower().strip()
            if respuesta != 's' and respuesta != 'sí':
                shutil.rmtree(carpeta_test)
                print(f"🗑️  Archivos de prueba eliminados.")
            else:
                print(f"📁 Archivos mantenidos en: {carpeta_test}")
        else:
            print(f"\n❌ La prueba falló.")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Prueba cancelada por el usuario.")
        shutil.rmtree(carpeta_test, ignore_errors=True)
        return 1
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        shutil.rmtree(carpeta_test, ignore_errors=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 