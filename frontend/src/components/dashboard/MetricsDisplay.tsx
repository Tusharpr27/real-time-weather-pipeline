import React from 'react';
import { Card } from '@/components/ui';
import { Activity, Zap, Database, AlertCircle } from 'lucide-react';

export interface MetricsData {
  totalRequests: number;
  requestsPerMinute: number;
  averageResponseTime: number;
  activeAlerts: number;
}

export interface MetricsDisplayProps {
  metrics: MetricsData;
  loading?: boolean;
}

export const MetricsDisplay: React.FC<MetricsDisplayProps> = ({
  metrics,
  loading = false,
}) => {
  const metricItems = [
    {
      icon: Activity,
      label: 'Total Requests',
      value: metrics.totalRequests?.toLocaleString() || '0',
      color: 'blue',
    },
    {
      icon: Zap,
      label: 'Requests/min',
      value: metrics.requestsPerMinute?.toFixed(1) || '0',
      color: 'yellow',
    },
    {
      icon: Database,
      label: 'Avg Response',
      value: `${metrics.averageResponseTime?.toFixed(0) || '0'}ms`,
      color: 'green',
    },
    {
      icon: AlertCircle,
      label: 'Active Alerts',
      value: metrics.activeAlerts?.toString() || '0',
      color: 'red',
    },
  ];

  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    green: 'bg-green-50 text-green-600',
    red: 'bg-red-50 text-red-600',
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {metricItems.map((item) => {
        const Icon = item.icon;
        return (
          <Card key={item.label}>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-xs font-medium text-gray-600 mb-1">
                  {item.label}
                </p>
                <p className="text-2xl font-bold text-gray-900">
                  {loading ? '-' : item.value}
                </p>
              </div>
              <div className={`p-2 rounded-lg ${colorClasses[item.color as keyof typeof colorClasses]}`}>
                <Icon size={20} />
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
};

MetricsDisplay.displayName = 'MetricsDisplay';
