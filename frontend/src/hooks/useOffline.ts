import { useEffect, useState } from 'react';

/**
 * useOffline Hook
 * Detects when the app goes offline/online
 * Useful for UI indicators and conditional rendering
 *
 * @returns Object with isOffline boolean and lastUpdated timestamp
 *
 * @example
 * const { isOffline } = useOffline();
 * if (isOffline) {
 *   return <OfflineIndicator />;
 * }
 */
export const useOffline = () => {
  const [isOffline, setIsOffline] = useState(!navigator.onLine);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  useEffect(() => {
    const handleOnline = () => {
      setIsOffline(false);
      setLastUpdated(new Date());
      console.log('[Offline] Connection restored');
    };

    const handleOffline = () => {
      setIsOffline(true);
      setLastUpdated(new Date());
      console.log('[Offline] Connection lost');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return {
    isOffline,
    isOnline: !isOffline,
    lastUpdated,
  };
};

export default useOffline;
