import React from 'react';

export default function Card({ children, className = '', title, ...props }) {
  return (
    <div className={className} {...props}>
      {title && <h1>{title}</h1>}
      {children}
    </div>
  );
}
