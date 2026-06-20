import React, { useEffect, useState } from "react";
import { useParams, Link, useLocation, useNavigate } from "react-router-dom";
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
  Heart,
  Info,
  Calendar,
  FileText,
  Users,
  Activity
} from "lucide-react";
import api from "../../../services/api";
import Logo from "../../../components/ui/logo";

export default function ChildInsights() {
  const { studentId } = useParams();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const initialTab = queryParams.get("tab") || "academic";
  const navigate = useNavigate();
  
  const [activeTab, setActiveTab] = useState(initialTab);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [childrenList, setChildrenList] = useState([]);

  useEffect(() => {
    // Fetch parent's children for the dropdown
    api.get("/parent/my-children")
      .then(res => setChildrenList(Array.isArray(res.data) ? res.data : []))
      .catch(err => console.error("Failed to load children list:", err));
  }, []);

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

  const sentimentValues = Array.isArray(data.sentiment_trend?.values) ? data.sentiment_trend.values : [];
  const sentimentLabels = Array.isArray(data.sentiment_trend?.labels) ? data.sentiment_trend.labels : [];
  const sentimentData = sentimentValues.map((val, idx) => ({
    day: sentimentLabels[idx],
    value: val
  }));

  return (
    <div className="parent-dashboard-wrapper report-container full-width-print">
      {/* Header */}
      <div className="no-print" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "40px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
          <button onClick={() => navigate(-1)} className="btn btn-outline" style={{ borderRadius: "15px", padding: "10px", height: "fit-content" }}>
            <ChevronLeft size={24} />
          </button>
          <div>
            <h1 className="topbar-title" style={{ fontSize: "2.5rem" }}>{data.child_name}'s Journey</h1>
            <p style={{ color: "var(--secondary-text)" }}>Detailed academic and emotional breakdown.</p>
          </div>
        </div>
        
        <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
          {childrenList.length > 0 && (
            <div style={{ background: "white", padding: "10px 20px", borderRadius: "16px", display: "flex", alignItems: "center", gap: "12px", boxShadow: "0 4px 15px rgba(0,0,0,0.05)", border: "1px solid var(--neutral)" }}>
              <Users size={20} color="var(--highlight)" />
              <select 
                value={studentId} 
                onChange={(e) => navigate(`/students/${e.target.value}/insights${location.search}`)}
                style={{ border: "none", outline: "none", fontSize: "1.05rem", fontWeight: 700, color: "var(--primary-text)", background: "transparent", cursor: "pointer", paddingRight: "10px" }}
              >
                {childrenList.map(c => (
                  <option key={c.id} value={c.id}>{c.username} (ID: {c.id})</option>
                ))}
              </select>
            </div>
          )}
          <button className="btn btn-primary" style={{ padding: "15px 30px" }} onClick={handlePrint}>
            <Download size={20} />
            Download PDF Report
          </button>
        </div>
      </div>

      {/* Print-only Professional Header */}
      <div className="print-only" style={{ marginBottom: "60px", textAlign: "center", borderBottom: "4px solid var(--highlight)", paddingBottom: "40px" }}>
        <div style={{ marginBottom: "30px", display: "flex", justifyContent: "center" }}>
          <Logo />
        </div>
        <h1 style={{ fontSize: "5.5rem", fontWeight: "950", margin: "10px 0", color: "#000" }}>{data.child_name}</h1>
        <p style={{ fontSize: "1.8rem", color: "var(--secondary-text)", textTransform: "uppercase", letterSpacing: "5px", fontWeight: "800" }}>Comprehensive Performance Report</p>
        <div style={{ display: "flex", justifyContent: "center", gap: "60px", marginTop: "50px", fontSize: "1.4rem", fontWeight: "700", borderTop: "1px solid #eee", paddingTop: "30px" }}>
          <span><strong>Date:</strong> {new Date().toLocaleDateString()}</span>
          <span><strong>ID:</strong> BASEET-{studentId}</span>
          <span><strong>Institution:</strong> Baseet Academy</span>
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

      <div className="parent-grid-print" style={{ display: "grid", gridTemplateColumns: "2.5fr 1fr", gap: "40px" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "50px" }}>
          
          {/* Academic Section */}
          <section className={`print-section ${activeTab === 'academic' ? '' : 'no-print-tab'}`}>
            <h2 className="print-only" style={{ fontSize: "2.5rem", marginBottom: "30px", color: "var(--highlight)", borderLeft: "10px solid var(--highlight)", paddingLeft: "20px" }}>I. Academic Performance</h2>
            <div className="parent-stat-row" style={{ gridTemplateColumns: "1fr 1fr 1fr", marginBottom: "30px", display: "grid", gap: "20px" }}>
              <div className="parent-stat-box" style={{ padding: "25px", textAlign: "center" }}>
                <Clock size={28} color="var(--highlight)" style={{ marginBottom: "15px" }} />
                <p className="parent-stat-label" style={{ fontSize: "1rem" }}>Daily Study Time</p>
                <p className="parent-stat-value" style={{ fontSize: "1.8rem" }}>{data.time_well_spent.study_hours_today}</p>
              </div>
              <div className="parent-stat-box" style={{ padding: "25px", textAlign: "center" }}>
                <Target size={28} color="var(--highlight)" style={{ marginBottom: "15px" }} />
                <p className="parent-stat-label" style={{ fontSize: "1rem" }}>Concentration Index</p>
                <p className="parent-stat-value" style={{ fontSize: "1.8rem" }}>{data.time_well_spent.focus_score}</p>
              </div>
              <div className="parent-stat-box" style={{ padding: "25px", textAlign: "center" }}>
                <Zap size={28} color="var(--highlight)" style={{ marginBottom: "15px" }} />
                <p className="parent-stat-label" style={{ fontSize: "1rem" }}>Learning Rate</p>
                <p className="parent-stat-value" style={{ fontSize: "1.8rem" }}>92%</p>
              </div>
            </div>

            <div className="parent-card" style={{ padding: "40px" }}>
              <h3 className="parent-section-title" style={{ fontSize: "1.8rem", marginBottom: "20px" }}>
                <Compass size={32} />
                Daily Mastery Roadmap
              </h3>
              <p style={{ fontSize: "1.1rem", color: "var(--secondary-text)", marginBottom: "40px", lineHeight: "1.6" }}>
                A granular breakdown of the student's learning path today, highlighting successful milestones and areas requiring reinforcement.
              </p>
              <div style={{ padding: "10px 0" }}>
                {(Array.isArray(data.learning_journey_map) ? data.learning_journey_map : []).map((item, idx) => (
                  <div key={idx} style={{ display: "flex", gap: "30px", marginBottom: "40px", borderLeft: "5px dashed var(--neutral)", paddingLeft: "45px", position: "relative" }}>
                    <div style={{ position: "absolute", left: "-18px", top: "0", width: "32px", height: "32px", borderRadius: "50%", background: item.success === true ? "var(--success-bg)" : item.success === false ? "var(--error-bg)" : "var(--neutral)", border: "5px solid white", boxShadow: "0 4px 15px rgba(0,0,0,0.1)" }} />
                    <div style={{ flex: 1 }}>
                      <span style={{ fontSize: "0.9rem", fontWeight: "900", color: "var(--secondary-text)", textTransform: "uppercase", letterSpacing: "2px" }}>{item.stage} Session</span>
                      <h4 style={{ fontSize: "1.5rem", fontWeight: "800", marginTop: "10px", color: "var(--primary-text)" }}>{item.activity}</h4>
                      <div style={{ marginTop: "10px", padding: "15px", background: "var(--primary-bg)", borderRadius: "12px", borderLeft: `5px solid ${item.success === true ? 'var(--success-bg)' : 'var(--error-bg)'}` }}>
                        <p style={{ fontSize: "1.05rem", color: "var(--primary-text)", fontWeight: "600" }}>
                          Status: {item.success === true ? "Mastered" : item.success === false ? "Review Suggested" : "In Progress"}
                        </p>
                        <p style={{ fontSize: "0.95rem", color: "var(--secondary-text)", marginTop: "5px" }}>
                          {item.success === true ? "The student demonstrated clear understanding and completed all interactive modules with high accuracy." : "Some concepts in this session proved challenging. We recommend a quick recap of this topic together."}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* Emotional Section - Page Break on Print */}
          <section className={`print-section ${activeTab === 'emotional' ? '' : 'no-print-tab'}`} style={{ pageBreakBefore: "always", paddingTop: "50px" }}>
            <h2 className="print-only" style={{ fontSize: "2.5rem", marginBottom: "30px", color: "var(--accent-color)", borderLeft: "10px solid var(--accent-color)", paddingLeft: "20px" }}>II. Emotional & Engagement Analysis</h2>
            <div className="parent-stat-row" style={{ gridTemplateColumns: "1fr 1fr 1fr", marginBottom: "30px", display: "grid", gap: "20px" }}>
              <div className="parent-stat-box" style={{ padding: "25px", textAlign: "center" }}>
                <Smile size={28} color="var(--accent-color)" style={{ marginBottom: "15px" }} />
                <p className="parent-stat-label" style={{ fontSize: "1rem" }}>Current State</p>
                <p className="parent-stat-value" style={{ fontSize: "1.8rem" }}>{data.daily_snapshot.overall_mood}</p>
              </div>
              <div className="parent-stat-box" style={{ padding: "25px", textAlign: "center" }}>
                <Zap size={28} color="var(--secondary-color)" style={{ marginBottom: "15px" }} />
                <p className="parent-stat-label" style={{ fontSize: "1rem" }}>Energy Profile</p>
                <p className="parent-stat-value" style={{ fontSize: "1.8rem" }}>{data.daily_snapshot.energy_level}</p>
              </div>
              <div className="parent-stat-box" style={{ padding: "25px", textAlign: "center" }}>
                <Activity size={28} color="var(--highlight)" style={{ marginBottom: "15px" }} />
                <p className="parent-stat-label" style={{ fontSize: "1rem" }}>Social Response</p>
                <p className="parent-stat-value" style={{ fontSize: "1.8rem" }}>{data.daily_snapshot.social_engagement}</p>
              </div>
            </div>

            <div className="parent-card" style={{ padding: "40px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "30px" }}>
                <h3 className="parent-section-title" style={{ fontSize: "1.8rem" }}>
                  <TrendingUp size={32} color="var(--accent-color)" />
                  Weekly Engagement Index
                </h3>
                <div style={{ background: "var(--primary-bg)", padding: "10px 20px", borderRadius: "15px", display: "flex", alignItems: "center", gap: "10px", fontSize: "1rem", color: "var(--secondary-text)", fontWeight: "700" }}>
                  <Info size={18} />
                  Range: 0 (Low) - 100 (Peak)
                </div>
              </div>
              <p style={{ fontSize: "1.1rem", color: "var(--secondary-text)", marginBottom: "40px", lineHeight: "1.6" }}>
                This trend line tracks real-time emotional positivity. Consistency in the 70-90 range indicates a healthy, sustainable learning pace.
              </p>
              <div style={{ height: "450px", width: "100%", marginTop: "30px" }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={sentimentData}>
                    <defs>
                      <linearGradient id="colorVal" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="var(--accent-color)" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="var(--accent-color)" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--neutral)" />
                    <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{fill: 'var(--secondary-text)', fontSize: 14, fontWeight: "600"}} />
                    <YAxis hide domain={[0, 100]} />
                    <Tooltip contentStyle={{ borderRadius: "15px", border: "none", boxShadow: "0 10px 30px rgba(0,0,0,0.1)" }} />
                    <Area type="monotone" dataKey="value" stroke="var(--accent-color)" strokeWidth={5} fill="url(#colorVal)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </section>

          {/* Expert Observations - Print Only */}
          <div className="print-only" style={{ pageBreakBefore: "always", paddingTop: "50px" }}>
             <h2 style={{ fontSize: "2.5rem", borderBottom: "4px solid #000", paddingBottom: "20px", marginBottom: "40px", color: "#000" }}>
               <FileText size={32} style={{ marginRight: "15px" }} />
               III. Clinical & Pedagogical Summary
             </h2>
             <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "40px" }}>
               <div style={{ padding: "40px", border: "2px solid #eee", borderRadius: "25px" }}>
                 <h4 style={{ color: "var(--highlight)", fontSize: "1.5rem", marginBottom: "20px", fontWeight: "900" }}>Focus & Cognitive Engagement</h4>
                 <p style={{ fontSize: "1.2rem", lineHeight: "1.8", color: "#333" }}>
                   Data suggests that {data.child_name} is currently performing at an optimal cognitive load. 
                   The concentration score of {data.time_well_spent.focus_score} indicates strong task persistence. 
                   We observed the highest engagement during the "{Array.isArray(data.learning_journey_map) && data.learning_journey_map[0]?.activity}" module.
                 </p>
               </div>
               <div style={{ padding: "40px", border: "2px solid #eee", borderRadius: "25px" }}>
                 <h4 style={{ color: "var(--accent-color)", fontSize: "1.5rem", marginBottom: "20px", fontWeight: "900" }}>Emotional Resilience</h4>
                 <p style={{ fontSize: "1.2rem", lineHeight: "1.8", color: "#333" }}>
                   The student's emotional baseline is "{data.daily_snapshot.overall_mood}". 
                   There is a direct correlation between successful problem-solving and the positivity spikes seen in the weekly trend. 
                   Engagement remains {data.daily_snapshot.social_engagement}, showing great social-emotional growth.
                 </p>
               </div>
             </div>
             
             <div style={{ marginTop: "100px", textAlign: "center", borderTop: "1px solid #ddd", paddingTop: "40px" }}>
               <p style={{ fontSize: "1rem", color: "#999" }}>Generated by Baseet AI Intelligence System • End of Report</p>
             </div>
          </div>
        </div>

        {/* Toolkit Sidebar */}
        <div style={{ display: "flex", flexDirection: "column", gap: "30px" }}>
          <div className="parent-card" style={{ background: "#1A1C1E", color: "white", borderColor: "rgba(255,255,255,0.1)", boxShadow: "0 20px 50px rgba(0,0,0,0.3)", padding: "40px" }}>
            <h3 style={{ display: "flex", alignItems: "center", gap: "15px", marginBottom: "40px", fontSize: "1.8rem", fontWeight: "950" }}>
              <Lightbulb color="var(--primary-color)" size={32} />
              Parental Toolkit
            </h3>
            
            <div style={{ marginBottom: "40px" }}>
              <p style={{ fontSize: "0.9rem", fontWeight: "900", opacity: 0.6, textTransform: "uppercase", letterSpacing: "2px", marginBottom: "15px" }}>Discussion Starter</p>
              <p style={{ fontSize: "1.5rem", fontWeight: "700", lineHeight: "1.6", color: "var(--primary-color)" }}>"{data.parent_toolkit.discuss_today}"</p>
            </div>

            <div style={{ background: "rgba(255,255,255,0.03)", padding: "25px", borderRadius: "25px", marginBottom: "40px", border: "1px solid rgba(255,255,255,0.08)" }}>
              <h4 style={{ fontSize: "1.1rem", marginBottom: "10px", color: "white" }}>Recommended Activity</h4>
              <p style={{ fontSize: "1.1rem", lineHeight: "1.6", opacity: 0.9 }}>{data.parent_toolkit.suggested_activity}</p>
            </div>

            <div>
              <p style={{ fontSize: "0.9rem", fontWeight: "900", opacity: 0.6, textTransform: "uppercase", letterSpacing: "2px", marginBottom: "20px" }}>Active Vocabulary</p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "12px" }}>
                {(Array.isArray(data.parent_toolkit?.new_words) ? data.parent_toolkit.new_words : []).map((w, i) => (
                  <span key={i} style={{ background: "var(--highlight)", color: "white", padding: "10px 20px", borderRadius: "15px", fontSize: "1rem", fontWeight: "800" }}>{w}</span>
                ))}
              </div>
            </div>
          </div>

          <div className="parent-card no-print" style={{ background: "var(--primary-bg)", textAlign: "center", border: "2px dashed var(--neutral)", padding: "30px" }}>
            <Calendar size={40} color="var(--secondary-text)" style={{ margin: "0 auto 20px", opacity: 0.5 }} />
            <h4 style={{ fontWeight: "900", fontSize: "1.3rem", marginBottom: "15px" }}>Adjustment Center</h4>
            <p style={{ fontSize: "1rem", color: "var(--secondary-text)", marginBottom: "30px" }}>Customize {data.child_name}'s learning environment for tomorrow's sessions.</p>
            <Link to={`/dashboard/parent/child/${studentId}/settings`} className="parent-btn-wide" style={{ background: "white", border: "2px solid var(--neutral)", fontSize: "1.1rem" }}>
              Configure Settings
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
