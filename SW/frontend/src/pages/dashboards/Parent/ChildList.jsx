import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { 
  Search, 
  Users, 
  TrendingUp, 
  HeartPulse, 
  ChevronRight,
  Activity
} from "lucide-react";
import api from "../../../services/api";

export default function ChildList() {
  const [children, setChildren] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    const fetchChildren = async () => {
      try {
        const res = await api.get("/parent/my-children");
        setChildren(res.data);
      } catch (err) {
        console.error("Error fetching children:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchChildren();
  }, []);

  const filteredChildren = children.filter(c => 
    c.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <div className="status checking p-10">Loading profiles...</div>;
  }

  return (
    <div className="parent-dashboard-wrapper">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "40px" }}>
        <div>
          <h1 className="topbar-title" style={{ fontSize: "2.5rem" }}>Children Profiles</h1>
          <p style={{ color: "var(--secondary-text)" }}>Explore individual progress and manage insights.</p>
        </div>

        <div style={{ position: "relative" }}>
          <Search style={{ position: "absolute", left: "15px", top: "50%", transform: "translateY(-50%)", color: "var(--secondary-text)" }} size={18} />
          <input 
            type="text" 
            placeholder="Search name..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ paddingLeft: "45px", marginBottom: 0, width: "250px" }}
          />
        </div>
      </div>

      {filteredChildren.length > 0 ? (
        <div className="parent-grid" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(400px, 1fr))" }}>
          {filteredChildren.map((child) => (
            <div key={child.id} className="parent-card">
              <div className="parent-card-header" style={{ marginBottom: "25px" }}>
                <div className="child-avatar-circle">
                  {child.name.charAt(0)}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <h3 style={{ fontSize: "1.6rem", fontWeight: "900" }}>{child.name}</h3>
                    <div className={`online-status-badge ${child.online ? 'status-online' : 'status-offline'}`} style={{ position: "static" }}>
                      <div className="status-dot" />
                      {child.online ? 'Online Now' : 'Offline'}
                    </div>
                  </div>
                  <p style={{ color: "var(--secondary-text)", fontSize: "0.95rem" }}>
                    Learning Difficulty: Level {child.difficulty_level}
                  </p>
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "15px" }}>
                <Link 
                  to={`/dashboard/parent/students/${child.id}/insights?tab=academic`}
                  className="parent-btn-wide"
                  style={{ background: "var(--primary-bg)", color: "var(--highlight)", border: "2px solid var(--highlight)" }}
                >
                  <TrendingUp size={20} />
                  Academic Insights
                </Link>
                
                <Link 
                  to={`/dashboard/parent/students/${child.id}/insights?tab=emotional`}
                  className="parent-btn-wide"
                  style={{ background: "var(--secondary-bg)", color: "var(--secondary-text)", border: "2px solid var(--neutral)" }}
                >
                  <HeartPulse size={20} />
                  Emotional Insights
                </Link>
              </div>

              <div style={{ marginTop: "20px", paddingTop: "20px", borderTop: "1px solid var(--neutral)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px", color: "var(--secondary-text)", fontSize: "0.85rem" }}>
                  <Activity size={16} />
                  <span>Last activity: Today at 10:45 AM</span>
                </div>
                <Link to={`/dashboard/parent/child/${child.id}/settings`} style={{ fontSize: "0.85rem", fontWeight: "800", color: "var(--highlight)", display: "flex", alignItems: "center" }}>
                  Manage Settings <ChevronRight size={14} />
                </Link>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="parent-card" style={{ textAlign: "center", padding: "100px" }}>
          <Users size={80} style={{ opacity: 0.1, marginBottom: "20px" }} />
          <h2>No children found</h2>
          <p style={{ color: "var(--secondary-text)" }}>Try searching for a different name or link a new child.</p>
        </div>
      )}
    </div>
  );
}
