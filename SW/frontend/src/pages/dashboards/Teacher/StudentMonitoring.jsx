import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
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
            const formData = new FormData();
            formData.append("title", noteData.title);
            formData.append("message", noteData.message);
            formData.append("is_urgent", noteData.is_urgent);

            await api.post(`/teacher/students/${selectedStudent.id}/note-to-parent`, formData);
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
                            <div className={`online-status-badge ${student.online ? 'status-online' : 'status-offline'}`}>
                                <div className="status-dot" />
                                {student.online ? 'Online' : 'Offline'}
                            </div>

                            <div className="card-student-header">
                                <div className="card-avatar">
                                    {student.username ? student.username[0].toUpperCase() : "?"}
                                </div>
                                <div className="card-student-info">
                                    <h3 style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                                        {student.username}
                                        <button 
                                          title="Message Parent"
                                          onClick={() => { setSelectedStudent(student); setShowNoteModal(true); }}
                                          style={{ background: "var(--primary-bg)", border: "none", borderRadius: "10px", padding: "8px", color: "var(--highlight)", cursor: "pointer" }}
                                        >
                                          <MessageSquare size={18} />
                                        </button>
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
            <AnimatePresence>
                {showNoteModal && (
                    <div style={{ 
                        position: "fixed", top: 0, left: 0, width: "100%", height: "100%", 
                        background: "rgba(0,0,0,0.6)", zIndex: 1000, display: "flex", 
                        alignItems: "center", justifyContent: "center", padding: "20px",
                        backdropFilter: "blur(5px)"
                    }}>
                        <motion.div 
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            className="teacher-card" 
                            style={{ width: "100%", maxWidth: "600px", padding: "40px", position: "relative", background: "white", borderRadius: "30px", border: "4px solid var(--neutral)" }}
                        >
                            <button 
                                onClick={() => setShowNoteModal(false)}
                                style={{ position: "absolute", right: "20px", top: "20px", background: "none", border: "none", cursor: "pointer", color: "var(--secondary-text)" }}
                            >
                                <X size={24} />
                            </button>

                            <div style={{ marginBottom: "30px" }}>
                                <h2 style={{ fontSize: "1.8rem", fontWeight: "900", color: "var(--highlight)" }}>Note to Parent</h2>
                                <p style={{ color: "var(--secondary-text)" }}>
                                    Sending a message to <strong>{selectedStudent?.username}</strong>'s parent.
                                </p>
                            </div>

                            {noteStatus.success ? (
                                <div style={{ textAlign: "center", padding: "40px 0" }}>
                                    <CheckCircle2 size={64} color="var(--success-bg)" style={{ margin: "0 auto 20px" }} />
                                    <h3 style={{ color: "var(--success-bg)", fontSize: "1.5rem" }}>Message Sent!</h3>
                                    <p>The parent will receive this notification immediately.</p>
                                </div>
                            ) : (
                                <form onSubmit={handleSendNote}>
                                    <div style={{ marginBottom: "20px" }}>
                                        <label style={{ fontWeight: "700", display: "block", marginBottom: "8px" }}>Subject</label>
                                        <input 
                                            type="text" 
                                            placeholder="e.g. Great progress today!" 
                                            value={noteData.title}
                                            onChange={(e) => setNoteData({ ...noteData, title: e.target.value })}
                                            required
                                        />
                                    </div>

                                    <div style={{ marginBottom: "20px" }}>
                                        <label style={{ fontWeight: "700", display: "block", marginBottom: "8px" }}>Message</label>
                                        <textarea 
                                            placeholder="Enter your feedback or comments here..." 
                                            rows={5}
                                            value={noteData.message}
                                            onChange={(e) => setNoteData({ ...noteData, message: e.target.value })}
                                            style={{ width: "100%", padding: "15px", borderRadius: "15px", border: "3px solid var(--neutral)", fontFamily: "inherit" }}
                                            required
                                        />
                                    </div>

                                    <div style={{ marginBottom: "30px", display: "flex", alignItems: "center", gap: "10px", background: noteData.is_urgent ? "#fff5f5" : "var(--primary-bg)", padding: "15px", borderRadius: "15px", transition: "all 0.2s" }}>
                                        <input 
                                            type="checkbox" 
                                            id="urgent" 
                                            checked={noteData.is_urgent}
                                            onChange={(e) => setNoteData({ ...noteData, is_urgent: e.target.checked })}
                                            style={{ width: "20px", height: "20px", margin: 0 }}
                                        />
                                        <label htmlFor="urgent" style={{ fontWeight: "800", color: noteData.is_urgent ? "var(--error-bg)" : "inherit", display: "flex", alignItems: "center", gap: "8px" }}>
                                            {noteData.is_urgent && <AlertTriangle size={16} />}
                                            Mark as Urgent Alert
                                        </label>
                                    </div>

                                    {noteStatus.error && (
                                        <p style={{ color: "var(--error-bg)", fontSize: "0.9rem", fontWeight: "700", marginBottom: "20px", textAlign: "center" }}>
                                            {noteStatus.error}
                                        </p>
                                    )}

                                    <button 
                                        type="submit" 
                                        className="btn btn-primary" 
                                        style={{ width: "100%", padding: "15px", fontSize: "1.1rem" }}
                                        disabled={noteStatus.loading}
                                    >
                                        {noteStatus.loading ? "Sending..." : <><Send size={18} style={{ marginRight: "10px" }} /> Send to Parent</>}
                                    </button>
                                </form>
                            )}
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
}
