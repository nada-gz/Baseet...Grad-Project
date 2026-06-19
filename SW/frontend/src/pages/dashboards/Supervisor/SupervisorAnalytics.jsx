import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend, Cell
} from "recharts";
import { Users, BookOpen, Server, TrendingUp, ShieldCheck, AlertTriangle, Activity, Clock, AlertCircle } from "lucide-react";
import { fetchSupervisorDashboard } from "../../../api/dashboard";
import api from "../../../services/api";

const StatCard = ({ icon: Icon, label, value, color, delay = 0, critical = false }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }}
    className="parent-card"
    style={{
      display: "flex", alignItems: "center", gap: "20px", padding: "24px",
      borderLeft: `6px solid ${color}`,
      ...(critical ? { border: `4px solid var(--error-bg)`, boxShadow: "0 0 20px rgba(255,94,94,0.2)" } : {})
    }}
  >
    <div style={{ background: color + "18", borderRadius: "16px", padding: "14px" }}>
      <Icon size={28} color={color} />
    </div>
    <div>
      <p style={{ fontSize: "0.8rem", color: "var(--secondary-text)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "1px", marginBottom: "4px" }}>{label}</p>
      <p style={{ fontSize: "1.8rem", fontWeight: 950, lineHeight: 1, color: critical ? "var(--error-bg)" : "var(--primary-text)" }}>{value}</p>
    </div>
  </motion.div>
);

export default function SupervisorAnalytics() {
  const [students, setStudents] = useState([]);
  const [selectedStudentId, setSelectedStudentId] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    // Fetch available students
    api.get("/supervisor/students/all")
      .then(res => {
        if (res.data && res.data.length > 0) {
          setStudents(res.data);
          // Don't auto-select to show org-wide by default, or auto-select the first if needed.
          // Let's keep it null by default for org-wide view.
        }
      })
      .catch(err => console.error("Failed to load students:", err));
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);
    // If selectedStudentId is empty/null, it fetches org-wide
    fetchSupervisorDashboard(selectedStudentId)
      .then(setData)
      .catch(err => setError(err.response?.data?.detail || err.message || "Failed to load report"))
      .finally(() => setLoading(false));
  }, [selectedStudentId, retryCount]);

  if (loading) {
    return (
      <div className="parent-dashboard-wrapper" style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "60vh", flexDirection: "column", gap: "20px" }}>
        <div className="auth-spinner" />
        <p style={{ color: "var(--secondary-text)", fontWeight: 700 }}>Generating organization analytics…</p>
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

  const classData = (data?.class_comparison_chart ?? []).map(c => ({
    name: c.class,
    Progress: c.progress,
    "Stress Index": c.stress_index
  }));

  const resourceData = (data?.resource_utilization ?? []).map(r => ({
    name: r.module,
    usage: r.usage
  }));

  const kpi = data?.kpi_cards ?? {};
  const org = data?.org_time_metrics ?? {};
  const safety = data?.safety_and_wellness ?? {};

  return (
    <div className="parent-dashboard-wrapper">
      {/* Dark Hero Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}
        style={{
          background: "#1A1C1E", borderRadius: "24px", padding: "40px 48px",
          marginBottom: "40px", color: "white", display: "flex", justifyContent: "space-between", alignItems: "center"
        }}
      >
        <div>
          <h1 style={{ fontSize: "2.5rem", fontWeight: 950, marginBottom: "8px" }}>Organization Analytics</h1>
          <p style={{ color: "rgba(255,255,255,0.6)", fontSize: "1rem" }}>
            {selectedStudentId 
              ? `Student ID: ${selectedStudentId} · AI-powered analysis` 
              : `AI-powered dashboard for org-wide metrics · ${data?.org_id}`}
          </p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
          {/* Student Selector */}
          {students.length > 0 && (
            <div style={{ background: "rgba(255,255,255,0.1)", padding: "10px 20px", borderRadius: "16px", display: "flex", alignItems: "center", gap: "12px", border: "1px solid rgba(255,255,255,0.2)" }}>
              <Users size={20} color="rgba(255,255,255,0.8)" />
              <select 
                value={selectedStudentId || ""} 
                onChange={(e) => setSelectedStudentId(e.target.value ? Number(e.target.value) : null)}
                style={{ border: "none", outline: "none", fontSize: "1.05rem", fontWeight: 700, color: "white", background: "transparent", cursor: "pointer", paddingRight: "10px" }}
              >
                <option value="" style={{ color: "black" }}>Org-Wide Overview</option>
                {students.map(s => (
                  <option key={s.id} value={s.id} style={{ color: "black" }}>{s.username} (ID: {s.id})</option>
                ))}
              </select>
            </div>
          )}
          <div style={{ background: "rgba(108,99,255,0.2)", border: "2px solid rgba(108,99,255,0.4)", borderRadius: "16px", padding: "16px 28px", textAlign: "center" }}>
            <p style={{ fontSize: "0.75rem", color: "rgba(255,255,255,0.5)", fontWeight: 700, letterSpacing: "2px", textTransform: "uppercase", marginBottom: "4px" }}>Uptime</p>
            <p style={{ fontSize: "2rem", fontWeight: 950, color: "#00b894" }}>{kpi.system_uptime ?? 0}%</p>
          </div>
        </div>
      </motion.div>

      {/* Section 1: KPI Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "20px", marginBottom: "40px" }}>
        <StatCard icon={Users}      label="Total Students"       value={kpi.total_students ?? 0}           color="#6C63FF" delay={0.05} />
        <StatCard icon={BookOpen}   label="Lessons Completed"    value={kpi.total_lessons_completed ?? 0}  color="#00b894" delay={0.1}  />
        <StatCard icon={Server}     label="System Uptime"        value={`${kpi.system_uptime ?? 0}%`}     color="#FFBE0B" delay={0.15} />
        <StatCard icon={TrendingUp} label="Avg Org Progress"     value={`${kpi.avg_org_progress ?? 0}%`}  color="#FB5607" delay={0.2}  />
      </div>

      {/* Section 2: Class Comparison + Org Metrics */}
      <div style={{ display: "grid", gridTemplateColumns: "1.6fr 1fr", gap: "30px", marginBottom: "40px" }}>
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.25 }} className="parent-card" style={{ padding: "30px" }}>
          <h3 style={{ fontWeight: 900, fontSize: "1.3rem", marginBottom: "24px" }}>
            <TrendingUp size={20} style={{ marginRight: "10px", verticalAlign: "middle", color: "var(--highlight)" }} />
            Class Comparison
          </h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={classData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--neutral)" />
              <XAxis dataKey="name" tick={{ fill: "var(--secondary-text)", fontSize: 12, fontWeight: 700 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "var(--secondary-text)", fontSize: 12 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ borderRadius: "12px", border: "none" }} />
              <Legend />
              <Bar dataKey="Progress" fill="#6C63FF" radius={[8, 8, 0, 0]} />
              <Bar dataKey="Stress Index" fill="#FF5E5E" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }} className="parent-card" style={{ padding: "30px" }}>
          <h3 style={{ fontWeight: 900, fontSize: "1.3rem", marginBottom: "24px" }}>
            <Clock size={20} style={{ marginRight: "10px", verticalAlign: "middle", color: "var(--highlight)" }} />
            Org Time Metrics
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {[
              { label: "Avg Hours / Student / Day", value: `${org.avg_hours_per_student_daily ?? 0}h`,  color: "#6C63FF" },
              { label: "Total Hours This Month",    value: `${(org.total_hours_this_month ?? 0).toLocaleString()}h`, color: "#FFBE0B" },
              { label: "Org Focus Average",         value: `${org.org_focus_avg ?? 0}%`,               color: "#00b894" },
              { label: "Org Stress Average",        value: `${org.org_stress_avg ?? 0}%`,              color: "#FF5E5E" },
            ].map(({ label, value, color }) => (
              <div key={label} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 0", borderBottom: "2px solid var(--neutral)" }}>
                <span style={{ fontWeight: 700, color: "var(--secondary-text)", fontSize: "0.9rem" }}>{label}</span>
                <span style={{ fontWeight: 950, color, fontSize: "1.3rem" }}>{value}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Section 3: Resource Utilization */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }} className="parent-card" style={{ padding: "30px", marginBottom: "40px" }}>
        <h3 style={{ fontWeight: 900, fontSize: "1.3rem", marginBottom: "24px" }}>
          <Activity size={20} style={{ marginRight: "10px", verticalAlign: "middle", color: "var(--highlight)" }} />
          Resource Utilization
        </h3>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={resourceData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--neutral)" />
            <XAxis type="number" tick={{ fill: "var(--secondary-text)", fontSize: 12 }} axisLine={false} tickLine={false} />
            <YAxis type="category" dataKey="name" tick={{ fill: "var(--primary-text)", fontSize: 13, fontWeight: 700 }} axisLine={false} tickLine={false} width={100} />
            <Tooltip contentStyle={{ borderRadius: "12px", border: "none" }} />
            <Bar dataKey="usage" fill="#6C63FF" radius={[0, 8, 8, 0]}>
              {resourceData.map((_, i) => <Cell key={i} fill={["#6C63FF", "#FF006E", "#FFBE0B", "#00b894"][i % 4]} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </motion.div>

      {/* Section 4: Safety & Wellness */}
      <h2 style={{ fontWeight: 900, fontSize: "1.5rem", marginBottom: "20px" }}>
        <ShieldCheck size={24} style={{ marginRight: "10px", verticalAlign: "middle", color: "var(--highlight)" }} />
        Safety & Wellness
      </h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "20px" }}>
        <StatCard icon={AlertTriangle} label="Stress Alerts (Week)" value={safety.stress_alerts_weekly ?? 0}  color="#FFBE0B" delay={0.4} />
        <StatCard icon={ShieldCheck}   label="Resolved Cases"        value={safety.resolved_cases ?? 0}        color="#00b894" delay={0.45} />
        <StatCard
          icon={AlertTriangle}
          label="Critical Alerts"
          value={safety.critical_alerts ?? 0}
          color="var(--error-bg)"
          delay={0.5}
          critical={(safety.critical_alerts ?? 0) > 0}
        />
      </div>
    </div>
  );
}
