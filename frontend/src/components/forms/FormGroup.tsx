import React from 'react';

export interface FormGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  spacing?: 'sm' | 'md' | 'lg';
}

export const FormGroup = React.forwardRef<HTMLDivElement, FormGroupProps>(
  (
    { spacing = 'md', children, className = '', ...props },
    ref
  ) => {
    const spacingClasses = {
      sm: 'space-y-2',
      md: 'space-y-4',
      lg: 'space-y-6',
    };

    return (
      <div
        ref={ref}
        className={`${spacingClasses[spacing]} ${className}`}
        {...props}
      >
        {children}
      </div>
    );
  }
);

FormGroup.displayName = 'FormGroup';
