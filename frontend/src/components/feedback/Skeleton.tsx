import React from 'react';

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  count?: number;
  height?: 'sm' | 'md' | 'lg';
  variant?: 'text' | 'circle' | 'rect';
}

export const Skeleton: React.FC<SkeletonProps> = ({
  count = 1,
  height = 'md',
  variant = 'rect',
  className = '',
  ...props
}) => {
  const heightClasses = {
    sm: 'h-3',
    md: 'h-4',
    lg: 'h-6',
  };

  const variantClasses = {
    text: `${heightClasses[height]} rounded`,
    circle: 'h-10 w-10 rounded-full',
    rect: `${heightClasses[height]} rounded-lg`,
  };

  const items = Array.from({ length: count });

  return (
    <>
      {items.map((_, i) => (
        <div
          key={i}
          className={`${variantClasses[variant]} bg-gray-200 animate-pulse mb-2 ${className}`}
          {...props}
        />
      ))}
    </>
  );
};

Skeleton.displayName = 'Skeleton';
