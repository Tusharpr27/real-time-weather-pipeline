import React from 'react';

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  fullWidth?: boolean;
  icon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      helperText,
      fullWidth = false,
      icon,
      id,
      className = '',
      ...props
    },
    ref
  ) => {
    const inputId = id || `input-${Math.random()}`;

    return (
      <div className={fullWidth ? 'w-full' : ''}>
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            {label}
          </label>
        )}
        <div className="relative">
          <input
            ref={ref}
            id={inputId}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors ${
              error ? 'border-red-500' : 'border-gray-300'
            } ${icon ? 'pl-10' : ''} ${className}`}
            {...props}
          />
          {icon && (
            <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
              {icon}
            </span>
          )}
        </div>
        {error && (
          <p className="text-red-500 text-sm mt-1">{error}</p>
        )}
        {helperText && !error && (
          <p className="text-gray-500 text-sm mt-1">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
