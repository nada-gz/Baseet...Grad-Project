import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { testConnection, register } from "../../services/api";
import { FormContainer, Card, ErrorMessage, Input, Button } from "../../components/ui";

export default function Register() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState("checking");

  // Test backend connection on mount
  useEffect(() => {
    testConnection()
      .then(() => setBackendStatus("connected"))
      .catch(() => setBackendStatus("disconnected"));
  }, []);

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      // Validate form
      if (!username || !email || !password || !role) {
        setError("Please fill in all fields");
        setLoading(false);
        return;
      }

      // Register user with backend (role will be added to backend later)
      await register(username, email, password);
      
      // Store role in localStorage for now (until backend supports it)
      localStorage.setItem("role", role);
      
      // Navigate to login after successful registration
      navigate("/login");
    } catch (err) {
      // Show specific error message from backend if available
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
    <FormContainer>
      <Card title="Register">
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

        <form onSubmit={handleRegister} className="space-y-4">
          <Input
            label="Username"
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter your username"
            required
          />
          <Input
            label="Email"
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email"
            required
          />
          <Input
            label="Password"
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            required
          />
          <div>
            <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-1">
              Role
            </label>
            <select
              id="role"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Select a role</option>
              <option value="student">Student</option>
              <option value="teacher">Teacher</option>
              <option value="parent">Parent</option>
              <option value="supervisor">Supervisor</option>
            </select>
          </div>
          <Button
            type="submit"
            variant="primary"
            disabled={loading}
            loading={loading}
            className="w-full"
          >
            Register
          </Button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-600">
          Already have an account?{" "}
          <a href="/login" className="text-blue-600 hover:underline">
            Login
          </a>
        </p>
      </Card>
    </FormContainer>
  );
}

