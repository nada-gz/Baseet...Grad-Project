import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { register as registerAPI } from "../../api/auth";
import { useAuth } from "../../context/AuthContext";
import api from "../../api/axios";

export default function Register() {
  const navigate = useNavigate();
  const { login: loginContext } = useAuth();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState("checking");

  // Test backend connection on mount
  useEffect(() => {
    api.get('/')
      .then(() => setBackendStatus("connected"))
      .catch(() => setBackendStatus("disconnected"));
  }, []);

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (!username || !email || !password || !role) {
        setError("Please fill in all fields");
        setLoading(false);
        return;
      }

      const response = await registerAPI({ username, email, password, role });
      const userRole = response.user?.role || role;
      loginContext(response.access_token, response.user, userRole);
      navigate("/login");
    } catch (err) {
      let errorMessage = "Registration failed. Please check if backend is running and try again.";
      
      if (err.code === 'ERR_NETWORK' || err.message === 'Network Error') {
        errorMessage = "Cannot connect to backend server. Please make sure the backend is running on http://127.0.0.1:8000";
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      console.error("Registration error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <div className="form-inner card">
        <h2 className="card-title">Register</h2>

        {/* Backend Status
        <div className={`status ${
          backendStatus === "connected"
            ? "connected"
            : backendStatus === "disconnected"
            ? "disconnected"
            : "checking"
        }`}>
          {backendStatus === "connected" && "✓ Backend Connected"}
          {backendStatus === "disconnected" && "✗ Backend Disconnected"}
          {backendStatus === "checking" && "Checking backend..."}
        </div> */}

        {/* Error Message */}
        {error && <p className="error-message">{error}</p>}

        <form onSubmit={handleRegister} className="form">
          <label htmlFor="username">
            Username 
          </label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter your username"
            required
          />

          <label htmlFor="email">
            Email 
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email"
            required
          />

          <label htmlFor="password">
            Password 
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            required
          />

          <label htmlFor="role">
            Role 
          </label>
          <select
            id="role"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            required
          >
            <option value="">Select a role</option>
            <option value="student">Student</option>
            <option value="teacher">Teacher</option>
            <option value="parent">Parent</option>
            <option value="supervisor">Supervisor</option>
          </select>

          <button
            type="submit"
            className="btn btn-primary formButton"
            disabled={loading}
          >
            {loading ? "Registering..." : "Register"}
          </button>
        </form>

        <p className="text-center mt-4 text-sm">
          Already have an account? <a href="/login">Login</a>
        </p>
      </div>
    </div>
  );
}
