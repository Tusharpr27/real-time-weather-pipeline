import React, { useState, useEffect } from 'react';
import { RotateCcw, Play, Pause } from 'lucide-react';
import { Button } from '@/components/ui';

export interface RefreshControlProps {
  onManualRefresh: () => void;
  autoRefreshEnabled: boolean;
  onAutoRefreshChange: (enabled: boolean) => void;
  refreshInterval: number;
  onIntervalChange: (interval: number) => void;
  loading?: boolean;
}

export const RefreshControl: React.FC<RefreshControlProps> = ({
  onManualRefresh,
  autoRefreshEnabled,
  onAutoRefreshChange,
  refreshInterval,
  onIntervalChange,
  loading = false,
}) => {
  const [nextRefresh, setNextRefresh] = useState(refreshInterval);

  useEffect(() => {
    if (!autoRefreshEnabled) return;

    const timer = setInterval(() => {
      setNextRefresh((prev) => {
        if (prev <= 1) {
          onManualRefresh();
          return refreshInterval;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [autoRefreshEnabled, refreshInterval, onManualRefresh]);

  const handleIntervalChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const interval = parseInt(e.target.value);
    onIntervalChange(interval);
    setNextRefresh(interval);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center gap-4 flex-wrap">
        {/* Manual Refresh Button */}
        <Button
          variant="primary"
          size="md"
          onClick={onManualRefresh}
          isLoading={loading}
          leftIcon={<RotateCcw size={16} />}
        >
          Refresh Now
        </Button>

        {/* Auto Refresh Toggle */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => onAutoRefreshChange(!autoRefreshEnabled)}
            className={`p-2 rounded-lg transition-colors ${
              autoRefreshEnabled
                ? 'bg-blue-100 text-blue-600'
                : 'bg-gray-100 text-gray-600'
            }`}
            title={autoRefreshEnabled ? 'Pause Auto-Refresh' : 'Start Auto-Refresh'}
          >
            {autoRefreshEnabled ? (
              <Pause size={16} />
            ) : (
              <Play size={16} />
            )}
          </button>
          <span className="text-xs font-medium text-gray-700">
            {autoRefreshEnabled ? 'Auto-Refresh ON' : 'Auto-Refresh OFF'}
          </span>
        </div>

        {/* Interval Selector */}
        <div className="flex items-center gap-2">
          <label htmlFor="refresh-interval" className="text-xs font-medium text-gray-700">
            Interval:
          </label>
          <select
            id="refresh-interval"
            value={refreshInterval}
            onChange={handleIntervalChange}
            className="px-2 py-1 text-xs border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={10}>10s</option>
            <option value={30}>30s</option>
            <option value={60}>1m</option>
            <option value={300}>5m</option>
            <option value={600}>10m</option>
          </select>
        </div>

        {/* Next Refresh Display */}
        {autoRefreshEnabled && (
          <div className="text-xs text-gray-600 font-medium">
            Next in: <span className="text-blue-600">{nextRefresh}s</span>
          </div>
        )}
      </div>
    </div>
  );
};

RefreshControl.displayName = 'RefreshControl';
