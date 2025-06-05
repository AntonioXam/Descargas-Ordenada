# DescargasOrdenadas by x4mp0

Organizador de carpeta de descargas multiplataforma con interfaz gráfica para Windows, macOS y Linux.

## Características

- **Organización inteligente**: Clasifica automáticamente los archivos por tipo (imágenes, vídeos, documentos, etc.)
- **Interfaz gráfica amigable**: Fácil de usar con botón "Organizar ahora" y feedback visual
- **Arranque automático**: Opción para iniciar al arrancar el sistema
- **Soporte multiplataforma**: Funciona en Windows, macOS y Linux
- **Instalación sencilla**: Detecta e instala dependencias automáticamente

## Requisitos

- Python 3.10 o superior
- Conexión a internet (para la primera instalación de dependencias)

## Instalación

### Opción 1: Desde el código fuente

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu-usuario/DescargasOrdenadas.git
   cd DescargasOrdenadas
   ```

2. Ejecuta el programa:
   ```bash
   python main.py
   ```

   La primera vez que se ejecute, se instalarán automáticamente las dependencias necesarias (PySide6 y requests).

### Opción 2: Usando binarios precompilados

Descarga los binarios precompilados desde la sección [Releases](https://github.com/tu-usuario/DescargasOrdenadas/releases) para tu sistema operativo:

- Windows: `DescargasOrdenadas.exe`
- macOS: `DescargasOrdenadas.app`
- Linux: `DescargasOrdenadas.AppImage`

## Uso

1. **Ejecución**: Haz doble clic en el ejecutable `DescargasOrdenadas.exe` (Windows), `DescargasOrdenadas.app` (macOS) o `DescargasOrdenadas.AppImage` (Linux).

2. **Organizar archivos**: Haz clic en el botón "Organizar ahora" para clasificar y mover los archivos de tu carpeta de descargas.

3. **Auto-arranque**: Activa la opción "Auto-iniciar al arrancar el sistema" para que el programa se inicie automáticamente al encender el ordenador.

4. **Bandeja del sistema**: 
   - Al cerrar la ventana principal, la aplicación se minimiza a la bandeja del sistema.
   - Haz clic derecho en el icono de la bandeja para mostrar el menú con opciones.
   - Selecciona "Salir" para cerrar completamente la aplicación.

5. **Resultados**: La aplicación muestra un registro de los archivos procesados y te notifica cuando finaliza la organización.

## Estructura de carpetas

La aplicación organiza los archivos en una amplia variedad de carpetas según el tipo:

- **Imágenes**: jpg, png, gif, bmp, tiff, webp, svg, ico, psd, etc.
- **Vídeos**: mp4, avi, mkv, mov, wmv, webm, etc.
- **Audio**: mp3, wav, ogg, flac, aac, etc.
- **Documentos**: doc, docx, odt, rtf, txt, md, etc.
- **Hojas de cálculo**: xls, xlsx, ods, csv, etc.
- **Presentaciones**: ppt, pptx, odp, key, etc.
- **PDFs**: pdf
- **Ebooks**: epub, mobi, azw, etc.
- **Archivos 3D**: obj, fbx, 3ds, blend, stl, etc.
- **CAD**: dwg, dxf, step, iges, etc.
- **Código Fuente**: py, js, java, c, cpp, etc.
- **Web**: html, css, js, php, etc.
- **Datos**: json, xml, yaml, csv, sql, etc.
- **Imágenes de Disco**: iso, img, vhd, etc.
- **Fuentes**: ttf, otf, woff, etc.
- **Configuración**: ini, cfg, conf, json, etc.
- **Vectoriales**: svg, ai, eps, etc.
- **Subtítulos**: srt, sub, vtt, etc.
- **Backups**: bak, old, tmp, etc.
- **Ejecutables**: exe, msi, app, etc.
- **Comprimidos**: zip, rar, 7z, tar, etc.
- **Otros**: Extensiones no reconocidas
- **Carpetas**: Subdirectorios encontrados en la carpeta de descargas

## Desarrollo

### Configuración del entorno de desarrollo

1. Clona el repositorio y crea un entorno virtual:
   ```bash
   git clone https://github.com/tu-usuario/DescargasOrdenadas.git
   cd DescargasOrdenadas
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

2. Instala las dependencias de desarrollo:
   ```bash
   pip install -r requirements.txt
   ```

### Estructura del proyecto

- `main.py`: Punto de entrada de la aplicación
- `organizer/`: Módulo principal
  - `__init__.py`: Definición del paquete
  - `file_organizer.py`: Lógica de organización de archivos
  - `gui.py`: Interfaz gráfica con PySide6
  - `autostart.py`: Gestión del autoarranque
- `resources/`: Iconos y recursos
- `tests/`: Pruebas automatizadas
- `build.py`: Script para construir binarios

### Pruebas

Ejecuta las pruebas automatizadas con:

```bash
pytest
```

### Empaquetado

Usa el script `build.py` para crear binarios ejecutables para diferentes plataformas:

```bash
# Construir para la plataforma actual
python build.py

# Construir para una plataforma específica
python build.py --platform win  # Opciones: win, mac, linux

# Limpiar archivos de build anteriores
python build.py --clean
```

#### Requisitos para empaquetado

- **Windows**: PyInstaller
- **macOS**: PyInstaller y py2app
- **Linux**: PyInstaller y appimagetool

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Contribuir

Las contribuciones son bienvenidas. Para cambios importantes, por favor abre primero un issue para discutir lo que te gustaría cambiar. 
