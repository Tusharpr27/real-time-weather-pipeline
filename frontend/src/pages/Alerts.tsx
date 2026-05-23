import React, { useState, useEffect } from 'react';
import { useAlerts } from '@/hooks/useAlerts';
import { useUI } from '@/hooks/useUI';
import {
  AlertList,
  AlertDetail,
  AlertFilter,
  AlertActions,
  AlertStatistics,
} from '@/components/alerts';
import { PageContainer, Divider } from '@/components/common';
import { Alert } from '@/types';
import { Download } from 'lucide-react';

const Alerts: React.FC = () => {
  // Redux hooks
  const {
    items,
    activeCount,
    loading,
    error,
    filter,
    pagination,
    getAlerts,
    acknowledge,
    resolve,
    updateFilter,
    changePage,
  } = useAlerts();
  const { showNotification } = useUI();

  // Local state
  const [selectedAlertId, setSelectedAlertId] = useState<string | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [exportLoading, setExportLoading] = useState(false);
  const [refreshLoading, setRefreshLoading] = useState(false);

  // Calculate statistics
  const activeAlerts = items.filter((a) => a.status === 'ACTIVE').length;
  const acknowledgedAlerts = items.filter((a) => a.status === 'ACKNOWLEDGED').length;
  const resolvedAlerts = items.filter((a) => a.status === 'RESOLVED').length;

  // Initialize
  useEffect(() => {
    handleRefresh();
  }, []);

  // Filter local alerts
  const filteredAlerts = items.filter((alert) => {
    // Severity filter
    if (filter.severity !== 'ALL' && alert.severity !== filter.severity) {
      return false;
    }

    // Status filter
    if (filter.status !== 'ALL' && alert.status !== filter.status) {
      return false;
    }

    // Search filter
    if (searchTerm) {
      const term = (searchTerm || '').toLowerCase();
      return (
        (alert.title || '').toLowerCase().includes(term) ||
        (alert.message || '').toLowerCase().includes(term)
      );
    }

    return true;
  });

  // Handlers
  const handleRefresh = async () => {
    setRefreshLoading(true);
    try {
      getAlerts({
        page: pagination.page,
        pageSize: pagination.pageSize,
      });
      showNotification({
        type: 'success',
        message: 'Alerts refreshed',
      });
    } catch (err) {
      showNotification({
        type: 'error',
        message: 'Failed to refresh alerts',
      });
    } finally {
      setRefreshLoading(false);
    }
  };

  const handleExport = async () => {
    setExportLoading(true);
    try {
      // Simulate export - in production, call API
      const csvContent = [
        ['ID', 'Title', 'Message', 'Severity', 'Status', 'Created At'],
        ...filteredAlerts.map((alert) => [
          alert.id,
          alert.title,
          alert.message,
          alert.severity,
          alert.status,
          new Date(alert.created_at).toISOString(),
        ]),
      ]
        .map((row) => row.map((cell) => `"${cell}"`).join(','))
        .join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `alerts-${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);

      showNotification({
        type: 'success',
        message: `Exported ${filteredAlerts.length} alerts`,
      });
    } catch (err) {
      showNotification({
        type: 'error',
        message: 'Failed to export alerts',
      });
    } finally {
      setExportLoading(false);
    }
  };

  const handleAcknowledge = async (alertId: string) => {
    try {
      await acknowledge(alertId);
      showNotification({
        type: 'success',
        message: 'Alert acknowledged',
      });
      setShowDetailModal(false);
    } catch (err) {
      showNotification({
        type: 'error',
        message: 'Failed to acknowledge alert',
      });
    }
  };

  const handleResolve = async (alertId: string) => {
    try {
      await resolve(alertId);
      showNotification({
        type: 'success',
        message: 'Alert resolved',
      });
      setShowDetailModal(false);
    } catch (err) {
      showNotification({
        type: 'error',
        message: 'Failed to resolve alert',
      });
    }
  };

  const handleFilterChange = (
    key: 'severity' | 'status',
    value: string
  ) => {
    updateFilter({
      [key]: value,
    });
  };

  const handleResetFilters = () => {
    updateFilter({
      severity: 'ALL',
      status: 'ALL',
    });
    setSearchTerm('');
  };

  const selectedAlert = items.find((a) => a.id === selectedAlertId);

  return (
    <div className="flex-1 bg-gray-50">
      <PageContainer maxWidth="2xl" padding="lg">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Alert Management</h1>
          <p className="text-gray-600 mt-2">
            Monitor and manage system alerts, filter by severity and status
          </p>
        </div>

        <Divider spacing="lg" />

        {/* Statistics */}
        <div className="mb-6">
          <AlertStatistics
            totalAlerts={items.length}
            activeAlerts={activeAlerts}
            acknowledgedAlerts={acknowledgedAlerts}
            resolvedAlerts={resolvedAlerts}
            loading={loading}
          />
        </div>

        <Divider spacing="lg" />

        {/* Action Bar */}
        <div className="mb-6">
          <AlertActions
            onExport={handleExport}
            onRefresh={handleRefresh}
            exportLoading={exportLoading}
            refreshLoading={refreshLoading}
            selectedCount={selectedAlertId ? 1 : 0}
          />
        </div>

        <Divider spacing="lg" />

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <AlertFilter
              severityFilter={filter.severity}
              onSeverityChange={(severity) => handleFilterChange('severity', severity)}
              statusFilter={filter.status}
              onStatusChange={(status) => handleFilterChange('status', status)}
              searchTerm={searchTerm}
              onSearchChange={setSearchTerm}
              onReset={handleResetFilters}
            />
          </div>

          {/* Alerts List */}
          <div className="lg:col-span-3">
            <AlertList
              alerts={filteredAlerts}
              loading={loading}
              selectedAlertId={selectedAlertId}
              onSelectAlert={(alertId) => {
                setSelectedAlertId(alertId);
                setShowDetailModal(true);
              }}
              onAcknowledge={handleAcknowledge}
              onResolve={handleResolve}
              pagination={{
                page: pagination.page,
                pageSize: pagination.pageSize,
                total: pagination.total,
                onPageChange: changePage,
              }}
            />
          </div>
        </div>
      </PageContainer>

      {/* Detail Modal */}
      <AlertDetail
        alert={selectedAlert || null}
        isOpen={showDetailModal}
        onClose={() => setShowDetailModal(false)}
        onAcknowledge={() => {
          if (selectedAlertId) {
            handleAcknowledge(selectedAlertId);
          }
        }}
        onResolve={() => {
          if (selectedAlertId) {
            handleResolve(selectedAlertId);
          }
        }}
        loading={loading}
      />
    </div>
  );
};

export default Alerts;
