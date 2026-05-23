import React from 'react';
import { WifiOff, Wifi } from 'lucide-react';
import { useOffline } from '@/hooks/useOffline';

/**
 * OfflineIndicator Component
 * Shows a banner when the user loses internet connection
 * Automatically hides when connection is restored
 */
const OfflineIndicator: React.FC = () => {
  const { isOffline } = useOffline();

  if (!isOffline) {
    return null;
  }

  return (
    <div className="fixed top-0 left-0 right-0 bg-red-500 text-white p-3 z-50 shadow-lg animate-pulse">
      <div className="max-w-7xl mx-auto flex items-center justify-center gap-2">
        <WifiOff className="w-5 h-5 flex-shrink-0" />
        <span className="text-sm font-medium">No internet connection</span>
        <span className="text-xs opacity-75 hidden sm:inline">• Using cached data</span>
      </div>
    </div>
  );
};

export default OfflineIndicator;
