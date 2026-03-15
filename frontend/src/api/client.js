import axios from 'axios';

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: BASE });

// Attach JWT token automatically
api.interceptors.request.use((cfg) => {
  const token = localStorage.getItem('token');
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

// ── Auth ──────────────────────────────────────────────────
export const login = (email, password) =>
  api.post('/auth/login', { email, password });

export const register = (email, password, seller_name) =>
  api.post('/auth/register', { email, password, seller_name });

// ── Agents ────────────────────────────────────────────────
export const getHealth = () => api.get('/api/health');
export const getPricing = () => api.get('/api/pricing');
export const getSentiment = () => api.get('/api/sentiment');
export const getGaps = () => api.get('/api/gaps');
export const getCompetitors = () => api.get('/api/competitors');
export const getProduct = () => api.get('/api/product');

export const postStrategy = (seller_id = 'default_seller') =>
  api.post('/api/strategy', { seller_id });

export const postListingRewrite = (title, bullets, gaps) =>
  api.post('/api/listing/rewrite', { title, bullets, gaps });

export const postChat = (question) =>
  api.post('/api/chat', { question });

export default api;
