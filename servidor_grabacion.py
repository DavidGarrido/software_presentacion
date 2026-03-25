#!/usr/bin/env python3
"""
Servidor de control de grabación sincronizado
Accede desde PC: http://localhost:8000/PRESENTACION_PRESENTADOR.html
Accede desde celular: https://<ngrok>/control_celular.html  (via celular.html)
"""

import http.server
import socketserver
import socket
import os
import json
from datetime import datetime
from urllib.parse import urlparse

PUERTO = 8000
CARPETA_BASE = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_ESTADO = os.path.join(CARPETA_BASE, "estado_grabacion.json")

def obtener_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def leer_estado():
    if os.path.exists(ARCHIVO_ESTADO):
        try:
            with open(ARCHIVO_ESTADO, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"grabando": False, "inicio": None, "fin": None}

def guardar_estado(estado):
    with open(ARCHIVO_ESTADO, 'w') as f:
        json.dump(estado, f)


class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=CARPETA_BASE, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/audio':
            length = int(self.headers.get('Content-Length', 0))
            data   = self.rfile.read(length)
            ts     = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            ext    = self.headers.get('Content-Type', 'audio/webm').split('/')[-1].split(';')[0]
            fname  = f'audio_celular_{ts}.{ext}'
            carpeta = os.path.join(CARPETA_BASE, 'grabaciones')
            os.makedirs(carpeta, exist_ok=True)
            fpath  = os.path.join(carpeta, fname)
            with open(fpath, 'wb') as f:
                f.write(data)
            print(f'✅ Audio guardado: {fname} ({len(data)//1024} KB)')
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'archivo': fname}).encode())
            return
        self.send_response(404)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # API: Último audio grabado
        if path == '/api/ultimo_audio':
            carpeta = os.path.join(CARPETA_BASE, 'grabaciones')
            try:
                audios = sorted(
                    [f for f in os.listdir(carpeta) if f.startswith('audio_celular_')],
                    reverse=True
                )
            except:
                audios = []
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'archivo': audios[0] if audios else None}).encode())
            return

        # API: Obtener estado
        if path == '/api/estado':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(leer_estado()).encode())
            return

        # API: Iniciar grabación
        if path == '/api/iniciar':
            estado = {"grabando": True, "inicio": datetime.now().isoformat(), "fin": None}
            guardar_estado(estado)
            # Reproducir música al iniciar grabación
            try:
                import urllib.request
                urllib.request.urlopen(urllib.request.Request(
                    'http://localhost:26538/api/v1/previous', data=b'',
                    headers={'accept': '*/*'}, method='POST'), timeout=2)
                urllib.request.urlopen(urllib.request.Request(
                    'http://localhost:26538/api/v1/play', data=b'',
                    headers={'accept': '*/*'}, method='POST'), timeout=2)
                print('🎵 Música iniciada')
            except Exception as e:
                print(f'⚠️  Música: {e}')
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "estado": estado}).encode())
            return

        # API: Detener grabación
        if path == '/api/detener':
            estado = leer_estado()
            estado["grabando"] = False
            estado["fin"] = datetime.now().isoformat()
            guardar_estado(estado)
            # Pausar música al terminar grabación
            try:
                import urllib.request
                urllib.request.urlopen(urllib.request.Request(
                    'http://localhost:26538/api/v1/pause', data=b'',
                    headers={'accept': '*/*'}, method='POST'), timeout=2)
                print('⏸️  Música pausada')
            except Exception as e:
                print(f'⚠️  Música: {e}')
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "estado": estado}).encode())
            return

        # Página celular
        if path in ('/control_celular.html', '/celular_control'):
            self.servir_pagina_celular()
            return

        return super().do_GET()

    def servir_pagina_celular(self):
        ip_local = obtener_ip_local()
        html = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Control de Grabación</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            padding: 20px;
        }
        .container { text-align: center; width: 100%; max-width: 400px; }
        h1 { color: #fff; margin-bottom: 10px; font-size: 1.8rem; }
        .info { color: #888; margin-bottom: 30px; font-size: 0.9rem; }
        .ip { color: #00ff88; font-weight: bold; }
        .status {
            font-size: 2rem; margin: 30px 0; padding: 20px;
            border-radius: 20px; font-weight: bold;
        }
        .status.grabando {
            background: rgba(231,76,60,0.2); color: #e74c3c;
            animation: pulse 1.5s infinite;
        }
        .status.detenido { background: rgba(127,140,141,0.2); color: #7f8c8d; }
        @keyframes pulse {
            0%,100% { box-shadow: 0 0 0 0 rgba(231,76,60,0.5); }
            50% { box-shadow: 0 0 0 20px rgba(231,76,60,0); }
        }
        .timer { color: #00d4ff; font-size: 3rem; font-weight: bold; font-family: monospace; margin: 20px 0; }
        .mic-status { margin-top: 20px; padding: 12px; border-radius: 12px;
            background: rgba(255,255,255,0.05); font-size: 0.9rem; color: #aaa; }
        .btn { margin-top: 15px; width: 100%; padding: 14px; border: none; border-radius: 12px;
            background: #00d4ff; color: #1a1a2e; font-size: 1rem; font-weight: bold; cursor: pointer; }
        .audio-guardado { display:none; margin-top:10px; padding:10px;
            background: rgba(46,204,113,0.15); border-radius:10px;
            font-size: 0.85rem; color: #2ecc71; }
        .help { color: #666; font-size: 0.8rem; margin-top: 30px; }
    </style>
</head>
<body>
<div class="container">
    <h1>📹 Control de Grabación</h1>
    <p class="info">PC: <span class="ip">''' + ip_local + '''</span></p>

    <div id="status" class="status detenido">⏹ NO GRABANDO</div>
    <div id="timer" class="timer">00:00</div>

    <div class="mic-status">🎤 <span id="micLabel">Toca para activar micrófono</span></div>
    <button class="btn" id="micBtn" onclick="pedirMicrofono()">🎤 Activar Micrófono</button>
    <div class="audio-guardado" id="audioGuardado"></div>

    <p class="help">El audio se graba automáticamente con OBS<br>y se guarda en el servidor</p>
</div>

<script>
    let estadoAnterior = null;
    let micStream = null;
    let mediaRecorder = null;
    let audioChunks = [];
    let grabandoAudio = false;

    async function pedirMicrofono() {
        const label = document.getElementById('micLabel');
        const btn   = document.getElementById('micBtn');
        try {
            micStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
            label.textContent = '✅ Micrófono activo — esperando grabación';
            label.style.color = '#2ecc71';
            btn.textContent = '🎤 Micrófono activo';
            btn.style.background = '#2ecc71';
        } catch(e) {
            label.textContent = '❌ ' + (e.name === 'NotAllowedError' ? 'Permiso denegado' : e.message);
            label.style.color = '#e74c3c';
        }
    }

    function iniciarGrabacionAudio() {
        if (!micStream || grabandoAudio) return;
        audioChunks = [];
        const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
            ? 'audio/webm;codecs=opus' : 'audio/webm';
        mediaRecorder = new MediaRecorder(micStream, { mimeType });
        mediaRecorder.ondataavailable = e => { if (e.data.size > 0) audioChunks.push(e.data); };
        mediaRecorder.onstop = enviarAudio;
        mediaRecorder.start(1000);
        grabandoAudio = true;
        document.getElementById('micLabel').textContent = '🔴 Grabando audio...';
    }

    function detenerGrabacionAudio() {
        if (!mediaRecorder || !grabandoAudio) return;
        mediaRecorder.stop();
        grabandoAudio = false;
    }

    async function enviarAudio() {
        if (audioChunks.length === 0) return;
        const blob = new Blob(audioChunks, { type: mediaRecorder.mimeType });
        document.getElementById('micLabel').textContent = '⬆️ Enviando audio...';
        try {
            const res  = await fetch('/api/audio', {
                method: 'POST',
                headers: { 'Content-Type': mediaRecorder.mimeType },
                body: blob
            });
            const data = await res.json();
            const div  = document.getElementById('audioGuardado');
            div.style.display = 'block';
            div.textContent = '✅ Guardado: ' + data.archivo;
            document.getElementById('micLabel').textContent = '✅ Listo — esperando grabación';
        } catch(e) {
            document.getElementById('micLabel').textContent = '❌ Error: ' + e.message;
        }
    }

    function actualizarEstado() {
        fetch('/api/estado')
            .then(r => r.json())
            .then(estado => {
                const key = JSON.stringify(estado);
                if (key === estadoAnterior) return;
                estadoAnterior = key;

                const statusEl = document.getElementById('status');
                const timerEl  = document.getElementById('timer');

                if (estado.grabando) {
                    statusEl.innerHTML = '🔴 GRABANDO';
                    statusEl.className = 'status grabando';
                    iniciarGrabacionAudio();
                    if (estado.inicio) {
                        const diff = Math.floor((new Date() - new Date(estado.inicio)) / 1000);
                        const m = String(Math.floor(diff/60)).padStart(2,'0');
                        const s = String(diff % 60).padStart(2,'0');
                        timerEl.textContent = m + ':' + s;
                    }
                } else {
                    statusEl.innerHTML = '⏹ NO GRABANDO';
                    statusEl.className = 'status detenido';
                    detenerGrabacionAudio();
                    timerEl.textContent = '00:00';
                }
            })
            .catch(() => {});
    }

    window.addEventListener('load', () => setTimeout(pedirMicrofono, 500));
    setInterval(actualizarEstado, 1000);
</script>
</body>
</html>'''
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def log_message(self, format, *args):
        # Suprimir logs de polling frecuente
        if '/api/estado' in (args[0] if args else ''):
            return
        super().log_message(format, *args)


def main():
    ip_local = obtener_ip_local()
    print(f"\n{'='*60}")
    print(f"🎬 SERVIDOR DE GRABACIÓN SINCRONIZADA")
    print(f"{'='*60}")
    print(f"\n💻 Presentador: http://localhost:{PUERTO}/PRESENTACION_PRESENTADOR.html")
    print(f"📱 Celular:     http://localhost:{PUERTO}/celular.html  (redirige a ngrok)")
    print(f"\n{'='*60}\n")

    with ThreadedServer(("", PUERTO), Handler) as httpd:
        print(f"✅ Servidor HTTP en puerto {PUERTO}")
        print(f"Presiona Ctrl+C para detener\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Servidor detenido")

if __name__ == "__main__":
    main()
