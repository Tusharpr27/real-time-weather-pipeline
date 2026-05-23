import React, { useState, useEffect } from 'react';
import { useWeather } from '@/hooks/useWeather';
import { useUI } from '@/hooks/useUI';
import { useRealTimeWeather, useRealtimeMetrics, useRealtimeAlerts } from '@/hooks/useRealtime';
import useLocations from '@/hooks/useLocations'
import {
  StatusIndicator,
  RefreshControl,
  WeatherGrid,
  MetricsDisplay,
  RealtimeIndicator,
  LocationSelector,
} from '@/components/dashboard';
import { PageContainer, Grid } from '@/components/common';
import { Divider } from '@/components/common';
import { Alert } from '@/components/feedback';

const Dashboard: React.FC = () => {
  // Redux hooks
  const { current, forecast, loading, selectedLocation, getCurrentWeather } = useWeather();
  const { showNotification } = useUI();

  // Real-time hooks
  const { weatherUpdates, connected: weatherConnected, updateTimestamp } = useRealTimeWeather(true);
  const { metrics, connected: metricsConnected } = useRealtimeMetrics(true);
  const { alerts: realtimeAlerts, newAlertCount } = useRealtimeAlerts(true);

  // Local state
  const [selectedLocations, setSelectedLocations] = useState<string[]>([]);
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30);
  const [displayMetrics, setDisplayMetrics] = useState<any>({
    totalRequests: 0,
    requestsPerMinute: 0,
    averageResponseTime: 0,
    activeAlerts: realtimeAlerts.length,
  });

  // Live available locations from backend
  const { locations: availableLocations, loading: locationsLoading } = useLocations()

  // Initialize with first location when backend locations available
  useEffect(() => {
    if (selectedLocations.length === 0 && availableLocations.length > 0) {
      setSelectedLocations([availableLocations[0].id])
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [availableLocations])

  // Fetch current weather for primary selected location when it changes
  useEffect(() => {
    if (selectedLocations.length > 0) {
      // fetch current weather for the first selected location as a fallback
      getCurrentWeather(selectedLocations[0]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedLocations]);

  // Handle manual refresh
  const handleManualRefresh = async () => {
    if (selectedLocations.length === 0) {
      showNotification({
        type: 'warning',
        message: 'Please select a location first',
      });
      return;
    }

    showNotification({
      type: 'info',
      message: 'Refreshing data...',
    });

    // Fetch weather for selected locations
    for (const locationId of selectedLocations) {
      getCurrentWeather(locationId);
    }
  };

  // Handle auto-refresh
  useEffect(() => {
    if (!autoRefreshEnabled) return;

    const timer = setInterval(() => {
      handleManualRefresh();
    }, refreshInterval * 1000);

    return () => clearInterval(timer);
  }, [autoRefreshEnabled, refreshInterval, selectedLocations]);

  // Update metrics from real-time data
  useEffect(() => {
    setDisplayMetrics((prev: any) => ({
      ...prev,
      ...metrics,
      activeAlerts: realtimeAlerts.length,
    }));
  }, [metrics, realtimeAlerts.length]);

  // Show new alert notification
  useEffect(() => {
    if (newAlertCount > 0) {
      showNotification({
        type: 'warning',
        message: `${newAlertCount} new alert(s) received`,
      });
    }
  }, [newAlertCount]);

  const getConnectionStatus = (): 'connected' | 'disconnected' | 'connecting' | 'error' => {
    if (weatherConnected && metricsConnected) return 'connected';
    if (!weatherConnected && !metricsConnected) return 'disconnected';
    return 'connecting';
  };

  return (
    <div className="flex-1 bg-gray-50">
      <PageContainer maxWidth="2xl" padding="lg">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <h1 className="text-4xl font-bold text-gray-900">Real-Time Dashboard</h1>
            <RealtimeIndicator active={weatherConnected} label="Weather Updates" />
          </div>
          <p className="text-gray-600">
            Monitor live weather conditions and system metrics across multiple locations
          </p>
        </div>

        {/* Status Section */}
        <div className="mb-6 space-y-3">
          <StatusIndicator
            status={getConnectionStatus()}
            label="WebSocket Connection"
            showTimestamp={true}
            timestamp={updateTimestamp || undefined}
          />
        </div>

        {/* New Alerts Alert */}
        {newAlertCount > 0 && (
          <div className="mb-6">
            <Alert type="warning" title="New Alerts" closeable>
              You have {newAlertCount} new alert(s). Check the alerts page for details.
            </Alert>
          </div>
        )}

        <Divider spacing="lg" />

        {/* Refresh Control */}
        <div className="mb-6">
          <RefreshControl
            onManualRefresh={handleManualRefresh}
            autoRefreshEnabled={autoRefreshEnabled}
            onAutoRefreshChange={setAutoRefreshEnabled}
            refreshInterval={refreshInterval}
            onIntervalChange={setRefreshInterval}
            loading={loading}
          />
        </div>

        <Divider spacing="lg" />

        {/* Location Selector */}
        <div className="mb-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <LocationSelector
              selectedLocations={selectedLocations}
              availableLocations={availableLocations}
              onSelectionChange={setSelectedLocations}
              maxSelections={5}
            />
          </div>

          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Dashboard Info</h3>
              <dl className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <dt className="text-gray-600">Locations Monitored:</dt>
                  <dd className="font-medium text-gray-900">{selectedLocations.length}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-600">Connection Status:</dt>
                  <dd className={`font-medium ${getConnectionStatus() === 'connected' ? 'text-green-600' : 'text-gray-900'}`}>
                    {getConnectionStatus().charAt(0).toUpperCase() + getConnectionStatus().slice(1)}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-600">Last Update:</dt>
                  <dd className="font-medium text-gray-900">
                    {updateTimestamp ? new Date(updateTimestamp).toLocaleTimeString() : 'Never'}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-600">Active Alerts:</dt>
                  <dd className="font-medium text-red-600">{realtimeAlerts.length}</dd>
                </div>
              </dl>
            </div>
          </div>
        </div>

        <Divider spacing="lg" />

        {/* Metrics */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">System Metrics</h2>
          <MetricsDisplay metrics={displayMetrics} loading={loading} />
        </div>

        <Divider spacing="lg" />

        {/* Weather Grid */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Weather Conditions</h2>
          <WeatherGrid
            data={weatherUpdates.length > 0 ? weatherUpdates : (current ? [current] : [])}
            loading={loading}
            gridCols={3}
            onCardClick={(locationId) => {
              showNotification({
                type: 'info',
                message: `Selected ${availableLocations.find((l) => l.id === locationId)?.name}`,
              });
            }}
          />
        </div>
      </PageContainer>
    </div>
  );
};

export default Dashboard;
