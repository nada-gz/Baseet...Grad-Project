import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  RadialBarChart, RadialBar, ResponsiveContainer, Tooltip, Legend
} from "recharts";
import {
  Clock, Calendar, Target, Zap, Flame, Trophy, BookOpen,
  AlertCircle, BarChart3, ShieldCheck, Link as LinkIcon,
  Copy, CheckCircle2, RefreshCw
} from "lucide-react";
import { fetchStudentDashboard } from "../../../api/dashboard";
import api from "../../../services/api";
import { AnimatePresence } from "framer-motion";

const CARD_COLORS = ["#6C63FF", "#FF006E", "#FFBE0B", "#FB5607"];

const StatCard = ({ icon: Icon, label, value, color, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay }}
    className="parent-card"
    style={{
      display: "flex", alignItems: "center", gap: "20px", padding: "24px",
      borderLeft: `6px solid ${color}`
    }}
  >
    <div style={{
      background: color + "18", borderRadius: "16px", padding: "14px",
      display: "flex", alignItems: "center", justifyContent: "center"
    }}>
      <Icon size={28} color={color} />
    </div>
    <div>
      <p style={{ fontSize: "0.85rem", color: "var(--secondary-text)", fontWeight: 700, marginBottom: "4px", textTransform: "uppercase", letterSpacing: "1px" }}>{label}</p>
      <p style={{ fontSize: "1.8rem", fontWeight: 950, color: "var(--primary-text)", lineHeight: 1 }}>{value}</p>
    </div>
  </motion.div>
);

export default function StudentAnalytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Parent linking state
  const [linkingCode, setLinkingCode] = useState(null);
  const [linkLoading, setLinkLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchStudentDashboard()
      .then(setData)
      .catch(err => setError(err.response?.data?.detail || err.message || "Failed to load analytics"))
      .finally(() => setLoading(false));
  }, [retryCount]);

  const generateCode = async () => {
    setLinkLoading(true);
    try {
      const response = await api.post("/students/linking-code");
      setLinkingCode(response.data);
    } catch (err) {
      console.error("Error generating linking code:", err);
    } finally {
      setLinkLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (linkingCode) {
      navigator.clipboard.writeText(linkingCode.code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return (
      <div className="parent-dashboard-wrapper" style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "60vh", flexDirection: "column", gap: "20px" }}>
        <div className="auth-spinner" />
        <p style={{ color: "var(--secondary-text)", fontWeight: 700 }}>Generating your AI analytics report…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="parent-dashboard-wrapper">
        <div className="parent-card" style={{ display: "flex", alignItems: "center", gap: "24px", padding: "40px", borderLeft: "6px solid var(--error-bg)" }}>
          <AlertCircle size={48} color="var(--error-bg)" style={{ flexShrink: 0 }} />
          <div style={{ flex: 1 }}>
            <h3 style={{ fontWeight: 900, marginBottom: "8px" }}>Could not load analytics</h3>
            <p style={{ color: "var(--secondary-text)", marginBottom: "20px", fontSize: "0.95rem" }}>
              The AI report service is temporarily busy. Your data is loading from the local database instead.
            </p>
            <button
              onClick={() => setRetryCount(c => c + 1)}
              className="btn btn-primary"
              style={{ display: "inline-flex", alignItems: "center", gap: "8px", padding: "12px 28px" }}
            >
              <RefreshCw size={16} /> Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Prepare RadialBar for daily goal
  const goalPct = data?.daily_goal
    ? Math.round((data.daily_goal.progress / data.daily_goal.target) * 100)
    : 0;
  const radialData = [{ name: "Progress", value: goalPct, fill: "#6C63FF" }];

  // Mood color map
  const moodColors = { Excited: "#FFBE0B", Focused: "#6C63FF", "Lunch Time": "#FB5607", Calm: "#00b894", Happy: "#3A86FF" };

  return (
    <div className="parent-dashboard-wrapper">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: "40px" }}>
        <h1 className="topbar-title" style={{ fontSize: "2.5rem" }}>My Analytics</h1>
        <p style={{ color: "var(--secondary-text)" }}>
          {data?.identity?.name} · {data?.identity?.level} · AI-powered insights
        </p>
      </motion.div>

      {/* Section 1: Stat Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "20px", marginBottom: "40px" }}>
        <StatCard icon={Clock}     label="Hours Today"    value={`${data?.time_metrics?.hours_today ?? 0}h`}    color="#6C63FF" delay={0.05} />
        <StatCard icon={Calendar}  label="Hours This Week" value={`${data?.time_metrics?.hours_this_week ?? 0}h`} color="#FF006E" delay={0.1}  />
        <StatCard icon={Target}    label="Focus Score"    value={`${data?.time_metrics?.focus_percentage ?? 0}%`} color="#FFBE0B" delay={0.15} />
        <StatCard icon={Zap}       label="Total XP"       value={(data?.stats?.total_xp ?? 0).toLocaleString()} color="#FB5607" delay={0.2}  />
      </div>

      {/* Section 2: Radar Chart + Mini Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "1.6fr 1fr", gap: "30px", marginBottom: "40px" }}>
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }} className="parent-card" style={{ padding: "30px" }}>
          <h3 style={{ fontWeight: 900, fontSize: "1.3rem", marginBottom: "24px" }}>
            <BarChart3 size={20} style={{ marginRight: "10px", verticalAlign: "middle", color: "var(--highlight)" }} />
            Skill Radar
          </h3>
          <ResponsiveContainer width="100%" height={280}>
            <RadarChart data={data?.radar_chart_data ?? []}>
              <PolarGrid stroke="var(--neutral)" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: "var(--secondary-text)", fontSize: 13, fontWeight: 700 }} />
              <Radar name="Score" dataKey="score" stroke="#6C63FF" fill="#6C63FF" fillOpacity={0.35} strokeWidth={3} />
              <Tooltip contentStyle={{ borderRadius: "12px", border: "none", boxShadow: "0 8px 20px rgba(0,0,0,0.1)" }} />
            </RadarChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.25 }} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {[
            { icon: Flame,   label: "Current Streak",         value: `${data?.stats?.current_streak ?? 0} days`,         color: "#FB5607" },
            { icon: BookOpen, label: "Lessons This Week",     value: `${data?.stats?.lessons_completed_this_week ?? 0}`,  color: "#6C63FF" },
            { icon: Trophy,  label: "Achievements Unlocked",  value: `${data?.stats?.achievements_unlocked ?? 0}`,        color: "#FFBE0B" },
            { icon: Clock,   label: "Hours This Month",       value: `${data?.time_metrics?.hours_this_month ?? 0}h`,    color: "#FF006E" },
          ].map(({ icon: Icon, label, value, color }, i) => (
            <div key={label} className="parent-card" style={{ display: "flex", alignItems: "center", gap: "16px", padding: "18px 20px", borderLeft: `5px solid ${color}`, flex: 1 }}>
              <div style={{ background: color + "18", borderRadius: "12px", padding: "10px" }}>
                <Icon size={22} color={color} />
              </div>
              <div>
                <p style={{ fontSize: "0.75rem", color: "var(--secondary-text)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "1px" }}>{label}</p>
                <p style={{ fontSize: "1.4rem", fontWeight: 950 }}>{value}</p>
              </div>
            </div>
          ))}
        </motion.div>
      </div>

      {/* Section 3: Mood Timeline */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="parent-card" style={{ padding: "30px", marginBottom: "40px" }}>
        <h3 style={{ fontWeight: 900, fontSize: "1.3rem", marginBottom: "24px" }}>Today's Mood Timeline</h3>
        <div style={{ display: "flex", gap: "16px", overflowX: "auto", paddingBottom: "8px" }}>
          {(data?.mood_timeline ?? []).map((mood, i) => {
            const color = moodColors[mood.label] || "#6C63FF";
            return (
              <div key={i} style={{
                display: "flex", flexDirection: "column", alignItems: "center",
                background: "var(--primary-bg)", borderRadius: "20px", padding: "20px 24px",
                borderBottom: `5px solid ${color}`, minWidth: "120px", gap: "8px"
              }}>
                <span style={{ fontSize: "2.2rem" }}>{mood.emoji}</span>
                <p style={{ fontWeight: 900, fontSize: "0.95rem" }}>{mood.label}</p>
                <p style={{ fontSize: "0.75rem", color: "var(--secondary-text)", fontWeight: 700 }}>{mood.time}</p>
              </div>
            );
          })}
        </div>
      </motion.div>

      {/* Section 4: Daily Goal */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }} className="parent-card" style={{ padding: "30px", marginBottom: "40px", display: "flex", alignItems: "center", gap: "40px" }}>
        <div style={{ width: 180, height: 180, flexShrink: 0 }}>
          <ResponsiveContainer width="100%" height="100%">
            <RadialBarChart cx="50%" cy="50%" innerRadius="60%" outerRadius="100%" data={radialData} startAngle={90} endAngle={-270}>
              <RadialBar background={{ fill: "var(--neutral)" }} dataKey="value" cornerRadius={12} />
              <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" style={{ fontSize: "1.5rem", fontWeight: 950, fill: "var(--primary-text)" }}>
                {goalPct}%
              </text>
            </RadialBarChart>
          </ResponsiveContainer>
        </div>
        <div>
          <p style={{ fontSize: "0.85rem", color: "var(--secondary-text)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "1px", marginBottom: "8px" }}>Daily Goal</p>
          <h2 style={{ fontSize: "2rem", fontWeight: 950, marginBottom: "12px" }}>
            {data?.daily_goal?.progress ?? 0} / {data?.daily_goal?.target ?? 100}
          </h2>
          <p style={{ fontSize: "1.1rem", color: "var(--highlight)", fontWeight: 700 }}>
            {data?.daily_goal?.message}
          </p>
        </div>
      </motion.div>

      {/* Section 5: Parent Link (preserved from original) */}
      <div className="parent-grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
        <div className="parent-card" style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "60px", minHeight: "300px" }}>
          <BarChart3 size={64} style={{ opacity: 0.1, marginBottom: "20px" }} />
          <h3 style={{ color: "var(--secondary-text)" }}>More insights coming soon</h3>
          <p style={{ fontSize: "0.9rem", color: "var(--secondary-text)", textAlign: "center", marginTop: "10px" }}>
            Your full academic history will appear here as you complete more lessons.
          </p>
        </div>

        <div className="parent-card" style={{ border: "4px solid var(--highlight)", background: "var(--secondary-bg)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "15px", marginBottom: "30px" }}>
            <div style={{ background: "var(--primary-bg)", padding: "12px", borderRadius: "15px", color: "var(--highlight)" }}>
              <ShieldCheck size={32} />
            </div>
            <div>
              <h2 style={{ fontSize: "1.6rem", fontWeight: 900 }}>Parent Link</h2>
              <p style={{ fontSize: "0.9rem", color: "var(--secondary-text)" }}>Securely link your account to your parent.</p>
            </div>
          </div>
          <div style={{ background: "var(--primary-bg)", padding: "25px", borderRadius: "20px", marginBottom: "30px" }}>
            <h4 style={{ fontWeight: 800, marginBottom: "10px", display: "flex", alignItems: "center", gap: "8px" }}>
              <AlertCircle size={16} color="var(--highlight)" /> How it works
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
              <motion.div key="code" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.9 }} style={{ textAlign: "center" }}>
                <div style={{ background: "white", border: "4px dashed var(--highlight)", padding: "30px", borderRadius: "20px", marginBottom: "20px", position: "relative" }}>
                  <p style={{ fontSize: "0.75rem", fontWeight: 900, color: "var(--secondary-text)", textTransform: "uppercase", marginBottom: "10px" }}>Your Link Code</p>
                  <p style={{ fontSize: "3.5rem", fontWeight: 950, color: "var(--highlight)", letterSpacing: "8px" }}>{linkingCode.code}</p>
                  <button onClick={copyToClipboard} style={{ position: "absolute", right: "15px", bottom: "15px", background: "var(--primary-bg)", border: "none", borderRadius: "10px", padding: "8px", cursor: "pointer", color: "var(--highlight)" }}>
                    {copied ? <CheckCircle2 size={18} /> : <Copy size={18} />}
                  </button>
                </div>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", color: "var(--secondary-text)", fontSize: "0.85rem", marginBottom: "20px" }}>
                  <Clock size={14} /><span>Expires in 15 minutes</span>
                </div>
                <button onClick={generateCode} className="parent-btn-wide" style={{ background: "transparent", borderColor: "var(--neutral)", color: "var(--secondary-text)" }}>
                  <RefreshCw size={16} /> Generate New Code
                </button>
              </motion.div>
            ) : (
              <motion.div key="btn" initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ textAlign: "center", padding: "20px 0" }}>
                <button className="btn btn-primary" style={{ width: "100%", padding: "20px", fontSize: "1.1rem" }} onClick={generateCode} disabled={linkLoading}>
                  {linkLoading ? "Generating..." : <><LinkIcon size={18} style={{ marginRight: "10px" }} /> Generate Link Code</>}
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}