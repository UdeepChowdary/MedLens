// MedLens PWA Service Worker (v1.0.0)
const CACHE_NAME = "medlens-cache-v1";

const PRECACHE_ASSETS = [
  "/",
  "/dashboard/scan",
  "/dashboard/history",
  "/dashboard/compare",
  "/dashboard/profile",
  "/icon.svg",
  "/icons/icon-192x192.png",
  "/icons/icon-512x512.png",
  "/icons/apple-touch-icon.png",
  "/manifest.webmanifest",
];

// Install: pre-cache application shell
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_ASSETS).catch((err) => {
        console.warn("[MedLens SW] Pre-caching warning:", err);
      });
    })
  );
  self.skipWaiting();
});

// Activate: clean up outdated legacy caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME) {
            return caches.delete(name);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch: Network-first for navigation/HTML, Cache-first for static assets
self.addEventListener("fetch", (event) => {
  const request = event.request;
  const url = new URL(request.url);

  // Bypass non-GET requests and external/backend API calls
  if (request.method !== "GET" || url.pathname.startsWith("/api/")) {
    return;
  }

  // HTML Page Navigation: Network-first with offline cache fallback
  if (request.mode === "navigate" || request.headers.get("accept")?.includes("text/html")) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response && response.status === 200) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          }
          return response;
        })
        .catch(async () => {
          const cached = await caches.match(request);
          if (cached) return cached;
          const fallback = await caches.match("/dashboard/scan");
          if (fallback) return fallback;
          return caches.match("/");
        })
    );
    return;
  }

  // Static Assets (Scripts, Styles, Fonts, Images): Cache-first with network revalidation
  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) {
        // Asynchronously update cache in background
        fetch(request)
          .then((networkResponse) => {
            if (networkResponse && networkResponse.status === 200 && url.origin === self.location.origin) {
              caches.open(CACHE_NAME).then((cache) => cache.put(request, networkResponse));
            }
          })
          .catch(() => {});
        return cached;
      }

      return fetch(request).then((response) => {
        if (response && response.status === 200 && url.origin === self.location.origin) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
        }
        return response;
      });
    })
  );
});
