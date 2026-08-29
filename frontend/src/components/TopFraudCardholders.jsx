import React, { useState } from 'react';

const TopFraudCardholders = ({ data, cypher }) => {
  const [showCypher, setShowCypher] = useState(false);

  if (!data || data.length === 0) {
    return <div className="text-gray-400 text-center py-8">No data available</div>;
  }
  return (
    <div>
      <button
        onClick={() => setShowCypher(!showCypher)}
        className="text-xs text-purple-400 hover:underline mb-2"
      >
        {showCypher ? 'Hide Cypher' : 'Show Cypher'}
      </button>
      {showCypher && (
        <pre className="bg-gray-900 p-3 rounded text-xs text-green-400 overflow-x-auto border border-gray-700 mb-4">
          {cypher}
        </pre>
      )}
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="text-xs uppercase bg-gray-800 text-gray-300">
            <tr>
              <th className="px-4 py-3">#</th>
              <th className="px-4 py-3">Cardholder ID</th>
              <th className="px-4 py-3 text-right">Fraud Count</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, idx) => (
              <tr key={idx} className="border-b border-gray-700 hover:bg-gray-800 transition-colors">
                <td className="px-4 py-3 text-gray-500">{idx + 1}</td>
                <td className="px-4 py-3 font-mono text-xs">{item.cardholder_id}</td>
                <td className="px-4 py-3 text-right font-bold text-red-400">{item.fraud_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TopFraudCardholders;