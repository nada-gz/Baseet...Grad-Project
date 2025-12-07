import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { login as loginAPI } from "../../api/auth";
import { useAuth } from "../../context/AuthContext";
import api from "../../api/axios";

export default function Login() {
  const navigate = useNavigate();
  const { login: loginContext } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState("checking");

  useEffect(() => {
    api.get('/')
      .then(() => setBackendStatus("connected"))
      .catch(() => setBackendStatus("disconnected"));
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    if (!email || !password) {
      setError("Please enter both email and password");
      setLoading(false);
      return;
    }

    try {
      const response = await loginAPI({ email, password });
      const role = response.user?.role || "student";
      loginContext(response.access_token, response.user, role);
      navigate(`/dashboard/${role}`);
    } catch (err) {
      let errorMessage = "Login failed. Please check your credentials and try again.";

      if (err.code === 'ERR_NETWORK') {
        errorMessage = "Cannot connect to backend. Make sure the server is running.";
      } else if (err.response?.status === 401) {
        errorMessage = "Invalid email or password.";
      }

      setError(errorMessage);
      console.error("Login error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <div className="form-inner card">
        <h2 className="card-title">Login</h2>

        {/* Backend Status
        {backendStatus !== "checking" && (
          <div
            className={`status ${
              backendStatus === "connected"
                ? "connected"
                : "disconnected"
            }`}
          >
            {backendStatus === "connected" ? "✓ Backend Connected" : "✗ Backend Disconnected"}
          </div>
        )} */}

        {/* Error Message */}
        {error && <p className="error-message">{error}</p>}

        {/* Login Form */}
        <form onSubmit={handleLogin} className="form">
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

          <button
            type="submit"
            className="btn btn-primary formButton"
            disabled={loading}
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        {/* Register Link */}
        <p className="text-center mt-6 text-sm">
          Don't have an account?{" "}
          <a href="/register">Register</a>
        </p>
      </div>
    </div>
  );
}
