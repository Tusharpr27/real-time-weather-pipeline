import React from 'react';
import { Check } from 'lucide-react';

export interface CheckboxProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  helperText?: string;
}

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  (
    { label, helperText, id, className = '', ...props },
    ref
  ) => {
    const checkboxId = id || `checkbox-${Math.random()}`;

    return (
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <input
            ref={ref}
            type="checkbox"
            id={checkboxId}
            className="hidden"
            {...props}
          />
          <label
            htmlFor={checkboxId}
            className={`flex items-center cursor-pointer gap-2 ${className}`}
          >
            <div className="relative inline-flex items-center justify-center w-5 h-5 border-2 border-gray-300 rounded bg-white peer-checked:bg-blue-600 peer-checked:border-blue-600 transition-colors">
              <Check
                size={16}
                className={`text-white ${
                  (props as any).checked ? 'block' : 'hidden'
                }`}
              />
            </div>
            {label && (
              <span className="text-sm font-medium text-gray-700">
                {label}
              </span>
            )}
          </label>
        </div>
        {helperText && (
          <p className="text-gray-500 text-sm ml-7">{helperText}</p>
        )}
      </div>
    );
  }
);

Checkbox.displayName = 'Checkbox';
