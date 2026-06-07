import axios from 'axios';
import { API_BASE_URL } from '../config';

// Base URL comes from src/config.js — change it there when deploying
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auto-attach Authorization header with Bearer token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      window.location.href = '/login';
    }

    if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
      console.error('Network Error - Backend may not be running or CORS issue:', {
        url: error.config?.url,
        baseURL: error.config?.baseURL,
      });
    }

    return Promise.reject(error);
  }
);

export default api;
