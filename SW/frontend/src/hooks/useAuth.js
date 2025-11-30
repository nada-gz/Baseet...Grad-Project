import { useState, useEffect } from "react";
import { getCurrentUser } from "../services/api";

const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Optional: provide logout function
  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    setUser(null);
    setError(null);
    window.location.href = "/login";
  };

  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem("token");
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const data = await getCurrentUser();

        // Save latest role + user info locally, fallback to "student"
        const role = data?.role || "student";
        localStorage.setItem("role", role);

        setUser(data);
      } catch (err) {
        // Invalid token → logout
        logout();
        setError(err?.response?.data?.detail || err.message || "Failed to fetch user");
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  return { user, loading, error, logout };
};

export default useAuth;
