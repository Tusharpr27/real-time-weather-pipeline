import React from 'react';

export interface DividerProps extends React.HTMLAttributes<HTMLDivElement> {
  orientation?: 'horizontal' | 'vertical';
  variant?: 'solid' | 'dashed' | 'dotted';
  spacing?: 'sm' | 'md' | 'lg';
}

export const Divider = React.forwardRef<HTMLDivElement, DividerProps>(
  (
    {
      orientation = 'horizontal',
      variant = 'solid',
      spacing = 'md',
      className = '',
      ...props
    },
    ref
  ) => {
    const orientationClasses = {
      horizontal: 'h-px w-full',
      vertical: 'h-full w-px',
    };

    const variantClasses = {
      solid: 'border-solid',
      dashed: 'border-dashed',
      dotted: 'border-dotted',
    };

    const spacingClasses = {
      sm: 'my-2',
      md: 'my-4',
      lg: 'my-6',
    };

    return (
      <div
        ref={ref}
        className={`border border-gray-200 ${orientationClasses[orientation]} ${variantClasses[variant]} ${spacing && orientation === 'horizontal' ? spacingClasses[spacing] : ''} ${className}`}
        {...props}
      />
    );
  }
);

Divider.displayName = 'Divider';
