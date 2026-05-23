import React from 'react';

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'default';
  size?: 'sm' | 'md' | 'lg';
  dot?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = 'default',
  size = 'md',
  dot = false,
  children,
  className = '',
  ...props
}) => {
  const variantClasses = {
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    danger: 'bg-red-100 text-red-800',
    info: 'bg-blue-100 text-blue-800',
    default: 'bg-gray-100 text-gray-800',
  };

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  };

  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full font-medium ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      {...props}
    >
      {dot && (
        <span
          className={`inline-block rounded-full h-2 w-2 ${
            variant === 'success'
              ? 'bg-green-600'
              : variant === 'warning'
                ? 'bg-yellow-600'
                : variant === 'danger'
                  ? 'bg-red-600'
                  : variant === 'info'
                    ? 'bg-blue-600'
                    : 'bg-gray-600'
          }`}
        />
      )}
      {children}
    </span>
  );
};

Badge.displayName = 'Badge';
