import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { login as loginAPI } from "../../api/auth";
import { useAuth } from "../../context/AuthContext";
import api from "../../api/axios";
import GraduationIllustration from "../../assets/undraw_graduation_u7uc.svg";
import Logo from "../../components/ui/logo";

export default function Login() {
  const navigate = useNavigate();
  const { login: loginContext } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get('/').catch(() => setError("Cannot connect to backend"));
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
      if (err.code === 'ERR_NETWORK') errorMessage = "Cannot connect to backend.";
      else if (err.response?.status === 401) errorMessage = "Invalid email or password.";
      setError(errorMessage);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container relative">
      {/* Fixed Logo */}
      <Logo />

      {/* Left side: Illustration */}
      <div className="form-left">
        <img
          src={GraduationIllustration}
          alt="Kids learning illustration"
          className="w-full max-w-md"
        />
      </div>

      {/* Right side: Form */}
      <div className="form-right">
        <div className="form-inner card">
          <h2 className="card-title">Login</h2>
          {error && <p className="error-message">{error}</p>}

          <form onSubmit={handleLogin} className="form">
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

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? "Logging in..." : "Login"}
            </button>
          </form>

          <p className="text-center mt-6 text-sm">
            Don't have an account? <a href="/register">Register</a>
          </p>
        </div>
      </div>
    </div>
  );
}
