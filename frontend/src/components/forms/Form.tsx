import React from 'react';

export interface FormProps extends React.FormHTMLAttributes<HTMLFormElement> {
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
}

export const Form = React.forwardRef<HTMLFormElement, FormProps>(
  (
    { children, onSubmit, className = '', ...props },
    ref
  ) => {
    return (
      <form
        ref={ref}
        onSubmit={onSubmit}
        className={`space-y-6 ${className}`}
        {...props}
      >
        {children}
      </form>
    );
  }
);

Form.displayName = 'Form';
