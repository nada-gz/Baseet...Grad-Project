import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  BarChart3, 
  Link as LinkIcon, 
  ShieldCheck, 
  Clock, 
  Copy, 
  CheckCircle2,
  AlertCircle,
  RefreshCw
} from "lucide-react";
import api from "../../../services/api";

export default function StudentAnalytics() {
  const [linkingCode, setLinkingCode] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const generateCode = async () => {
    setLoading(true);
    try {
      const response = await api.post("/students/linking-code");
      setLinkingCode(response.data);
    } catch (err) {
      console.error("Error generating linking code:", err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (linkingCode) {
      navigator.clipboard.writeText(linkingCode.code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="parent-dashboard-wrapper">
      <div style={{ marginBottom: "40px" }}>
        <h1 className="topbar-title" style={{ fontSize: "2.5rem" }}>My Analytics</h1>
        <p style={{ color: "var(--secondary-text)" }}>Track your progress and manage your account privacy.</p>
      </div>

      <div className="parent-grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
        {/* Placeholder for real analytics */}
        <div className="parent-card" style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "60px", minHeight: "400px" }}>
          <BarChart3 size={64} style={{ opacity: 0.1, marginBottom: "20px" }} />
          <h3 style={{ color: "var(--secondary-text)" }}>Detailed Analytics Coming Soon</h3>
          <p style={{ fontSize: "0.9rem", color: "var(--secondary-text)", textAlign: "center" }}>
            Your learning milestones and academic data will appear here as you complete more lessons.
          </p>
        </div>

        {/* Parent Linking Section */}
        <div className="parent-card" style={{ border: "4px solid var(--highlight)", background: "var(--secondary-bg)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "15px", marginBottom: "30px" }}>
            <div style={{ background: "var(--primary-bg)", padding: "12px", borderRadius: "15px", color: "var(--highlight)" }}>
              <ShieldCheck size={32} />
            </div>
            <div>
              <h2 style={{ fontSize: "1.6rem", fontWeight: "900" }}>Parent Link</h2>
              <p style={{ fontSize: "0.9rem", color: "var(--secondary-text)" }}>Securely link your account to your parent.</p>
            </div>
          </div>

          <div style={{ background: "var(--primary-bg)", padding: "25px", borderRadius: "20px", marginBottom: "30px" }}>
            <h4 style={{ fontWeight: "800", marginBottom: "10px", display: "flex", alignItems: "center", gap: "8px" }}>
              <AlertCircle size={16} color="var(--highlight)" />
              How it works
            </h4>
            <ul style={{ fontSize: "0.85rem", color: "var(--secondary-text)", paddingLeft: "20px", display: "flex", flexDirection: "column", gap: "8px" }}>
              <li>Generate a temporary 6-digit code below.</li>
              <li>Give this code to your parent.</li>
              <li>They will enter it in their dashboard to link accounts.</li>
              <li>Your password remains private and secure!</li>
            </ul>
          </div>

          <AnimatePresence mode="wait">
            {linkingCode ? (
              <motion.div 
                key="code"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                style={{ textAlign: "center" }}
              >
                <div style={{ 
                  background: "white", border: "4px dashed var(--highlight)", 
                  padding: "30px", borderRadius: "20px", marginBottom: "20px",
                  position: "relative"
                }}>
                  <p style={{ fontSize: "0.75rem", fontWeight: "900", color: "var(--secondary-text)", textTransform: "uppercase", marginBottom: "10px" }}>Your Link Code</p>
                  <p style={{ fontSize: "3.5rem", fontWeight: "950", color: "var(--highlight)", letterSpacing: "8px" }}>{linkingCode.code}</p>
                  
                  <button 
                    onClick={copyToClipboard}
                    style={{ position: "absolute", right: "15px", bottom: "15px", background: "var(--primary-bg)", border: "none", borderRadius: "10px", padding: "8px", cursor: "pointer", color: "var(--highlight)" }}
                  >
                    {copied ? <CheckCircle2 size={18} /> : <Copy size={18} />}
                  </button>
                </div>

                <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", color: "var(--secondary-text)", fontSize: "0.85rem", marginBottom: "20px" }}>
                  <Clock size={14} />
                  <span>Expires in 15 minutes</span>
                </div>

                <button 
                  onClick={generateCode} 
                  className="parent-btn-wide" 
                  style={{ background: "transparent", borderColor: "var(--neutral)", color: "var(--secondary-text)" }}
                >
                  <RefreshCw size={16} />
                  Generate New Code
                </button>
              </motion.div>
            ) : (
              <motion.div 
                key="btn"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                style={{ textAlign: "center", padding: "20px 0" }}
              >
                <button 
                  className="btn btn-primary" 
                  style={{ width: "100%", padding: "20px", fontSize: "1.1rem" }}
                  onClick={generateCode}
                  disabled={loading}
                >
                  {loading ? "Generating..." : <><LinkIcon size={18} style={{ marginRight: "10px" }} /> Generate Link Code</>}
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}