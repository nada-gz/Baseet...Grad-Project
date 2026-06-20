import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  PieChart, Pie, Cell, BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from "recharts";
import { Target, BookOpen, FileText, Clock, Brain, Activity, Zap, AlertCircle, Users } from "lucide-react";
import { fetchTeacherDashboard } from "../../../api/dashboard";
import api from "../../../services/api";

const StatCard = ({ icon: Icon, label, value, color, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }}
    className="parent-card"
    style={{ display: "flex", alignItems: "center", gap: "20px", padding: "24px", borderLeft: `6px solid ${color}` }}
  >
    <div style={{ background: color + "18", borderRadius: "16px", padding: "14px" }}>
      <Icon size={28} color={color} />
    </div>
    <div>
      <p style={{ fontSize: "0.8rem", color: "var(--secondary-text)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "1px", marginBottom: "4px" }}>{label}</p>
      <p style={{ fontSize: "1.8rem", fontWeight: 950, lineHeight: 1 }}>{value}</p>
    </div>
  </motion.div>
);

const ENG_COLORS = ["#6C63FF", "#FF5E5E", "#FFBE0B"];

const skillColor = (val) => val >= 80 ? "#00b894" : val >= 40 ? "#FFBE0B" : "#FF5E5E";

export default function TeacherAnalytics() {
  const [students, setStudents] = useState([]);
  const [selectedStudentId, setSelectedStudentId] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    // Fetch available students once
    api.get("/teacher/students")
      .then(res => {
        if (res.data && Array.isArray(res.data) && res.data.length > 0) {
          setStudents(res.data);
          setSelectedStudentId(res.data[0].id);
        }
      })
      .catch(err => console.error("Failed to load students:", err));
  }, []);

  useEffect(() => {
    if (!selectedStudentId) return;

    setLoading(true);
    setError(null);
    fetchTeacherDashboard(selectedStudentId)
      .then(setData)
      .catch(err => setError(err.response?.data?.detail || err.message || "Failed to load report"))
      .finally(() => setLoading(false));
  }, [selectedStudentId, retryCount]);

  if (loading) {
    return (
      <div className="parent-dashboard-wrapper" style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "60vh", flexDirection: "column", gap: "20px" }}>
        <div className="auth-spinner" />
        <p style={{ color: "var(--secondary-text)", fontWeight: 700 }}>Generating AI student report…</p>
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
              The AI report service is temporarily busy. The system will use live DB data instead.
            </p>
            <button
              onClick={() => setRetryCount(c => c + 1)}
              style={{ display: "inline-flex", alignItems: "center", gap: "8px", padding: "12px 28px", background: "var(--highlight)", color: "white", border: "none", borderRadius: "12px", fontWeight: 800, cursor: "pointer", fontSize: "0.95rem" }}
            >
              ↻ Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  const engProfile = data?.time_analytics?.engagement_profile ?? {};
  const pieData = [
    { name: "Focused", value: engProfile.focused ?? 0 },
    { name: "Stressed", value: engProfile.stressed ?? 0 },
    { name: "Distracted", value: engProfile.distracted ?? 0 },
  ];

  const sg = data?.skill_gap_analysis?.story_grammar ?? {};
  const sgData = Object.entries(sg).map(([key, val]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    value: val,
    fill: skillColor(val)
  }));

  const biometric = (Array.isArray(data?.biometric_correlation_chart) ? data.biometric_correlation_chart : []).map(r => ({
    task: r.task,
    hr: r.hr,
    gsr: Math.round(r.gsr * 100),
    status: r.status
  }));

  const connectives = Array.isArray(data?.skill_gap_analysis?.connective_usage) ? data.skill_gap_analysis.connective_usage : [];
  const maxCount = Math.max(...connectives.map(c => c.count), 1);

  return (
    <div className="parent-dashboard-wrapper">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: "40px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 className="topbar-title" style={{ fontSize: "2.5rem" }}>Student Analytics Report</h1>
          <p style={{ color: "var(--secondary-text)" }}>
            Student ID: {data?.student_id} · AI-powered academic & biometric breakdown
          </p>
        </div>
        
        {/* Student Selector */}
        {students.length > 0 && (
          <div style={{ background: "white", padding: "10px 20px", borderRadius: "16px", display: "flex", alignItems: "center", gap: "12px", boxShadow: "0 4px 15px rgba(0,0,0,0.05)", border: "1px solid var(--neutral)" }}>
            <Users size={20} color="var(--highlight)" />
            <select 
              value={selectedStudentId || ""} 
              onChange={(e) => setSelectedStudentId(Number(e.target.value))}
              style={{ border: "none", outline: "none", fontSize: "1.05rem", fontWeight: 700, color: "var(--primary-text)", background: "transparent", cursor: "pointer", paddingRight: "10px" }}
            >
              {students.map(s => (
                <option key={s.id} value={s.id}>{s.username} (ID: {s.id})</option>
              ))}
            </select>
          </div>
        )}
      </motion.div>

      {/* Section 1: Performance KPIs */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "20px", marginBottom: "40px" }}>
        <StatCard icon={Target}   label="Avg Accuracy"          value={`${data?.performance_summary?.avg_accuracy ?? 0}%`}        color="#6C63FF" delay={0.05} />
        <StatCard icon={BookOpen} label="Lessons Completed"      value={data?.performance_summary?.lessons_completed ?? 0}         color="#00b894" delay={0.1}  />
        <StatCard icon={FileText} label="Assignments Submitted"  value={data?.performance_summary?.assignments_submitted ?? 0}     color="#FFBE0B" delay={0.15} />
      </div>

      {/* Section 2: Engagement Pie + Usage Hours */}
      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "30px", marginBottom: "40px" }}>
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }} className="parent-card" style={{ padding: "30px" }}>
          <h3 style={{ fontWeight: 900, fontSize: "1.3rem", marginBottom: "24px" }}>
            <Brain size={20} style={{ marginRight: "10px", verticalAlign: "middle", color: "var(--highlight)" }} />
            Engagement Profile
          </h3>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={4} dataKey="value">
                {pieData.map((_, i) => <Cell key={i} fill={ENG_COLORS[i]} />)}
              </Pie>
              <Tooltip contentStyle={{ borderRadius: "12px", border: "none" }} />
              <Legend iconType="circle" />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.25 }} className="parent-card" style={{ padding: "30px" }}>
          <h3 style={{ fontWeight: 900, fontSize: "1.3rem", marginBottom: "24px" }}>
            <Clock size={20} style={{ marginRight: "10px", verticalAlign: "middle", color: "var(--highlight)" }} />
            Usage Hours
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {[
              { label: "Today",     value: data?.time_analytics?.usage_hours?.today ?? 0,  color: "#6C63FF" },
              { label: "This Week", value: data?.time_analytics?.usage_hours?.week  ?? 0,  color: "#FFBE0B" },
              { label: "This Month",value: data?.time_analytics?.usage_hours?.month ?? 0,  color: "#FF006E" },
            ].map(({ label, value, color }) => (
              <div key={label}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
                  <span style={{ fontWeight: 700, color: "var(--secondary-text)", fontSize: "0.9rem" }}>{label}</span>
                  <span style={{ fontWeight: 900, color }}>{value}h</span>
                </div>
                <div style={{ height: "10px", background: "var(--neutral)", borderRadius: "99px", overflow: "hidden" }}>
                  <div style={{ height: "100%", width: `${Math.min((value / 50) * 100, 100)}%`, background: color, borderRadius: "99px", transition: "width 0.8s ease" }} />
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Section 3: Skill Gap Analysis */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="parent-card" style={{ padding: "30px", marginBottom: "40px" }}>
        <h3 style={{ fontWeight: 900, fontSize: "1.3rem", marginBottom: "24px" }}>
          <Zap size={20} style={{ marginRight: "10px", verticalAlign: "middle", color: "var(--highlight)" }} />
          Skill Gap Analysis
        </h3>
        <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: "40px", alignItems: "center" }}>
          <div>
            <p style={{ fontWeight: 800, marginBottom: "16px", color: "var(--secondary-text)", fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "1px" }}>Story Grammar Breakdown</p>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={sgData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--neutral)" />
                <XAxis type="number" domain={[0, 100]} tick={{ fill: "var(--secondary-text)", fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="name" tick={{ fill: "var(--primary-text)", fontSize: 13, fontWeight: 700 }} axisLine={false} tickLine={false} width={90} />
                <Tooltip contentStyle={{ borderRadius: "12px", border: "none" }} />
                <Bar dataKey="value" radius={[0, 8, 8, 0]}>
                  {sgData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div>
            <p style={{ fontWeight: 800, marginBottom: "16px", color: "var(--secondary-text)", fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "1px" }}>Connective Words Used</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "12px" }}>
              {connectives.map((c, i) => {
                const size = 0.8 + (c.count / maxCount) * 1.2;
                const alpha = Math.max(0.3, c.count / maxCount);
                return (
                  <div key={i} style={{
                    background: `rgba(108, 99, 255, ${alpha})`,
                    color: alpha > 0.5 ? "white" : "var(--highlight)",
                    padding: "8px 18px", borderRadius: "99px",
                    fontSize: `${size}rem`, fontWeight: 800,
                    border: "2px solid rgba(108,99,255,0.2)"
                  }}>
                    {c.word} <span style={{ opacity: 0.7, fontSize: "0.8em" }}>×{c.count}</span>
                  </div>
                );
              })}
              {connectives.length === 0 && <p style={{ color: "var(--secondary-text)" }}>No connective data yet.</p>}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Section 4: Biometric Chart */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }} className="parent-card" style={{ padding: "30px", marginBottom: "40px" }}>
        <h3 style={{ fontWeight: 900, fontSize: "1.3rem", marginBottom: "24px" }}>
          <Activity size={20} style={{ marginRight: "10px", verticalAlign: "middle", color: "var(--accent-color)" }} />
          Biometric Correlation (Heart Rate over Tasks)
        </h3>
        {biometric.length > 0 ? (
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={biometric}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--neutral)" />
              <XAxis dataKey="task" tick={{ fill: "var(--secondary-text)", fontSize: 13, fontWeight: 700 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "var(--secondary-text)", fontSize: 12 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ borderRadius: "12px", border: "none" }} />
              <Legend />
              <Line type="monotone" dataKey="hr" name="Heart Rate (bpm)" stroke="#FF5E5E" strokeWidth={3} dot={{ r: 6, fill: "#FF5E5E" }} />
              <Line type="monotone" dataKey="gsr" name="GSR ×100" stroke="#6C63FF" strokeWidth={3} dot={{ r: 5, fill: "#6C63FF" }} strokeDasharray="5 5" />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div style={{ textAlign: "center", padding: "60px", color: "var(--secondary-text)" }}>
            <Activity size={40} style={{ opacity: 0.2, margin: "0 auto 16px" }} />
            <p>No biometric data recorded yet for this student.</p>
          </div>
        )}
      </motion.div>

      {/* Section 5: AI Orchestrator */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "20px" }}>
        <StatCard icon={Brain}    label="Total Prompts Needed"  value={data?.ai_orchestrator_logs?.total_prompts_needed ?? 0}  color="#6C63FF" delay={0.4} />
        <StatCard icon={Target}   label="Autonomy Score"        value={`${data?.ai_orchestrator_logs?.autonomy_score ?? 0}%`}  color="#00b894" delay={0.45} />
        <StatCard icon={Zap}      label="Preferred Topic"       value={data?.ai_orchestrator_logs?.preferred_topic ?? "N/A"}  color="#FFBE0B" delay={0.5} />
      </div>
    </div>
  );
}
