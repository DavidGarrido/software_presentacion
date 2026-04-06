#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Matar instancias previas
pkill -f "servidor_grabacion.py" 2>/dev/null
pkill ngrok 2>/dev/null
sleep 2

# Iniciar servidor
python3 servidor_grabacion.py > /tmp/srv.log 2>&1 &
echo "✅ Servidor HTTP iniciado en http://localhost:8000"

# Iniciar ngrok
ngrok http 8000 --log=stdout > /tmp/ngrok.log 2>&1 &
echo "⏳ Esperando ngrok..."
sleep 4

# Obtener URL de ngrok
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | \
    python3 -c "import sys,json; [print(t['public_url']) for t in json.load(sys.stdin)['tunnels'] if t['proto']=='https']" 2>/dev/null)

if [ -z "$NGROK_URL" ]; then
    echo "❌ No se pudo obtener la URL de ngrok"
    exit 1
fi

TARGET="${NGROK_URL}/control_celular.html"

# Generar celular.html con la URL actualizada
cat > "$DIR/celular.html" << EOF
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=${TARGET}">
    <title>Redirigiendo...</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: white;
               display: flex; flex-direction: column; align-items: center;
               justify-content: center; height: 100vh; margin: 0; }
        a { color: #00d4ff; font-size: 1.2rem; margin-top: 20px; }
        p { color: #aaa; }
    </style>
</head>
<body>
    <p>Redirigiendo al celular...</p>
    <a href="${TARGET}">${TARGET}</a>
    <script>window.location.href = "${TARGET}";</script>
</body>
</html>
EOF

echo ""
echo "=========================================="
echo "  Presentador: http://localhost:8000/PRESENTACION_PRESENTADOR.html"
echo "  Celular:     http://localhost:8000/celular.html"
echo "  Ngrok:       ${TARGET}"
echo "=========================================="
