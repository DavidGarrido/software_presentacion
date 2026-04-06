# Cómo crear una presentación personalizada con plantilla HTML

Esta guía explica cómo crear una presentación con diseño HTML propio (como `PRESENTACION_BELEN.html`) y conectarla al sistema del presentador.

---

## Estructura del sistema

```
PRESENTACION_PRESENTADOR.html   ← Panel del presentador (controles)
        │
        │  postMessage (goto / next / prev / camera)
        ▼
[tu_presentacion.html]          ← Plantilla HTML personalizada
```

El presentador envía mensajes a tu HTML para:
- Cambiar de slide
- Activar/desactivar la cámara

---

## Paso 1 — Crear el archivo HTML

Crea un archivo HTML (ej. `MI_PRESENTACION.html`) con tus slides.

### Estructura mínima requerida

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { overflow:hidden; height:100vh; }

        .slide {
            position:absolute;
            inset:0;
            display:flex;
            flex-direction:column;
            align-items:center;
            justify-content:center;
            opacity:0;
            visibility:hidden;
            transition:opacity 0.5s;
        }
        .slide.active { opacity:1; visibility:visible; }

        /* Espacio para la cámara — oculto hasta que se active */
        .cam-wrap { display:none; }
        .cam-wrap.activa { display:flex; }
    </style>
</head>
<body>

    <!-- Slide 0 -->
    <div class="slide active" data-slide="0">
        <h1>Título del slide</h1>
        <!-- Espacio para la cámara -->
        <div class="cam-wrap">
            <div class="cam-inner"></div>
        </div>
        <p>Contenido del slide</p>
    </div>

    <!-- Slide 1 -->
    <div class="slide" data-slide="1">
        <h1>Segundo slide</h1>
        <div class="cam-wrap">
            <div class="cam-inner"></div>
        </div>
        <p>Más contenido</p>
    </div>

<script>
    // ── Control de slides ────────────────────────────────────
    let currentSlide = 0;
    const slides = document.querySelectorAll('.slide');

    function showSlide(n) {
        if (n < 0 || n >= slides.length) return;
        slides[currentSlide].classList.remove('active');
        currentSlide = n;
        slides[currentSlide].classList.add('active');
        // Notificar al presentador
        try { window.parent.postMessage({ action:'slideChanged', index:n }, '*'); } catch(e){}
    }

    function nextSlide() { showSlide(currentSlide + 1); }
    function prevSlide() { showSlide(currentSlide - 1); }

    // Teclas
    document.addEventListener('keydown', e => {
        if (e.key === 'ArrowRight' || e.key === ' ') nextSlide();
        if (e.key === 'ArrowLeft')                   prevSlide();
    });

    // ── Cámara ───────────────────────────────────────────────
    let camStream = null;

    async function activarCamara() {
        if (camStream) return;
        try {
            camStream = await navigator.mediaDevices.getUserMedia({ video:true, audio:false });
            document.querySelectorAll('.cam-inner').forEach(el => {
                const v = document.createElement('video');
                v.srcObject = camStream;
                v.autoplay = true;
                v.muted = true;
                v.playsInline = true;
                v.style.cssText = 'width:100%;height:100%;object-fit:cover;';
                el.innerHTML = '';
                el.appendChild(v);
            });
            document.querySelectorAll('.cam-wrap').forEach(el => el.classList.add('activa'));
        } catch(e) {
            console.warn('Cámara no disponible:', e.message);
        }
    }

    function desactivarCamara() {
        if (camStream) { camStream.getTracks().forEach(t => t.stop()); camStream = null; }
        document.querySelectorAll('.cam-wrap').forEach(el => el.classList.remove('activa'));
    }

    // ── Mensajes del presentador (OBLIGATORIO) ───────────────
    window.addEventListener('message', e => {
        const d = e.data;
        if (!d) return;
        if (d.action === 'goto')   showSlide(d.index);
        if (d.action === 'next')   nextSlide();
        if (d.action === 'prev')   prevSlide();
        if (d.action === 'load' && typeof d.index === 'number') showSlide(d.index);
        if (d.action === 'camera') {
            if (d.enabled) activarCamara();
            else           desactivarCamara();
        }
    });
</script>
</body>
</html>
```

---

## Paso 2 — Crear el archivo JSON

Crea `slides_mi_presentacion.json`:

```json
{
  "name": "Nombre de la presentación",
  "viewer": "MI_PRESENTACION.html",
  "slides": [
    {
      "layout": "cover",
      "bg": "#1a1a2e",
      "tag": "Subtítulo",
      "title": "Título principal",
      "content": "Descripción",
      "notes": "Notas del presentador para este slide."
    },
    {
      "layout": "",
      "bg": "#0d0d1a",
      "tag": "Sección",
      "title": "Segundo slide",
      "content": "Punto 1\nPunto 2\nPunto 3",
      "notes": "Explica cada punto."
    }
  ]
}
```

### Campo `viewer` (clave)
El campo `"viewer"` le dice al presentador qué HTML cargar en vez del genérico `viewer.html`. Debe ser el nombre del archivo HTML en la misma carpeta.

### Campos de cada slide

| Campo | Descripción |
|-------|-------------|
| `title` | Título principal del slide |
| `content` | Cuerpo / puntos (separados por `\n`) |
| `notes` | Notas del presentador (no se muestran en pantalla) |
| `tag` | Etiqueta pequeña encima del título |
| `layout` | `cover`, `highlight`, `image`, o `""` para bullets |
| `bg` | Color o gradiente de fondo (solo lo usa `viewer.html`, no el HTML personalizado) |

> **Nota:** En un HTML personalizado los campos `layout` y `bg` del JSON no se aplican automáticamente — el diseño visual lo controla tu HTML. Los campos `notes` sí los lee el presentador para mostrarlos en su panel.

---

## Paso 3 — Importar al presentador

1. Abre `PRESENTACION_PRESENTADOR.html`
2. Haz clic en **Presentaciones → Importar JSON**
3. Selecciona tu archivo `.json`
4. El presentador carga automáticamente tu HTML personalizado

---

## Consideraciones para la cámara

### Posición de la cámara en el slide
Coloca `.cam-wrap` donde quieras que aparezca la cámara. Ejemplos:

```html
<!-- Cámara en esquina inferior derecha -->
<div class="cam-wrap" style="position:fixed;bottom:20px;right:20px;width:200px;height:200px;">
    <div class="cam-inner" style="width:100%;height:100%;border-radius:50%;overflow:hidden;"></div>
</div>

<!-- Cámara centrada grande (como en PRESENTACION_BELEN.html) -->
<div class="cam-wrap" style="width:400px;height:400px;border-radius:50%;overflow:hidden;">
    <div class="cam-inner" style="width:100%;height:100%;"></div>
</div>
```

### Activación
La cámara se activa/desactiva desde el panel del presentador con el botón de cámara. El HTML la recibe por `postMessage` con `{ action: 'camera', enabled: true/false }`.

---

## Mensajes postMessage soportados

Tu HTML **debe** escuchar estos mensajes para funcionar con el presentador:

| Mensaje | Descripción |
|---------|-------------|
| `{ action: 'goto', index: N }` | Ir al slide N |
| `{ action: 'next' }` | Siguiente slide |
| `{ action: 'prev' }` | Slide anterior |
| `{ action: 'load', index: N }` | Carga inicial al slide N |
| `{ action: 'camera', enabled: true/false }` | Activar/desactivar cámara |

---

## Ejemplo real: `PRESENTACION_BELEN.html`

Esta presentación usa:
- Fondo rosado con partículas flotantes de emojis
- Anillo giratorio con la cámara en el centro de cada slide
- JSON: `slides_belen.json` con `"viewer": "PRESENTACION_BELEN.html"`

Puedes usarla como base para crear nuevas presentaciones personalizadas.
