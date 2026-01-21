import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../../services/api";
import { Search, User as UserIcon, BookOpen, Activity } from "lucide-react";

export default function StudentMonitoring() {
    const navigate = useNavigate();
    const [allStudents, setAllStudents] = useState([]);
    const [filteredStudents, setFilteredStudents] = useState([]);
    const [loading, setLoading] = useState(true);

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
                                    <h3>{student.username}</h3>
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
        </div>
    );
}


