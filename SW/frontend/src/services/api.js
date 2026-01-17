import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,// it was 'http://127.0.0.1:8000', i changed it for deployment 
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    if (error.code === 'ERR_NETWORK') {
      console.error("Network Error: Backend not reachable");
    }
    return Promise.reject(error);
  }
);

export const register = async (username, email, password, role) => {
  const response = await api.post('/auth/register', { username, email, password, role });
  const { access_token, user } = response.data;
  localStorage.setItem('token', access_token);
  localStorage.setItem('user', JSON.stringify(user));
  return response.data;
};

export const login = async (email, password) => {
  const response = await api.post('/auth/login', { email, password });
  const { access_token, user } = response.data;
  localStorage.setItem('token', access_token);
  localStorage.setItem('user', JSON.stringify(user));
  return response.data;
};

export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location.href = '/login';
};

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

export const testConnection = async () => {
  const response = await api.get('/');
  return response.data;
};

export const getUsers = async () => {
  const response = await api.get('/users/');
  return response.data;
};

export const getUserById = async (userId) => {
  const response = await api.get(`/users/${userId}`);
  return response.data;
};

export default api;
