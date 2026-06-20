import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Search, User, Filter, ArrowLeft, ChevronRight } from "lucide-react";
import api from "../../../services/api";

export default function AllStudents() {
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterLevel, setFilterLevel] = useState("all");
  const [filterClass, setFilterClass] = useState("all");

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        const response = await api.get("/supervisor/students/all");
        console.log("Supervisor Students All:", response.data);
        setStudents(Array.isArray(response.data) ? response.data : []);
      } catch (err) {
        console.error("Error fetching students:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStudents();
  }, []);

  const filteredStudents = students.filter(s => {
    const matchesSearch = s.username.toLowerCase().includes(searchTerm.toLowerCase()) || 
                         s.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesClass = filterClass === "all" || s.classroom_name === filterClass;
    const matchesLevel = filterLevel === "all" || s.level_name === filterLevel;
    return matchesSearch && matchesClass && matchesLevel;
  });

  // Get unique classes and levels for filter
  const classes = ["all", ...new Set(students.map(s => s.classroom_name).filter(Boolean))];
  const levels = ["all", ...new Set(students.map(s => s.level_name).filter(Boolean))];

  if (loading) {
    return (
      <div className="supervisor-dashboard-container">
        <div className="status-checking">Accessing Student Directory...</div>
      </div>
    );
  }

  return (
    <div className="supervisor-dashboard-container">
      <header className="supervisor-header" style={{ alignItems: 'flex-end', gap: '20px', flexWrap: 'wrap', marginBottom: '40px' }}>
        <div style={{ flex: 1 }}>
          <button 
            onClick={() => navigate(-1)}
            className="back-btn"
          >
            <ArrowLeft size={16} /> Back
          </button>
          <h1 className="supervisor-title">Student <span>Directory</span></h1>
          <p className="stat-label" style={{ textTransform: 'none', marginTop: '5px' }}>Comprehensive list of all registered students in the system.</p>
        </div>

        <div className="supervisor-controls" style={{ gap: '15px' }}>
          <div className="search-wrapper">
            <Search className="search-icon" size={18} />
            <input 
              type="text" 
              placeholder="Search by name or email..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
          
          <div className="search-wrapper" style={{ width: 'auto' }}>
            {/* <Filter className="search-icon" size={16} /> */}
            <select 
              value={filterLevel}
              onChange={(e) => setFilterLevel(e.target.value)}
              className="filter-select"
              style={{ minWidth: '160px' }}
            >
              <option value="all">All Levels</option>
              {levels.filter(l => l !== "all").map(l => (
                <option key={l} value={l}>{l}</option>
              ))}
            </select>
          </div>

          <div className="search-wrapper" style={{ width: 'auto' }}>
            {/* <Filter className="search-icon" size={16} /> */}
            <select 
              value={filterClass}
              onChange={(e) => setFilterClass(e.target.value)}
              className="filter-select"
              style={{ minWidth: '160px' }}
            >
              <option value="all">All Classes</option>
              {classes.filter(c => c !== "all").map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
        </div>
      </header>

      <div className="monitoring-grid-premium">
        {filteredStudents.map((student) => (
          <div key={student.id} className="supervisor-student-card" style={{ padding: '25px' }}>
            <div className="student-card-header" style={{ marginBottom: '20px' }}>
              <div className="student-initials-box" style={{ width: '50px', height: '50px', fontSize: '1.2rem' }}>
                {student.username.charAt(0).toUpperCase()}
              </div>
              <div className="student-name-status">
                <h3 style={{ fontSize: '1rem' }}>{student.username}</h3>
                <div className="stat-label" style={{ textTransform: 'none', fontSize: '0.75rem', marginTop: '2px' }}>{student.email}</div>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '25px' }}>
              <div style={{ background: 'var(--secondary-bg)', padding: '12px', borderRadius: '15px' }}>
                <span className="stat-label" style={{ fontSize: '8px' }}>Classroom</span>
                <span style={{ display: 'block', fontSize: '0.85rem', fontWeight: 800 }}>{student.classroom_name || "Unassigned"}</span>
              </div>
              <div style={{ background: 'var(--secondary-bg)', padding: '12px', borderRadius: '15px' }}>
                <span className="stat-label" style={{ fontSize: '8px' }}>Status</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <span className={`indicator-dot ${student.online ? "online" : "offline"}`} style={{ width: '6px', height: '6px' }}></span>
                  <span style={{ fontSize: '0.85rem', fontWeight: 800 }}>{student.online ? "Online" : "Offline"}</span>
                </div>
              </div>
            </div>

            <Link 
              to={`/students/${student.id}/profile`}
              className="alert-btn"
              style={{ background: 'var(--primary-bg)', color: 'var(--highlight)', marginTop: 0, justifyContent: 'space-between', padding: '12px 20px' }}
            >
              Full Profile <ChevronRight size={16} />
            </Link>
          </div>
        ))}
      </div>

      {filteredStudents.length === 0 && (
        <div style={{ textAlign: 'center', padding: '100px 0' }}>
          <User className="stat-label" style={{ fontSize: '4rem', opacity: 0.1, marginBottom: '20px' }} size={64} />
          <h2 className="stat-value" style={{ color: 'var(--neutral)', fontSize: '1.5rem' }}>No students found.</h2>
        </div>
      )}
    </div>
  );
}
