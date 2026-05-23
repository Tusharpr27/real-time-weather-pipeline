import React from 'react';
import { Loader } from 'lucide-react';

export interface SpinnerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg';
  variant?: 'primary' | 'secondary' | 'white';
  label?: string;
}

export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  variant = 'primary',
  label,
  className = '',
  ...props
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  const variantClasses = {
    primary: 'text-blue-600',
    secondary: 'text-gray-600',
    white: 'text-white',
  };

  return (
    <div
      className={`flex flex-col items-center justify-center gap-2 ${className}`}
      {...props}
    >
      <Loader
        className={`animate-spin ${sizeClasses[size]} ${variantClasses[variant]}`}
      />
      {label && <p className="text-sm font-medium text-gray-600">{label}</p>}
    </div>
  );
};

Spinner.displayName = 'Spinner';
