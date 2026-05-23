import React from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined';
  padding?: 'sm' | 'md' | 'lg';
  hoverable?: boolean;
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  (
    {
      variant = 'default',
      padding = 'md',
      hoverable = false,
      children,
      className = '',
      ...props
    },
    ref
  ) => {
    const variantClasses = {
      default: 'bg-white border border-gray-200',
      elevated: 'bg-white shadow-lg',
      outlined: 'bg-transparent border-2 border-gray-300',
    };

    const paddingClasses = {
      sm: 'p-2',
      md: 'p-4',
      lg: 'p-6',
    };

    const hoverClass = hoverable
      ? 'transition-all duration-200 hover:shadow-lg hover:-translate-y-1 cursor-pointer'
      : '';

    return (
      <div
        ref={ref}
        className={`rounded-lg ${variantClasses[variant]} ${paddingClasses[padding]} ${hoverClass} ${className}`}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';
