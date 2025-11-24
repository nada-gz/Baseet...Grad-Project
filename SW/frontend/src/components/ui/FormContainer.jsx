import React from 'react';

/**
 * Reusable FormContainer component that centers forms
 * @param {React.ReactNode} children - Form content
 * @param {string} className - Additional CSS classes
 * @param {string} maxWidth - Maximum width class (max-w-sm, max-w-md, max-w-lg, etc.)
 */
export default function FormContainer({
  children,
  className = '',
  maxWidth = 'max-w-md',
}) {
  return (
    <div className={`min-h-screen flex items-center justify-center bg-gray-100 ${className}`}>
      <div className={`${maxWidth} w-full px-4`}>
        {children}
      </div>
    </div>
  );
}

