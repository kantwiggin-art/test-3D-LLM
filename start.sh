#!/usr/bin/env bash

# Exit on error
set -e

PORT=8080

echo "=========================================================="
echo "  🚀 INICIANDO MUNDO PSICODÉLICO BABYLON.JS EN CODESPACES"
echo "=========================================================="
echo ""

# Check if port 8080 is already in use and free it
if lsof -t -i :$PORT >/dev/null 2>&1; then
    echo "📌 Liberando puerto $PORT..."
    kill -9 $(lsof -t -i :$PORT) 2>/dev/null || true
fi

echo "🌐 Servidor web iniciando en el puerto $PORT..."
echo ""
echo "----------------------------------------------------------"
echo "   Para jugar en tu navegador desde GitHub Codespaces:"
echo "   1. Haz clic en la pestaña 'PORTS' (PUERTOS) abajo en VS Code."
echo "   2. Ubica el puerto $PORT."
echo "   3. Haz clic en el icono del globo 🌐 (Abrir en el navegador) o navega a:"
echo "      http://localhost:$PORT/babylon_scene/index.html"
echo "----------------------------------------------------------"
echo ""

# Launch Python HTTP server
python3 -m http.server $PORT
