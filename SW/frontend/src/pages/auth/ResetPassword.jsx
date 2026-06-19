import { useState, useEffect } from "react";
import { useSearchParams, Link, useNavigate } from "react-router-dom";
import { verifyResetToken, resetPassword } from "../../api/auth";
import Baseet from "../../assets/BASEET-smiling-hat.png";
import Logo from "../../components/ui/logo";

// ── Password rules (same as Register) ───────────────────────────
const PASSWORD_RULES = [
  { id: "length",  label: "At least 8 characters",        test: (p) => p.length >= 8 },
  { id: "upper",   label: "One uppercase letter (A–Z)",   test: (p) => /[A-Z]/.test(p) },
  { id: "lower",   label: "One lowercase letter (a–z)",   test: (p) => /[a-z]/.test(p) },
  { id: "digit",   label: "One number (0–9)",             test: (p) => /[0-9]/.test(p) },
  { id: "special", label: "One special character (!@#…)", test: (p) => /[!@#$%^&*(),.?":{}|<>_\-]/.test(p) },
];

function getStrength(password) {
  const passed = PASSWORD_RULES.filter((r) => r.test(password)).length;
  if (passed === 0) return { score: 0, label: "",           color: "" };
  if (passed <= 1)  return { score: 1, label: "Weak",       color: "#FF5E5E" };
  if (passed <= 2)  return { score: 2, label: "Fair",       color: "#FFBE0B" };
  if (passed <= 3)  return { score: 3, label: "Good",       color: "#3A86FF" };
  if (passed === 4) return { score: 4, label: "Strong",     color: "#00b894" };
  return               { score: 5, label: "Very Strong", color: "#6C63FF" };
}

export default function ResetPassword() {
  const [searchParams]          = useSearchParams();
  const navigate                = useNavigate();
  const token                   = searchParams.get("token") || "";

  const [tokenState, setTokenState] = useState("checking"); // "checking" | "valid" | "invalid"
  const [userEmail, setUserEmail]   = useState("");
  const [errorDetails, setErrorDetails] = useState("");

  const [password, setPassword]     = useState("");
  const [confirm, setConfirm]       = useState("");
  const [showPass, setShowPass]     = useState(false);
  const [showConf, setShowConf]     = useState(false);

  const [loading, setLoading]       = useState(false);
  const [success, setSuccess]       = useState(false);
  const [error, setError]           = useState("");

  // ── On mount: validate the token ──────────────────────────────
  useEffect(() => {
    if (!token) { 
      setTokenState("invalid"); 
      setErrorDetails("No reset token was found in the URL.");
      return; 
    }
    verifyResetToken(token)
      .then((data) => { 
        setTokenState("valid"); 
        setUserEmail(data.email || ""); 
      })
      .catch((err) => {
        console.error("Token verification failed:", err);
        setTokenState("invalid");
        if (err.message === "Network Error" || err.code === "ERR_NETWORK") {
          setErrorDetails("Cannot connect to the backend server. Please verify that your backend server is running.");
        } else if (err.response?.data?.detail) {
          setErrorDetails(err.response.data.detail);
        } else {
          setErrorDetails("This reset link is invalid or has expired (links are valid for 1 hour).");
        }
      });
  }, [token]);

  const strength   = getStrength(password);
  const allPassed  = PASSWORD_RULES.every((r) => r.test(password));
  const noMismatch = password === confirm;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!allPassed) {
      setError("Please meet all password requirements.");
      return;
    }
    if (!noMismatch) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      await resetPassword(token, password);
      setSuccess(true);
      setTimeout(() => navigate("/login"), 3000);
    } catch (err) {
      let msg = "Something went wrong. Please try again.";
      if (err.response?.data?.detail) msg = err.response.data.detail;
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  // ── Render: checking ──────────────────────────────────────────
  if (tokenState === "checking") {
    return (
      <div className="form-container relative">
        <Logo />
        <div className="form-right" style={{ width: "100%", justifyContent: "center" }}>
          <div className="form-inner card" style={{ textAlign: "center" }}>
            <div className="auth-spinner" />
            <p style={{ marginTop: "1rem", color: "var(--secondary-text)" }}>
              Verifying your reset link…
            </p>
          </div>
        </div>
      </div>
    );
  }

  // ── Render: invalid token ─────────────────────────────────────
  if (tokenState === "invalid") {
    return (
      <div className="form-container relative">
        <Logo />
        <div className="form-left">
          <img src={Baseet} alt="Baseet" className="w-full max-w-md" />
        </div>
        <div className="form-right">
          <div className="form-inner card">
            <div className="auth-sent-icon">⚠️</div>
            <h2 className="card-title">Verification Failed</h2>
            <p className="auth-sent-desc">
              {errorDetails}
            </p>
            <Link to="/forgot-password" className="btn btn-primary auth-back-btn">
              Request New Link
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // ── Render: success ───────────────────────────────────────────
  if (success) {
    return (
      <div className="form-container relative">
        <Logo />
        <div className="form-left">
          <img src={Baseet} alt="Baseet" className="w-full max-w-md" />
        </div>
        <div className="form-right">
          <div className="form-inner card">
            <div className="auth-sent-icon">🎉</div>
            <h2 className="card-title">Password Reset!</h2>
            <p className="auth-sent-desc">
              Your password has been updated successfully. Redirecting you to login…
            </p>
            <Link to="/login" className="btn btn-primary auth-back-btn">
              Go to Login
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // ── Render: form ──────────────────────────────────────────────
  return (
    <div className="form-container relative">
      <Logo />

      <div className="form-left">
        <img src={Baseet} alt="Baseet" className="w-full max-w-md" />
      </div>

      <div className="form-right">
        <div className="form-inner card">
          <h2 className="card-title">Set New Password</h2>
          {userEmail && (
            <p className="auth-subtitle">
              Resetting password for <strong>{userEmail}</strong>
            </p>
          )}

          {error && <p className="error-message">{error}</p>}

          <form onSubmit={handleSubmit} className="form">
            {/* New password */}
            <div className="auth-field-header">
              <label htmlFor="reset-password">New Password</label>
            </div>
            <div className="auth-password-wrap">
              <input
                id="reset-password"
                type={showPass ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Create a strong password"
                required
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

            {/* Confirm password */}
            <div className="auth-field-header" style={{ marginTop: "0.5rem" }}>
              <label htmlFor="reset-confirm">Confirm Password</label>
              {confirm.length > 0 && (
                <span style={{ fontSize: "0.85rem", color: noMismatch ? "#00b894" : "#FF5E5E", fontWeight: 700 }}>
                  {noMismatch ? "✅ Match" : "✗ Mismatch"}
                </span>
              )}
            </div>
            <div className="auth-password-wrap">
              <input
                id="reset-confirm"
                type={showConf ? "text" : "password"}
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                placeholder="Repeat your password"
                required
              />
              <button
                type="button"
                className="auth-eye-btn"
                onClick={() => setShowConf((p) => !p)}
                aria-label={showConf ? "Hide" : "Show"}
              >
                {showConf ? "🙈" : "👁️"}
              </button>
            </div>

            <button
              type="submit"
              id="reset-submit-btn"
              className="btn btn-primary"
              disabled={loading || !allPassed || !noMismatch || !confirm}
            >
              {loading ? "Saving…" : "Set New Password"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
