import { useState, useEffect } from "react";
import { testConnection, getUsers } from "../../services/api";

export default function StudentDashboard() {
  const [backendStatus, setBackendStatus] = useState("checking");
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Test backend connection
    testConnection()
      .then(() => {
        setBackendStatus("connected");
        // Load users as a test
        loadUsers();
      })
      .catch(() => setBackendStatus("disconnected"));
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await getUsers();
      setUsers(data);
    } catch (err) {
      console.error("Error loading users:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-4">Student Dashboard</h1>
      
      {/* Backend Status */}
      <div className={`mb-4 p-3 rounded ${
        backendStatus === "connected" 
          ? "bg-green-100 text-green-700" 
          : "bg-red-100 text-red-700"
      }`}>
        {backendStatus === "connected" ? "✓ Backend Connected" : "✗ Backend Disconnected"}
      </div>

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
              {users.map((user) => (
                <li key={user.id}>
                  {user.username} ({user.email})
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-gray-700">Student Dashboard Content</p>
      </div>
    </div>
  );
}

