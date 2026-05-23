import { useMemo } from 'react';
import { useAppSelector } from '@/store/hooks';

export interface ChartTimeRange {
  start: Date;
  end: Date;
  label: string;
}

export const TIME_RANGES: Record<string, ChartTimeRange> = {
  '24h': {
    start: new Date(Date.now() - 24 * 60 * 60 * 1000),
    end: new Date(),
    label: 'Last 24 Hours',
  },
  '7d': {
    start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
    end: new Date(),
    label: 'Last 7 Days',
  },
  '30d': {
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    end: new Date(),
    label: 'Last 30 Days',
  },
  '90d': {
    start: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000),
    end: new Date(),
    label: 'Last 90 Days',
  },
  '1y': {
    start: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000),
    end: new Date(),
    label: 'Last Year',
  },
};

export const useChartData = (timeRange: keyof typeof TIME_RANGES = '24h') => {
  const weather = useAppSelector((state) => state.weather);
  const selectedLocation = useAppSelector((state) => state.weather.selectedLocation);

  // Format timestamps for chart labels (HH:MM format)
  const formatChartLabel = (date: Date): string => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    });
  };

  // Generate labels based on time range
  const generateLabels = (): string[] => {
    const range = TIME_RANGES[timeRange];
    const diff = range.end.getTime() - range.start.getTime();
    const intervals = Math.min(24, Math.ceil(diff / (1000 * 60 * 60)));
    
    const labels: string[] = [];
    for (let i = 0; i < intervals; i++) {
      const timestamp = new Date(
        range.start.getTime() + (i / intervals) * diff
      );
      labels.push(formatChartLabel(timestamp));
    }
    return labels;
  };

  // Mock data generators (in production, would fetch from API)
  const generateTemperatureData = useMemo(
    () => ({
      labels: generateLabels(),
      current: Array.from(
        { length: generateLabels().length },
        () => 15 + Math.random() * 15
      ),
      min: Array.from(
        { length: generateLabels().length },
        () => 8 + Math.random() * 10
      ),
      max: Array.from(
        { length: generateLabels().length },
        () => 22 + Math.random() * 15
      ),
    }),
    [timeRange]
  );

  const generateHumidityData = useMemo(
    () => ({
      labels: generateLabels(),
      current: Array.from(
        { length: generateLabels().length },
        () => 40 + Math.random() * 50
      ),
      avg: Array.from(
        { length: generateLabels().length },
        () => 50 + Math.random() * 30
      ),
    }),
    [timeRange]
  );

  const generatePressureData = useMemo(
    () => ({
      labels: generateLabels(),
      data: Array.from(
        { length: generateLabels().length },
        () => 1013 + (Math.random() - 0.5) * 10
      ),
    }),
    [timeRange]
  );

  const generateWindData = useMemo(
    () => ({
      labels: generateLabels(),
      speed: Array.from(
        { length: generateLabels().length },
        () => 5 + Math.random() * 10
      ),
      gust: Array.from(
        { length: generateLabels().length },
        () => 8 + Math.random() * 12
      ),
    }),
    [timeRange]
  );

  const generatePrecipitationData = useMemo(
    () => ({
      labels: generateLabels(),
      data: Array.from(
        { length: generateLabels().length },
        () => Math.random() > 0.7 ? Math.random() * 20 : 0
      ),
      probability: Array.from(
        { length: generateLabels().length },
        () => Math.floor(Math.random() * 100)
      ),
    }),
    [timeRange]
  );

  return {
    timeRange,
    selectedLocation,
    temperatureData: generateTemperatureData,
    humidityData: generateHumidityData,
    pressureData: generatePressureData,
    windData: generateWindData,
    precipitationData: generatePrecipitationData,
    loading: weather.loading,
    error: weather.error,
  };
};
