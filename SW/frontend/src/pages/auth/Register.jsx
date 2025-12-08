import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { register as registerAPI } from "../../api/auth";
import { useAuth } from "../../context/AuthContext";
import api from "../../api/axios";
import GraduationIllustration from "../../assets/undraw_graduation_u7uc.svg";

export default function Register() {
  const navigate = useNavigate();
  const { login: loginContext } = useAuth();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get('/')
      .catch(() => setError("Cannot connect to backend"));
  }, []);

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    if (!username || !email || !password || !role) {
      setError("Please fill in all fields");
      setLoading(false);
      return;
    }

    try {
      const response = await registerAPI({ username, email, password, role });
      const userRole = response.user?.role || role;
      loginContext(response.access_token, response.user, userRole);
      navigate("/login");
    } catch (err) {
      let errorMessage = "Registration failed.";
      if (err.code === 'ERR_NETWORK' || err.message === 'Network Error')
        errorMessage = "Cannot connect to backend.";
      else if (err.response?.data?.detail)
        errorMessage = err.response.data.detail;
      else if (err.message)
        errorMessage = err.message;

      setError(errorMessage);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      {/* Left side: Form */}
      <div className="form-left">
        <div className="form-inner card">
          <h2 className="card-title">Register</h2>

          {error && <p className="error-message">{error}</p>}

          <form onSubmit={handleRegister} className="form">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
            />

            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
            />

            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
            />

            <label htmlFor="role">Role</label>
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
              className="btn btn-primary"
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

      {/* Right side: Illustration */}
      <div className="form-right">
        <img
          src={GraduationIllustration}
          alt="Kids learning illustration"
          className="w-full max-w-md"
        />
      </div>
    </div>
  );
}
