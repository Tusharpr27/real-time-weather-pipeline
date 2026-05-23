import React from 'react'

export interface ToggleProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  description?: string
}

export const Toggle = React.forwardRef<HTMLInputElement, ToggleProps>(
  ({ label, description, className = '', ...props }, ref) => {
    return (
      <div className="flex items-center gap-3">
        <label className="flex items-center cursor-pointer">
          <input
            ref={ref}
            type="checkbox"
            className="w-5 h-5 rounded bg-gray-200 border border-gray-300 cursor-pointer accent-blue-600"
            {...props}
          />
          {label && (
            <span className="ml-2 text-sm font-medium text-gray-700">
              {label}
            </span>
          )}
        </label>
        {description && (
          <span className="text-sm text-gray-500">{description}</span>
        )}
      </div>
    )
  }
)

Toggle.displayName = 'Toggle'
