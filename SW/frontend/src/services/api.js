import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to every request
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

// Global response error handler
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid → logout
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      window.location.href = '/login';
    }

    if (error.code === 'ERR_NETWORK') {
      console.error("Network Error: Backend not reachable");
    }

    return Promise.reject(error);
  }
);

// =======================
// AUTH
// =======================

export const register = async (username, email, password, role) => {
  const response = await api.post('/auth/register', {
    username,
    email,
    password,
    role,
  });

  localStorage.setItem('token', response.data.access_token);
  localStorage.setItem('role', response.data.role); // only role

  return response.data;
};

export const login = async (email, password) => {
  const response = await api.post('/auth/login', {
    email,
    password,
  });

  localStorage.setItem('token', response.data.access_token);
  localStorage.setItem('role', response.data.role); // only role

  return response.data;
};

export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('role');
  window.location.href = '/login';
};

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

// =======================
// SYSTEM CHECK / TEST
// =======================

export const testConnection = async () => {
  const response = await api.get('/');
  return response.data;
};

export default api;
