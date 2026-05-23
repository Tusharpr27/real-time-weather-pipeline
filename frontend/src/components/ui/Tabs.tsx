import React, { useState } from 'react';

export interface Tab {
  id: string;
  label: string;
  content: React.ReactNode;
  icon?: React.ReactNode;
  disabled?: boolean;
}

export interface TabsProps {
  tabs: Tab[];
  defaultTab?: string;
  onChange?: (tabId: string) => void;
  variant?: 'default' | 'pill';
}

export const Tabs: React.FC<TabsProps> = ({
  tabs,
  defaultTab,
  onChange,
  variant = 'default',
}) => {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    onChange?.(tabId);
  };

  const tabClasses = {
    default: (isActive: boolean) =>
      `px-4 py-2 border-b-2 font-medium transition-colors ${
        isActive
          ? 'border-blue-600 text-blue-600'
          : 'border-transparent text-gray-600 hover:text-gray-900'
      }`,
    pill: (isActive: boolean) =>
      `px-4 py-2 rounded-full font-medium transition-colors ${
        isActive
          ? 'bg-blue-600 text-white'
          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
      }`,
  };

  const activeTabData = tabs.find((t) => t.id === activeTab);

  return (
    <div className="w-full">
      {/* Tab Headers */}
      <div
        className={`flex gap-2 ${
          variant === 'default'
            ? 'border-b border-gray-200'
            : 'gap-2'
        }`}
      >
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => handleTabChange(tab.id)}
            disabled={tab.disabled}
            className={`${tabClasses[variant](activeTab === tab.id)} disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2`}
          >
            {tab.icon && <span>{tab.icon}</span>}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="mt-4">{activeTabData?.content}</div>
    </div>
  );
};

Tabs.displayName = 'Tabs';
