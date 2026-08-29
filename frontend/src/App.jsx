import React, { useState, useEffect } from 'react';
import {
  getTopFraudMerchants,
  getTopFraudCardholders,
  getFraudByType,
  getHighValueTransactions,
  getMerchantRisk,
  getStats,
} from './api';
import TopFraudMerchants from './components/TopFraudMerchants';
import TopFraudCardholders from './components/TopFraudCardholders';
import FraudByTypeChart from './components/FraudByTypeChart';
import HighValueTransactions from './components/HighValueTransactions';
import MerchantRisk from './components/MerchantRisk';
import GraphView from './components/GraphView';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorDisplay from './components/ErrorDisplay';

const cypherQueries = {
  merchants: `
MATCH (m:Merchant)<-[:AT_MERCHANT]-(t:Transaction)-[:HAS_FRAUD]->(f:FraudCase)
RETURN m.merchant_id AS merchant_id, 
       m.merchant_name AS merchant_name, 
       count(f) AS fraud_count
ORDER BY fraud_count DESC LIMIT 10
  `,
  cardholders: `
MATCH (ch:Cardholder)-[:OWNS]->(c:Card)-[:MADE]->(t:Transaction)-[:HAS_FRAUD]->(f:FraudCase)
RETURN ch.cardholder_id AS cardholder_id, count(f) AS fraud_count
ORDER BY fraud_count DESC LIMIT 10
  `,
  fraudTypes: `
MATCH (f:FraudCase)
RETURN f.fraudType AS fraud_type, count(f) AS count
ORDER BY count DESC
  `,
  highValue: `
MATCH (t:Transaction)
WHERE t.transaction_amount > 7000
RETURN t.transaction_id AS transaction_id, 
       t.transaction_amount AS transaction_amount, 
       toString(t.transaction_date) AS transaction_date
ORDER BY t.transaction_amount DESC LIMIT 20
  `,
  risk: `
MATCH (m:Merchant)
WHERE m.merchant_risk_band IN ['high', 'elevated']
RETURN m.merchant_id AS merchant_id, 
       m.merchant_name AS merchant_name, 
       m.merchant_risk_band AS merchant_risk_band, 
       m.chargeback_ratio AS chargeback_ratio
ORDER BY m.chargeback_ratio DESC LIMIT 10
  `,
};

const App = () => {
  const [activeTab, setActiveTab] = useState('merchants');
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);

  const tabs = [
    { id: 'merchants', label: '🏪 Top Merchants' },
    { id: 'cardholders', label: '👤 Top Cardholders' },
    { id: 'fraudTypes', label: '📊 Fraud Types' },
    { id: 'highValue', label: '💰 High-Value Txns' },
    { id: 'risk', label: '⚠️ Merchant Risk' },
    { id: 'graph', label: '📊 Graph View' },
  ];

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      setError(null);
      try {
        const [merchants, cardholders, fraudTypes, highValue, risk] = await Promise.all([
          getTopFraudMerchants(),
          getTopFraudCardholders(),
          getFraudByType(),
          getHighValueTransactions(),
          getMerchantRisk(),
        ]);
        setData({
          merchants: merchants.data,
          cardholders: cardholders.data,
          fraudTypes: fraudTypes.data,
          highValue: highValue.data,
          risk: risk.data,
        });
      } catch (err) {
        console.error('Fetch error:', err);
        setError(err.message || 'Failed to load data. Please try again.');
      }
      setLoading(false);
    };

    const fetchStats = async () => {
      try {
        const res = await getStats();
        setStats(res.data);
      } catch (e) {
        console.error('Stats fetch error:', e);
      }
    };

    fetchAll();
    fetchStats();
  }, []);

  const renderContent = () => {
    if (loading) return <LoadingSpinner />;
    if (error) return <ErrorDisplay message={error} />;
    switch (activeTab) {
      case 'merchants': return <TopFraudMerchants data={data.merchants || []} cypher={cypherQueries.merchants} />;
      case 'cardholders': return <TopFraudCardholders data={data.cardholders || []} cypher={cypherQueries.cardholders} />;
      case 'fraudTypes': return <FraudByTypeChart data={data.fraudTypes || []} cypher={cypherQueries.fraudTypes} />;
      case 'highValue': return <HighValueTransactions data={data.highValue || []} cypher={cypherQueries.highValue} />;
      case 'risk': return <MerchantRisk data={data.risk || []} cypher={cypherQueries.risk} />;
      case 'graph': return <GraphView />;
      default: return null;
    }
  };

  return (
    <div className="min-h-screen bg-[#0f0f1a] text-gray-200 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-purple-400 font-semibold">⚡ Powered by Neo4j</span>
            <span className="text-xs text-gray-500">|</span>
            {stats && <span className="text-xs text-gray-400">Nodes: {stats.nodes} • Relationships: {stats.relationships}</span>}
          </div>
          <h1 className="text-3xl font-bold text-purple-400">🛡️ Fraud Detection Dashboard</h1>
          <p className="text-gray-400 text-sm mt-1">Live data from Neo4j graph</p>
          <div className="text-xs text-gray-500 mt-2">
            <span>API: {import.meta.env.VITE_API_URL || 'fraud-detection-poc1.onrender.com'}</span>
          </div>
        </header>

        <div className="flex flex-wrap gap-2 mb-6 border-b border-gray-800 pb-2">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`px-4 py-2.5 rounded-t-lg transition-colors text-sm font-medium ${
                activeTab === tab.id
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700'
              }`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="bg-[#1a1a2e] rounded-xl p-4 md:p-6 shadow-2xl border border-gray-800 min-h-[400px]">
          {renderContent()}
        </div>

        <footer className="mt-8 text-center text-gray-600 text-xs">
          Built with Neo4j, FastAPI, React • Deployed on Render & Netlify
        </footer>
      </div>
    </div>
  );
};

export default App;