import React, { useEffect } from 'react';

export interface RealtimeIndicatorProps {
  active: boolean;
  label?: string;
}

export const RealtimeIndicator: React.FC<RealtimeIndicatorProps> = ({
  active,
  label = 'Live Updates',
}) => {
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-lg">
      {/* Pulse Circle */}
      <div className="relative w-2 h-2">
        <div
          className={`absolute inset-0 rounded-full ${
            active ? 'bg-blue-600 animate-pulse' : 'bg-gray-400'
          }`}
        />
        {active && (
          <div className="absolute inset-0 rounded-full bg-blue-600 animate-ping opacity-75" />
        )}
      </div>

      {/* Label */}
      <span className="text-xs font-semibold text-blue-700">{label}</span>

      {/* Status Badge */}
      <span
        className={`text-xs font-medium px-2 py-0.5 rounded-full ${
          active
            ? 'bg-green-100 text-green-700'
            : 'bg-gray-100 text-gray-700'
        }`}
      >
        {active ? 'ON' : 'OFF'}
      </span>
    </div>
  );
};

RealtimeIndicator.displayName = 'RealtimeIndicator';
