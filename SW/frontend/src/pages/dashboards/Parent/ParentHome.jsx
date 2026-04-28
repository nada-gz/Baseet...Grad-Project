import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Users, 
  Bell, 
  TrendingUp, 
  ChevronRight, 
  Heart,
  Zap,
  Plus,
  X,
  Link as LinkIcon,
  CheckCircle2
} from "lucide-react";
import useAuth from "../../../hooks/useAuth";
import api from "../../../services/api";

export default function ParentHome() {
  const { user } = useAuth();
  const [children, setChildren] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showLinkModal, setShowLinkModal] = useState(false);
  const [linkCode, setLinkCode] = useState("");
  const [linkStatus, setLinkStatus] = useState({ loading: false, error: null, success: false });

  const fetchData = async () => {
    try {
      const [childrenRes, notifyRes] = await Promise.all([
        api.get("/parent/my-children"),
        api.get("/parent/notifications")
      ]);
      setChildren(childrenRes.data);
      setNotifications(notifyRes.data);
    } catch (err) {
      console.error("Error fetching parent home data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleLinkChild = async (e) => {
    e.preventDefault();
    setLinkStatus({ loading: true, error: null, success: false });
    try {
      await api.post(`/parent/link-child?code=${linkCode}`);
      setLinkStatus({ loading: false, error: null, success: true });
      setTimeout(() => {
        setShowLinkModal(false);
        setLinkCode("");
        setLinkStatus({ loading: false, error: null, success: false });
        fetchData();
      }, 2000);
    } catch (err) {
      setLinkStatus({ 
        loading: false, 
        error: err.response?.data?.detail || "Invalid code. Please try again.", 
        success: false 
      });
    }
  };

  const urgentAlerts = notifications.filter(n => n.is_urgent && !n.is_read);

  if (loading) {
    return <div className="status checking p-10">Loading your dashboard...</div>;
  }

  return (
    <div className="parent-dashboard-wrapper">
      {/* Hero Section */}
      <section className="parent-hero-section">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              Welcome back, {user?.username || "Parent"}!
            </motion.h1>
            <p>
              Stay connected with your child's learning journey and personalize their experience.
            </p>
          </div>
          <button 
            className="btn btn-secondary" 
            style={{ borderRadius: "2rem", padding: "15px 30px" }}
            onClick={() => setShowLinkModal(true)}
          >
            <Plus size={20} />
            Link New Child
          </button>
        </div>
      </section>

      <div className="parent-grid">
        {/* Children Overview */}
        <div style={{ gridColumn: "span 2" }}>
          <h2 className="parent-section-title">
            <Users size={28} />
            My Children
          </h2>

          <div className="parent-grid" style={{ gridTemplateColumns: children.length > 0 ? "1fr 1fr" : "1fr" }}>
            {children.length > 0 ? (
              children.map((child) => (
                <div key={child.id} className="parent-card">
                  <div className="parent-card-header">
                    <div className="child-avatar-circle">
                      {child.name.charAt(0)}
                    </div>
                    <div>
                      <h3 style={{ fontSize: "1.4rem", fontWeight: "900" }}>{child.name}</h3>
                      <p style={{ color: "var(--secondary-text)", fontSize: "0.9rem" }}>Active Learner</p>
                    </div>
                  </div>

                  <div className="parent-stat-row">
                    <div className="parent-stat-box">
                      <p className="parent-stat-label">Learning Level</p>
                      <p className="parent-stat-value">{child.difficulty_level}</p>
                    </div>
                    <div className="parent-stat-box">
                      <p className="parent-stat-label">Current Mood</p>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px", justifyContent: "flex-start", marginLeft: "-10px" }}>
                        <span className="status-dot" style={{ width: "8px", height: "8px" }} />
                        <p className="parent-stat-value" style={{ color: "var(--success-bg)", fontSize: "0.95rem" }}>Stable (Live)</p>
                      </div>
                    </div>
                  </div>

                  <Link 
                    to={`/dashboard/parent/students/${child.id}/insights`}
                    className="parent-btn-wide"
                  >
                    View Insights
                    <TrendingUp size={18} />
                  </Link>
                </div>
              ))
            ) : (
              <div className="parent-card" style={{ textAlign: "center", padding: "80px" }}>
                <Users size={64} style={{ opacity: 0.1, marginBottom: "20px" }} />
                <h3 style={{ marginBottom: "10px" }}>No children linked yet</h3>
                <p style={{ color: "var(--secondary-text)", marginBottom: "30px" }}>
                  To see insights, you need to link your child's account using a 6-digit code.
                </p>
                <button 
                  className="btn btn-primary"
                  onClick={() => setShowLinkModal(true)}
                >
                  <LinkIcon size={18} style={{ marginRight: "10px" }} />
                  Link a Child Now
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar Alerts */}
        <div>
          <h2 className="parent-section-title">
            <Bell size={24} />
            Recent Alerts
          </h2>

          <div className="notification-feed">
            {urgentAlerts.length > 0 ? (
              urgentAlerts.slice(0, 3).map((alert) => (
                <Link 
                  key={alert.id}
                  to="/dashboard/parent/notifications"
                  className="notification-item urgent"
                  style={{ display: "block" }}
                >
                  <div style={{ display: "flex", gap: "10px", alignItems: "center", marginBottom: "8px" }}>
                    <Zap size={14} color="var(--error-bg)" fill="var(--error-bg)" />
                    <span style={{ fontSize: "0.7rem", fontWeight: "900", color: "var(--error-bg)", textTransform: "uppercase" }}>Urgent</span>
                  </div>
                  <h3 style={{ fontSize: "1rem", fontWeight: "800" }}>{alert.title}</h3>
                  <p style={{ fontSize: "0.85rem" }}>{alert.message}</p>
                </Link>
              ))
            ) : (
              <div className="parent-card" style={{ textAlign: "center" }}>
                <Heart size={32} style={{ opacity: 0.1, marginBottom: "10px" }} />
                <p style={{ fontSize: "0.9rem", color: "var(--secondary-text)" }}>All is well.</p>
              </div>
            )}

            <Link 
              to="/dashboard/parent/notifications" 
              style={{ textAlign: "center", display: "block", fontWeight: "800", marginTop: "15px" }}
            >
              See All Notifications
            </Link>
          </div>
        </div>
      </div>

      {/* Link Modal */}
      <AnimatePresence>
        {showLinkModal && (
          <div style={{ 
            position: "fixed", top: 0, left: 0, width: "100%", height: "100%", 
            background: "rgba(0,0,0,0.6)", zIndex: 1000, display: "flex", 
            alignItems: "center", justifyContent: "center", padding: "20px",
            backdropFilter: "blur(5px)"
          }}>
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="parent-card" 
              style={{ width: "100%", maxWidth: "500px", position: "relative" }}
            >
              <button 
                onClick={() => setShowLinkModal(false)}
                style={{ position: "absolute", right: "20px", top: "20px", background: "none", border: "none", cursor: "pointer", color: "var(--secondary-text)" }}
              >
                <X size={24} />
              </button>

              <div style={{ textAlign: "center", marginBottom: "30px" }}>
                <div style={{ width: "80px", height: "80px", background: "var(--primary-bg)", borderRadius: "2rem", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 20px", color: "var(--highlight)" }}>
                  <LinkIcon size={40} />
                </div>
                <h2 style={{ fontSize: "2rem", fontWeight: "900" }}>Link a Child</h2>
                <p style={{ color: "var(--secondary-text)" }}>
                  Enter the 6-digit code generated from your child's dashboard to link their account.
                </p>
              </div>

              {linkStatus.success ? (
                <div style={{ textAlign: "center", padding: "20px" }}>
                  <CheckCircle2 size={48} color="var(--success-bg)" style={{ margin: "0 auto 15px" }} />
                  <h3 style={{ color: "var(--success-bg)" }}>Successfully Linked!</h3>
                  <p>Your child's profile will appear in your dashboard shortly.</p>
                </div>
              ) : (
                <form onSubmit={handleLinkChild}>
                  <div style={{ marginBottom: "25px" }}>
                    <label style={{ fontWeight: "800", display: "block", marginBottom: "10px" }}>6-Digit Link Code</label>
                    <input 
                      type="text" 
                      placeholder="e.g. 123456" 
                      maxLength={6}
                      value={linkCode}
                      onChange={(e) => setLinkCode(e.target.value.replace(/\D/g, ''))}
                      style={{ fontSize: "2rem", textAlign: "center", letterSpacing: "10px", fontWeight: "950", padding: "20px" }}
                      required
                    />
                    {linkStatus.error && (
                      <p style={{ color: "var(--error-bg)", fontSize: "0.85rem", fontWeight: "700", marginTop: "10px", textAlign: "center" }}>
                        {linkStatus.error}
                      </p>
                    )}
                  </div>

                  <button 
                    type="submit" 
                    className="btn btn-primary" 
                    style={{ width: "100%", padding: "20px", fontSize: "1.2rem" }}
                    disabled={linkStatus.loading || linkCode.length < 6}
                  >
                    {linkStatus.loading ? "Verifying..." : "Link Child Account"}
                  </button>
                </form>
              )}

              <p style={{ fontSize: "0.8rem", color: "var(--secondary-text)", textAlign: "center", marginTop: "25px" }}>
                Don't have a code? Ask your child to generate one from their Analytics page.
              </p>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
