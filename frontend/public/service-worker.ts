/**
 * Service Worker for Weather Pipeline
 * Provides:
 * - Offline capability with caching
 * - Network-first strategy for API calls
 * - Cache-first strategy for static assets
 * - Background sync support
 */

const CACHE_NAME = 'weather-pipeline-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/favicon.ico',
];
const API_CACHE = 'weather-pipeline-api-v1';
const IMAGE_CACHE = 'weather-pipeline-images-v1';

/**
 * Installation: Cache static assets
 */
self.addEventListener('install', (event: ExtendableEvent) => {
  event.waitUntil(
    (async () => {
      try {
        const cache = await caches.open(CACHE_NAME);
        await cache.addAll(STATIC_ASSETS);
        console.log('[Service Worker] Static assets cached');
      } catch (error) {
        console.error('[Service Worker] Cache installation failed:', error);
      }
    })()
  );
  self.skipWaiting();
});

/**
 * Activation: Clean up old caches
 */
self.addEventListener('activate', (event: ExtendableEvent) => {
  event.waitUntil(
    (async () => {
      const cacheNames = await caches.keys();
      await Promise.all(
        cacheNames
          .filter(name => name !== CACHE_NAME && name !== API_CACHE && name !== IMAGE_CACHE)
          .map(name => caches.delete(name))
      );
      console.log('[Service Worker] Old caches cleaned');
    })()
  );
  self.clients.claim();
});

/**
 * Fetch: Implement caching strategies
 * - Network-first for API calls
 * - Cache-first for images
 * - Stale-while-revalidate for critical data
 */
self.addEventListener('fetch', (event: FetchEvent) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // API requests: Network-first, fall back to cache
  if (url.pathname.startsWith('/api/')) {
    handleApiRequest(event);
  }
  // Image requests: Cache-first, fall back to network
  else if (request.destination === 'image') {
    handleImageRequest(event);
  }
  // Static assets: Cache-first
  else {
    handleStaticRequest(event);
  }
});

/**
 * Handle API requests with network-first strategy
 */
function handleApiRequest(event: FetchEvent) {
  event.respondWith(
    fetch(event.request)
      .then(async (response) => {
        // Cache successful responses
        if (response.ok) {
          const cache = await caches.open(API_CACHE);
          cache.put(event.request, response.clone());
        }
        return response;
      })
      .catch(async () => {
        // Fall back to cache if network fails
        const cached = await caches.match(event.request);
        if (cached) {
          return cached;
        }
        // Return offline response
        return createOfflineResponse();
      })
  );
}

/**
 * Handle image requests with cache-first strategy
 */
function handleImageRequest(event: FetchEvent) {
  event.respondWith(
    (async () => {
      const cached = await caches.match(event.request);
      if (cached) {
        return cached;
      }

      try {
        const response = await fetch(event.request);
        if (response.ok) {
          const cache = await caches.open(IMAGE_CACHE);
          cache.put(event.request, response.clone());
        }
        return response;
      } catch {
        // Return placeholder image if offline
        return createPlaceholderImage();
      }
    })()
  );
}

/**
 * Handle static asset requests with cache-first strategy
 */
function handleStaticRequest(event: FetchEvent) {
  event.respondWith(
    (async () => {
      const cached = await caches.match(event.request);
      if (cached) {
        return cached;
      }

      try {
        const response = await fetch(event.request);
        if (response.ok) {
          const cache = await caches.open(CACHE_NAME);
          cache.put(event.request, response.clone());
        }
        return response;
      } catch {
        // Return offline page for navigation requests
        if (event.request.mode === 'navigate') {
          return caches.match('/index.html') || createOfflineResponse();
        }
        return createOfflineResponse();
      }
    })()
  );
}

/**
 * Create offline response
 */
function createOfflineResponse(): Response {
  return new Response(
    JSON.stringify({
      error: 'Offline - No cached data available',
      status: 'offline',
    }),
    {
      status: 503,
      statusText: 'Service Unavailable',
      headers: { 'Content-Type': 'application/json' },
    }
  );
}

/**
 * Create placeholder image
 */
function createPlaceholderImage(): Response {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
    <rect width="200" height="200" fill="#f0f0f0"/>
    <text x="50%" y="50%" text-anchor="middle" dy=".3em" font-family="system-ui" fill="#999">
      Image unavailable
    </text>
  </svg>`;

  return new Response(svg, {
    status: 200,
    headers: { 'Content-Type': 'image/svg+xml' },
  });
}

/**
 * Background sync for offline actions
 */
self.addEventListener('sync', (event: any) => {
  if (event.tag === 'sync-weather-data') {
    event.waitUntil(syncWeatherData());
  }
});

async function syncWeatherData() {
  try {
    console.log('[Service Worker] Syncing weather data');
    // Implement background sync logic here
  } catch (error) {
    console.error('[Service Worker] Sync failed:', error);
  }
}

declare const self: ServiceWorkerGlobalScope;
export {};
