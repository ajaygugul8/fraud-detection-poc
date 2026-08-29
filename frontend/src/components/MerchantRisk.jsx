import React, { useState } from 'react';

const MerchantRisk = ({ data, cypher }) => {
  const [showCypher, setShowCypher] = useState(false);

  if (!data || data.length === 0) {
    return <div className="text-gray-400 text-center py-8">No data available</div>;
  }

  const getRiskColor = (band) => {
    const colors = {
      high: 'bg-red-600',
      elevated: 'bg-orange-600',
      moderate: 'bg-yellow-600',
      low: 'bg-green-600',
    };
    return colors[band?.toLowerCase()] || 'bg-gray-600';
  };

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
              <th className="px-4 py-3">Merchant Name</th>
              <th className="px-4 py-3">Risk Band</th>
              <th className="px-4 py-3 text-right">Chargeback Ratio</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, idx) => (
              <tr key={idx} className="border-b border-gray-700 hover:bg-gray-800 transition-colors">
                <td className="px-4 py-3 text-gray-500">{idx + 1}</td>
                <td className="px-4 py-3">{item.merchant_name}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded text-xs font-semibold text-white ${getRiskColor(item.merchant_risk_band)}`}>
                    {item.merchant_risk_band || 'Unknown'}
                  </span>
                </td>
                <td className="px-4 py-3 text-right font-mono">
                  {(Number(item.chargeback_ratio) * 100).toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default MerchantRisk;