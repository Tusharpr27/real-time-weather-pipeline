import React from 'react';

export interface RadioOption {
  value: string | number;
  label: string;
  disabled?: boolean;
}

export interface RadioGroupProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  options: RadioOption[];
  label?: string;
  error?: string;
  helperText?: string;
  orientation?: 'vertical' | 'horizontal';
}

export const RadioGroup = React.forwardRef<HTMLDivElement, RadioGroupProps>(
  (
    {
      options,
      label,
      error,
      helperText,
      orientation = 'vertical',
      value,
      onChange,
      id,
      className = '',
      ...props
    },
    ref
  ) => {
    const groupId = id || `radio-group-${Math.random()}`;

    return (
      <div ref={ref} className={className}>
        {label && (
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {label}
          </label>
        )}
        <div
          className={`space-y-2 ${
            orientation === 'horizontal' ? 'flex gap-4' : ''
          }`}
        >
          {options.map((option) => (
            <div key={option.value} className="flex items-center">
              <input
                type="radio"
                id={`${groupId}-${option.value}`}
                name={groupId}
                value={option.value}
                checked={value === option.value}
                onChange={onChange}
                disabled={option.disabled}
                className="w-4 h-4 cursor-pointer accent-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                {...props}
              />
              <label
                htmlFor={`${groupId}-${option.value}`}
                className="ml-2 text-sm text-gray-700 cursor-pointer"
              >
                {option.label}
              </label>
            </div>
          ))}
        </div>
        {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
        {helperText && !error && (
          <p className="text-gray-500 text-sm mt-1">{helperText}</p>
        )}
      </div>
    );
  }
);

RadioGroup.displayName = 'RadioGroup';
