import React from 'react';
import { AlertCircle, CheckCircle, Clock } from 'lucide-react';
import { Card } from '@/components/ui';
import { Badge } from '@/components/ui';
import { Alert } from '@/types';

export interface AlertCardProps {
  alert: Alert;
  onAcknowledge?: () => void;
  onResolve?: () => void;
}

export const AlertCard: React.FC<AlertCardProps> = ({
  alert,
  onAcknowledge,
  onResolve,
}) => {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'HIGH':
        return 'danger';
      case 'MEDIUM':
        return 'warning';
      case 'LOW':
        return 'info';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'RESOLVED':
        return <CheckCircle size={16} className="text-green-600" />;
      case 'ACKNOWLEDGED':
        return <Clock size={16} className="text-yellow-600" />;
      default:
        return <AlertCircle size={16} className="text-red-600" />;
    }
  };

  return (
    <Card className="bg-gradient-to-r from-red-50 to-orange-50 border-l-4 border-red-500">
      <div className="space-y-3">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3 flex-1">
            <div className="mt-1">{getStatusIcon(alert.status)}</div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">{alert.title}</h3>
              <p className="text-sm text-gray-600">{alert.message}</p>
            </div>
          </div>
          <Badge variant={getSeverityColor(alert.severity) as any}>
            {alert.severity}
          </Badge>
        </div>

        {/* Metadata */}
        <div className="flex items-center justify-between text-xs text-gray-600">
          <span>
            {new Date(alert.created_at).toLocaleString()}
          </span>
          <span className="capitalize">{alert.status}</span>
        </div>

        {/* Actions */}
        {alert.status === 'ACTIVE' && (
          <div className="flex gap-2 pt-2">
            <button
              onClick={onAcknowledge}
              className="flex-1 px-3 py-1.5 text-sm font-medium bg-yellow-100 text-yellow-800 rounded hover:bg-yellow-200 transition-colors"
            >
              Acknowledge
            </button>
            <button
              onClick={onResolve}
              className="flex-1 px-3 py-1.5 text-sm font-medium bg-green-100 text-green-800 rounded hover:bg-green-200 transition-colors"
            >
              Resolve
            </button>
          </div>
        )}
      </div>
    </Card>
  );
};

AlertCard.displayName = 'AlertCard';
