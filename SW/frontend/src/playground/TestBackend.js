import { useState, useEffect } from 'react';

export default function TestBackend() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetch('http://127.0.0.1:8000/')
      .then(res => res.json())
      .then(data => setMessage(data.message))
      .catch(err => console.error('Error fetching:', err));
  }, []);

  return (
    <div className="mt-4 p-4 bg-white rounded shadow text-center">
      <h1 className="text-lg font-semibold text-gray-800">
        {message || 'Loading...'}
      </h1>
    </div>
  );
}
