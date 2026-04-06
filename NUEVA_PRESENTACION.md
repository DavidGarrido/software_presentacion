# Cómo crear una nueva presentación

## Archivos que debes crear (3 en total)

---

## 1. `PRESENTACION_NOMBRE.html`

La presentación visual que se muestra en el proyector y en las miniaturas.

**Estructura base:**

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Mi Presentación</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family:'Segoe UI',Arial,sans-serif; background:#1a1a0e; color:white; overflow:hidden; }
        .slide-container { position:relative; width:100%; height:100vh; }
        .slide {
            position:absolute; top:0; left:0; width:100%; height:100%;
            display:flex; flex-direction:column; justify-content:center; align-items:center;
            padding:50px; opacity:0; visibility:hidden;
            transition:opacity 0.5s ease, transform 0.5s ease;
            transform:translateX(30px);
        }
        .slide.active { opacity:1; visibility:visible; transform:translateX(0); }
        .slide-counter { position:fixed; bottom:20px; left:50%; transform:translateX(-50%);
            font-size:0.9rem; color:rgba(255,255,255,0.4); }
    </style>
</head>
<body>
<div class="slide-container">

    <!-- DIAPOSITIVA 1 -->
    <div class="slide active">
        <h1>Título de la diapositiva 1</h1>
        <p>Contenido...</p>
    </div>

    <!-- DIAPOSITIVA 2 -->
    <div class="slide">
        <h1>Título de la diapositiva 2</h1>
        <p>Contenido...</p>
    </div>

    <!-- Agrega más diapositivas aquí -->

</div>

<div class="slide-counter">
    <span id="currentSlideNum">1</span> / <span id="totalSlidesNum">2</span>
</div>

<script>
    let currentSlide = 0;
    const slides = document.querySelectorAll('.slide');
    const total  = slides.length;
    document.getElementById('totalSlidesNum').textContent = total;
    let transitioning = false;

    function showSlide(n) {
        if (n < 0 || n >= total || transitioning) return;
        transitioning = true;
        slides[currentSlide].classList.remove('active');
        currentSlide = n;
        slides[currentSlide].classList.add('active');
        document.getElementById('currentSlideNum').textContent = currentSlide + 1;
        setTimeout(() => { transitioning = false; }, 500);
    }
    function nextSlide() { showSlide(currentSlide + 1); }
    function prevSlide() { showSlide(currentSlide - 1); }

    document.addEventListener('keydown', e => {
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') nextSlide();
        if (e.key === 'ArrowLeft'  || e.key === 'ArrowUp')   prevSlide();
    });
</script>
</body>
</html>
```

> **Importante:** Las funciones `showSlide()`, `nextSlide()` y `prevSlide()` deben existir con esos nombres exactos — el presentador las llama desde las miniaturas y los controles.

---

## 2. `slides_nombre.json`

Las notas del guión para cada diapositiva. Deben coincidir en cantidad con las diapositivas del HTML.

```json
[
  {
    "title": "1. TÍTULO DIAPOSITIVA 1",
    "notes": "Texto del guión para la diapositiva 1.\n\nPuedes usar saltos de línea con \\n"
  },
  {
    "title": "2. TÍTULO DIAPOSITIVA 2",
    "notes": "Texto del guión para la diapositiva 2."
  }
]
```

**Reglas:**
- El orden debe ser el mismo que en el HTML
- El campo `title` aparece en el panel del presentador encima de las notas
- El campo `notes` aparece como guión en el panel derecho

---

## 3. Registrar en `PRESENTACION_PRESENTADOR.html`

Abre el archivo y agrega dos líneas en dos lugares:

### a) En el objeto `slidesMap` (línea ~130):

```js
const slidesMap = {
    'PRESENTACION_CENSO.html':   'slides_censo.json',
    'PRESENTACION_INGLES.html':  'slides_ingles.json',
    'PRESENTACION_NOMBRE.html':  'slides_nombre.json',  // ← agregar
};
```

### b) En el `<select>` del HTML (línea ~92):

```html
<select id="presSelector" onchange="cambiarPresentacion(this.value)" ...>
    <option value="PRESENTACION_CENSO.html">Censo DANE 2018</option>
    <option value="PRESENTACION_INGLES.html">Villa de Leyva (English)</option>
    <option value="PRESENTACION_NOMBRE.html">Mi Nueva Presentación</option>  <!-- ← agregar -->
</select>
```

---

## Resumen de archivos por presentación

| Archivo | Descripción |
|---|---|
| `PRESENTACION_NOMBRE.html` | Diapositivas visuales |
| `slides_nombre.json` | Guión y notas por diapositiva |
| Entrada en `slidesMap` | Conecta HTML con JSON |
| Entrada en `<select>` | Aparece en el menú del presentador |

---

## Presentaciones existentes como referencia

| Presentación | HTML | JSON |
|---|---|---|
| Censo DANE 2018 | `PRESENTACION_CENSO.html` | `slides_censo.json` |
| Villa de Leyva (English) | `PRESENTACION_INGLES.html` | `slides_ingles.json` |
