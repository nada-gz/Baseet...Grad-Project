import React from 'react';

/**
 * Reusable Card component for containers
 * @param {React.ReactNode} children - Card content
 * @param {string} className - Additional CSS classes
 * @param {string} title - Optional card title
 * @param {object} ...props - Other div props
 */
export default function Card({ children, className = '', title, ...props }) {
  return (
    <div
      className={`bg-white rounded-lg shadow-md p-8 ${className}`}
      {...props}
    >
      {title && (
        <h1 className="text-2xl font-bold text-center mb-6">{title}</h1>
      )}
      {children}
    </div>
  );
}

