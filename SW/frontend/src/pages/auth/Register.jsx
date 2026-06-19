import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { register as registerAPI } from "../../api/auth";
import { useAuth } from "../../context/AuthContext";
import api from "../../api/axios";
import Baseet from "../../assets/BASEET-smiling-hat.png";
import Logo from "../../components/ui/logo";

// ── Password rules (mirroring backend) ──────────────────────────
const PASSWORD_RULES = [
  { id: "length",    label: "At least 8 characters",        test: (p) => p.length >= 8 },
  { id: "upper",     label: "One uppercase letter (A–Z)",   test: (p) => /[A-Z]/.test(p) },
  { id: "lower",     label: "One lowercase letter (a–z)",   test: (p) => /[a-z]/.test(p) },
  { id: "digit",     label: "One number (0–9)",             test: (p) => /[0-9]/.test(p) },
  { id: "special",   label: "One special character (!@#…)", test: (p) => /[!@#$%^&*(),.?":{}|<>_\-]/.test(p) },
];

// ── Strength score & label ───────────────────────────────────────
function getStrength(password) {
  const passed = PASSWORD_RULES.filter((r) => r.test(password)).length;
  if (passed === 0) return { score: 0, label: "",          color: "" };
  if (passed <= 1)  return { score: 1, label: "Weak",      color: "#FF5E5E" };
  if (passed <= 2)  return { score: 2, label: "Fair",      color: "#FFBE0B" };
  if (passed <= 3)  return { score: 3, label: "Good",      color: "#3A86FF" };
  if (passed === 4) return { score: 4, label: "Strong",    color: "#00b894" };
  return              { score: 5, label: "Very Strong", color: "#6C63FF" };
}

// ── Random strong password generator ────────────────────────────
const UPPER   = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
const LOWER   = "abcdefghijklmnopqrstuvwxyz";
const DIGITS  = "0123456789";
const SPECIAL = "!@#$%^&*()_-";

function generatePassword(length = 14) {
  const all = UPPER + LOWER + DIGITS + SPECIAL;
  const required = [
    UPPER[Math.floor(Math.random() * UPPER.length)],
    LOWER[Math.floor(Math.random() * LOWER.length)],
    DIGITS[Math.floor(Math.random() * DIGITS.length)],
    SPECIAL[Math.floor(Math.random() * SPECIAL.length)],
  ];
  const rest = Array.from({ length: length - 4 }, () =>
    all[Math.floor(Math.random() * all.length)]
  );
  return [...required, ...rest].sort(() => Math.random() - 0.5).join("");
}

export default function Register() {
  const navigate = useNavigate();
  const { login: loginContext } = useAuth();

  const [username, setUsername]   = useState("");
  const [email, setEmail]         = useState("");
  const [password, setPassword]   = useState("");
  const [role, setRole]           = useState("");
  const [showPass, setShowPass]   = useState(false);
  const [error, setError]         = useState("");
  const [loading, setLoading]     = useState(false);
  const [generated, setGenerated] = useState(false);

  useEffect(() => {
    api.get('/').catch(() => setError("Cannot connect to backend"));
  }, []);

  const strength  = getStrength(password);
  const rulesPassed = PASSWORD_RULES.filter((r) => r.test(password));
  const allPassed = rulesPassed.length === PASSWORD_RULES.length;

  const handleGenerate = () => {
    const pwd = generatePassword();
    setPassword(pwd);
    setShowPass(true);
    setGenerated(true);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");

    if (!allPassed) {
      setError("Please meet all password requirements before registering.");
      return;
    }

    setLoading(true);
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
    <div className="form-container relative">
      <Logo />

      {/* Left: Illustration */}
      <div className="form-left">
        <img src={Baseet} alt="Kids learning illustration" className="w-full max-w-md" />
      </div>

      {/* Right: Form */}
      <div className="form-right" style={{ width: '600px', maxWidth: '100%' }}>
        <div className="form-inner card" style={{ padding: '1.5rem 2.5rem', gap: '0.75rem' }}>
          <h2 className="card-title" style={{ marginBottom: '0.25rem' }}>Join the Waitlist</h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", marginBottom: "8px" }}>
            Register your interest and we will notify you as soon as a spot opens up!
          </p>
          {error && <p className="error-message">{error}</p>}

          <form onSubmit={handleRegister} className="form" style={{ gap: 0 }}>
            {/* Username */}
            <label htmlFor="reg-username" style={{ marginTop: '0.75rem', display: 'block' }}>Username</label>
            <input
              id="reg-username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
              style={{ marginBottom: '8px', padding: '0.65rem 1rem' }}
            />

            {/* Email */}
            <label htmlFor="reg-email">Email</label>
            <input
              id="reg-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
              style={{ marginBottom: '8px', padding: '0.65rem 1rem' }}
            />

            {/* Password */}
            <div className="auth-field-header">
              <label htmlFor="reg-password">Password</label>
              <button
                type="button"
                id="generate-password-btn"
                className="auth-generate-btn"
                onClick={handleGenerate}
                title="Generate a strong password"
              >
                🎲 Generate
              </button>
            </div>

            <div className="auth-password-wrap">
              <input
                id="reg-password"
                type={showPass ? "text" : "password"}
                value={password}
                onChange={(e) => { setPassword(e.target.value); setGenerated(false); }}
                placeholder="Create a strong password"
                required
                style={{ marginBottom: '8px', padding: '0.65rem 1rem' }}
              />
              <button
                type="button"
                className="auth-eye-btn"
                onClick={() => setShowPass((p) => !p)}
                aria-label={showPass ? "Hide password" : "Show password"}
              >
                {showPass ? "🙈" : "👁️"}
              </button>
            </div>

            {/* Strength meter */}
            {password.length > 0 && (
              <div className="auth-strength-wrap">
                <div className="auth-strength-bar-track">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div
                      key={i}
                      className="auth-strength-segment"
                      style={{
                        backgroundColor: i <= strength.score ? strength.color : "#DFE6E9",
                        transition: "background-color 0.3s ease",
                      }}
                    />
                  ))}
                </div>
                {strength.label && (
                  <span className="auth-strength-label" style={{ color: strength.color }}>
                    {strength.label}
                  </span>
                )}
              </div>
            )}

            {/* Requirements checklist */}
            {password.length > 0 && (
              <ul className="auth-requirements">
                {PASSWORD_RULES.map((rule) => {
                  const ok = rule.test(password);
                  return (
                    <li key={rule.id} className={`auth-req-item ${ok ? "auth-req-ok" : "auth-req-fail"}`}>
                      <span className="auth-req-icon">{ok ? "✅" : "✗"}</span>
                      {rule.label}
                    </li>
                  );
                })}
              </ul>
            )}

            {generated && (
              <p className="auth-generated-note">
                💡 Password generated! Make sure to save it before continuing.
              </p>
            )}

            {/* Role */}
            <label htmlFor="reg-role" style={{ marginTop: '2px', display: 'block' }}>Role</label>
            <select
              id="reg-role"
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
              id="register-submit-btn"
              className="btn btn-primary"
              disabled={loading || !allPassed}
            >
              {loading ? "Registering…" : "Register"}
            </button>
          </form>

          <p className="text-center mt-4 text-sm">
            Already have an account? <a href="/login">Login</a>
          </p>
        </div>
      </div>
    </div>
  );
}
