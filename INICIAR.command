#!/usr/bin/env bash
# DescargasOrdenadas - Lanzador de doble clic para macOS
# Al abrirlo desde Finder se ejecuta INICIAR.sh en una ventana de Terminal.
cd "$(dirname "$0")"
exec ./INICIAR.sh "$@"
