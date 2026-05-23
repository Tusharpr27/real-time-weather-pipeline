import React from 'react';

export interface PageContainerProps
  extends React.HTMLAttributes<HTMLDivElement> {
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  padding?: 'sm' | 'md' | 'lg';
}

export const PageContainer = React.forwardRef<
  HTMLDivElement,
  PageContainerProps
>(
  (
    {
      maxWidth = 'xl',
      padding = 'md',
      children,
      className = '',
      ...props
    },
    ref
  ) => {
    const maxWidthClasses = {
      sm: 'max-w-sm',
      md: 'max-w-md',
      lg: 'max-w-lg',
      xl: 'max-w-6xl',
      '2xl': 'max-w-7xl',
    };

    const paddingClasses = {
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-8',
    };

    return (
      <div
        ref={ref}
        className={`mx-auto ${maxWidthClasses[maxWidth]} ${paddingClasses[padding]} ${className}`}
        {...props}
      >
        {children}
      </div>
    );
  }
);

PageContainer.displayName = 'PageContainer';
