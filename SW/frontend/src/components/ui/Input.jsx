import React from 'react';

/**
 * Reusable Input component
 * @param {string} label - Label text for the input
 * @param {string} id - Unique ID for the input (also used for htmlFor in label)
 * @param {string} type - Input type (text, email, password, etc.)
 * @param {string} value - Controlled input value
 * @param {function} onChange - Change handler function
 * @param {string} placeholder - Placeholder text
 * @param {boolean} required - Whether the input is required
 * @param {string} error - Error message to display
 * @param {string} className - Additional CSS classes
 * @param {object} ...props - Other input props (maxLength, disabled, etc.)
 */
export default function Input({
  label,
  id,
  type = 'text',
  value,
  onChange,
  placeholder,
  required = false,
  error,
  className = '',
  ...props
}) {
  return (
    <div>
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-gray-700 mb-1">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <input
        type={type}
        id={id}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 transition ${
          error
            ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
            : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
        } ${className}`}
        {...props}
      />
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
    </div>
  );
}

