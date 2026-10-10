# Directrices Operativas del Repositorio

- **PROHIBIDO:** Levantar servidores HTTP locales (`python -m http.server`, `http-server`, etc.) o usar navegadores apuntando a `localhost`.
- **MANDATORIO:** Al terminar cualquier tarea, siempre realizar `git add .`, commit semántico y `git push origin main`.
- **GENERACIÓN DE ARTÍCULOS:** Los artículos residen en `articles/{slug}.json`, indexados en `articles/index.json`. Se compilan ejecutando `python scripts/build_articles.py`.
- **INTEGRACIÓN DEL SISTEMA:** Todo artículo se articula con el CMS, Grafo D3 de conocimiento, Terminal UNIX (`blog`, `open`), Paleta de comandos (Ctrl+K), Drawer con TOC interactivo y Service Worker (`sw.js`).
