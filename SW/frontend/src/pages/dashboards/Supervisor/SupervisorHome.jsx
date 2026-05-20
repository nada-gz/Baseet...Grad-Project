import React, { useEffect, useState } from "react";
import { 
  Users, 
  UserCheck, 
  AlertCircle, 
  Activity, 
  ChevronRight,
  ShieldAlert,
  ClipboardList
} from "lucide-react";
import { Link } from "react-router-dom";
import api from "../../../services/api";

export default function SupervisorHome() {
  const [stats, setStats] = useState({
    totalStudents: 0,
    activeStudents: 0,
    flaggedStudents: 0,
    totalTeachers: 0
  });
  const [recentFlags, setRecentFlags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSupervisorData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [studentsRes, teachersRes, flagsRes] = await Promise.all([
          api.get("/supervisor/students/all"),
          api.get("/supervisor/teachers"),
          api.get("/supervisor/students/flagged")
        ]);

        setStats({
          totalStudents: studentsRes.data.length || 0,
          activeStudents: studentsRes.data.filter(s => s.online).length || 0,
          flaggedStudents: studentsRes.data.filter(s => s.is_flagged).length || 0,
          totalTeachers: teachersRes.data.length || 0
        });
        setRecentFlags(flagsRes.data.slice(0, 5));
      } catch (err) {
        console.error("Error fetching supervisor data:", err);
        setError("Failed to sync with central server. Please check connection.");
      } finally {
        setLoading(false);
      }
    };
    fetchSupervisorData();
  }, []);

  if (loading) {
    return (
      <div className="supervisor-dashboard-container">
        <div className="status-checking">Loading Supervisor Dashboard...</div>
      </div>
    );
  }

  return (
    <div className="supervisor-dashboard-container">
      {/* Welcome Section */}
      <header className="supervisor-header">
        <div>
          <h1 className="supervisor-title">
            Supervisor <span>Overview</span>
          </h1>
          <p className="stat-label" style={{ textTransform: 'none', marginTop: '5px' }}>Monitor the system and manage student safety.</p>
        </div>
      </header>

      {error && (
        <div style={{ background: 'var(--error-bg)', color: 'white', padding: '15px 25px', borderRadius: '15px', marginBottom: '30px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '15px' }}>
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      {/* Stats Grid */}
      <div className="supervisor-stats-grid">
        <StatCard 
          icon={<Users />} 
          label="Total Students" 
          value={stats.totalStudents} 
        />
        <StatCard 
          icon={<UserCheck />} 
          label="Active Now" 
          value={stats.activeStudents} 
        />
        <StatCard 
          icon={<AlertCircle />} 
          label="Flagged Case" 
          value={stats.flaggedStudents} 
        />
        <StatCard 
          icon={<ClipboardList />} 
          label="Teachers" 
          value={stats.totalTeachers} 
        />
      </div>

      <div className="supervisor-layout-grid">
        {/* Main Monitoring Entry */}
        <div className="monitoring-main-panel">
          <section className="supervisor-card">
            <div className="supervisor-card-header">
              <h2 className="supervisor-card-title">
                <Activity size={24} />
                Live Student Pulse
              </h2>
              <Link to="/dashboard/supervisor/monitoring" className="online-indicator" style={{ color: 'var(--highlight)', textDecoration: 'none' }}>
                View Full Monitoring <ChevronRight size={16} />
              </Link>
            </div>
            <div style={{ padding: '60px 0', textAlign: 'center', border: '3px dashed var(--neutral)', borderRadius: '24px' }}>
              <Activity className="stat-icon-box" style={{ margin: '0 auto 20px', background: 'var(--primary-bg)', color: 'var(--highlight)' }} size={48} />
              <p className="stat-label">Monitoring engine active. {stats.activeStudents} students currently in session.</p>
            </div>
          </section>
        </div>

        {/* Alerts Sidebar */}
        <div className="alerts-sidebar-panel">
          <section className="supervisor-alert-sidebar">
            <ShieldAlert className="alert-icon-bg" style={{ position: 'absolute', right: '-20px', bottom: '-20px', opacity: 0.1 }} size={150} />
            <h2 className="supervisor-card-title" style={{ color: 'white', marginBottom: '30px' }}>Active Alerts</h2>
            
            <div className="alerts-list" style={{ position: 'relative', zIndex: 1 }}>
              {recentFlags.length > 0 ? (
                recentFlags.map((flag) => (
                  <div key={flag.id} className="alert-item">
                    <div className="alert-item-header">
                      <span className="alert-type">
                        {flag.source} Alert
                      </span>
                      <span className="alert-time">Just now</span>
                    </div>
                    <p style={{ fontSize: '0.9rem', fontWeight: 600, margin: '10px 0' }}>
                      {flag.student?.username}: {flag.reason}
                    </p>
                    <Link 
                      to={`/dashboard/supervisor/investigation/${flag.student_id}`}
                      className="alert-btn"
                    >
                      Investigate Case
                    </Link>
                  </div>
                ))
              ) : (
                <p className="stat-label" style={{ color: 'rgba(255,255,255,0.5)' }}>No urgent flags at the moment.</p>
              )}
            </div>
          </section>

          <Link to="/dashboard/supervisor/teachers" className="supervisor-link-card" style={{ marginTop: '30px' }}>
            <div className="link-card-content">
              <div className="link-card-info">
                <div className="link-card-icon-box">
                  <ClipboardList size={24} />
                </div>
                <div>
                  <h3 className="stat-value" style={{ fontSize: '1.1rem', margin: 0 }}>Teachers Management</h3>
                  <p className="stat-label" style={{ fontSize: '0.7rem' }}>Configure student assignments</p>
                </div>
              </div>
              <ChevronRight className="stat-label" />
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value }) {
  return (
    <div className="supervisor-stat-card">
      <div className="stat-icon-box" style={{ background: 'var(--primary-bg)', color: 'var(--highlight)' }}>
        {icon}
      </div>
      <p className="stat-label">{label}</p>
      <h3 className="stat-value">{value}</h3>
    </div>
  );
}
