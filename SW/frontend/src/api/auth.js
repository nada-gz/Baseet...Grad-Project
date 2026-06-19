import api from './axios';

/**
 * Login user
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

/**
 * Request a password reset email
 * @param {string} email
 */
export const forgotPassword = async (email) => {
  const response = await api.post('/auth/forgot-password', { email });
  return response.data;
};

/**
 * Verify that a reset token is valid and not expired
 * @param {string} token
 */
export const verifyResetToken = async (token) => {
  const response = await api.post('/auth/verify-reset-token', { token });
  return response.data;
};

/**
 * Set a new password using a valid reset token
 * @param {string} token
 * @param {string} newPassword
 */
export const resetPassword = async (token, newPassword) => {
  const response = await api.post('/auth/reset-password', {
    token,
    new_password: newPassword,
  });
  return response.data;
};
