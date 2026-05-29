import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../../services/api";
import { 
  Search, 
  User as UserIcon, 
  BookOpen, 
  Activity, 
  MessageSquare, 
  X, 
  Send,
  AlertTriangle,
  CheckCircle2
} from "lucide-react";

export default function StudentMonitoring() {
    const navigate = useNavigate();
    const [allStudents, setAllStudents] = useState([]);
    const [filteredStudents, setFilteredStudents] = useState([]);
    const [loading, setLoading] = useState(true);

    // Modal state
    const [showNoteModal, setShowNoteModal] = useState(false);
    const [selectedStudent, setSelectedStudent] = useState(null);
    const [noteData, setNoteData] = useState({ title: "", message: "", is_urgent: false });
    const [noteStatus, setNoteStatus] = useState({ loading: false, error: null, success: false });
    const [isFlagging, setIsFlagging] = useState(false);

    // Filters state
    const [searchTerm, setSearchTerm] = useState("");
    const [filters, setFilters] = useState({
        classroom: "All",
        course: "All",
        status: "All",
        level: "All"
    });

    useEffect(() => {
        fetchStudents();
    }, []);

    const fetchStudents = async () => {
        setLoading(true);
        try {
            const res = await api.get("/teacher/students");
            setAllStudents(res.data);
            setFilteredStudents(res.data);
        } catch (err) {
            console.error("Error fetching students:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleSendNote = async (e) => {
        e.preventDefault();
        if (!selectedStudent) return;
        setNoteStatus({ loading: true, error: null, success: false });
        
        try {
            // Send as JSON instead of FormData
            await api.post(`/teacher/students/${selectedStudent.id}/note-to-parent`, {
                title: noteData.title,
                message: noteData.message,
                is_urgent: noteData.is_urgent
            });

            setNoteStatus({ loading: false, error: null, success: true });
            setTimeout(() => {
                setShowNoteModal(false);
                setNoteData({ title: "", message: "", is_urgent: false });
                setNoteStatus({ loading: false, error: null, success: false });
            }, 2000);
        } catch (err) {
            setNoteStatus({ 
                loading: false, 
                error: err.response?.data?.detail || "Could not send note. Is the parent linked?", 
                success: false 
            });
        }
    };

    // ... (keep filterOptions as is)

    // Unique filter options
    const filterOptions = {
        classrooms: ["All", ...new Set(allStudents.map(s => s.classroom_name).filter(Boolean))],
        courses: ["All", ...new Set(allStudents.map(s => s.course_number).filter(Boolean))],
        statuses: ["All", "Online", "Offline", ...new Set(allStudents.map(s => s.status).filter(Boolean))],
        levels: ["All", ...new Set(allStudents.map(s => s.level_name).filter(Boolean))]
    };

    useEffect(() => {
        let result = allStudents.filter(student => {
            const matchesSearch = student.username.toLowerCase().includes(searchTerm.toLowerCase());
            const matchesClass = filters.classroom === "All" || student.classroom_name === filters.classroom;
            const matchesCourse = filters.course === "All" || String(student.course_number) === String(filters.course);
            const matchesStatus = filters.status === "All" ||
                (filters.status === "Online" ? student.online :
                    filters.status === "Offline" ? !student.online :
                        student.status === filters.status);
            const matchesLevel = filters.level === "All" || student.level_name === filters.level;

            return matchesSearch && matchesClass && matchesCourse && matchesStatus && matchesLevel;
        });
        setFilteredStudents(result);
    }, [searchTerm, filters, allStudents]);

    const handleFilterChange = (name, value) => {
        setFilters(prev => ({ ...prev, [name]: value }));
    };

    const handleFlagStudent = async (studentId, reason) => {
        setIsFlagging(true);
        try {
            await api.post(`/teacher/students/${studentId}/flag`, `reason=${encodeURIComponent(reason)}`, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });
            setAllStudents(allStudents.map(s => s.id === studentId ? { ...s, is_flagged: true } : s));
        } catch (err) {
            console.error("Error flagging student:", err);
            alert("Failed to send alert to supervisor.");
        } finally {
            setIsFlagging(false);
        }
    };

    if (loading) return <div className="loading-state">Loading Students...</div>;

    return (
        <div className="page-container">

            {/* Search and Filters */}
            <div className="monitoring-controls">
                <div className="search-input-wrapper">
                    <Search className="search-icon" size={20} />
                    <input
                        type="text"
                        placeholder="Search student name..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>

                <div className="filter-group">
                    <span className="filter-label">Filter by:</span>
                    <select
                        className="filter-select"
                        value={filters.level}
                        onChange={(e) => handleFilterChange("level", e.target.value)}
                    >
                        <option value="All">Level: All</option>
                        {filterOptions.levels.filter(l => l !== "All").map(l => (
                            <option key={l} value={l}>{l}</option>
                        ))}
                    </select>

                    <select
                        className="filter-select"
                        value={filters.classroom}
                        onChange={(e) => handleFilterChange("classroom", e.target.value)}
                    >
                        <option value="All">Class: All</option>
                        {filterOptions.classrooms.filter(c => c !== "All").map(c => (
                            <option key={c} value={c}>{c}</option>
                        ))}
                    </select>

                    <select
                        className="filter-select"
                        value={filters.course}
                        onChange={(e) => handleFilterChange("course", e.target.value)}
                    >
                        <option value="All">Course: All</option>
                        {filterOptions.courses.filter(c => c !== "All").map(c => (
                            <option key={c} value={c}>Course {c}</option>
                        ))}
                    </select>

                    <select
                        className="filter-select"
                        value={filters.status}
                        onChange={(e) => handleFilterChange("status", e.target.value)}
                    >
                        <option value="All">Status: All</option>
                        <option value="Online">Online</option>
                        <option value="Offline">Offline</option>
                        {filterOptions.statuses.filter(s => s !== "All" && s !== "Online" && s !== "Offline" && s !== "Active").map(s => (
                            <option key={s} value={s}>{s}</option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Students Grid */}
            <div className="monitoring-grid">
                {filteredStudents.length === 0 ? (
                    <div className="empty-placeholder" style={{ gridColumn: "1 / -1" }}>
                        <UserIcon size={40} />
                        <p>No students found matching your criteria.</p>
                    </div>
                ) : (
                    filteredStudents.map(student => (
                        <div key={student.id} className="student-monitoring-card">
                            {/* Online Badge */}
                            <div className="status-container" style={{ display: "flex", flexDirection: "column", alignItems: "flex-start", gap: "10px", marginBottom: "15px" }}>
                                <div className={`online-status-badge ${student.online ? 'status-online' : 'status-offline'}`} style={{ margin: 0 }}>
                                    <div className="status-dot" />
                                    {student.online ? 'Online' : 'Offline'}
                                </div>
                                <button 
                                    title="Message Parent"
                                    onClick={() => { setSelectedStudent(student); setShowNoteModal(true); }}
                                    className="parent-msg-btn"
                                    style={{ 
                                        background: "var(--primary-bg)", 
                                        border: "2px solid var(--neutral)", 
                                        borderRadius: "12px", 
                                        padding: "6px 14px", 
                                        color: "var(--highlight)", 
                                        cursor: "pointer",
                                        display: "flex",
                                        alignItems: "center",
                                        gap: "8px",
                                        fontSize: "0.75rem",
                                        fontWeight: "800",
                                        transition: "all 0.3s ease",
                                        width: "fit-content"
                                    }}
                                >
                                    <MessageSquare size={14} />
                                    <span>Message Parent...</span>
                                </button>
                                <button 
                                    title="Alert Supervisor"
                                    onClick={() => {
                                        const reason = prompt("Describe the urgent issue for the supervisor:");
                                        if (reason) handleFlagStudent(student.id, reason);
                                    }}
                                    disabled={student.is_flagged || isFlagging}
                                    className="supervisor-alert-btn"
                                    style={{ 
                                        background: student.is_flagged ? "var(--error-bg)" : "white", 
                                        border: `2px solid ${student.is_flagged ? 'var(--error-bg)' : '#FF4757'}`, 
                                        borderRadius: "12px", 
                                        padding: "6px 14px", 
                                        color: student.is_flagged ? "white" : "#FF4757", 
                                        cursor: student.is_flagged ? "default" : "pointer",
                                        display: "flex",
                                        alignItems: "center",
                                        gap: "8px",
                                        fontSize: "0.75rem",
                                        fontWeight: "800",
                                        transition: "all 0.3s ease",
                                        width: "fit-content",
                                        opacity: student.is_flagged ? 0.7 : 1
                                    }}
                                >
                                    <AlertTriangle size={14} />
                                    <span>{student.is_flagged ? 'Supervisor Alerted' : 'Alert Supervisor'}</span>
                                </button>
                            </div>

                            <div className="card-student-header">
                                <div className="card-avatar">
                                    {student.username ? student.username[0].toUpperCase() : "?"}
                                </div>
                                <div className="card-student-info">
                                    <h3 style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "10px" }}>
                                        <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{student.username}</span>
                                    </h3>
                                    <p>{student.email}</p>
                                </div>
                            </div>

                            <div className="card-details-grid">
                                <div className="detail-item">
                                    <span className="detail-label">Level</span>
                                    <span className="detail-value">{student.level_name || "N/A"}</span>
                                </div>
                                <div className="detail-item">
                                    <span className="detail-label">Class</span>
                                    <span className="detail-value">{student.classroom_name || "N/A"}</span>
                                </div>
                                <div className="detail-item">
                                    <span className="detail-label">Course</span>
                                    <span className="detail-value">{student.course_number ? `Course ${student.course_number}` : "N/A"}</span>
                                </div>
                                <div className="detail-item">
                                    <span className="detail-label">Status</span>
                                    <span className="detail-value">{student.status}</span>
                                </div>
                                <div className="detail-item">
                                    <span className="detail-label">Age</span>
                                    <span className="detail-value">{student.age || "N/A"} yrs</span>
                                </div>
                                <div className="detail-item">
                                    <span className="detail-label">State</span>
                                    <span className={`detail-value ${student.state === 'Stressed' ? 'state-stressed' : 'state-relaxed'}`}>
                                        {student.state || "Relaxed"}
                                    </span>
                                </div>
                            </div>

                            <div className="card-progress-summary">
                                <div className="progress-label">
                                    <span>Lesson Progress</span>
                                    <span>{student.progress || 0}%</span>
                                </div>
                                <div className="progress-bar-small">
                                    <div className="progress-fill-small" style={{ width: `${student.progress || 0}%` }} />
                                </div>
                            </div>

                            <div className="card-actions">
                                <button
                                    className="btn-monitoring btn-academic"
                                    onClick={() => navigate(`/dashboard/teacher/students/${student.id}/progress`)}
                                >
                                    <BookOpen size={18} />
                                    Academic Progress
                                </button>
                                <button
                                    className="btn-monitoring btn-live"
                                    onClick={() => navigate(`/dashboard/teacher/students/${student.id}/live`)}
                                >
                                    <Activity size={18} />
                                    Live Monitoring
                                </button>
                            </div>

                            {!student.online && student.last_access && (
                                <div className="last-access-text">
                                    Last active: {new Date(student.last_access).toLocaleString()}
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>

            {/* Note Modal */}
            {showNoteModal && (
                <div 
                    style={{ 
                        position: "fixed", top: 0, left: 0, width: "100%", height: "100%", 
                        background: "rgba(0,0,0,0.7)", zIndex: 1000, display: "flex", 
                        alignItems: "center", justifyContent: "center", padding: "20px",
                        backdropFilter: "blur(12px)"
                    }}
                >
                    <div 
                            className="teacher-modal-box" 
                            style={{ 
                                width: "100%", 
                                maxWidth: "700px", 
                                minHeight: "500px",
                                padding: "60px", 
                                position: "relative", 
                                background: "white", 
                                borderRadius: "40px", 
                                border: "10px solid var(--neutral)",
                                boxShadow: "0 40px 80px rgba(0,0,0,0.3)",
                                textAlign: "left", // Override teacher-card center
                                display: "flex",
                                flexDirection: "column"
                            }}
                        >
                            <button 
                                onClick={() => setShowNoteModal(false)}
                                style={{ position: "absolute", right: "25px", top: "25px", background: "var(--primary-bg)", border: "none", borderRadius: "15px", padding: "12px", cursor: "pointer", color: "var(--secondary-text)", transition: "all 0.2s" }}
                            >
                                <X size={24} />
                            </button>

                            <div style={{ marginBottom: "40px" }}>
                                <h2 style={{ fontSize: "2.2rem", fontWeight: "950", color: "var(--highlight)", margin: "0 0 10px 0" }}>Message Parent</h2>
                                <p style={{ color: "var(--secondary-text)", fontSize: "1.1rem" }}>
                                    Direct feedback for <strong>{selectedStudent?.username}</strong>'s guardian.
                                </p>
                            </div>

                            {/* Static DOM structure to prevent removeChild crashes */}
                            <div style={{ display: noteStatus.success ? 'none' : 'block', flex: 1 }}>
                                <form 
                                    onSubmit={handleSendNote}
                                    style={{ flex: 1 }}
                                >
                                    <div style={{ marginBottom: "25px" }}>
                                        <label style={{ fontWeight: "800", display: "block", marginBottom: "12px", fontSize: "1rem", color: "var(--primary-text)" }}>Subject / Title</label>
                                        <input 
                                            type="text" 
                                            placeholder="e.g. Excellent participation today" 
                                            value={noteData.title}
                                            onChange={(e) => setNoteData({ ...noteData, title: e.target.value })}
                                            required
                                            style={{ width: "100%", padding: "18px", borderRadius: "18px", border: "4px solid var(--neutral)", fontSize: "1.1rem", outline: "none" }}
                                        />
                                    </div>

                                    <div style={{ marginBottom: "25px" }}>
                                        <label style={{ fontWeight: "800", display: "block", marginBottom: "12px", fontSize: "1rem", color: "var(--primary-text)" }}>Detailed Message</label>
                                        <textarea 
                                            placeholder="Write your feedback here..." 
                                            rows={6}
                                            value={noteData.message}
                                            onChange={(e) => setNoteData({ ...noteData, message: e.target.value })}
                                            style={{ width: "100%", padding: "20px", borderRadius: "20px", border: "4px solid var(--neutral)", fontFamily: "inherit", fontSize: "1.1rem", outline: "none", resize: "none" }}
                                            required
                                        />
                                    </div>

                                    <div style={{ 
                                        marginBottom: "35px", 
                                        display: "flex", 
                                        alignItems: "center", 
                                        gap: "15px", 
                                        background: noteData.is_urgent ? "rgba(255, 71, 87, 0.05)" : "var(--primary-bg)", 
                                        padding: "20px", 
                                        borderRadius: "20px", 
                                        border: `2px solid ${noteData.is_urgent ? 'rgba(255, 71, 87, 0.2)' : 'transparent'}`,
                                        transition: "all 0.3s" 
                                    }}>
                                        <input 
                                            type="checkbox" 
                                            id="urgent" 
                                            checked={noteData.is_urgent}
                                            onChange={(e) => setNoteData({ ...noteData, is_urgent: e.target.checked })}
                                            style={{ width: "24px", height: "24px", margin: 0, cursor: "pointer" }}
                                        />
                                        <label htmlFor="urgent" style={{ fontWeight: "900", color: noteData.is_urgent ? "#FF4757" : "var(--primary-text)", display: "flex", alignItems: "center", gap: "10px", cursor: "pointer", fontSize: "1rem" }}>
                                            {noteData.is_urgent && <AlertTriangle size={20} />}
                                            Mark as Urgent Priority
                                        </label>
                                    </div>

                                    {noteStatus.error && (
                                        <p style={{ color: "#FF4757", fontSize: "0.95rem", fontWeight: "800", marginBottom: "25px", textAlign: "center", padding: "10px", background: "rgba(255, 71, 87, 0.1)", borderRadius: "10px" }}>
                                            {noteStatus.error}
                                        </p>
                                    )}

                                    <button 
                                        type="submit" 
                                        className="btn btn-primary" 
                                        style={{ width: "100%", padding: "20px", fontSize: "1.2rem", borderRadius: "20px", boxShadow: "0 10px 20px rgba(108, 99, 255, 0.3)" }}
                                        disabled={noteStatus.loading}
                                    >
                                        {noteStatus.loading ? "Processing..." : <><Send size={22} style={{ marginRight: "12px" }} /> Send to Parent</>}
                                    </button>
                                </form>
                            </div>

                            <div style={{ display: noteStatus.success ? 'flex' : 'none', textAlign: "center", padding: "60px 0", flex: 1, flexDirection: "column", justifyContent: "center", alignItems: "center" }}>
                                <CheckCircle2 size={80} color="#00F5D4" style={{ marginBottom: "25px" }} />
                                <h3 style={{ color: "var(--primary-text)", fontSize: "2rem", fontWeight: "900" }}>Sent Successfully!</h3>
                                <p style={{ color: "var(--secondary-text)", fontSize: "1.1rem", marginTop: "10px" }}>The parent has been notified.</p>
                            </div>
                    </div>
                </div>
            )}
        </div>
    );
}
