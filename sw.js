// MF Transaction Editor — Service Worker
// Bump CACHE_VERSION whenever index.html (or any cached asset) changes,
// so returning users get the update instead of a stale cached copy.
const CACHE_VERSION = 'v1';
const CACHE_NAME = `mf-editor-${CACHE_VERSION}`;

// Core app shell — same-origin files needed to run offline.
const APP_SHELL = [
  './',
  './index.html',
  './manifest.json',
  './icon-72.png',
  './icon-96.png',
  './icon-128.png',
  './icon-144.png',
  './icon-152.png',
  './icon-192.png',
  './icon-384.png',
  './icon-512.png',
  './maskable-192.png',
  './maskable-512.png'
];

// Third-party assets the page loads (font CSS, ExcelJS). Cached opportunistically
// as they're fetched — see fetch handler — so the very first load must be online.
const RUNTIME_HOSTS = [
  'fonts.googleapis.com',
  'fonts.gstatic.com',
  'cdnjs.cloudflare.com'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(APP_SHELL))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((names) => Promise.all(
        names
          .filter((name) => name.startsWith('mf-editor-') && name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  const isSameOrigin = url.origin === self.location.origin;
  const isRuntimeAsset = RUNTIME_HOSTS.includes(url.hostname);

  // Navigations: try the network first (so users get updates when online),
  // fall back to the cached shell when offline.
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put('./index.html', copy));
          return response;
        })
        .catch(() => caches.match('./index.html'))
    );
    return;
  }

  if (isSameOrigin || isRuntimeAsset) {
    // Cache-first, then update the cache in the background (stale-while-revalidate).
    event.respondWith(
      caches.match(request).then((cached) => {
        const networkFetch = fetch(request)
          .then((response) => {
            if (response && response.status === 200) {
              const copy = response.clone();
              caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
            }
            return response;
          })
          .catch(() => cached);
        return cached || networkFetch;
      })
    );
  }
});
