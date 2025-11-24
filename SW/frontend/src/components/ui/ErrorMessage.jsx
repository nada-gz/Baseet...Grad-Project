import React from 'react';

/**
 * Reusable ErrorMessage component
 * @param {string} message - Error message to display
 * @param {string} variant - Error variant (error, warning, info)
 * @param {string} className - Additional CSS classes
 * @param {boolean} dismissible - Whether the error can be dismissed
 * @param {function} onDismiss - Dismiss handler function
 */
export default function ErrorMessage({
  message,
  variant = 'error',
  className = '',
  dismissible = false,
  onDismiss,
}) {
  if (!message) return null;

  const variantStyles = {
    error: 'bg-red-100 text-red-700 border-red-300',
    warning: 'bg-yellow-100 text-yellow-700 border-yellow-300',
    info: 'bg-blue-100 text-blue-700 border-blue-300',
  };

  return (
    <div
      className={`mb-4 p-3 rounded text-sm border ${variantStyles[variant]} ${className}`}
      role="alert"
    >
      <div className="flex items-center justify-between">
        <span>{message}</span>
        {dismissible && onDismiss && (
          <button
            onClick={onDismiss}
            className="ml-4 text-current opacity-70 hover:opacity-100 focus:outline-none"
            aria-label="Dismiss"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}

