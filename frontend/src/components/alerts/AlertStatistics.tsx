import React from 'react';
import { Card } from '@/components/ui';
import { AlertCircle, CheckCircle, Clock } from 'lucide-react';

export interface AlertStatisticsProps {
  totalAlerts: number;
  activeAlerts: number;
  acknowledgedAlerts: number;
  resolvedAlerts: number;
  loading?: boolean;
}

export const AlertStatistics: React.FC<AlertStatisticsProps> = ({
  totalAlerts,
  activeAlerts,
  acknowledgedAlerts,
  resolvedAlerts,
  loading = false,
}) => {
  const stats = [
    {
      icon: AlertCircle,
      label: 'Active',
      value: activeAlerts,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
    },
    {
      icon: Clock,
      label: 'Acknowledged',
      value: acknowledgedAlerts,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
    },
    {
      icon: CheckCircle,
      label: 'Resolved',
      value: resolvedAlerts,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      icon: AlertCircle,
      label: 'Total',
      value: totalAlerts,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {stats.map((stat) => {
        const Icon = stat.icon;
        return (
          <Card key={stat.label}>
            <div className="flex items-start gap-3">
              <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                <Icon size={20} className={stat.color} />
              </div>
              <div className="flex-1">
                <p className="text-xs font-medium text-gray-600 mb-1">
                  {stat.label}
                </p>
                <p className="text-2xl font-bold text-gray-900">
                  {loading ? '-' : stat.value}
                </p>
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
};

AlertStatistics.displayName = 'AlertStatistics';
