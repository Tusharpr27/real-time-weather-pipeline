import { useState, useCallback, useEffect } from 'react';
import { useWebSocket, WebSocketMessage } from '@/services/websocket';
import { WeatherData } from '@/types';

export const useRealTimeWeather = (enabled: boolean = true) => {
  const [weatherUpdates, setWeatherUpdates] = useState<WeatherData[]>([]);
  const [updateTimestamp, setUpdateTimestamp] = useState<string | null>(null);
  const { connected, lastMessage, error, send } = useWebSocket(
    import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/realtime/ws'
  );

  useEffect(() => {
    if (connected && enabled) {
      send({ type: 'subscribe', event: 'weather_update', locations: ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata'] });
    }
  }, [connected, enabled, send]);

  useEffect(() => {
    if (!enabled || !lastMessage) return;

    if (lastMessage.type === 'weather_update') {
      setWeatherUpdates(lastMessage.data);
      setUpdateTimestamp(lastMessage.timestamp);
    }
  }, [lastMessage, enabled]);

  return {
    weatherUpdates,
    connected,
    error,
    updateTimestamp,
  };
};

export const useRealtimeMetrics = (enabled: boolean = true) => {
  const [metrics, setMetrics] = useState({
    totalRequests: 0,
    requestsPerMinute: 0,
    averageResponseTime: 0,
    activeAlerts: 0,
  });
  const { connected, lastMessage, error, send } = useWebSocket(
    import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/realtime/ws'
  );

  useEffect(() => {
    if (connected && enabled) {
      send({ type: 'subscribe', event: 'system_metrics' });
    }
  }, [connected, enabled, send]);

  useEffect(() => {
    if (!enabled || !lastMessage) return;

    if (lastMessage.type === 'status') {
      setMetrics(lastMessage.data);
    }
  }, [lastMessage, enabled]);

  return {
    metrics,
    connected,
    error,
  };
};

export const useRealtimeAlerts = (enabled: boolean = true) => {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [newAlertCount, setNewAlertCount] = useState(0);
  const { connected, lastMessage, error, send } = useWebSocket(
    import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/realtime/ws'
  );

  useEffect(() => {
    if (connected && enabled) {
      send({ type: 'subscribe', event: 'alert' });
    }
  }, [connected, enabled, send]);

  useEffect(() => {
    if (!enabled || !lastMessage) return;

    if (lastMessage.type === 'alert') {
      setAlerts((prev) => [lastMessage.data, ...prev]);
      setNewAlertCount((prev) => prev + 1);
    }
  }, [lastMessage, enabled]);

  const clearNewAlertCount = useCallback(() => {
    setNewAlertCount(0);
  }, []);

  return {
    alerts,
    newAlertCount,
    connected,
    error,
    clearNewAlertCount,
  };
};
