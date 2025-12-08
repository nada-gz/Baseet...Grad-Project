import api from './axios';

/**
 * Login user
 * @param {Object} data - Login credentials
 * @param {string} data.email - User email
 * @param {string} data.password - User password
 * @returns {Promise<Object>} Response with access_token and user data
 */
export const login = async (data) => {
  const response = await api.post('/auth/login', {
    email: data.email,
    password: data.password,
  });
  return response.data;
};

/**
 * Register new user
 * @param {Object} data - Registration data
 * @param {string} data.username - Username
 * @param {string} data.email - User email
 * @param {string} data.password - User password
 * @param {string} data.role - User role (student, teacher, parent, supervisor)
 * @returns {Promise<Object>} Response with access_token and user data
 */
export const register = async (data) => {
  const response = await api.post('/auth/register', {
    username: data.username,
    email: data.email,
    password: data.password,
    role: data.role,
  });
  return response.data;
};

