import React, { useState } from 'react';
import { Modal, Button, Badge } from '@/components/ui';
import { AlertCircle, Clock, CheckCircle } from 'lucide-react';
import { Alert } from '@/types';

export interface AlertDetailProps {
  alert: Alert | null;
  isOpen: boolean;
  onClose: () => void;
  onAcknowledge?: () => Promise<void>;
  onResolve?: () => Promise<void>;
  loading?: boolean;
}

export const AlertDetail: React.FC<AlertDetailProps> = ({
  alert,
  isOpen,
  onClose,
  onAcknowledge,
  onResolve,
  loading = false,
}) => {
  const [processing, setProcessing] = useState(false);

  const handleAcknowledge = async () => {
    if (!onAcknowledge) return;
    setProcessing(true);
    try {
      await onAcknowledge();
    } finally {
      setProcessing(false);
    }
  };

  const handleResolve = async () => {
    if (!onResolve) return;
    setProcessing(true);
    try {
      await onResolve();
    } finally {
      setProcessing(false);
    }
  };

  if (!alert) return null;

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
        return <CheckCircle className="text-green-600" size={20} />;
      case 'ACKNOWLEDGED':
        return <Clock className="text-yellow-600" size={20} />;
      default:
        return <AlertCircle className="text-red-600" size={20} />;
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Alert Details"
      size="md"
      footer={
        alert.status === 'ACTIVE' ? (
          <>
            <Button variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button
              variant="warning"
              onClick={handleAcknowledge}
              isLoading={processing}
            >
              Acknowledge
            </Button>
            <Button
              variant="success"
              onClick={handleResolve}
              isLoading={processing}
            >
              Resolve
            </Button>
          </>
        ) : (
          <Button variant="secondary" onClick={onClose}>
            Close
          </Button>
        )
      }
    >
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3 flex-1">
            <div className="mt-1">{getStatusIcon(alert.status)}</div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                {alert.title}
              </h3>
              <p className="text-gray-600">{alert.message}</p>
            </div>
          </div>
          <Badge variant={getSeverityColor(alert.severity) as any}>
            {alert.severity}
          </Badge>
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-2 gap-4 bg-gray-50 rounded-lg p-4">
          <div>
            <p className="text-xs font-medium text-gray-600 mb-1">Status</p>
            <p className="text-sm font-semibold text-gray-900 capitalize">
              {alert.status}
            </p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-600 mb-1">Severity</p>
            <p className="text-sm font-semibold text-gray-900">
              {alert.severity}
            </p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-600 mb-1">Created</p>
            <p className="text-sm font-semibold text-gray-900">
              {new Date(alert.created_at).toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-600 mb-1">
              Last Updated
            </p>
            <p className="text-sm font-semibold text-gray-900">
              {new Date(alert.updated_at).toLocaleString()}
            </p>
          </div>
        </div>

        {/* Additional Info */}
        {alert.metadata && Object.keys(alert.metadata).length > 0 && (
          <div>
            <p className="text-xs font-medium text-gray-600 mb-2">Metadata</p>
            <div className="bg-gray-50 rounded-lg p-3 space-y-2">
              {Object.entries(alert.metadata).map(([key, value]) => (
                <div key={key} className="flex justify-between text-sm">
                  <span className="text-gray-600">{key}:</span>
                  <span className="text-gray-900 font-medium">{String(value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Description */}
        {alert.description && (
          <div>
            <p className="text-xs font-medium text-gray-600 mb-2">Description</p>
            <p className="text-sm text-gray-700 leading-relaxed">
              {alert.description}
            </p>
          </div>
        )}

        {/* Acknowledgment Info */}
        {alert.status !== 'ACTIVE' && (
          <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
            <p className="text-xs font-medium text-blue-900 mb-1">
              {alert.status === 'ACKNOWLEDGED' ? 'Acknowledged' : 'Resolved'}
            </p>
            <p className="text-xs text-blue-800">
              {alert.status === 'ACKNOWLEDGED'
                ? `Acknowledged on ${new Date(alert.acknowledged_at || '').toLocaleString()}`
                : `Resolved on ${new Date(alert.resolved_at || '').toLocaleString()}`}
            </p>
          </div>
        )}
      </div>
    </Modal>
  );
};

AlertDetail.displayName = 'AlertDetail';
