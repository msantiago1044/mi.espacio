// P12: Service Worker — offline-first con cache estratégico
const CACHE_NAME = 'marcelo-blog-v3';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/styles.css',
  '/manifest.json'
];

// Instalar: pre-cachear assets estáticos
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// Activar: limpiar caches viejos
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch: cache-first para assets, network-first para API
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // APIs de GitHub y Google: network-first (datos frescos)
  if (url.hostname.includes('api.github.com') || url.hostname.includes('googleapis.com')) {
    event.respondWith(
      fetch(request)
        .then(res => {
          const clone = res.clone();
          caches.open(CACHE_NAME).then(c => c.put(request, clone));
          return res;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // Assets estáticos: cache-first
  if (request.method === 'GET') {
    event.respondWith(
      caches.match(request).then(cached => {
        if (cached) return cached;
        return fetch(request).then(res => {
          if (res && res.status === 200) {
            const clone = res.clone();
            caches.open(CACHE_NAME).then(c => c.put(request, clone));
          }
          return res;
        });
      })
    );
  }
});
