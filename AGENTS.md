# Reglas de Agente para mi.espacio

## REGLAS ESTRICTAS DE OPERACIÓN
1. **NO MONTAR SERVIDORES LOCALES**: Jamás ejecutar `http-server`, `python -m http.server`, `npx serve`, o servidores express/node para realizar pruebas.
2. **NO USAR CHROME LOCALHOST**: Jamás navegar a `localhost` ni usar subagentes de navegador contra puertos locales.
3. **SIEMPRE HACER PUSH**: Toda tarea completada debe finalizarse con `git add .`, commit explicativo y `git push origin main`.
4. **FLUJO DE ARTÍCULOS**:
   - Se crean en `articles/{slug}.json`.
   - Se registran en `articles/index.json`.
   - Se compilan con `python scripts/build_articles.py` (genera `articulos/{slug}/index.html`, `articulos/{slug}.html`, `articulos/index.html`, `sitemap.xml` y `robots.txt`).
   - Se integran automáticamente con CMS, Grafo D3, Terminal (`blog`, `open`), Paleta de comandos (Ctrl+K), Drawer con TOC y Service Worker.
   - Consulta `DOCUMENTACION_Y_WORKFLOW.md` para más detalles.
