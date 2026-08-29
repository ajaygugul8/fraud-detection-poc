import React, { useState } from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const FraudByTypeChart = ({ data, cypher }) => {
  const [showCypher, setShowCypher] = useState(false);

  if (!data || data.length === 0) {
    return <div className="text-gray-400 text-center py-8">No data available</div>;
  }

  const labels = data.map(item => item.fraud_type || 'Unknown');
  const counts = data.map(item => item.count);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Fraud Cases',
        data: counts,
        backgroundColor: 'rgba(168, 85, 247, 0.7)',
        borderColor: 'rgba(168, 85, 247, 1)',
        borderWidth: 2,
        borderRadius: 6,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: '#cccccc', font: { size: 14 } } },
      title: {
        display: true,
        text: 'Fraud Cases by Type',
        color: '#cccccc',
        font: { size: 18, weight: 'bold' },
      },
    },
    scales: {
      x: {
        ticks: { color: '#aaaaaa' },
        grid: { color: 'rgba(255,255,255,0.05)' },
      },
      y: {
        ticks: { color: '#aaaaaa' },
        grid: { color: 'rgba(255,255,255,0.05)' },
        beginAtZero: true,
      },
    },
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
      <div className="h-80 w-full"><Bar data={chartData} options={options} /></div>
    </div>
  );
};

export default FraudByTypeChart;