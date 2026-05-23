import React from 'react';
import { Button } from '@/components/ui';
import { Download, RefreshCw } from 'lucide-react';

export interface AlertActionsProps {
  onExport: () => Promise<void>;
  onRefresh: () => Promise<void>;
  exportLoading?: boolean;
  refreshLoading?: boolean;
  selectedCount?: number;
}

export const AlertActions: React.FC<AlertActionsProps> = ({
  onExport,
  onRefresh,
  exportLoading = false,
  refreshLoading = false,
  selectedCount = 0,
}) => {
  return (
    <div className="flex gap-2 flex-wrap">
      <Button
        variant="primary"
        size="md"
        onClick={onRefresh}
        isLoading={refreshLoading}
        leftIcon={<RefreshCw size={16} />}
      >
        Refresh
      </Button>

      <Button
        variant="secondary"
        size="md"
        onClick={onExport}
        isLoading={exportLoading}
        leftIcon={<Download size={16} />}
      >
        Export
      </Button>

      {selectedCount > 0 && (
        <div className="flex items-center gap-2 px-3 py-2 bg-blue-50 rounded-lg border border-blue-200">
          <span className="text-sm font-medium text-blue-700">
            {selectedCount} selected
          </span>
        </div>
      )}
    </div>
  );
};

AlertActions.displayName = 'AlertActions';
