import React from 'react';
import { Card } from '@/components/ui';

export interface StatCardProps {
  icon?: React.ReactNode;
  label: string;
  value: string | number;
  change?: {
    value: number;
    direction: 'up' | 'down';
  };
  color?: 'blue' | 'green' | 'red' | 'yellow';
}

export const StatCard: React.FC<StatCardProps> = ({
  icon,
  label,
  value,
  change,
  color = 'blue',
}) => {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    red: 'bg-red-50 text-red-600',
    yellow: 'bg-yellow-50 text-yellow-600',
  };

  const changeColorClass = change?.direction === 'up' ? 'text-green-600' : 'text-red-600';

  return (
    <Card>
      <div className="space-y-3">
        {/* Icon */}
        {icon && (
          <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${colorClasses[color]}`}>
            {icon}
          </div>
        )}

        {/* Content */}
        <div>
          <p className="text-sm text-gray-600">{label}</p>
          <div className="flex items-end gap-2 mt-1">
            <span className="text-2xl font-bold text-gray-900">{value}</span>
            {change && (
              <span className={`text-sm font-semibold ${changeColorClass}`}>
                {change.direction === 'up' ? '↑' : '↓'} {Math.abs(change.value)}%
              </span>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
};

StatCard.displayName = 'StatCard';
