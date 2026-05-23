import { Circle, AlertCircle, CheckCircle } from 'lucide-react';

export interface StatusIndicatorProps {
  status: 'connected' | 'connecting' | 'disconnected' | 'error';
  label?: string;
  showTimestamp?: boolean;
  timestamp?: string;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  label = 'Connection Status',
  showTimestamp = true,
  timestamp,
}) => {
  const getStatusConfig = (s: typeof status) => {
    switch (s) {
      case 'connected':
        return {
          color: 'text-green-600',
          bgColor: 'bg-green-50',
          icon: CircleIcon,
          text: 'Connected',
          dot: 'bg-green-600',
        };
      case 'connecting':
        return {
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-50',
          icon: CircleIcon,
          text: 'Connecting...',
          dot: 'bg-yellow-600 animate-pulse',
        };
      case 'disconnected':
        return {
          color: 'text-gray-600',
          bgColor: 'bg-gray-50',
          icon: CircleIcon,
          text: 'Disconnected',
          dot: 'bg-gray-600',
        };
      case 'error':
        return {
          color: 'text-red-600',
          bgColor: 'bg-red-50',
          icon: AlertCircle,
          text: 'Error',
          dot: 'bg-red-600',
        };
    }
  };

  const config = getStatusConfig(status);

  return (
    <div className={`rounded-lg ${config.bgColor} p-3`}>
      <div className="flex items-center gap-3">
        <div className={`rounded-full w-3 h-3 ${config.dot}`} />
        <div className="flex-1">
          <p className="text-xs font-medium text-gray-600">{label}</p>
          <p className={`text-sm font-semibold ${config.color}`}>{config.text}</p>
        </div>
        {showTimestamp && timestamp && (
          <p className="text-xs text-gray-500">
            {new Date(timestamp).toLocaleTimeString()}
          </p>
        )}
      </div>
    </div>
  );
};

const CircleIcon = Circle;

StatusIndicator.displayName = 'StatusIndicator';
