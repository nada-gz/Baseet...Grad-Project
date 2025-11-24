import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Don't redirect on 401 for login/register endpoints - let them handle the error
    const isAuthEndpoint = error.config?.url?.includes('/auth/login') || 
                          error.config?.url?.includes('/auth/register');
    
    if (error.response?.status === 401 && !isAuthEndpoint) {
      // Unauthorized on protected routes - clear token and redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      window.location.href = '/login';
    }
    
    // Better error handling for network errors
    if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
      console.error('Network Error - Backend may not be running:', {
        url: error.config?.url,
        baseURL: error.config?.baseURL,
        message: 'Make sure the backend server is running on http://127.0.0.1:8000'
      });
    }
    
    return Promise.reject(error);
  }
);

// API functions
export const testConnection = async () => {
  const response = await api.get('/');
  return response.data;
};

export const getUsers = async () => {
  const response = await api.get('/users/');
  return response.data;
};

export const createUser = async (username, email, role) => {
  const response = await api.post('/users/', null, {
    params: { username, email, role },
  });
  return response.data;
};

export const register = async (username, email, password) => {
  const response = await api.post('/auth/register', {
    username,
    email,
    password,
  });
  return response.data;
};

export const login = async (email, password) => {
  const response = await api.post('/auth/login', {
    email,
    password,
  });
  return response.data;
};

export const getUserById = async (userId) => {
  const response = await api.get(`/users/${userId}`);
  return response.data;
};

export default api;

