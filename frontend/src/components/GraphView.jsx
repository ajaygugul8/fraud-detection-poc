import React, { useState, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { getTransactionGraph } from '../api';

// Neo4j-inspired colors
const NODE_COLORS = {
  Transaction: '#FBBF24', // yellow
  Card: '#34D399',       // green
  Cardholder: '#60A5FA', // blue
  Merchant: '#F472B6',   // pink
  FraudCase: '#F87171',  // red
};

const NODE_LABELS = {
  Transaction: 'Transaction',
  Card: 'Card',
  Cardholder: 'Cardholder',
  Merchant: 'Merchant',
  FraudCase: 'Fraud Case',
};

const GraphView = () => {
  const [txnId, setTxnId] = useState('');
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [highlightedId, setHighlightedId] = useState(null);
  const fgRef = useRef();

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
        // Auto-fit after render
        setTimeout(() => {
          if (fgRef.current) {
            fgRef.current.zoomToFit(400, 50);
          }
        }, 200);
      }
    } catch (e) {
      setError('Error fetching graph');
    }
    setLoading(false);
  };

  const handleNodeClick = (node) => {
    setHighlightedId(node.id === highlightedId ? null : node.id);
  };

  // Custom node renderer with clean labels
  const nodeCanvasObject = (node, ctx, globalScale) => {
    const label = node.display_name || node.id;
    const fontSize = Math.min(12, 14 / globalScale);
    const radius = Math.max(8, 12 / globalScale);

    // Dim non-highlighted nodes
    const isHighlighted = !highlightedId || node.id === highlightedId;
    const isConnected = highlightedId && graphData.links.some(
      l => (l.source === node.id && l.target === highlightedId) ||
           (l.source === highlightedId && l.target === node.id)
    );
    const alpha = !highlightedId ? 1 : (isHighlighted || isConnected ? 1 : 0.2);

    ctx.globalAlpha = alpha;

    // Draw circle
    ctx.beginPath();
    ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI);
    ctx.fillStyle = node.color || '#888';
    ctx.fill();
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Draw label
    ctx.fillStyle = '#fff';
    ctx.font = `${fontSize}px Inter, sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, node.x, node.y);

    ctx.globalAlpha = 1;
  };

  // Prepare graph data with colors and display names
  const enhancedGraph = {
    nodes: graphData.nodes.map((node) => ({
      ...node,
      color: NODE_COLORS[node.label] || '#888',
      label: node.display_name || node.id,
    })),
    links: graphData.links.map((link) => ({
      ...link,
      color: '#9ca3af',
    })),
  };

  return (
    <div className="space-y-3">
      {/* Search */}
      <div className="flex flex-col sm:flex-row gap-2">
        <input
          type="number"
          placeholder="Enter Transaction ID (e.g., 1417)"
          value={txnId}
          onChange={(e) => setTxnId(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          className="flex-1 p-2 bg-gray-800 border border-gray-700 rounded text-white placeholder-gray-500"
        />
        <button
          onClick={handleSearch}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded text-white transition-colors"
        >
          Show Graph
        </button>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 text-xs">
        {Object.entries(NODE_COLORS).map(([label, color]) => (
          <div key={label} className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
            <span className="text-gray-300">{NODE_LABELS[label]}</span>
          </div>
        ))}
      </div>

      {/* Graph Canvas */}
      {loading && <div className="text-center text-gray-400 py-12">Loading graph...</div>}
      {error && <div className="text-red-400 text-center py-12">{error}</div>}

      {enhancedGraph.nodes.length > 0 && (
        <div className="border border-gray-700 rounded bg-[#111827] overflow-hidden relative">
          <ForceGraph2D
            ref={fgRef}
            graphData={enhancedGraph}
            nodeCanvasObject={nodeCanvasObject}
            linkColor={() => '#9ca3af'}
            linkWidth={2}
            linkDirectionalParticles={2}
            linkDirectionalParticleSpeed={0.003}
            linkLabel={(link) => link.type}
            nodeRelSize={4}
            cooldownTicks={80}
            onNodeClick={handleNodeClick}
            backgroundColor="#111827"
            width={800}
            height={500}
          />
          <div className="absolute bottom-2 right-2 flex gap-2">
            <button
              onClick={() => fgRef.current.zoomToFit(400, 50)}
              className="px-3 py-1 bg-gray-800/80 hover:bg-gray-700 text-gray-300 text-xs rounded border border-gray-700 transition-colors"
            >
              Re-center
            </button>
          </div>
        </div>
      )}

      {enhancedGraph.nodes.length === 0 && !loading && !error && (
        <div className="text-center text-gray-500 py-12 border border-gray-800 rounded bg-gray-900/50">
          <div className="text-4xl mb-2">🔍</div>
          <div>Enter a transaction ID and click "Show Graph"</div>
          <div className="text-xs text-gray-600 mt-1">e.g., 1417</div>
        </div>
      )}

      {enhancedGraph.nodes.length > 0 && (
        <div className="text-xs text-gray-500 text-center">
          Click a node to highlight connections • Drag to pan • Scroll to zoom
        </div>
      )}
    </div>
  );
};

export default GraphView;
