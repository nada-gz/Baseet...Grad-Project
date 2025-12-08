import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { testConnection, login, getCurrentUser } from "../../services/api";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState("checking");

  // Test backend connection on mount
  useEffect(() => {
    testConnection()
      .then(() => setBackendStatus("connected"))
      .catch(() => setBackendStatus("disconnected"));
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      // Call actual login API
      const loginResponse = await login(email, password);
      
      // Store token
      localStorage.setItem("token", loginResponse.access_token);
      
      // Get user info to determine role
      try {
        const userResponse = await getCurrentUser();
        
        // Get role from backend response
        const userRole = userResponse.role || "student";
        
        // Store role in localStorage
        localStorage.setItem("role", userRole);
        
        // Navigate to dashboard based on role
        navigate(`/dashboard/${userRole}`);
      } catch (userErr) {
        // If we can't get user info, default to student
        const userRole = "student";
        localStorage.setItem("role", userRole);
        navigate(`/dashboard/${userRole}`);
      }
    } catch (err) {
      if (err.response?.status === 401) {
        setError("Invalid email or password. Please try again.");
      } else if (err.code === 'ERR_NETWORK' || err.message === 'Network Error') {
        setError("Failed to connect to server. Please check if backend is running.");
      } else {
        setError(err.response?.data?.detail || "Login failed. Please try again.");
      }
      console.error("Login error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
        <h1 className="text-2xl font-bold text-center mb-6">Login</h1>
        
        {/* Backend Status Indicator */}
        <div className={`mb-4 p-2 rounded text-center text-sm ${
          backendStatus === "connected" 
            ? "bg-green-100 text-green-700" 
            : backendStatus === "disconnected"
            ? "bg-red-100 text-red-700"
            : "bg-yellow-100 text-yellow-700"
        }`}>
          {backendStatus === "connected" && "✓ Backend Connected"}
          {backendStatus === "disconnected" && "✗ Backend Disconnected"}
          {backendStatus === "checking" && "Checking backend..."}
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your email"
              required
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your password"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-600">
          Don't have an account?{" "}
          <a href="/register" className="text-blue-600 hover:underline">
            Register
          </a>
        </p>
      </div>
    </div>
  );
}

