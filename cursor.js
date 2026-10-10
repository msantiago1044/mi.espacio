/**
 * Marcelo Barraza — Custom Cursor Engine
 * Spring physics cursor with halo for all desktop pages.
 */
(() => {
    'use strict';

    // Touch devices use the native touch interaction
    if (window.matchMedia('(pointer: coarse)').matches) {
        return;
    }

    function initCustomCursor() {
        let cursor = document.getElementById('custom-cursor');
        let halo = document.getElementById('cursor-halo');

        // Dynamically inject elements if not present in markup
        if (!cursor) {
            cursor = document.createElement('div');
            cursor.id = 'custom-cursor';
            cursor.setAttribute('aria-hidden', 'true');
            document.body.appendChild(cursor);
        }
        if (!halo) {
            halo = document.createElement('div');
            halo.id = 'cursor-halo';
            halo.setAttribute('aria-hidden', 'true');
            document.body.appendChild(halo);
        }

        document.body.classList.add('has-custom-cursor');

        let mx = -100, my = -100;
        let hx = -100, hy = -100;
        let haloRafId = null;

        function animHalo() {
            const dx = mx - hx;
            const dy = my - hy;
            if (Math.abs(dx) < 0.1 && Math.abs(dy) < 0.1) {
                hx = mx;
                hy = my;
                halo.style.transform = `translate(${hx}px, ${hy}px)`;
                haloRafId = null;
                return;
            }
            hx += dx * 0.1;
            hy += dy * 0.1;
            halo.style.transform = `translate(${hx}px, ${hy}px)`;
            haloRafId = requestAnimationFrame(animHalo);
        }

        document.addEventListener('mousemove', e => {
            mx = e.clientX;
            my = e.clientY;
            cursor.style.transform = `translate(${mx}px, ${my}px)`;
            if (!haloRafId) {
                haloRafId = requestAnimationFrame(animHalo);
            }
        }, { passive: true });

        document.addEventListener('mousedown', () => cursor.classList.add('pressing'));
        document.addEventListener('mouseup', () => cursor.classList.remove('pressing'));

        document.addEventListener('mouseleave', () => {
            cursor.style.opacity = '0';
            halo.style.opacity = '0';
        });
        document.addEventListener('mouseenter', () => {
            cursor.style.opacity = '1';
            halo.style.opacity = '1';
        });

        const interactiveSelector = 'a, button, [role="button"], input, select, textarea, .feed-post, .featured-post, .filter-tag, .search-post-item, .cmd-item, .srv-btn-primary, .srv-btn-ghost, .wa-btn, .theme-picker-opt, .metric-card';

        document.addEventListener('mouseover', e => {
            if (e.target && e.target.closest && e.target.closest(interactiveSelector)) {
                halo.classList.add('hovering');
                if (typeof window.playHover === 'function') {
                    window.playHover();
                }
            }
        });

        document.addEventListener('mouseout', e => {
            if (e.target && e.target.closest && e.target.closest(interactiveSelector)) {
                if (!e.relatedTarget || !e.relatedTarget.closest || !e.relatedTarget.closest(interactiveSelector)) {
                    halo.classList.remove('hovering');
                }
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCustomCursor);
    } else {
        initCustomCursor();
    }
})();
