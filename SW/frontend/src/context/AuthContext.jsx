import { createContext, useContext, useState, useEffect, useCallback } from 'react';
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
  const [studentId, setStudentId] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Logout function
  const logout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('user');
    localStorage.removeItem('studentId');
    setUser(null);
    setRole(null);
    setStudentId(null);
    setIsAuthenticated(false);
  }, []);

  // Fetch current user from backend
  const fetchCurrentUser = useCallback(async () => {
    try {
      const response = await api.get('/auth/me');
      const userData = response.data;
      const userRole = userData.role?.value || userData.role || localStorage.getItem('role');
      const userStudentId = userData.studentId || null;
      
      // Update localStorage to keep it in sync
      localStorage.setItem('user', JSON.stringify(userData));
      if (userRole) {
        localStorage.setItem('role', userRole);
      }
      if (userStudentId) {
        localStorage.setItem('studentId', userStudentId.toString());
        setStudentId(userStudentId);
      } else {
        localStorage.removeItem('studentId');
        setStudentId(null);
      }
      
      setUser(userData);
      setRole(userRole);
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
  }, [logout]);

  // Initialize auth state from localStorage
  useEffect(() => {
    const token = localStorage.getItem('token');
    const storedRole = localStorage.getItem('role');
    const storedStudentId = localStorage.getItem('studentId');
    
    if (token && storedRole) {
      setRole(storedRole);
      setIsAuthenticated(true);
      if (storedStudentId) {
        setStudentId(parseInt(storedStudentId));
      }
      // Optionally fetch user data from backend
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, [fetchCurrentUser]);

  // Login function
  const login = (token, userData, userRole) => {
    localStorage.setItem('token', token);
    localStorage.setItem('role', userRole);
    localStorage.setItem('user', JSON.stringify(userData));
    
    // Store studentId if available
    const userStudentId = userData.studentId || null;
    if (userStudentId) {
      localStorage.setItem('studentId', userStudentId.toString());
      setStudentId(userStudentId);
    } else {
      localStorage.removeItem('studentId');
      setStudentId(null);
    }
    
    setUser(userData);
    setRole(userRole);
    setIsAuthenticated(true);
  };

  const value = {
    user,
    role,
    studentId,
    isAuthenticated,
    loading,
    login,
    logout,
    fetchCurrentUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

