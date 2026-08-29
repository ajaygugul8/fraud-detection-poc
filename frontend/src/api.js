import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'https://fraud-detection-poc1.onrender.com';

export const getTopFraudMerchants = () => axios.get(`${API_BASE}/top-fraud-merchants`);
export const getTopFraudCardholders = () => axios.get(`${API_BASE}/top-fraud-cardholders`);
export const getFraudByType = () => axios.get(`${API_BASE}/fraud-by-type`);
export const getHighValueTransactions = () => axios.get(`${API_BASE}/high-value-transactions`);
export const getMerchantRisk = () => axios.get(`${API_BASE}/merchant-risk`);
export const getStats = () => axios.get(`${API_BASE}/stats`);
export const getTransactionGraph = (txnId) => axios.get(`${API_BASE}/graph/transaction/${txnId}`);