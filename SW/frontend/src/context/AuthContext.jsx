import { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/axios';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [role, setRole] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Initialize auth state from localStorage
  useEffect(() => {
    const token = localStorage.getItem('token');
    const storedRole = localStorage.getItem('role');
    
    if (token && storedRole) {
      setRole(storedRole);
      setIsAuthenticated(true);
      // Optionally fetch user data from backend
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, []);

  // Fetch current user from backend
  const fetchCurrentUser = async () => {
    try {
      const response = await api.get('/auth/me');
      setUser(response.data);
      setRole(response.data.role?.value || response.data.role || localStorage.getItem('role'));
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Error fetching current user:', error);
      // If token is invalid, clear auth state
      if (error.response?.status === 401) {
        logout();
      }
    } finally {
      setLoading(false);
    }
  };

  // Login function
  const login = (token, userData, userRole) => {
    localStorage.setItem('token', token);
    localStorage.setItem('role', userRole);
    setUser(userData);
    setRole(userRole);
    setIsAuthenticated(true);
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    setUser(null);
    setRole(null);
    setIsAuthenticated(false);
  };

  const value = {
    user,
    role,
    isAuthenticated,
    loading,
    login,
    logout,
    fetchCurrentUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

