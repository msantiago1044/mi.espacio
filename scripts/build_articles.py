#!/usr/bin/env python3
"""
Static Site Generator (SSG) for mi.espacio articles.
Reads articles from articles/*.json and generates static, SEO-optimized HTML pages
with complete semantic content, Open Graph tags, Twitter cards, and Schema.org JSON-LD.
"""

import os
import re
import json
import html
from datetime import datetime

BASE_URL = "https://msantiago1044.github.io/mi.espacio"
AUTHOR_NAME = "Marcelo Barraza"
AUTHOR_ROLE = "Arquitecto Principal de Sistemas"
SITE_NAME = "Marcelo Barraza | Espacio Técnico"

MONTHS_ES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}

def format_date_es(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        month = MONTHS_ES.get(dt.month, str(dt.month))
        return f"{dt.day} de {month} de {dt.year}"
    except Exception:
        return date_str

def markdown_to_html(md_text):
    """Converts article markdown to clean semantic HTML with TOC anchor IDs."""
    lines = md_text.split("\n")
    html_lines = []
    in_list = False
    in_code_block = False
    code_block_lang = ""
    code_lines = []
    h2_counter = 0
    h3_counter = 0

    for line in lines:
        stripped = line.strip()

        # Handle fenced code blocks
        if stripped.startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_block_lang = stripped[3:].strip()
                code_lines = []
            else:
                in_code_block = False
                escaped = html.escape("\n".join(code_lines))
                lang_cls = f' class="language-{code_block_lang}"' if code_block_lang else ''
                html_lines.append(f'<pre><code{lang_cls}>{escaped}</code></pre>')
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        # Handle lists
        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                in_list = True
                html_lines.append("<ul>")
            item_text = stripped[2:].strip()
            item_html = inline_markdown(item_text)
            html_lines.append(f"<li>{item_html}</li>")
            continue
        else:
            if in_list:
                in_list = False
                html_lines.append("</ul>")

        if not stripped:
            continue

        # Headings
        if stripped.startswith("## "):
            h_text = stripped[3:].strip()
            h_id = f"toc-{h2_counter}"
            h2_counter += 1
            html_lines.append(f'<h2 id="{h_id}">{inline_markdown(h_text)}</h2>')
            continue
        elif stripped.startswith("### "):
            h_text = stripped[4:].strip()
            h_id = f"toc-sec-{h3_counter}"
            h3_counter += 1
            html_lines.append(f'<h3 id="{h_id}">{inline_markdown(h_text)}</h3>')
            continue
        elif stripped.startswith("# "):
            h_text = stripped[2:].strip()
            html_lines.append(f'<h2>{inline_markdown(h_text)}</h2>')
            continue

        # Blockquotes
        if stripped.startswith("> "):
            bq_text = stripped[2:].strip()
            html_lines.append(f'<blockquote><p>{inline_markdown(bq_text)}</p></blockquote>')
            continue

        # Regular paragraph
        p_html = inline_markdown(stripped)
        html_lines.append(f"<p>{p_html}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)

def inline_markdown(text):
    """Processes bold, italics, code, and links within text."""
    text = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        r'<a href="\2" target="_blank" rel="noopener">\1</a>',
        text
    )
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text

def build_article_page(art, all_articles, root_rel="../../"):
    """Generates full HTML page for a single article."""
    slug = art["slug"]
    title = art["title"]
    category = art.get("category", "Artículo")
    tags = art.get("tags", [])
    date_str = art.get("date", "")
    date_formatted = format_date_es(date_str)
    reading_time = art.get("reading_time", 8)
    excerpt = art.get("excerpt", "")
    cover = art.get("cover", "")
    toc = art.get("toc", [])
    content_md = art.get("content", "")
    content_html = markdown_to_html(content_md)

    if cover.startswith("http://") or cover.startswith("https://"):
        og_image = cover
        img_src = cover
    else:
        clean_cover = cover.lstrip("/")
        og_image = f"{BASE_URL}/{clean_cover}"
        img_src = f"{root_rel}{clean_cover}"

    canonical_url = f"{BASE_URL}/articulos/{slug}/"

    toc_items_html = ""
    if toc:
        toc_items_html = "\n".join([
            f'<li><a href="#toc-{i}" class="toc-link">{html.escape(item)}</a></li>'
            for i, item in enumerate(toc)
        ])

    tags_html = "".join([
        f'<span class="tag-pill">#{html.escape(t)}</span>'
        for t in tags
    ])

    related = [a for a in all_articles if a["slug"] != slug and a.get("category") == category]
    if len(related) < 2:
        related = [a for a in all_articles if a["slug"] != slug][:2]
    related = related[:2]

    related_html = "".join([
        f'''<a href="../{r["slug"]}/" class="related-card">
            <span class="related-cat">{html.escape(r.get("category", ""))}</span>
            <h4>{html.escape(r["title"])}</h4>
            <span class="related-date">{format_date_es(r.get("date", ""))} · {r.get("reading_time", 5)} min</span>
        </a>'''
        for r in related
    ])

    json_ld = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": title,
        "description": excerpt,
        "image": og_image,
        "datePublished": date_str,
        "dateModified": date_str,
        "author": {
            "@type": "Person",
            "name": AUTHOR_NAME,
            "jobTitle": AUTHOR_ROLE,
            "url": BASE_URL + "/"
        },
        "publisher": {
            "@type": "Person",
            "name": AUTHOR_NAME
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": canonical_url
        },
        "keywords": ", ".join(tags)
    }

    return f"""<!DOCTYPE html>
<html lang="es" data-theme="dark">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)} · {AUTHOR_NAME}</title>
    <meta name="description" content="{html.escape(excerpt)}">
    <meta name="author" content="{AUTHOR_NAME}">
    <meta name="robots" content="index, follow, max-image-preview:large">
    <link rel="canonical" href="{canonical_url}">

    <!-- Open Graph / Facebook / LinkedIn / WhatsApp -->
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="{SITE_NAME}">
    <meta property="og:title" content="{html.escape(title)}">
    <meta property="og:description" content="{html.escape(excerpt)}">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:image" content="{og_image}">
    <meta property="og:image:alt" content="{html.escape(title)}">
    <meta property="article:published_time" content="{date_str}">
    <meta property="article:author" content="{AUTHOR_NAME}">
    <meta property="article:section" content="{html.escape(category)}">
    {"".join([f'<meta property="article:tag" content="{html.escape(t)}">' for t in tags])}

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{html.escape(title)}">
    <meta name="twitter:description" content="{html.escape(excerpt)}">
    <meta name="twitter:image" content="{og_image}">

    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,700;1,400&family=Source+Code+Pro:wght@400;600&display=swap" rel="stylesheet">

    <!-- CSS & Favicon -->
    <link rel="stylesheet" href="{root_rel}styles.css?v=6.2.0">
    <link rel="icon" type="image/svg+xml" href="{root_rel}favicon.svg">

    <!-- Structured Data -->
    <script type="application/ld+json">
{json.dumps(json_ld, ensure_ascii=False, indent=2)}
    </script>

    <!-- Theme detection before render (prevents flash) -->
    <script>
        (function() {{
            const saved = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
            document.documentElement.setAttribute('data-theme', saved);
        }})();
    </script>

    <style>
        .site-header {{
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            background-color: rgba(11, 15, 25, 0.88);
            border-bottom: 1px solid var(--color-border);
            transition: background-color 300ms ease, border-color 300ms ease;
        }}
        [data-theme="light"] .site-header {{
            background-color: rgba(248, 250, 252, 0.92);
            border-bottom: 1px solid var(--color-border);
        }}
        .site-header a {{
            color: var(--color-text-muted);
            text-decoration: none;
            font-size: 13px;
            font-weight: 500;
            transition: color 200ms ease;
        }}
        .site-header a:hover {{
            color: var(--color-accent);
        }}
        .site-header .brand-title {{
            color: var(--color-text);
            font-weight: 700;
            font-family: var(--font-display);
            font-size: 1.15rem;
            display: flex;
            align-items: center;
            gap: 10px;
            text-decoration: none;
        }}
        .theme-toggle {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: transparent;
            border: 1px solid var(--color-border);
            color: var(--color-text-muted);
            border-radius: 8px;
            width: 34px;
            height: 34px;
            cursor: pointer;
            transition: color 200ms, border-color 200ms, background 200ms;
        }}
        .theme-toggle:hover {{
            color: var(--color-accent);
            border-color: var(--color-accent);
            background: var(--color-accent-subtle);
        }}
        [data-theme="dark"] .sun-icon {{ display: block; }}
        [data-theme="dark"] .moon-icon {{ display: none; }}
        [data-theme="light"] .sun-icon {{ display: none; }}
        [data-theme="light"] .moon-icon {{ display: block; }}

        .article-page {{
            max-width: 860px;
            margin: 0 auto;
            padding: var(--space-xl) var(--space-md) var(--space-3xl);
        }}
        .article-breadcrumb {{
            font-family: var(--font-mono);
            font-size: var(--font-size-xs);
            color: var(--color-text-muted);
            margin-bottom: var(--space-lg);
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .article-breadcrumb a {{
            color: var(--color-accent);
            text-decoration: none;
        }}
        .article-breadcrumb a:hover {{
            text-decoration: underline;
        }}
        .article-hero-wrap {{
            margin-bottom: var(--space-xl);
            border-radius: 12px;
            overflow: hidden;
            background: radial-gradient(circle at center, #231221 0%, #0d0a11 100%);
            border: 1px solid var(--color-border);
            aspect-ratio: 16/9;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .article-hero-wrap img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }}
        .article-title-main {{
            font-family: var(--font-display);
            font-size: clamp(2rem, 4vw, 3rem);
            font-weight: 700;
            line-height: 1.2;
            margin: var(--space-sm) 0 var(--space-md);
            color: var(--color-text);
        }}
        .article-author-card {{
            display: flex;
            align-items: center;
            gap: var(--space-sm);
            padding: var(--space-sm) 0;
            border-top: 1px solid var(--color-border);
            border-bottom: 1px solid var(--color-border);
            margin-bottom: var(--space-lg);
        }}
        .article-author-card img {{
            width: 44px;
            height: 44px;
            border-radius: 50%;
            border: 2px solid var(--color-accent);
        }}
        .article-author-meta strong {{
            display: block;
            font-size: var(--font-size-sm);
            color: var(--color-text);
        }}
        .article-author-meta span {{
            font-size: var(--font-size-xs);
            color: var(--color-text-muted);
            font-family: var(--font-mono);
        }}
        .article-toc-box {{
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 10px;
            padding: var(--space-md);
            margin: var(--space-xl) 0;
        }}
        .article-toc-box h3 {{
            font-size: var(--font-size-sm);
            font-family: var(--font-mono);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--color-accent);
            margin-bottom: var(--space-sm);
        }}
        .article-toc-box ul {{
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .article-toc-box a {{
            color: var(--color-text);
            font-size: var(--font-size-sm);
            text-decoration: none;
            transition: color var(--duration-hover);
        }}
        .article-toc-box a:hover {{
            color: var(--color-accent);
        }}
        .article-content-body {{
            font-size: 1.08rem;
            line-height: 1.85;
            color: var(--color-text);
        }}
        .article-content-body h2 {{
            font-family: var(--font-display);
            font-size: 1.75rem;
            margin: var(--space-2xl) 0 var(--space-md);
            color: var(--color-text);
            scroll-margin-top: 80px;
        }}
        .article-content-body h3 {{
            font-size: 1.35rem;
            margin: var(--space-xl) 0 var(--space-sm);
            color: var(--color-text);
            scroll-margin-top: 80px;
        }}
        .article-content-body p {{
            margin-bottom: 1.4rem;
        }}
        .article-content-body ul, .article-content-body ol {{
            margin-bottom: 1.4rem;
            padding-left: 1.5rem;
        }}
        .article-content-body li {{
            margin-bottom: 0.5rem;
        }}
        .article-content-body pre {{
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            padding: var(--space-md);
            border-radius: 8px;
            overflow-x: auto;
            margin: var(--space-md) 0 var(--space-xl);
            font-family: var(--font-mono);
            font-size: 0.9em;
        }}
        .article-content-body blockquote {{
            border-left: 3px solid var(--color-accent);
            padding-left: var(--space-md);
            margin: var(--space-md) 0;
            color: var(--color-text-muted);
            font-style: italic;
        }}
        .tag-pill {{
            font-size: 11px;
            padding: 3px 10px;
            border-radius: 20px;
            border: 1px solid var(--color-border);
            color: var(--color-text-muted);
            display: inline-block;
            margin: 4px;
        }}
        .article-cta-box {{
            margin-top: var(--space-3xl);
            padding: var(--space-xl);
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 12px;
            text-align: center;
        }}
        .related-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: var(--space-md);
            margin-top: var(--space-md);
        }}
        .related-card {{
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 10px;
            padding: var(--space-md);
            text-decoration: none;
            color: inherit;
            transition: all var(--duration-hover);
        }}
        .related-card:hover {{
            border-color: var(--color-accent);
            transform: translateY(-2px);
        }}
        .related-cat {{
            font-size: 11px;
            color: var(--color-accent);
            font-weight: 700;
            text-transform: uppercase;
        }}
        .related-card h4 {{
            margin: 6px 0;
            font-size: var(--font-size-base);
            font-family: var(--font-display);
        }}
        .related-date {{
            font-size: 11px;
            color: var(--color-text-muted);
            font-family: var(--font-mono);
        }}
    </style>
</head>

<body>
    <!-- Top Navigation -->
    <header class="site-header">
        <div class="container" style="display:flex;align-items:center;justify-content:space-between;padding:12px var(--space-md)">
            <a href="{root_rel}" class="brand-title">
                <span>{AUTHOR_NAME}</span>
            </a>
            <nav style="display:flex;align-items:center;gap:16px">
                <a href="{root_rel}#inicio" style="text-decoration:none;color:var(--color-text-muted);font-size:13px">Inicio</a>
                <a href="{root_rel}#blog" style="text-decoration:none;color:var(--color-text);font-weight:600;font-size:13px">Artículos</a>
                <a href="{root_rel}#grafo" style="text-decoration:none;color:var(--color-text-muted);font-size:13px">Grafo D3</a>
                <a href="{root_rel}#terminal-section" style="text-decoration:none;color:var(--color-text-muted);font-size:13px">Terminal</a>
                <a href="{root_rel}servicios.html" style="text-decoration:none;color:var(--color-text-muted);font-size:13px">Servicios</a>
                <a href="{root_rel}#contacto" style="text-decoration:none;color:var(--color-text-muted);font-size:13px">Contacto</a>
                <button id="theme-toggle" class="theme-toggle" aria-label="Cambiar tema" style="margin-left:8px">
                    <svg class="sun-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
                    <svg class="moon-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
                </button>
            </nav>
        </div>
    </header>

    <main class="article-page">
        <!-- Breadcrumb -->
        <nav class="article-breadcrumb" aria-label="Breadcrumb">
            <a href="{root_rel}">Inicio</a>
            <span>/</span>
            <a href="{root_rel}#blog">Artículos</a>
            <span>/</span>
            <span>{html.escape(category)}</span>
        </nav>

        <article>
            {f'<div class="article-hero-wrap"><img src="{img_src}" alt="{html.escape(title)}"></div>' if cover else ''}

            <div class="post-meta-row" style="margin-bottom:var(--space-xs)">
                <span class="post-category">{html.escape(category)}</span>
                <span class="reading-time">⏱ {reading_time} min de lectura</span>
            </div>

            <h1 class="article-title-main">{html.escape(title)}</h1>

            <div class="article-author-card">
                <img src="{root_rel}assets/profile.png" alt="{AUTHOR_NAME}">
                <div class="article-author-meta">
                    <strong>{AUTHOR_NAME}</strong>
                    <span>{AUTHOR_ROLE} · Publicado el {date_formatted}</span>
                </div>
            </div>

            <!-- Barra de Difusión Superior -->
            <div class="drawer-share-bar">
                <span class="drawer-share-label">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
                    Difundir:
                </span>
                <button class="share-action-btn share-native" onclick="handleShare()" aria-label="Compartir">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
                    <span>Compartir</span>
                </button>
                <button class="share-action-btn" onclick="copyLink()" title="Copiar enlace">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
                    <span>Copiar enlace</span>
                </button>
                <a href="https://www.linkedin.com/sharing/share-offsite/?url={canonical_url}" target="_blank" rel="noopener" class="share-action-btn" title="Compartir en LinkedIn">
                    <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.46 10.9v8.37H9.2V10.9H6.46M7.83 6.45a1.62 1.62 0 1 0 0 3.24 1.62 1.62 0 0 0 0-3.24z"/></svg>
                    <span>LinkedIn</span>
                </a>
                <a href="https://twitter.com/intent/tweet?text={html.escape(title)}&url={canonical_url}" target="_blank" rel="noopener" class="share-action-btn" title="Compartir en X">
                    <svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                    <span>X</span>
                </a>
                <a href="https://api.whatsapp.com/send?text={html.escape(title)}%20{canonical_url}" target="_blank" rel="noopener" class="share-action-btn" title="Compartir en WhatsApp">
                    <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2c-5.46 0-9.91 4.45-9.91 9.91 0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21 5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.816 9.816 0 0 0 12.04 2m.01 1.67c2.2 0 4.26.86 5.82 2.42a8.225 8.225 0 0 1 2.41 5.83c0 4.54-3.7 8.24-8.24 8.24-1.48 0-2.93-.4-4.2-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.196 8.196 0 0 1-1.26-4.38c0-4.54 3.7-8.24 8.24-8.24m4.52 11.66c-.25-.13-1.47-.72-1.7-.81-.23-.08-.39-.13-.56.13-.17.25-.64.81-.79.97-.14.17-.29.19-.54.06-.25-.13-1.06-.39-2.01-1.24-.74-.66-1.24-1.48-1.39-1.73-.14-.25-.02-.39.11-.51.11-.11.25-.29.37-.43.13-.15.17-.25.25-.42.08-.17.04-.31-.02-.44-.06-.13-.56-1.35-.77-1.85-.2-.49-.41-.42-.56-.43h-.48c-.17 0-.44.06-.67.31-.23.25-.88.86-.88 2.1 0 1.24.9 2.44 1.03 2.61.13.17 1.77 2.7 4.29 3.79.6.26 1.07.41 1.43.53.6.19 1.15.16 1.58.1.48-.07 1.47-.6 1.68-1.18.21-.58.21-1.07.15-1.18-.06-.1-.23-.17-.48-.29"/></svg>
                    <span>WhatsApp</span>
                </a>
            </div>

            <!-- Tabla de Contenido -->
            {f'''<nav class="article-toc-box" aria-label="Tabla de contenidos">
                <h3>En este artículo</h3>
                <ul>{toc_items_html}</ul>
            </nav>''' if toc_items_html else ''}

            <!-- Contenido Principal Pre-renderizado -->
            <div class="article-content-body">
                {content_html}
            </div>

            <!-- Etiquetas -->
            <div style="margin-top:var(--space-2xl);padding-top:var(--space-md);border-top:1px solid var(--color-border)">
                <strong style="font-size:12px;font-family:var(--font-mono);color:var(--color-text-muted);display:block;margin-bottom:8px">TEMAS RELACIONADOS:</strong>
                {tags_html}
            </div>

            <!-- Barra de Difusión Inferior -->
            <div class="drawer-share-bar" style="margin-top:var(--space-2xl);justify-content:space-between">
                <div>
                    <strong style="display:block;font-size:14px;color:var(--color-text)">¿Te pareció valioso este artículo?</strong>
                    <span style="font-size:12px;color:var(--color-text-muted)">Difúndelo con tu equipo y red profesional</span>
                </div>
                <div style="display:flex;gap:6px;flex-wrap:wrap">
                    <button class="share-action-btn share-native" onclick="handleShare()">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
                        <span>Compartir</span>
                    </button>
                    <button class="share-action-btn" onclick="copyLink()">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
                        <span>Copiar enlace</span>
                    </button>
                </div>
            </div>

            <!-- Llamado a la acción del autor -->
            <div class="article-cta-box">
                <h3 style="font-family:var(--font-display);font-size:1.4rem;margin-bottom:8px">¿Tienes un reto de ingeniería o un sistema por escalar?</h3>
                <p style="color:var(--color-text-muted);max-width:540px;margin:0 auto var(--space-md);font-size:14px">Diseño arquitecturas de baja entropía, automatización de procesos e integración de IA y misión crítica para entornos de alta exigencia.</p>
                <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
                    <a href="{root_rel}#contacto" class="btn btn-primary" style="padding:8px 18px;border-radius:8px;font-size:13px;text-decoration:none">Iniciar conversación →</a>
                    <a href="{root_rel}" class="btn btn-secondary" style="padding:8px 18px;border-radius:8px;font-size:13px;text-decoration:none">Explorar portafolio interactivo</a>
                </div>
            </div>

            <!-- Articulación con Ecosistema Interactivo -->
            <div style="margin-top:var(--space-2xl);padding:var(--space-lg);border-radius:12px;background:var(--color-surface);border:1px solid var(--color-border)">
                <h4 style="font-family:var(--font-mono);font-size:12px;text-transform:uppercase;letter-spacing:0.1em;color:var(--color-accent);margin-bottom:8px">Ecosistema Interactivo</h4>
                <p style="font-size:13px;color:var(--color-text-muted);margin-bottom:var(--space-md)">Explora este artículo en las herramientas interactivas del espacio técnico:</p>
                <div style="display:flex;gap:12px;flex-wrap:wrap">
                    <a href="{root_rel}#grafo" style="font-size:12px;text-decoration:none;color:var(--color-text);background:rgba(255,255,255,0.05);padding:6px 12px;border-radius:6px;border:1px solid var(--color-border);display:inline-flex;align-items:center;gap:6px">
                        <span>🕸️</span> Ver en Grafo D3
                    </a>
                    <a href="{root_rel}#terminal-section" style="font-size:12px;text-decoration:none;color:var(--color-text);background:rgba(255,255,255,0.05);padding:6px 12px;border-radius:6px;border:1px solid var(--color-border);display:inline-flex;align-items:center;gap:6px">
                        <span>💻</span> Abrir en Terminal (<code>open {slug}</code>)
                    </a>
                    <a href="{root_rel}#blog" style="font-size:12px;text-decoration:none;color:var(--color-text);background:rgba(255,255,255,0.05);padding:6px 12px;border-radius:6px;border:1px solid var(--color-border);display:inline-flex;align-items:center;gap:6px">
                        <span>📚</span> Bitácora Completa (CMS)
                    </a>
                </div>
            </div>

            <!-- Artículos recomendados -->
            {f'''<div style="margin-top:var(--space-3xl)">
                <h3 style="font-family:var(--font-display);font-size:1.25rem;margin-bottom:var(--space-sm)">Continuar leyendo</h3>
                <div class="related-grid">{related_html}</div>
            </div>''' if related_html else ''}
        </article>
    </main>

    <!-- Toast Notification -->
    <div id="toast-notify" class="toast-notify" role="status" aria-live="polite">
        <span class="toast-icon">✓</span>
        <span id="toast-text" class="toast-text">Enlace copiado al portapapeles</span>
    </div>

    <!-- Interactive Script -->
    <script>
        // Service Worker
        if ('serviceWorker' in navigator) {{
            window.addEventListener('load', () => {{
                navigator.serviceWorker.register('{root_rel}sw.js').then(reg => reg.update()).catch(() => {{}});
            }});
        }}

        // Theme toggle sync
        const htmlEl = document.documentElement;
        const themeBtn = document.getElementById('theme-toggle');
        const savedTheme = localStorage.getItem('theme') || 'dark';
        htmlEl.setAttribute('data-theme', savedTheme);

        themeBtn?.addEventListener('click', () => {{
            const current = htmlEl.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            htmlEl.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
        }});

        // Toast helper
        function showToast(msg) {{
            const toast = document.getElementById('toast-notify');
            const text = document.getElementById('toast-text');
            if (!toast || !text) return;
            text.textContent = msg;
            toast.classList.add('show');
            clearTimeout(window._toastTimer);
            window._toastTimer = setTimeout(() => toast.classList.remove('show'), 3000);
        }}

        // Copy link
        function copyLink() {{
            const url = window.location.href.split('#')[0];
            if (navigator.clipboard && navigator.clipboard.writeText) {{
                navigator.clipboard.writeText(url).then(() => showToast('✓ Enlace copiado al portapapeles'))
                    .catch(() => prompt('Copia este enlace:', url));
            }} else {{
                prompt('Copia este enlace:', url);
            }}
        }}

        // Native share
        async function handleShare() {{
            const url = window.location.href.split('#')[0];
            if (navigator.share) {{
                try {{
                    await navigator.share({{
                        title: {json.dumps(title)},
                        text: {json.dumps(title + " — " + AUTHOR_NAME)},
                        url: url
                    }});
                    showToast('✓ ¡Artículo compartido!');
                }} catch (e) {{
                    if (e.name !== 'AbortError') copyLink();
                }}
            }} else {{
                copyLink();
            }}
        }}
    </script>
</body>
</html>
"""

def build_archive_page(all_articles, root_rel="../"):
    """Generates the archive index listing all articles in articulos/index.html."""
    articles_cards = []
    for a in all_articles:
        slug = a["slug"]
        cat = a.get("category", "General")
        date = format_date_es(a.get("date", ""))
        read_time = a.get("reading_time", 8)
        title = a.get("title", "")
        excerpt = a.get("excerpt", "")
        cover = a.get("cover", "")

        if cover.startswith("http://") or cover.startswith("https://"):
            img_src = cover
        else:
            img_src = f"{root_rel}{cover.lstrip('/')}"

        card = f'''<article class="archive-card" style="background:var(--color-surface);border:1px solid var(--color-border);border-radius:12px;overflow:hidden;display:flex;flex-direction:column;transition:all var(--duration-hover)">
            {f'<div style="aspect-ratio:16/9;overflow:hidden;background:#110d14"><img src="{img_src}" alt="{html.escape(title)}" style="width:100%;height:100%;object-fit:cover"></div>' if cover else ''}
            <div style="padding:var(--space-md);display:flex;flex-direction:column;flex:1">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                    <span style="font-size:11px;color:var(--color-accent);font-weight:700;text-transform:uppercase">{html.escape(cat)}</span>
                    <span style="font-size:11px;color:var(--color-text-muted);font-family:var(--font-mono)">⏱ {read_time} min</span>
                </div>
                <h3 style="font-family:var(--font-display);font-size:1.25rem;margin:0 0 8px;line-height:1.3"><a href="./{slug}/" style="color:var(--color-text);text-decoration:none">{html.escape(title)}</a></h3>
                <p style="font-size:13px;color:var(--color-text-muted);line-height:1.6;margin-bottom:var(--space-md);flex:1">{html.escape(excerpt)}</p>
                <div style="display:flex;justify-content:space-between;align-items:center;border-top:1px solid var(--color-border);padding-top:12px">
                    <span style="font-size:11px;color:var(--color-text-muted);font-family:var(--font-mono)">{date}</span>
                    <a href="./{slug}/" style="font-size:12px;color:var(--color-accent);text-decoration:none;font-weight:600">Leer artículo →</a>
                </div>
            </div>
        </article>'''
        articles_cards.append(card)

    cards_html = "\n".join(articles_cards)
    canonical_url = f"{BASE_URL}/articulos/"

    return f"""<!DOCTYPE html>
<html lang="es" data-theme="dark">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Artículos Técnicos & Arquitectura · {AUTHOR_NAME}</title>
    <meta name="description" content="Publicaciones y análisis técnicos sobre sistemas de baja entropía, Gentle-AI, cibernética aplicada, DevOps y arquitecturas de misión crítica por {AUTHOR_NAME}.">
    <meta name="author" content="{AUTHOR_NAME}">
    <link rel="canonical" href="{canonical_url}">

    <meta property="og:type" content="website">
    <meta property="og:site_name" content="{SITE_NAME}">
    <meta property="og:title" content="Artículos Técnicos & Arquitectura · {AUTHOR_NAME}">
    <meta property="og:description" content="Publicaciones técnicas sobre sistemas de baja entropía, Gentle-AI, cibernética y misión crítica.">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:image" content="{BASE_URL}/assets/gentle-ai-banner.webp">

    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Artículos Técnicos & Arquitectura · {AUTHOR_NAME}">
    <meta name="twitter:description" content="Publicaciones técnicas sobre sistemas de baja entropía, Gentle-AI, cibernética y misión crítica.">
    <meta name="twitter:image" content="{BASE_URL}/assets/gentle-ai-banner.webp">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,700;1,400&family=Source+Code+Pro:wght@400;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{root_rel}styles.css?v=6.2.0">
    <link rel="icon" type="image/svg+xml" href="{root_rel}favicon.svg">

    <!-- Theme detection before render (prevents flash) -->
    <script>
        (function() {{
            const saved = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
            document.documentElement.setAttribute('data-theme', saved);
        }})();
    </script>
</head>

<body>
    <header class="site-header">
        <div class="container" style="display:flex;align-items:center;justify-content:space-between;padding:12px var(--space-md)">
            <a href="{root_rel}" class="brand-title">
                <span>{AUTHOR_NAME}</span>
            </a>
            <nav style="display:flex;align-items:center;gap:16px">
                <a href="{root_rel}#inicio" style="text-decoration:none;color:var(--color-text-muted);font-size:13px">Inicio</a>
                <a href="{root_rel}#blog" style="text-decoration:none;color:var(--color-text);font-weight:600;font-size:13px">Artículos</a>
                <a href="{root_rel}#grafo" style="text-decoration:none;color:var(--color-text-muted);font-size:13px">Grafo D3</a>
                <a href="{root_rel}#terminal-section" style="text-decoration:none;color:var(--color-text-muted);font-size:13px">Terminal</a>
                <a href="{root_rel}servicios.html" style="text-decoration:none;color:var(--color-text-muted);font-size:13px">Servicios</a>
                <a href="{root_rel}#contacto" style="text-decoration:none;color:var(--color-text-muted);font-size:13px">Contacto</a>
                <button id="theme-toggle" class="theme-toggle" aria-label="Cambiar tema" style="margin-left:8px">
                    <svg class="sun-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
                    <svg class="moon-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
                </button>
            </nav>
        </div>
    </header>

    <main class="container" style="max-width:1100px;margin:0 auto;padding:var(--space-2xl) var(--space-md) var(--space-3xl)">
        <div style="margin-bottom:var(--space-2xl);text-align:center">
            <span style="font-family:var(--font-mono);font-size:var(--font-size-xs);text-transform:uppercase;letter-spacing:0.15em;color:var(--color-accent);font-weight:700">Bitácora Técnica</span>
            <h1 style="font-family:var(--font-display);font-size:clamp(2.2rem, 5vw, 3.2rem);margin:8px 0 var(--space-sm)">Archivo de Artículos</h1>
            <p style="color:var(--color-text-muted);max-width:620px;margin:0 auto;font-size:15px">Análisis de arquitectura, diseño de sistemas de baja entropía, orquestación de agentes con Gentle-AI y resiliencia en entornos de misión crítica.</p>
        </div>

        <div style="display:grid;grid-template-columns:repeat(auto-fill, minmax(320px, 1fr));gap:var(--space-lg)">
            {cards_html}
        </div>
    </main>

    <script>
        if ('serviceWorker' in navigator) {{
            window.addEventListener('load', () => {{
                navigator.serviceWorker.register('{root_rel}sw.js').then(reg => reg.update()).catch(() => {{}});
            }});
        }}

        // Theme toggle sync
        const htmlEl = document.documentElement;
        const themeBtn = document.getElementById('theme-toggle');
        themeBtn?.addEventListener('click', () => {{
            const current = htmlEl.getAttribute('data-theme') || 'dark';
            const next = current === 'dark' ? 'light' : 'dark';
            htmlEl.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
        }});
    </script>
</body>
</html>
"""

def generate_sitemap(all_articles, root_dir):
    urls = [
        {"loc": f"{BASE_URL}/", "priority": "1.0", "changefreq": "weekly"},
        {"loc": f"{BASE_URL}/articulos/", "priority": "0.9", "changefreq": "weekly"},
        {"loc": f"{BASE_URL}/servicios.html", "priority": "0.8", "changefreq": "monthly"},
    ]
    for art in all_articles:
        date = art.get("date", datetime.now().strftime("%Y-%m-%d"))
        urls.append({
            "loc": f"{BASE_URL}/articulos/{art['slug']}/",
            "lastmod": date,
            "priority": "0.8",
            "changefreq": "monthly"
        })

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for u in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{u['loc']}</loc>")
        if "lastmod" in u:
            lines.append(f"    <lastmod>{u['lastmod']}</lastmod>")
        lines.append(f"    <changefreq>{u['changefreq']}</changefreq>")
        lines.append(f"    <priority>{u['priority']}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    sitemap_path = os.path.join(root_dir, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[+] Generated: sitemap.xml with {len(urls)} URLs")

def generate_robots_txt(root_dir):
    content = f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
"""
    robots_path = os.path.join(root_dir, "robots.txt")
    with open(robots_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[+] Generated: robots.txt")

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    articles_dir = os.path.join(root_dir, "articles")
    index_file = os.path.join(articles_dir, "index.json")
    out_dir = os.path.join(root_dir, "articulos")

    os.makedirs(out_dir, exist_ok=True)

    with open(index_file, "r", encoding="utf-8") as f:
        index_data = json.load(f)

    slugs = index_data.get("slugs", [])
    print(f"[*] Found {len(slugs)} articles in index.json")

    all_articles = []
    for slug in slugs:
        fpath = os.path.join(articles_dir, f"{slug}.json")
        if not os.path.exists(fpath):
            print(f"[-] Warning: article file not found: {fpath}")
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            art = json.load(f)
            all_articles.append(art)

    # Sort articles by date descending
    all_articles.sort(key=lambda a: a.get("date", ""), reverse=True)

    generated_count = 0
    for art in all_articles:
        slug = art["slug"]
        slug_dir = os.path.join(out_dir, slug)
        os.makedirs(slug_dir, exist_ok=True)

        # Generate articulos/{slug}/index.html (clean directory URL)
        html_content = build_article_page(art, all_articles, root_rel="../../")
        out_file = os.path.join(slug_dir, "index.html")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Generate fallback articulos/{slug}.html
        fallback_file = os.path.join(out_dir, f"{slug}.html")
        fallback_html = build_article_page(art, all_articles, root_rel="../")
        with open(fallback_file, "w", encoding="utf-8") as f:
            f.write(fallback_html)

        print(f"[+] Generated: articulos/{slug}/index.html and articulos/{slug}.html")
        generated_count += 1

    # Generate archive index articulos/index.html
    archive_html = build_archive_page(all_articles, root_rel="../")
    archive_file = os.path.join(out_dir, "index.html")
    with open(archive_file, "w", encoding="utf-8") as f:
        f.write(archive_html)
    print("[+] Generated: articulos/index.html (Archive index)")

    # Generate sitemap.xml and robots.txt
    generate_sitemap(all_articles, root_dir)
    generate_robots_txt(root_dir)

    print(f"\n[OK] Successfully pre-rendered {generated_count} articles + archive + sitemap.xml to static HTML!")

if __name__ == "__main__":
    main()
