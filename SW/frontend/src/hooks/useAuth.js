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
    localStorage.removeItem("student_id"); // remove student_id on logout
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

        // Backend returns `studentId` (camelCase) for students.
        // Normalize it to `student_id` and keep all original fields.
        const normalizedUser = {
          ...data,
          student_id: data?.student_id ?? data?.studentId ?? null,
        };

        // Save latest role + user info locally, fallback to "student"
        const role = normalizedUser?.role || "student";
        localStorage.setItem("role", role);

        // Save student_id if exists (from either `student_id` or `studentId`)
        if (normalizedUser.student_id) {
          localStorage.setItem("student_id", normalizedUser.student_id);
        }

        setUser(normalizedUser);
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
