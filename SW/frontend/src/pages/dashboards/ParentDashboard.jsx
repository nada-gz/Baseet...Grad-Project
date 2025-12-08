import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import useAuth from "../../hooks/useAuth";
import api from "../../services/api";

export default function ParentDashboard() {
  const { user, loading, error } = useAuth();
  const [students, setStudents] = useState([]);
  const [fetchError, setFetchError] = useState("");

  useEffect(() => {
    const loadStudents = async () => {
      try {
        const response = await api.get("/users"); // make sure backend /users endpoint exists
        const allUsers = response.data;
        const studentUsers = allUsers.filter(
          (u) => u.role.toLowerCase() === "student"
        );
        setStudents(studentUsers);
      } catch (err) {
        console.error("Error fetching users:", err);
        setFetchError("Failed to load students. Please try again later.");
      }
    };

    loadStudents();
  }, []);

  if (loading) return <p className="p-6">Loading...</p>;
  if (error) return <p className="p-6 text-red-600">Error loading user.</p>;
  if (fetchError) return <p className="p-6 text-red-600">{fetchError}</p>;

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-4">Parent Dashboard</h1>

      <div className="bg-white rounded-lg shadow-md p-6 mb-4">
        <h2 className="text-xl font-semibold mb-2">
          Welcome, {user?.username}
        </h2>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Students</h2>

        <Link
          to="/students"
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          View All Students
        </Link>
      </div>
    </div>
  );
}
