# Marcelo Barraza — Pensamiento y Sistemas

Blog personal de ingeniería, arquitectura de software y automatización. **v3.0.0**

## Features implementadas (20/20)

| # | Feature | Tecnología |
|---|---------|-----------|
| P1  | Canvas de partículas WebGL | WebGL nativo |
| P2  | Tipografía kinética con glitch | Web Animations API |
| P3  | Cursor personalizado con spring physics | rAF + CSS custom props |
| P4  | Modo claro/oscuro con transición eclipse | View Transitions API |
| P5  | Feed de GitHub Activity en tiempo real | GitHub REST API v3 |
| P6  | Social links (LinkedIn, GitHub) | HTML semántico |
| P7  | Artículos con imagen, TOC y lectura | Drawer component |
| P8  | Badges dinámicos de GitHub | GitHub REST API v3 |
| P9  | Newsletter con Resend | Resend API |
| P10 | Command palette Cmd+K (fuzzy search) | Fuse.js-like, nativo |
| P11 | Tiempo de lectura + TOC flotante en drawer | IntersectionObserver |
| P12 | PWA con Service Worker offline-first | Service Worker API |
| P13 | Stack técnico animado con tooltips | DevIcons CDN |
| P14 | Terminal interactiva (9 comandos) | JS puro |
| P15 | Heatmap de contribuciones GitHub | Canvas generativo |
| P16 | Source peek — inspector de CSS en vivo | getComputedStyle |
| P17 | Sonido de interacción (Web Audio API) | OscillatorNode |
| P18 | Konami Code easter egg (Matrix rain) | Canvas 2D |
| P19 | prefers-reduced-data + prefers-reduced-motion | CSS Media Queries |
| P20 | JSON-LD Schema.org Person + Blog | Structured Data |

## Stack

- **Frontend**: HTML5 + CSS3 + JavaScript vanilla (sin frameworks)
- **APIs**: GitHub REST v3, Resend, DevIcons CDN
- **PWA**: Service Worker + Web App Manifest
- **Animaciones**: WebGL, Web Animations API, View Transitions API
- **Fuentes**: Playfair Display + Plus Jakarta Sans (Google Fonts)
- **Deploy**: GitHub Pages / Vercel / cualquier CDN estático

## Configuración

### Newsletter (Resend)
Reemplaza `RESEND_API_KEY_HERE` en `index.html` con tu API key de Resend.

### Despliegue
```bash
# GitHub Pages: solo push a main
git push origin main

# Vercel
vercel --prod
```

## Licencia
© 2026 Marcelo Barraza. Todos los derechos reservados.
