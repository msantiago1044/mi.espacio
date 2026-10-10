# Manual de Arquitectura, Workflow y Gestión de Artículos

> **Espacio Técnico de Marcelo Barraza** — Arquitectura de Misión Crítica, Baja Entropía y Gentle-AI.  
> Dominio de producción: `https://msantiago1044.github.io/mi.espacio/`

---

## ⚠️ REGLAS ESTRICTAS DE OPERACIÓN (LEER PRIMERO)

Cualquier desarrollador o agente de Inteligencia Artificial que opere en este repositorio **DEBE CUMPLIR OBLIGATORIAMENTE** las siguientes directrices:

1. **PROHIBIDO MONTAR SERVIDORES LOCALES:**  
   ❌ **NO** levantar `http-server`, `python -m http.server`, `npx serve`, `live-server` ni ningún servidor local bajo ninguna circunstancia.
2. **PROHIBIDO TESTEAR EN LOCALHOST O CHROME LOCAL:**  
   ❌ **NO** abrir navegadores ni subagentes apuntando a `localhost` o `127.0.0.1`. La validación es puramente estática, semántica y mediante scripts de inspección.
3. **SIEMPRE SE HACE PUSH:**  
   ✅ Al finalizar cualquier cambio, creación de artículo, actualización o fix, **SIEMPRE** se debe hacer commit y `git push origin main`.
4. **DEPLOYMENT 100% AUTOMATIZADO:**  
   El despliegue a GitHub Pages está gestionado automáticamente por GitHub Actions (`.github/workflows/deploy.yml`) y mediante la rama `main`.

---

## 1. Arquitectura del Sistema

El sitio está estructurado como una solución híbrida de alto rendimiento:
- **Core de la Aplicación (SPA Estática):** [index.html](file:///c:/Users/marce/Documents/mi.espacio/index.html) alberga la experiencia interactiva: canvas WebGL de partículas, terminal retroactiva tipo UNIX, paleta de comandos (Cmd+K), grafo de conocimiento en D3.js y drawer de lectura rápida.
- **SSG / Pre-renderizado (Static Site Generation):** Los artículos se escriben en formato desacoplado (`articles/*.json`) y el motor SSG [scripts/build_articles.py](file:///c:/Users/marce/Documents/mi.espacio/scripts/build_articles.py) compila páginas HTML semánticas completas en `articulos/{slug}/index.html` y `articulos/{slug}.html`.
- **Compatibilidad con Bots, Crawlers y LLMs:** Cada artículo pre-renderizado incluye etiquetas Open Graph completas con URLs absolutas para imágenes de portada, Twitter Cards, canonical tags y datos estructurados Schema.org (`TechArticle`).
- **Sitemap & Robots:** Cada build regenera automáticamente [sitemap.xml](file:///c:/Users/marce/Documents/mi.espacio/sitemap.xml) y [robots.txt](file:///c:/Users/marce/Documents/mi.espacio/robots.txt).

---

## 2. Articulación de los Artículos con el Ecosistema

Cada artículo está integrado de forma bidireccional con todas las capas de la plataforma:

### A. CMS Dinámico del Blog
- El archivo maestro [articles/index.json](file:///c:/Users/marce/Documents/mi.espacio/articles/index.json) define el orden y la lista de slugs disponibles.
- En `index.html`, la función `initBlogCMS()` realiza un fetch de `articles/index.json` y de cada `articles/{slug}.json`.
- Renderiza el grid del blog en el home con tarjeta destacada y feed cronológico, soporte para lazy-loading y modal tipo drawer.

### B. Grafo Interactivo de Conocimiento (D3.js)
- La función `buildKnowledgeGraph(allArticles)` toma los artículos cargados por el CMS.
- Genera nodos con colores asignados según su categoría (`Inteligencia Artificial`, `Cibernética`, `Arquitectura`, `DevOps`, etc.).
- Modela enlaces de fuerza basados en afinidad categórica y etiquetas compartidas (`tags`).
- Al hacer clic en cualquier nodo del grafo, se invoca `window.openArticleBySlug(slug)` abriendo instantáneamente el artículo en el drawer.

### C. Terminal Interactiva UNIX
- Comando `blog`: Lista dinámicamente todos los artículos publicados leyendo `window._allArticles`. Muestra el número ordinal, título y fecha.
- Comando `open [número | slug]`: Abre de forma interactiva el artículo seleccionado en el drawer (soporta tanto el número de la lista como el slug o fragmento del título).
- Comandos complementarios: `whoami`, `servicios`, `skills`, `contact`, `groq`, `clear`.

### D. Paleta de Comandos (Cmd/Ctrl + K)
- La paleta indexa dinámicamente todos los artículos mediante `window.cmdItems`.
- Permite buscar instantáneamente cualquier publicación y abrirla con navegación por teclado (flechas y Enter).
- Cuenta con modo de consulta semántica con IA (Groq) activable presionando `/`.

### E. Drawer Modal y Tabla de Contenidos (TOC)
- La lectura en la SPA no recarga la página: se despliega un drawer animado (`#articleDrawer`).
- Se genera una **Tabla de Contenidos (TOC)** interactiva vinculada a los encabezados (`#toc-{i}`).
- Barra de difusión superior e inferior con botones nativos (`Web Share API`), copia rápida al portapapeles y compartición directa en LinkedIn, X (Twitter) y WhatsApp.

### F. Service Worker & Caching Offline
- El archivo [sw.js](file:///c:/Users/marce/Documents/mi.espacio/sw.js) gestiona la estrategia de caché:
  - Cache-first para estilos, scripts e imágenes de portada.
  - Network-first para artículos JSON e índices para garantizar frescura inmediata.
  - Network-first con fallback para páginas estáticas pre-renderizadas.
- Tanto `index.html` como las páginas de `articulos/` registran activamente el Service Worker.

---

## 3. Guía Paso a Paso: Cómo Crear o Actualizar un Artículo

Para publicar un nuevo artículo, sigue estos pasos:

### Paso 1: Crear el archivo JSON en `articles/`
Crea `articles/{slug}.json` con la siguiente estructura:

```json
{
  "slug": "mi-nuevo-articulo",
  "title": "Título Completo del Artículo",
  "date": "2026-10-10",
  "category": "Inteligencia Artificial",
  "reading_time": 8,
  "excerpt": "Resumen conciso y de alto impacto para tarjetas y metadatos SEO.",
  "cover": "assets/gentle-ai-banner.webp",
  "tags": [
    "gentle-ai",
    "arquitectura",
    "baja-entropia",
    "mision-critica"
  ],
  "toc": [
    "Sección 1: Fundamentos",
    "Sección 2: Implementación",
    "Sección 3: Resultados"
  ],
  "content": "## Sección 1: Fundamentos\n\nContenido en markdown...\n\n## Sección 2: Implementación\n\nTexto adicional..."
}
```

### Paso 2: Registrar el Slug en `articles/index.json`
Edita [articles/index.json](file:///c:/Users/marce/Documents/mi.espacio/articles/index.json) y agrega el nuevo slug a la lista (al inicio para que aparezca primero):

```json
{
  "slugs": [
    "mi-nuevo-articulo",
    "gentle-ai-arquitectura-baja-entropia",
    ...
  ]
}
```

### Paso 3: Ejecutar el Generador SSG
Ejecuta el script generador desde la terminal:

```powershell
python scripts/build_articles.py
```

Esto generará automáticamente:
- `articulos/{slug}/index.html` (URL canónica limpia: `/articulos/{slug}/`)
- `articulos/{slug}.html` (Fallback para servidores estáticos estándar)
- `articulos/index.html` (Archivo general de artículos)
- `sitemap.xml` (Actualizado con la nueva URL y fecha de modificación)
- `robots.txt`

### Paso 4: Validar y Hacer Push (Sin Servidores Locales)
Verifica el estado de Git y haz push directo:

```powershell
git status
git add .
git commit -m "feat(blog): publicar articulo {slug} y compilar ssg"
git push origin main
```

Una vez realizado el push, GitHub Actions compilará y desplegará automáticamente la nueva versión en GitHub Pages.

---

## 4. Directorios y Archivos Clave

| Ruta | Descripción |
|---|---|
| `articles/` | Almacén de fuentes JSON desacopladas para cada artículo. |
| `articles/index.json` | Índice maestro y orden de publicación de los artículos. |
| `scripts/build_articles.py` | Motor SSG en Python que compila HTML, TOC, metadatos y sitemap. |
| `articulos/` | Directorio de salida pre-renderizado con HTML estático para cada artículo. |
| `.github/workflows/deploy.yml` | Pipeline de CI/CD en GitHub Actions para GitHub Pages. |
| `index.html` | SPA principal con Terminal, D3 Graph, CMS, Drawer y Paleta de Comandos. |
| `sw.js` | Service Worker para soporte PWA, offline y caching selectivo. |
| `sitemap.xml` | Mapa del sitio generado para motores de búsqueda y bots. |
| `robots.txt` | Directivas de indexación para crawlers web. |
