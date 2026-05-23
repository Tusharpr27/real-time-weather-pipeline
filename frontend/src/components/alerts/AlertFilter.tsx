import React from 'react';
import { Card } from '@/components/ui';
import { Filter, X } from 'lucide-react';

export interface AlertFilterProps {
  severityFilter: 'ALL' | 'LOW' | 'MEDIUM' | 'HIGH';
  onSeverityChange: (severity: 'ALL' | 'LOW' | 'MEDIUM' | 'HIGH') => void;
  statusFilter: 'ALL' | 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED';
  onStatusChange: (status: 'ALL' | 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED') => void;
  searchTerm: string;
  onSearchChange: (term: string) => void;
  onReset: () => void;
}

export const AlertFilter: React.FC<AlertFilterProps> = ({
  severityFilter,
  onSeverityChange,
  statusFilter,
  onStatusChange,
  searchTerm,
  onSearchChange,
  onReset,
}) => {
  const hasActiveFilters =
    severityFilter !== 'ALL' ||
    statusFilter !== 'ALL' ||
    searchTerm !== '';

  return (
    <Card>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter size={18} className="text-blue-600" />
            <h3 className="font-semibold text-gray-900">Filters</h3>
          </div>
          {hasActiveFilters && (
            <button
              onClick={onReset}
              className="flex items-center gap-1 text-xs font-medium text-blue-600 hover:text-blue-700 transition-colors"
            >
              <X size={14} />
              Reset
            </button>
          )}
        </div>

        {/* Search */}
        <div>
          <label className="text-sm font-medium text-gray-700 mb-2 block">
            Search
          </label>
          <input
            type="text"
            placeholder="Search by title or message..."
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          />
        </div>

        {/* Severity Filter */}
        <div>
          <label className="text-sm font-medium text-gray-700 mb-2 block">
            Severity
          </label>
          <div className="space-y-2">
            {['ALL', 'LOW', 'MEDIUM', 'HIGH'].map((severity) => (
              <label key={severity} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="severity"
                  value={severity}
                  checked={severityFilter === severity}
                  onChange={(e) =>
                    onSeverityChange(e.target.value as any)
                  }
                  className="w-4 h-4 accent-blue-600"
                />
                <span className="text-sm text-gray-700">
                  {severity === 'ALL' ? 'All Severities' : severity}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Status Filter */}
        <div>
          <label className="text-sm font-medium text-gray-700 mb-2 block">
            Status
          </label>
          <div className="space-y-2">
            {['ALL', 'ACTIVE', 'ACKNOWLEDGED', 'RESOLVED'].map((status) => (
              <label key={status} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="status"
                  value={status}
                  checked={statusFilter === status}
                  onChange={(e) =>
                    onStatusChange(e.target.value as any)
                  }
                  className="w-4 h-4 accent-blue-600"
                />
                <span className="text-sm text-gray-700">
                  {status === 'ALL' ? 'All Statuses' : status}
                </span>
              </label>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
};

AlertFilter.displayName = 'AlertFilter';
