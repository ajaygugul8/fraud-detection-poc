import React, { useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { getTransactionGraph } from '../api';

const GraphView = () => {
  const [txnId, setTxnId] = useState('');
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (!txnId) return;
    setLoading(true);
    setError('');
    try {
      const res = await getTransactionGraph(txnId);
      if (res.data.nodes.length === 0) {
        setError('Transaction not found');
        setGraphData({ nodes: [], links: [] });
      } else {
        setGraphData(res.data);
      }
    } catch (e) {
      setError('Error fetching graph');
    }
    setLoading(false);
  };

  return (
    <div>
      <div className="flex gap-2 mb-4">
        <input
          type="number"
          placeholder="Enter Transaction ID"
          value={txnId}
          onChange={(e) => setTxnId(e.target.value)}
          className="flex-1 p-2 bg-gray-800 border border-gray-700 rounded text-white"
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button
          onClick={handleSearch}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded text-white"
        >
          Show Graph
        </button>
      </div>

      {loading && <div className="text-center text-gray-400">Loading graph...</div>}
      {error && <div className="text-red-400 text-center">{error}</div>}

      {graphData.nodes.length > 0 && (
        <div className="h-96 border border-gray-700 rounded">
          <ForceGraph2D
            graphData={graphData}
            nodeLabel="label"
            nodeColor={(node) => {
              const colors = {
                Transaction: '#60a5fa',
                Card: '#34d399',
                Cardholder: '#fbbf24',
                Merchant: '#f472b6',
                FraudCase: '#f87171',
              };
              return colors[node.label] || '#9ca3af';
            }}
            linkLabel={(link) => link.type}
            linkColor={() => '#9ca3af'}
          />
        </div>
      )}
      {graphData.nodes.length === 0 && !loading && !error && (
        <div className="text-center text-gray-500 py-12">
          Enter a transaction ID and click "Show Graph" to see the network.
        </div>
      )}
    </div>
  );
};

export default GraphView;
