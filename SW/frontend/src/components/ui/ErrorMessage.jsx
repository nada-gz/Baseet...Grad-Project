import React from 'react';

export default function ErrorMessage({ message, className = '', ...props }) {
  if (!message) return null;

  return (
    <div className={className} role="alert" {...props}>
      {message}
    </div>
  );
}
