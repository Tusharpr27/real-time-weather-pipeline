/**
 * Register Service Worker
 * Enables offline capability and background sync
 */

const registerServiceWorker = async () => {
  if (!('serviceWorker' in navigator)) {
    console.log('[PWA] Service Workers are not supported');
    return;
  }

  try {
    const registration = await navigator.serviceWorker.register(
      '/service-worker.ts',
      { scope: '/' }
    );

    console.log('[PWA] Service Worker registered successfully:', registration);

    // Listen for updates
    registration.addEventListener('updatefound', () => {
      const newWorker = registration.installing;
      if (newWorker) {
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            // New service worker is ready, notify user
            console.log('[PWA] New version available, refreshing...');
            window.location.reload();
          }
        });
      }
    });

    // Periodic background sync (if supported)
    if ('periodicSync' in registration) {
      try {
        await registration.periodicSync.register('sync-weather-data', {
          minInterval: 24 * 60 * 60 * 1000, // 24 hours
        });
        console.log('[PWA] Background sync registered');
      } catch (error) {
        console.warn('[PWA] Background sync registration failed:', error);
      }
    }
  } catch (error) {
    console.error('[PWA] Service Worker registration failed:', error);
  }
};

export { registerServiceWorker };
