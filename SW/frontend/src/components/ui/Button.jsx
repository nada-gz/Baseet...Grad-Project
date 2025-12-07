import React from 'react';

export default function Button({
  type = 'button',
  disabled = false,
  loading = false,
  className = '',
  children,
  onClick,
  ...props
}) {
  return (
    <button
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      className={className}
      {...props}
    >
      {loading ? 'Loading...' : children}
    </button>
  );
}
