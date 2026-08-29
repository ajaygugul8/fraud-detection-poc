import React from 'react';

const ErrorDisplay = ({ message }) => (
  <div className="text-center py-8">
    <div className="text-red-400 text-lg">⚠️ {message}</div>
    <button
      onClick={() => window.location.reload()}
      className="mt-4 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded text-white transition-colors"
    >
      Retry
    </button>
  </div>
);

export default ErrorDisplay;