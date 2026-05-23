import React from 'react';

export interface GridProps extends React.HTMLAttributes<HTMLDivElement> {
  cols?: 1 | 2 | 3 | 4 | 6;
  gap?: 'sm' | 'md' | 'lg';
}

export const Grid = React.forwardRef<HTMLDivElement, GridProps>(
  (
    {
      cols = 3,
      gap = 'md',
      children,
      className = '',
      ...props
    },
    ref
  ) => {
    const colClasses = {
      1: 'grid-cols-1',
      2: 'grid-cols-2',
      3: 'grid-cols-3',
      4: 'grid-cols-4',
      6: 'grid-cols-6',
    };

    const gapClasses = {
      sm: 'gap-2',
      md: 'gap-4',
      lg: 'gap-6',
    };

    return (
      <div
        ref={ref}
        className={`grid ${colClasses[cols]} ${gapClasses[gap]} ${className}`}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Grid.displayName = 'Grid';
