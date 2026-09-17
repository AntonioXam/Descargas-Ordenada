# 📦 Instaladores de DescargasOrdenadas

DescargasOrdenadas se puede distribuir como aplicación instalable en **Windows**, **macOS** y **Linux**.

Los instaladores se generan automáticamente en GitHub cuando publicas un tag `vX.Y.Z`.

## 🚀 Cómo generar los instaladores

1. Sube tus cambios a `main`.
2. Publica un release con un tag tipo `v3.5.0`.
3. GitHub Actions genera automáticamente:
   - `DescargasOrdenadas-Setup-vX.Y.Z.exe` para Windows.
   - `DescargasOrdenadas-vX.Y.Z.pkg` para macOS.
   - `DescargasOrdenadas-vX.Y.Z-ARCH.deb` para Linux.

Los archivos se adjuntan solos al release.

## 🪟 Windows

El instalador `.exe` abre un asistente de instalación:

- Pide permisos de administrador.
- Crea el menú de inicio.
- Crea un icono en el escritorio.
- Instala la app en `Archivos de programa`.

## 🍎 macOS

El instalador `.pkg` abre el instalador nativo de macOS:

- Pide contraseña de administrador.
- Instala la app en `/Applications`.
- No necesita dependencias externas.

Como el paquete no está firmado con un certificado de Apple, la primera vez puede que macOS muestre un aviso de seguridad.

Para abrirlo la primera vez:

1. Haz clic derecho sobre la app.
2. Selecciona **Abrir**.
3. Confirma que quieres ejecutarla.

## 🐧 Linux

El paquete `.deb` se puede instalar con:

```bash
sudo dpkg -i DescargasOrdenadas-v3.5.0-amd64.deb
```

La app se instala en `/opt/DescargasOrdenadas` y crea una entrada en el menú de aplicaciones.

## 🧑‍💻 Construcción local

Si quieres generar un instalador en tu máquina, también puedes hacerlo manualmente.

En macOS:

```bash
.venv/bin/python -m PyInstaller packaging/DescargasOrdenadas.spec --noconfirm --clean
codesign --force --deep --sign - dist/DescargasOrdenadas.app
productbuild --component dist/DescargasOrdenadas.app /Applications \
  --identifier com.antonioxam.DescargasOrdenadas \
  --version "$(cat VERSION.txt)" \
  "dist/DescargasOrdenadas-v$(cat VERSION.txt).pkg"
```

El resto de sistemas usan el mismo spec de PyInstaller y luego empaquetan el resultado con Inno Setup o `dpkg-deb`.
