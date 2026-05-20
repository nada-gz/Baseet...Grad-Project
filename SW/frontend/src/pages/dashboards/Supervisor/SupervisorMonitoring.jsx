import React, { useEffect, useState } from "react";
import { 
  Search, 
  ShieldAlert,
  ArrowLeft
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import api from "../../../services/api";

export default function SupervisorMonitoring() {
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filter, setFilter] = useState("all"); // all, active, flagged

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        const response = await api.get("/supervisor/students/all");
        setStudents(response.data);
      } catch (err) {
        console.error("Error fetching students:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStudents();
  }, []);

  const filteredStudents = students.filter(s => {
    const matchesSearch = s.username.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filter === "all" || 
                         (filter === "active" && s.online) || 
                         (filter === "flagged" && s.is_flagged);
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return (
      <div className="supervisor-dashboard-container">
        <div className="status-checking">Loading Live Pulse...</div>
      </div>
    );
  }

  return (
    <div className="supervisor-dashboard-container">
      {/* Header & Controls */}
      <header className="supervisor-header" style={{ alignItems: 'flex-end', gap: '30px', flexWrap: 'wrap' }}>
        <div style={{ flex: 1 }}>
          <button 
            onClick={() => navigate("/dashboard/supervisor")}
            className="back-btn"
          >
            <ArrowLeft size={16} /> Back to Dashboard
          </button>
          <h1 className="supervisor-title">Student <span>Pulse Monitoring</span></h1>
        </div>

        <div className="supervisor-controls">
          <div className="search-wrapper">
            <Search className="search-icon" size={18} />
            <input 
              type="text" 
              placeholder="Search students..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
          <select 
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Students</option>
            <option value="active">Active Only</option>
            <option value="flagged">Flagged Cases</option>
          </select>
        </div>
      </header>

      {/* Grid */}
      <div className="monitoring-grid-premium">
        {filteredStudents.map((student) => (
          <div
            key={student.id}
            className={`supervisor-student-card ${student.is_flagged ? "flagged" : ""}`}
          >
            {student.is_flagged && (
              <div className="flag-badge-pulse">
                <ShieldAlert size={24} />
              </div>
            )}

            <div className="student-card-header">
              <div className="student-initials-box">
                {student.username.charAt(0).toUpperCase()}
              </div>
              <div className="student-name-status">
                <h3>{student.username}</h3>
                <div className="online-indicator">
                  <span className={`indicator-dot ${student.online ? "online" : "offline"}`}></span>
                  {student.online ? "Online" : "Offline"}
                </div>
              </div>
            </div>

            <div style={{ margin: '20px 0' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                <span className="stat-label" style={{ fontSize: '0.65rem' }}>Session Status</span>
                <span className="stat-label" style={{ fontSize: '0.65rem', color: student.is_flagged ? 'var(--error-bg)' : 'var(--primary-text)' }}>
                  {student.is_flagged ? "URGENT ATTENTION" : student.online ? "Monitoring..." : "Idle"}
                </span>
              </div>
              
              {student.is_flagged && (
                <div style={{ background: 'rgba(255, 82, 82, 0.05)', padding: '12px', borderRadius: '12px', border: '1px solid rgba(255, 82, 82, 0.1)' }}>
                  <p className="stat-label" style={{ fontSize: '0.6rem', color: '#FF5252', textTransform: 'none' }}>
                    Alert triggered by {student.flag_source || 'system'}. 
                  </p>
                </div>
              )}
            </div>

            <div style={{ borderTop: '2px solid var(--neutral)', paddingTop: '20px', display: 'flex', gap: '10px' }}>
              {student.is_flagged ? (
                <Link 
                  to={`/dashboard/supervisor/investigation/${student.id}`}
                  className="alert-btn"
                  style={{ background: 'var(--error-bg)', color: 'white', marginTop: 0 }}
                >
                  INVESTIGATE
                </Link>
              ) : (
                <Link 
                  to={`/students/${student.id}/profile`}
                  className="alert-btn"
                  style={{ background: 'var(--secondary-bg)', color: 'var(--primary-text)', marginTop: 0 }}
                >
                  VIEW PROFILE
                </Link>
              )}
            </div>
          </div>
        ))}
      </div>

      {filteredStudents.length === 0 && (
        <div style={{ textAlign: 'center', padding: '100px 0' }}>
          <Search className="stat-label" style={{ fontSize: '4rem', opacity: 0.1, marginBottom: '20px' }} size={64} />
          <h2 className="stat-value" style={{ color: 'var(--neutral)', fontSize: '1.5rem' }}>No students found matching your criteria.</h2>
        </div>
      )}
    </div>
  );
}
