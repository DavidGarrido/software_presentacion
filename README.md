# Video Sustentación - Censo DANE 2018
**GA2-240201528-AA3-EV01**

---

## Estructura del proyecto

```
video_censo_dane/
├── PRESENTACION_PRESENTADOR.html   # Vista del presentador (guión + control OBS)
├── PRESENTACION_PROYECTOR.html     # Vista del proyector (pantalla completa)
├── GUION_VIDEO_CENSO.md            # Guión por sección
├── DATOS_CENSO_2018.md             # Datos oficiales DANE corregidos
├── ANALISIS_VARIABLES_DEMOGRAFICAS.md
├── servidor_grabacion.py           # Servidor HTTP multihilo con API
├── generar_presentacion.py         # Genera el .pptx con notas
├── Censo_DANE_2018_Presentacion.pptx
├── celular.html                    # Redirección a ngrok para el celular
├── grabaciones/ → symlink a ~/Documentos/Documentos/videos/
├── enlaces_dane/                   # Accesos directos .desktop al DANE
└── iniciar.sh                      # Script de inicio del servidor + ngrok
```

---

## Servidor (`servidor_grabacion.py`)

Servidor HTTP multihilo que expone:

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/estado` | GET | Estado actual de grabación (JSON) |
| `/api/iniciar` | GET | Marcar inicio de grabación |
| `/api/detener` | GET | Marcar fin de grabación |
| `/api/ultimo_audio` | GET | Nombre del último audio grabado |
| `/api/audio` | POST | Recibe y guarda audio del celular |
| `/control_celular.html` | GET | Página para el celular |

**Puerto:** 8000
**Inicio:** `python3 servidor_grabacion.py`

---

## Celular

El celular accede via ngrok (HTTPS obligatorio para micrófono):
1. PC sirve `http://localhost:8000/celular.html`
2. Esa página redirige a `https://<ngrok>/control_celular.html`
3. El celular graba audio con `MediaRecorder` sincronizado con OBS
4. Al detener OBS, el audio se envía via POST a `/api/audio`

---

## Conexión OBS WebSocket

### Problema original
La integración usaba la librería `obs-websocket-js@5.0.3` cargada desde CDN.
Fallaba con el error `{"isTrusted":true}` porque:
- La librería no era compatible con OBS WebSocket 5.6.3 en contexto de navegador
- No había campo de contraseña (OBS 28+ requiere autenticación)

### Solución
Se reemplazó la librería externa por una implementación nativa con la API del navegador (`WebSocket` + `crypto.subtle`):

```js
// Autenticación manual con SHA-256
async function sha256b64(text) {
    const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
    return btoa(String.fromCharCode(...new Uint8Array(buf)));
}

// Flujo de conexión OBS WebSocket 5.x
// op 0 = Hello  → calcular auth y enviar Identify (op 1)
// op 2 = Identified → conectado
// op 5 = Event  → detectar RecordStateChanged
// op 6 = Request, op 7 = RequestResponse
```

La autenticación sigue el protocolo oficial:
```
secret = base64(sha256(password + salt))
auth   = base64(sha256(secret + challenge))
```

### Eventos suscritos
`eventSubscriptions: 64` (Output events) para detectar `RecordStateChanged`
y obtener `outputPath` cuando termina la grabación.

---

## Script de inicio (`iniciar.sh`)

Levanta el servidor y ngrok, genera `celular.html` con la URL actualizada:
```bash
bash iniciar.sh
```
