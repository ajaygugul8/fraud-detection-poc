import axios from 'axios';

// Development: http://localhost:8000
// Production: Render URL (or fallback)
const getBaseURL = () => {
  if (import.meta.env.MODE === 'development') {
    return 'http://localhost:8000';
  }
  // Production: use environment variable or fallback
  return import.meta.env.VITE_API_URL || 'https://fraud-detection-poc1.onrender.com';
};

const API_BASE = getBaseURL();

export const getTopFraudMerchants = () => axios.get(`${API_BASE}/top-fraud-merchants`);
export const getTopFraudCardholders = () => axios.get(`${API_BASE}/top-fraud-cardholders`);
export const getFraudByType = () => axios.get(`${API_BASE}/fraud-by-type`);
export const getHighValueTransactions = () => axios.get(`${API_BASE}/high-value-transactions`);
export const getMerchantRisk = () => axios.get(`${API_BASE}/merchant-risk`);
export const getStats = () => axios.get(`${API_BASE}/stats`);
export const getTransactionGraph = (txnId) => axios.get(`${API_BASE}/graph/transaction/${txnId}`);