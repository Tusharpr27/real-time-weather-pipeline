import React from 'react';
import { Cloud, CloudRain, Sun, Wind, Droplets } from 'lucide-react';
import { Card } from '@/components/ui';
import { WeatherData } from '@/types';

export interface WeatherCardProps {
  data: WeatherData;
  onClick?: () => void;
}

export const WeatherCard: React.FC<WeatherCardProps> = ({ data, onClick }) => {
  const getWeatherIcon = (condition: string) => {
    const cond = (condition || '').toLowerCase();
    switch (cond) {
      case 'sunny':
        return <Sun className="text-yellow-500" size={32} />;
      case 'cloudy':
        return <Cloud className="text-gray-500" size={32} />;
      case 'rainy':
        return <CloudRain className="text-blue-500" size={32} />;
      default:
        return <Cloud className="text-gray-500" size={32} />;
    }
  };

  return (
    <Card
      hoverable
      onClick={onClick}
      className="cursor-pointer bg-gradient-to-br from-blue-50 to-blue-100"
    >
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {data.location?.name}
            </h3>
            <p className="text-sm text-gray-600">
              {new Date(data.timestamp).toLocaleString()}
            </p>
          </div>
          <div>{getWeatherIcon(data.condition)}</div>
        </div>

        {/* Temperature */}
        <div className="flex items-baseline gap-2">
          <span className="text-4xl font-bold text-gray-900">
            {Math.round(data.temperature)}°C
          </span>
          <span className="text-sm text-gray-600">{data.condition}</span>
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-2 gap-3 pt-2 border-t border-blue-200">
          <div className="flex items-center gap-2">
            <Droplets size={16} className="text-blue-600" />
            <div>
              <p className="text-xs text-gray-600">Humidity</p>
              <p className="font-medium text-gray-900">{data.humidity}%</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Wind size={16} className="text-blue-600" />
            <div>
              <p className="text-xs text-gray-600">Wind Speed</p>
              <p className="font-medium text-gray-900">{data.wind_speed} m/s</p>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};

WeatherCard.displayName = 'WeatherCard';
