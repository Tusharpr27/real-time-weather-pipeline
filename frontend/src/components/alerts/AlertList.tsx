import React, { useState } from 'react';
import { Badge } from '@/components/ui';
import { AlertCard } from '@/components/common';
import { Alert } from '@/types';

export interface AlertListProps {
  alerts: Alert[];
  loading?: boolean;
  selectedAlertId?: string;
  onSelectAlert: (alertId: string) => void;
  onAcknowledge: (alertId: string) => Promise<void>;
  onResolve: (alertId: string) => Promise<void>;
  pagination?: {
    page: number;
    pageSize: number;
    total: number;
    onPageChange: (page: number) => void;
  };
}

export const AlertList: React.FC<AlertListProps> = ({
  alerts,
  loading = false,
  selectedAlertId,
  onSelectAlert,
  onAcknowledge,
  onResolve,
  pagination,
}) => {
  const [processingAlertId, setProcessingAlertId] = useState<string | null>(null);

  const handleAcknowledge = async (alertId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setProcessingAlertId(alertId);
    try {
      await onAcknowledge(alertId);
    } finally {
      setProcessingAlertId(null);
    }
  };

  const handleResolve = async (alertId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setProcessingAlertId(alertId);
    try {
      await onResolve(alertId);
    } finally {
      setProcessingAlertId(null);
    }
  };

  if (loading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-24 bg-gray-200 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  if (alerts.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400 text-5xl mb-4">✓</div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No Alerts</h3>
        <p className="text-gray-600">All systems are operating normally</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          onClick={() => onSelectAlert(alert.id)}
          className={`cursor-pointer transition-all ${
            selectedAlertId === alert.id
              ? 'ring-2 ring-blue-500 rounded-lg'
              : ''
          }`}
        >
          <AlertCard
            alert={alert}
            onAcknowledge={(e) => {
              handleAcknowledge(alert.id, e as any);
            }}
            onResolve={(e) => {
              handleResolve(alert.id, e as any);
            }}
          />
        </div>
      ))}

      {/* Pagination */}
      {pagination && (
        <div className="flex items-center justify-between mt-6 p-4 bg-white rounded-lg border border-gray-200">
          <span className="text-sm text-gray-600">
            Page {pagination.page} of{' '}
            {Math.ceil(pagination.total / pagination.pageSize)}
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => pagination.onPageChange(pagination.page - 1)}
              disabled={pagination.page === 1}
              className="px-3 py-1.5 text-sm font-medium bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            <button
              onClick={() => pagination.onPageChange(pagination.page + 1)}
              disabled={
                pagination.page >=
                Math.ceil(pagination.total / pagination.pageSize)
              }
              className="px-3 py-1.5 text-sm font-medium bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

AlertList.displayName = 'AlertList';
