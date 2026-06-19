import { useState } from "react";
import { Link } from "react-router-dom";
import { forgotPassword } from "../../api/auth";
import Baseet from "../../assets/BASEET-smiling-hat.png";
import Logo from "../../components/ui/logo";

export default function ForgotPassword() {
  const [email, setEmail]       = useState("");
  const [loading, setLoading]   = useState(false);
  const [sent, setSent]         = useState(false);
  const [error, setError]       = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await forgotPassword(email);
      setSent(true);
    } catch (err) {
      let msg = "Something went wrong. Please try again.";
      if (err.code === "ERR_NETWORK") msg = "Cannot connect to backend.";
      else if (err.response?.data?.detail) msg = err.response.data.detail;
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container relative">
      <Logo />

      <div className="form-left">
        <img src={Baseet} alt="Baseet illustration" className="w-full max-w-md" />
      </div>

      <div className="form-right">
        <div className="form-inner card">
          {sent ? (
            /* ── Success state ── */
            <div className="auth-sent-wrap">
              <div className="auth-sent-icon">📬</div>
              <h2 className="card-title">Check your inbox!</h2>
              <p className="auth-sent-desc">
                If <strong>{email}</strong> is registered with Baseet, you'll receive
                a password-reset link shortly. The link expires in <strong>1 hour</strong>.
              </p>
              <p className="auth-sent-tip">
                Don't see it? Check your spam folder or{" "}
                <button
                  type="button"
                  className="auth-resend-btn"
                  onClick={() => setSent(false)}
                >
                  try again
                </button>
                .
              </p>
              <Link to="/login" className="btn btn-primary auth-back-btn">
                ← Back to Login
              </Link>
            </div>
          ) : (
            /* ── Form state ── */
            <>
              <h2 className="card-title">Forgot Password?</h2>
              <p className="auth-subtitle">
                Enter your registered email and we'll send you a reset link.
              </p>

              {error && <p className="error-message">{error}</p>}

              <form onSubmit={handleSubmit} className="form">
                <label htmlFor="forgot-email">Email address</label>
                <input
                  id="forgot-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  required
                />

                <button
                  type="submit"
                  id="forgot-submit-btn"
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? "Sending…" : "Send Reset Link"}
                </button>
              </form>

              <p className="text-center mt-4 text-sm">
                Remembered it? <Link to="/login">Back to Login</Link>
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
