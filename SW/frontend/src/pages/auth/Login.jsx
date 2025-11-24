import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { testConnection, login } from "../../services/api";
import { FormContainer, Card, ErrorMessage, Input, Button } from "../../components/ui";

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
    // Don't clear error here - let it persist until user types or login succeeds
    setLoading(true);

    try {
      // Validate form
      if (!email || !password) {
        setError("Please enter both email and password");
        setLoading(false);
        return;
      }

      // Call login API
      const response = await login(email, password);
      
      // Clear error only on successful login
      setError("");
      
      // Store token
      localStorage.setItem("token", response.access_token);
      
      // Store role (default to "student" if not provided for backward compatibility)
      const role = response.role || localStorage.getItem("role") || "student";
      localStorage.setItem("role", role);
      
      // Navigate to dashboard based on role
      navigate(`/dashboard/${role}`);
    } catch (err) {
      // Handle authentication errors - show error message, don't redirect
      let errorMessage = "Login failed. Please check your credentials and try again.";
      
      if (err.code === 'ERR_NETWORK' || err.message === 'Network Error') {
        errorMessage = "Cannot connect to backend server. Please make sure the backend is running on http://127.0.0.1:8000";
      } else if (err.response?.status === 401) {
        errorMessage = err.response?.data?.detail || "Invalid email or password. Please try again.";
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      console.error("Login error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Don't clear error when typing - let it persist until successful login
  const handleEmailChange = (e) => {
    setEmail(e.target.value);
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };

  return (
    <FormContainer>
      <Card title="Login">
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

        <ErrorMessage message={error} variant="error" />

        <form onSubmit={handleLogin} className="space-y-4">
          <Input
            label="Email"
            id="email"
            type="email"
            value={email}
            onChange={handleEmailChange}
            placeholder="Enter your email"
            required
          />
          <Input
            label="Password"
            id="password"
            type="password"
            value={password}
            onChange={handlePasswordChange}
            placeholder="Enter your password"
            required
          />
          <Button
            type="submit"
            variant="primary"
            disabled={loading}
            loading={loading}
            className="w-full"
          >
            Login
          </Button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-600">
          Don't have an account?{" "}
          <a href="/register" className="text-blue-600 hover:underline">
            Register
          </a>
        </p>
      </Card>
    </FormContainer>
  );
}

