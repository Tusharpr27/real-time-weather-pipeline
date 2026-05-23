import React from 'react';
import { useResponsive } from '@/hooks/useResponsive';

interface MobileOptimizedInputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
  helperText?: string;
}

/**
 * MobileOptimizedInput Component
 * Adapts input field for better mobile experience:
 * - Proper keyboard types for email, phone, etc.
 * - Larger touch targets on mobile (min 44x44px)
 * - Adjusted font size to prevent auto-zoom on iOS
 * - Mobile-friendly spacing and styling
 */
const MobileOptimizedInput = React.forwardRef<
  HTMLInputElement,
  MobileOptimizedInputProps
>(
  (
    { label, error, icon, helperText, className = '', ...inputProps },
    ref
  ) => {
    const { isMobile } = useResponsive();

    // Auto-detect keyboard type for mobile based on input type
    const getKeyboardType = () => {
      if (isMobile) {
        switch (inputProps.type) {
          case 'email':
            return { pattern: '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}' };
          case 'tel':
            return { pattern: '[0-9+\\-\\s()]*', inputMode: 'tel' as const };
          case 'number':
            return { inputMode: 'numeric' as const };
          default:
            return {};
        }
      }
      return {};
    };

    const keyboardAttrs = getKeyboardType();

    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {label}
          </label>
        )}

        <div className="relative">
          {icon && (
            <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 pointer-events-none">
              {icon}
            </div>
          )}

          <input
            ref={ref}
            {...inputProps}
            {...keyboardAttrs}
            className={`
              w-full px-4 py-3 rounded-lg border-2 transition-colors
              ${icon ? 'pl-10' : ''}
              ${error ? 'border-red-500 bg-red-50' : 'border-gray-300 bg-white'}
              focus:outline-none focus:border-indigo-500 focus:bg-white
              text-base
              ${isMobile ? 'text-lg' : ''}
              disabled:bg-gray-100 disabled:text-gray-500 disabled:cursor-not-allowed
              ${className}
            `}
          />
        </div>

        {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
        {helperText && !error && (
          <p className="mt-1 text-xs text-gray-500">{helperText}</p>
        )}
      </div>
    );
  }
);

MobileOptimizedInput.displayName = 'MobileOptimizedInput';

export default MobileOptimizedInput;
