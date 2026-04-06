# Instructivo: Cómo incluir IA en un proyecto web

## 1. Elegir un proveedor de IA

| Proveedor | Modelo sugerido | API gratuita |
|-----------|----------------|--------------|
| [DeepSeek](https://platform.deepseek.com) | `deepseek-chat` | Sí (con límites) |
| [OpenAI](https://platform.openai.com) | `gpt-4o-mini` | No (pago) |
| [Google Gemini](https://aistudio.google.com) | `gemini-2.0-flash` | Sí |

---

## 2. Obtener la API Key

1. Registrarse en el sitio del proveedor elegido
2. Ir a la sección **API Keys** del panel de usuario
3. Crear una nueva clave y copiarla
4. Guardarla en un lugar seguro (no compartirla ni subirla a GitHub)

---

## 3. Estructura básica de una petición

La IA recibe una lista de **mensajes** con roles:

```json
{
  "model": "deepseek-chat",
  "messages": [
    { "role": "system", "content": "Eres un asistente útil." },
    { "role": "user",   "content": "¿Qué es el Censo DANE?" }
  ],
  "max_tokens": 500,
  "temperature": 0.7
}
```

- **system**: instrucciones de comportamiento para la IA
- **user**: la pregunta o entrada del usuario
- **assistant**: respuestas previas (para mantener historial)
- **max_tokens**: límite de palabras en la respuesta (~750 palabras = 1000 tokens)
- **temperature**: creatividad (0 = determinista, 1 = más creativo)

---

## 4. Código JavaScript para hacer la petición

```js
async function preguntarIA(pregunta) {
    const API_KEY = 'tu-api-key-aqui'; // nunca expongas esto en producción
    const endpoint = 'https://api.deepseek.com/v1/chat/completions';

    const respuesta = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + API_KEY
        },
        body: JSON.stringify({
            model: 'deepseek-chat',
            messages: [
                { role: 'system', content: 'Responde siempre en español.' },
                { role: 'user',   content: pregunta }
            ],
            max_tokens: 500,
            temperature: 0.7
        })
    });

    const data = await respuesta.json();
    return data.choices[0].message.content;
}

// Uso
preguntarIA('¿Cuántas personas se censaron en Colombia en 2018?')
    .then(texto => console.log(texto));
```

---

## 5. Mostrar la respuesta en el HTML

```html
<textarea id="pregunta" placeholder="Escribe tu pregunta..."></textarea>
<button onclick="consultar()">Preguntar</button>
<div id="respuesta"></div>

<script>
async function consultar() {
    const pregunta = document.getElementById('pregunta').value;
    document.getElementById('respuesta').textContent = 'Consultando…';
    const texto = await preguntarIA(pregunta);
    document.getElementById('respuesta').textContent = texto;
}
</script>
```

---

## 6. Variante con Google Gemini (API gratuita)

```js
async function preguntarGemini(pregunta) {
    const API_KEY = 'tu-api-key-de-google';
    const endpoint = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent';

    const respuesta = await fetch(endpoint + '?key=' + API_KEY, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            contents: [{ parts: [{ text: pregunta }] }],
            systemInstruction: { parts: [{ text: 'Responde siempre en español.' }] }
        })
    });

    const data = await respuesta.json();
    return data.candidates[0].content.parts[0].text;
}
```

---

## 7. Buenas prácticas

- **No expongas la API key en el código fuente** si el proyecto es público. Úsala desde un backend o variable de entorno.
- **Sanitiza el texto** antes de enviarlo como header HTTP: elimina caracteres no ASCII con `.replace(/[^\x20-\x7E]/g, '').trim()`.
- **Limita el alcance** de la IA con un prompt de sistema claro (qué puede y qué no puede responder).
- **Mantén el historial** de conversación enviando los mensajes anteriores en el array `messages` para que la IA recuerde el contexto.
- **Maneja los errores**: la petición puede fallar por red, cuota agotada o clave inválida.

```js
try {
    const texto = await preguntarIA(pregunta);
    // usar texto
} catch (e) {
    console.error('Error al consultar la IA:', e.message);
}
```

---

## 8. Recursos

- Documentación DeepSeek: https://platform.deepseek.com/api-docs
- Documentación OpenAI: https://platform.openai.com/docs
- Documentación Gemini: https://ai.google.dev/docs
