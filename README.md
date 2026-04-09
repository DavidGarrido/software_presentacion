# Sistema de Presentaciones Multimedia

Herramienta web para crear, gestionar y grabar presentaciones con soporte para múltiples formatos y plantillas visuales.

---

## Estructura del proyecto

```
/
├── index.html                    # Página principal / menú
├── editor_presentacion.html      # Editor de presentaciones con IA
├── PRESENTACION_PRESENTADOR.html # Panel del presentador (guión + control)
├── viewer.html                   # Visor de presentaciones
├── landing_mobile.html           # Vista mobile
├── celular.html                  # Control remoto desde celular
├── mascara_obs.html              # Máscara para OBS
├── mic_analyzer.html             # Analizador de micrófono
├── servidor_grabacion.py         # Servidor HTTP con API de grabación
├── iniciar.sh                    # Script de inicio (servidor + ngrok)
├── templates.json                # Registro de plantillas disponibles
├── grabaciones/                  # Carpeta de grabaciones
└── templates/
    ├── template_moderno.html
    ├── template_bold.html
    ├── template_neon.html
    ├── template_elegante.html
    ├── template_minimalista.html
    ├── template_corporativo.html
    ├── template_institucional.html
    ├── template_tecnologica.html
    ├── template_educativa.html
    └── template_deportiva.html
```

---

## Inicio rápido

```bash
bash iniciar.sh
```

Esto levanta el servidor en `http://localhost:8000` y configura ngrok para acceso desde el celular.

---

## Servidor (`servidor_grabacion.py`)

Servidor HTTP multihilo en el puerto 8000:

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/estado` | GET | Estado actual de grabación |
| `/api/iniciar` | GET | Marca inicio de grabación |
| `/api/detener` | GET | Marca fin de grabación |
| `/api/ultimo_audio` | GET | Nombre del último audio grabado |
| `/api/audio` | POST | Recibe y guarda audio del celular |

---

## Plantillas disponibles

10 plantillas con estilos visuales distintos: moderno, bold, neon, elegante, minimalista, corporativo, institucional, tecnológica, educativa y deportiva.

---

## Control desde celular

Con ngrok activo, el celular accede a `https://<ngrok>/control_celular.html` para:
- Controlar slides remotamente
- Grabar audio sincronizado con OBS

---

## Documentación

- `NUEVA_PRESENTACION.md` — Cómo crear una nueva presentación
- `PRESENTACION_PERSONALIZADA.md` — Cómo usar plantillas HTML propias
- `INSTRUCTIVO_IA.md` — Cómo integrar generación por IA
