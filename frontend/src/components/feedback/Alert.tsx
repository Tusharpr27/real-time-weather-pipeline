import React from 'react';
import { AlertCircle, CheckCircle, Info, AlertTriangle, X } from 'lucide-react';

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  type?: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  closeable?: boolean;
  onClose?: () => void;
  icon?: React.ReactNode;
}

export const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
  (
    {
      type = 'info',
      title,
      closeable = false,
      onClose,
      icon,
      children,
      className = '',
      ...props
    },
    ref
  ) => {
    const [isVisible, setIsVisible] = React.useState(true);

    const typeClasses = {
      success: {
        container: 'bg-green-50 border border-green-200',
        text: 'text-green-800',
        icon: <CheckCircle className="text-green-600" size={20} />,
      },
      error: {
        container: 'bg-red-50 border border-red-200',
        text: 'text-red-800',
        icon: <AlertCircle className="text-red-600" size={20} />,
      },
      warning: {
        container: 'bg-yellow-50 border border-yellow-200',
        text: 'text-yellow-800',
        icon: <AlertTriangle className="text-yellow-600" size={20} />,
      },
      info: {
        container: 'bg-blue-50 border border-blue-200',
        text: 'text-blue-800',
        icon: <Info className="text-blue-600" size={20} />,
      },
    };

    const handleClose = () => {
      setIsVisible(false);
      onClose?.();
    };

    if (!isVisible) return null;

    return (
      <div
        ref={ref}
        className={`rounded-lg p-4 ${typeClasses[type].container} ${className}`}
        {...props}
      >
        <div className="flex gap-3">
          <div className="flex-shrink-0">
            {icon || typeClasses[type].icon}
          </div>
          <div className="flex-1">
            {title && (
              <h3 className={`font-semibold ${typeClasses[type].text}`}>
                {title}
              </h3>
            )}
            <div className={`text-sm ${typeClasses[type].text}`}>
              {children}
            </div>
          </div>
          {closeable && (
            <button
              onClick={handleClose}
              className={`flex-shrink-0 ${typeClasses[type].text} hover:opacity-75 transition-opacity`}
              aria-label="Close alert"
            >
              <X size={20} />
            </button>
          )}
        </div>
      </div>
    );
  }
);

Alert.displayName = 'Alert';
