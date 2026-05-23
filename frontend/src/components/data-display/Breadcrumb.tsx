import React from 'react';
import { ChevronRight } from 'lucide-react';

export interface BreadcrumbItem {
  label: string;
  path?: string;
  onClick?: () => void;
}

export interface BreadcrumbProps {
  items: BreadcrumbItem[];
  separator?: React.ReactNode;
  className?: string;
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({
  items,
  separator = <ChevronRight size={16} className="text-gray-400" />,
  className = '',
}) => {
  return (
    <nav
      className={`flex items-center gap-2 text-sm ${className}`}
      aria-label="Breadcrumb"
    >
      {items.map((item, index) => (
        <React.Fragment key={index}>
          {index > 0 && <span className="text-gray-400">{separator}</span>}
          {item.path || item.onClick ? (
            <button
              onClick={item.onClick}
              className="text-blue-600 hover:text-blue-700 transition-colors"
            >
              {item.label}
            </button>
          ) : (
            <span className="text-gray-700">{item.label}</span>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
};

Breadcrumb.displayName = 'Breadcrumb';
