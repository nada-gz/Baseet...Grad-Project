import api from '../api/axios.js';

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
