import axios from "axios";

const API_URL = import.meta.env?.REACT_APP_API_URL;

if (!API_URL) {
  console.error("❌ REACT_APP_API_URL is missing");
}
const api = axios.create({
  baseURL: API_URL || "",
});

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
    if (
  error.response?.status === 401 &&
  error.config?.url?.startsWith('/auth')
) {
  localStorage.removeItem('token');
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