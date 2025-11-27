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
    const status = error.response?.status;

    if (status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }

    // Only log or alert for network errors or server errors (500+)
    if (!status || status >= 500) {
      console.error('API Error:', {
        url: error.config?.url,
        status: status,
        message: error.message,
      });
      alert('Server error or network issue occurred. Please try again.');
    }

    // Do not throw alert for 404 or client errors, just reject
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

export const register = async (username, email, password, role) => {
  const response = await api.post('/auth/register', {
    username,
    email,
    password,
    role,
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

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

export const getUserById = async (userId) => {
  try {
    const response = await api.get(`/users/${userId}`);
    return response.data;
  } catch (err) {
    // If 404, just return null instead of throwing
    if (err.response?.status === 404) {
      return null;
    }
    // Otherwise rethrow to let interceptor handle server/network errors
    throw err;
  }
};

export const getStudentById = async (studentId) => {
  try {
    const response = await api.get(`/students/${studentId}`);
    return response.data;
  } catch (err) {
    if (err.response?.status === 404) {
      return null; // student not found
    }
    throw err; // let interceptor handle other errors
  }
};

export default api;
