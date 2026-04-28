import React, { useEffect, useState } from "react";
import { useParams, Link, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  AreaChart, Area 
} from "recharts";
import { 
  ChevronLeft, 
  Download, 
  BookOpen, 
  Smile, 
  TrendingUp, 
  Target, 
  Zap, 
  Compass,
  Lightbulb,
  Clock,
  Activity,
  Heart,
  Info,
  Calendar,
  FileText
} from "lucide-react";
import api from "../../../services/api";

export default function ChildInsights() {
  const { studentId } = useParams();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const initialTab = queryParams.get("tab") || "academic";
  
  const [activeTab, setActiveTab] = useState(initialTab);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInsights = async () => {
      try {
        const response = await api.get(`/parent/child/${studentId}/insights`);
        setData(response.data);
      } catch (err) {
        console.error("Error fetching insights:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchInsights();
  }, [studentId]);

  useEffect(() => {
    const tab = queryParams.get("tab");
    if (tab) setActiveTab(tab);
  }, [location.search]);

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return <div className="status checking p-10">Analyzing insights...</div>;
  }

  if (!data) return <div className="parent-card p-10 text-center">No data available for this profile.</div>;

  const sentimentData = data.sentiment_trend.values.map((val, idx) => ({
    day: data.sentiment_trend.labels[idx],
    value: val
  }));

  return (
    <div className="parent-dashboard-wrapper report-container">
      {/* Header */}
      <div className="no-print" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "40px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
          <Link to="/dashboard/parent/students" className="btn btn-outline" style={{ borderRadius: "15px", padding: "10px" }}>
            <ChevronLeft size={24} />
          </Link>
          <div>
            <h1 className="topbar-title" style={{ fontSize: "2.5rem" }}>{data.child_name}'s Journey</h1>
            <p style={{ color: "var(--secondary-text)" }}>Detailed academic and emotional breakdown.</p>
          </div>
        </div>
        
        <button className="btn btn-primary" style={{ padding: "15px 30px" }} onClick={handlePrint}>
          <Download size={20} />
          Download PDF Report
        </button>
      </div>

      {/* Print-only Official Header */}
      <div className="print-only" style={{ marginBottom: "50px", borderBottom: "2px solid #000", paddingBottom: "30px", textAlign: "center" }}>
        <div style={{ fontSize: "1rem", fontWeight: "900", color: "var(--highlight)", textTransform: "uppercase", letterSpacing: "2px", marginBottom: "10px" }}>Official Student Analytics Report</div>
        <h1 style={{ fontSize: "3rem", margin: "10px 0", color: "#000" }}>Baseet Learning Platform</h1>
        <div style={{ display: "flex", justifyContent: "center", gap: "40px", marginTop: "20px", fontSize: "1.1rem" }}>
          <span><strong>Student:</strong> {data.child_name}</span>
          <span><strong>ID:</strong> #{studentId}</span>
          <span><strong>Date:</strong> {new Date().toLocaleDateString()}</span>
        </div>
      </div>

      {/* Tabs - Hidden on Print */}
      <div className="parent-tabs no-print">
        <button 
          className={`parent-tab ${activeTab === "academic" ? "active" : ""}`} 
          onClick={() => setActiveTab("academic")}
        >
          <BookOpen size={18} style={{ marginRight: "8px", verticalAlign: "middle" }} />
          Academic Insights
        </button>
        <button 
          className={`parent-tab ${activeTab === "emotional" ? "active" : ""}`} 
          onClick={() => setActiveTab("emotional")}
        >
          <Heart size={18} style={{ marginRight: "8px", verticalAlign: "middle" }} />
          Emotional Insights
        </button>
      </div>

      <div className="parent-grid" style={{ gridTemplateColumns: "2fr 1fr" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "40px" }}>
          
          {/* Conditional Rendering for Tabs */}
          <AnimatePresence mode="wait">
            {activeTab === "academic" && (
              <motion.div 
                key="academic"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
              >
                <div className="parent-stat-row" style={{ gridTemplateColumns: "1fr 1fr 1fr", marginBottom: "30px" }}>
                  <div className="parent-stat-box">
                    <Clock size={20} color="var(--highlight)" style={{ marginBottom: "10px" }} />
                    <p className="parent-stat-label">Study Time</p>
                    <p className="parent-stat-value">{data.time_well_spent.study_hours_today}</p>
                  </div>
                  <div className="parent-stat-box">
                    <Target size={20} color="var(--highlight)" style={{ marginBottom: "10px" }} />
                    <p className="parent-stat-label">Focus Score</p>
                    <p className="parent-stat-value">{data.time_well_spent.focus_score}</p>
                  </div>
                  <div className="parent-stat-box">
                    <Zap size={20} color="var(--highlight)" style={{ marginBottom: "10px" }} />
                    <p className="parent-stat-label">Success Rate</p>
                    <p className="parent-stat-value">92%</p>
                  </div>
                </div>

                <div className="parent-card">
                  <h3 className="parent-section-title" style={{ fontSize: "1.4rem" }}>
                    <Compass size={24} />
                    Daily Learning Success Map
                  </h3>
                  <p style={{ fontSize: "0.85rem", color: "var(--secondary-text)", marginBottom: "30px" }}>
                    Visual tracking of scheduled lessons and their current mastery status.
                  </p>
                  <div style={{ padding: "20px 0" }}>
                    {data.learning_journey_map.map((item, idx) => (
                      <div key={idx} style={{ display: "flex", gap: "20px", marginBottom: "30px", borderLeft: "4px dashed var(--neutral)", paddingLeft: "35px", position: "relative" }}>
                        <div style={{ position: "absolute", left: "-14px", top: "0", width: "24px", height: "24px", borderRadius: "50%", background: item.success === true ? "var(--success-bg)" : item.success === false ? "var(--error-bg)" : "var(--neutral)", border: "4px solid white", boxShadow: "0 2px 10px rgba(0,0,0,0.1)" }} />
                        <div>
                          <span style={{ fontSize: "0.75rem", fontWeight: "900", color: "var(--secondary-text)", textTransform: "uppercase", letterSpacing: "1px" }}>{item.stage}</span>
                          <h4 style={{ fontSize: "1.2rem", fontWeight: "800", marginTop: "8px" }}>{item.activity}</h4>
                          <p style={{ fontSize: "0.95rem", color: "var(--secondary-text)", marginTop: "4px" }}>
                            {item.success === true ? "Completed successfully" : item.success === false ? "Needs further review" : "Scheduled Activity"}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === "emotional" && (
              <motion.div 
                key="emotional"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
              >
                <div className="parent-stat-row" style={{ gridTemplateColumns: "1fr 1fr 1fr", marginBottom: "30px" }}>
                  <div className="parent-stat-box">
                    <Smile size={20} color="var(--accent-color)" style={{ marginBottom: "10px" }} />
                    <p className="parent-stat-label">Overall Mood</p>
                    <p className="parent-stat-value">{data.daily_snapshot.overall_mood}</p>
                  </div>
                  <div className="parent-stat-box">
                    <Zap size={20} color="var(--secondary-color)" style={{ marginBottom: "10px" }} />
                    <p className="parent-stat-label">Energy Level</p>
                    <p className="parent-stat-value">{data.daily_snapshot.energy_level}</p>
                  </div>
                  <div className="parent-stat-box">
                    <Activity size={20} color="var(--highlight)" style={{ marginBottom: "10px" }} />
                    <p className="parent-stat-label">Engagement</p>
                    <p className="parent-stat-value">{data.daily_snapshot.social_engagement}</p>
                  </div>
                </div>

                <div className="parent-card">
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <h3 className="parent-section-title" style={{ fontSize: "1.4rem" }}>
                      <TrendingUp size={24} color="var(--accent-color)" />
                      Weekly Positivity Index
                    </h3>
                    <div style={{ background: "var(--primary-bg)", padding: "8px 12px", borderRadius: "10px", display: "flex", alignItems: "center", gap: "8px", fontSize: "0.8rem", color: "var(--secondary-text)" }}>
                      <Info size={14} />
                      Range: 0 - 100
                    </div>
                  </div>
                  <p style={{ fontSize: "0.9rem", color: "var(--secondary-text)", marginTop: "15px" }}>
                    Continuous emotional analysis showing positivity levels during interaction with the platform.
                  </p>
                  <div style={{ height: "350px", width: "100%", marginTop: "30px" }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={sentimentData}>
                        <defs>
                          <linearGradient id="colorVal" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="var(--accent-color)" stopOpacity={0.2}/>
                            <stop offset="95%" stopColor="var(--accent-color)" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--neutral)" />
                        <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{fill: 'var(--secondary-text)', fontSize: 13}} />
                        <YAxis hide domain={[0, 100]} />
                        <Tooltip />
                        <Area type="monotone" dataKey="value" stroke="var(--accent-color)" strokeWidth={4} fill="url(#colorVal)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Print Only Academic Section */}
          <div className="print-only" style={{ marginTop: "30px" }}>
             <h2 style={{ fontSize: "1.8rem", borderBottom: "1px solid #ddd", paddingBottom: "10px", marginBottom: "20px" }}>
               <FileText size={24} style={{ marginRight: "10px" }} />
               Detailed Observations
             </h2>
             <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "30px" }}>
               <div style={{ padding: "20px", border: "1px solid #eee", borderRadius: "15px" }}>
                 <h4 style={{ color: "var(--highlight)", marginBottom: "10px" }}>Focus Analysis</h4>
                 <p style={{ fontSize: "1rem", lineHeight: "1.6" }}>
                   The student maintained an average focus score of {data.time_well_spent.focus_score}. 
                   This is {parseInt(data.time_well_spent.focus_score) > 70 ? 'above average' : 'within normal range'} for this difficulty level.
                 </p>
               </div>
               <div style={{ padding: "20px", border: "1px solid #eee", borderRadius: "15px" }}>
                 <h4 style={{ color: "var(--accent-color)", marginBottom: "10px" }}>Emotional Stability</h4>
                 <p style={{ fontSize: "1rem", lineHeight: "1.6" }}>
                   Overall mood recorded as {data.daily_snapshot.overall_mood}. 
                   Engagement levels remained {data.daily_snapshot.social_engagement} throughout the core learning sessions.
                 </p>
               </div>
             </div>
          </div>
        </div>

        {/* Toolkit Sidebar */}
        <div style={{ display: "flex", flexDirection: "column", gap: "30px" }}>
          <div className="parent-card" style={{ background: "#2D3436", color: "white", borderColor: "rgba(255,255,255,0.1)", boxShadow: "0 10px 30px rgba(0,0,0,0.15)" }}>
            <h3 style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "30px", fontSize: "1.5rem", fontWeight: "950" }}>
              <Lightbulb color="var(--primary-color)" size={28} />
              Parental Toolkit
            </h3>
            
            <div style={{ marginBottom: "30px" }}>
              <p style={{ fontSize: "0.8rem", fontWeight: "900", opacity: 0.7, textTransform: "uppercase", letterSpacing: "1px", marginBottom: "12px" }}>Daily Discussion Starter</p>
              <p style={{ fontSize: "1.25rem", fontWeight: "700", lineHeight: "1.5", color: "var(--primary-color)" }}>"{data.parent_toolkit.discuss_today}"</p>
            </div>

            <div style={{ background: "rgba(255,255,255,0.05)", padding: "20px", borderRadius: "20px", marginBottom: "30px", border: "1px solid rgba(255,255,255,0.1)" }}>
              <p style={{ fontSize: "1rem", lineHeight: "1.5" }}><strong>Nightly Activity:</strong> {data.parent_toolkit.suggested_activity}</p>
            </div>

            <div>
              <p style={{ fontSize: "0.8rem", fontWeight: "900", opacity: 0.7, textTransform: "uppercase", letterSpacing: "1px", marginBottom: "12px" }}>Curriculum Vocabulary</p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "10px" }}>
                {data.parent_toolkit.new_words.map((w, i) => (
                  <span key={i} style={{ background: "var(--highlight)", color: "white", padding: "6px 15px", borderRadius: "12px", fontSize: "0.85rem", fontWeight: "800" }}>{w}</span>
                ))}
              </div>
            </div>
          </div>

          <div className="parent-card no-print" style={{ background: "var(--primary-bg)", textAlign: "center", border: "2px dashed var(--neutral)" }}>
            <Calendar size={32} color="var(--secondary-text)" style={{ margin: "0 auto 15px", opacity: 0.5 }} />
            <h4 style={{ fontWeight: "800", marginBottom: "10px" }}>Adjustment Center</h4>
            <p style={{ fontSize: "0.85rem", color: "var(--secondary-text)", marginBottom: "20px" }}>Optimize {data.child_name}'s learning environment for tomorrow.</p>
            <Link to={`/dashboard/parent/child/${studentId}/settings`} className="parent-btn-wide" style={{ background: "white", border: "2px solid var(--neutral)" }}>
              Configure Settings
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
