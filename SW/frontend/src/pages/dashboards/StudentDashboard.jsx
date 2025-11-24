import { useState, useEffect } from "react";
import { testConnection, getUsers } from "../../services/api";
import useAuth from "../../hooks/useAuth";
import { Link } from "react-router-dom";

export default function StudentDashboard() {
  const { user, loading: authLoading, error: authError } = useAuth();

  const [backendStatus, setBackendStatus] = useState("checking");
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    testConnection()
      .then(() => {
        setBackendStatus("connected");
        loadUsers();
      })
      .catch(() => setBackendStatus("disconnected"));
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await getUsers();
      setUsers(data);
    } finally {
      setLoading(false);
    }
  };

  if (authLoading) return <p className="p-6">Loading...</p>;
  if (authError) return <p className="p-6 text-red-600">Error loading user.</p>;

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-4">Student Dashboard</h1>

      {/* Welcome box */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-4">
        <h2 className="text-xl font-semibold mb-2">
          Welcome, {user?.username}
        </h2>
        <p className="text-gray-700">
          This is your Student Dashboard.
        </p>
      </div>

      {/* Backend status */}
      <div
        className={`mb-4 p-3 rounded ${
          backendStatus === "connected"
            ? "bg-green-100 text-green-700"
            : "bg-red-100 text-red-700"
        }`}
      >
        {backendStatus === "connected"
          ? "✓ Backend Connected"
          : "✗ Backend Disconnected"}
      </div>

      {/* Load users test */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-4">
        <h2 className="text-xl font-semibold mb-4">Backend Connection Test</h2>

        <button
          onClick={loadUsers}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Loading..." : "Load Users from Backend"}
        </button>

        {users.length > 0 && (
          <div className="mt-4">
            <h3 className="font-semibold mb-2">Users from Database:</h3>
            <ul className="list-disc list-inside space-y-1">
              {users.map((u) => (
                <li key={u.id}>
                  {u.username} ({u.email})
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* 🚀 NEW: Button to go to my profile */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">My Profile</h2>

        <Link
          to={`/profile/${user?.id}`}
          className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
        >
          Go to My Profile
        </Link>
      </div>
    </div>
  );
}
