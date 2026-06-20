import React, { useState, useEffect } from "react";
import api from "../../../services/api";
import { Trash2, UserPlus, BookOpen, X, Check, Users, BookMarked, ArrowLeft, School } from "lucide-react";

export default function ClassManagement() {
    const [levels, setLevels] = useState([]);
    const [loading, setLoading] = useState(true);
    const [newLevelName, setNewLevelName] = useState("");

    // State for adding class
    const [addingClassToLevel, setAddingClassToLevel] = useState(null);
    const [newClassName, setNewClassName] = useState("");

    // Manage Views
    const [manageView, setManageView] = useState(null);
    const [activeClassroom, setActiveClassroom] = useState(null);

    useEffect(() => {
        fetchLevels();
    }, []);

    const fetchLevels = async () => {
        setLoading(true);
        try {
            const res = await api.get("/teacher/class-management/levels");
            setLevels(Array.isArray(res.data) ? res.data : []);
        } catch (err) {
            console.error("Error fetching levels:", err);
        } finally {
            setLoading(false);
        }
    };

    const addLevel = async () => {
        if (!newLevelName.trim()) return;
        try {
            await api.post("/teacher/class-management/levels", { name: newLevelName });
            setNewLevelName("");
            fetchLevels();
        } catch (err) {
            console.error("Error adding level:", err);
        }
    };

    const deleteLevel = async (levelId) => {
        if (!window.confirm("Are you sure? This will delete all classes in this level.")) return;
        try {
            await api.delete(`/teacher/class-management/levels/${levelId}`);
            fetchLevels();
        } catch (err) {
            console.error("Error deleting level:", err);
        }
    };

    const deleteClassroom = async (classroomId) => {
        if (!window.confirm("Are you sure you want to delete this class? Students will be unassigned.")) return;
        try {
            await api.delete(`/teacher/class-management/classrooms/${classroomId}`);
            fetchLevels();
        } catch (err) {
            console.error("Error deleting classroom:", err);
        }
    };

    const addClass = async (levelId) => {
        if (!newClassName.trim()) return;
        try {
            await api.post(`/teacher/class-management/levels/${levelId}/classrooms`, { name: newClassName, level_id: levelId });
            setNewClassName("");
            setAddingClassToLevel(null);
            fetchLevels();
        } catch (err) {
            console.error("Error adding class:", err);
        }
    };

    const openManageView = (classroom, viewType) => {
        setActiveClassroom(classroom);
        setManageView(viewType);
    };

    const closeManageView = () => {
        setManageView(null);
        setActiveClassroom(null);
        fetchLevels();
    };

    if (loading) return <div className="loading-state">Loading Class Management...</div>;

    if (manageView && activeClassroom) {
        return (
            <ManageClassroomView
                classroom={activeClassroom}
                viewType={manageView}
                onClose={closeManageView}
            />
        );
    }

    return (
        <div className="page-container">
            {/* <h1 className="page-title">
          Class Management
      </h1> */}

            {/* Add Level Section */}
            <div className="add-level-section">
                <div className="add-level-input-group">
                    <label className="add-level-label">Create New Level</label>
                    <input
                        type="text"
                        className="add-level-input"
                        placeholder="Ex: Level 10"
                        value={newLevelName}
                        onChange={(e) => setNewLevelName(e.target.value)}
                    />
                </div>
                <button className="btn btn-primary add-level-btn" onClick={addLevel}>
                    + Add Level
                </button>
            </div>

            {/* Levels List */}
            <div className="levels-container">
                {levels.map(level => (
                    <div key={level.id} className="level-section">
                        <div className="level-header">
                            <div className="level-title-group">
                                <h2 className="level-title">{level.name}</h2>
                                <span className="level-badge">{level.classrooms.length} Classes</span>
                            </div>

                            {/* Level Actions: Add Class & Delete */}
                            <div className="level-actions">
                                <button
                                    className="btn btn-sm btn-outline level-add-class-btn"
                                    onClick={() => {
                                        setAddingClassToLevel(level.id);
                                        setNewClassName("");
                                    }}
                                >
                                    + Add Class
                                </button>
                                <button
                                    className="delete-btn"
                                    onClick={() => deleteLevel(level.id)}
                                    title="Delete Level"
                                >
                                    <Trash2 size={20} />
                                </button>
                            </div>
                        </div>

                        {/* Add Class Input */}
                        {addingClassToLevel === level.id && (
                            <div className="add-class-form">
                                <input
                                    type="text"
                                    className="add-class-input"
                                    placeholder="Class Name (e.g. Class A)"
                                    value={newClassName}
                                    onChange={(e) => setNewClassName(e.target.value)}
                                    autoFocus
                                />
                                <button className="btn btn-primary" onClick={() => addClass(level.id)}>Save</button>
                                <button className="btn btn-text cancel-btn" onClick={() => setAddingClassToLevel(null)}>Cancel</button>
                            </div>
                        )}

                        <div className="class-list">
                            {level.classrooms.length === 0 ? (
                                <div className="empty-placeholder">
                                    <School size={40} />
                                    <p className="font-medium">No classes added yet</p>
                                </div>
                            ) : (
                                level.classrooms.map(classroom => (
                                    <div key={classroom.id} className="class-management-card">
                                        <div className="class-card-header">
                                            <h3 className="class-name">{classroom.name}</h3>
                                            <div className="icon-box">
                                                <button
                                                    className="delete-btn"
                                                    onClick={() => deleteClassroom(classroom.id)}
                                                    title="Delete Class"
                                                >
                                                    <Trash2 size={16} />
                                                </button>
                                            </div>
                                        </div>

                                        <div className="class-stats-grid">
                                            <div
                                                className="stat-box students"
                                                onClick={() => openManageView(classroom, 'students')}
                                            >
                                                <div className="icon-container"><Users size={16} /></div>
                                                <div className="stat-number stat-number-blue">{classroom.student_count}</div>
                                                <div className="stat-label">Students</div>
                                            </div>

                                            <div
                                                className="stat-box courses"
                                                onClick={() => openManageView(classroom, 'courses')}
                                            >
                                                <div className="icon-container"><BookOpen size={16} /></div>
                                                <div className="stat-number stat-number-green">{classroom.courses ? classroom.courses.length : 0}</div>
                                                <div className="stat-label">Courses</div>
                                            </div>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

// ----------------------------------------------------------------------
// Sub-Component: Manage Classroom View (Students/Courses)
// ----------------------------------------------------------------------

function ManageClassroomView({ classroom, viewType, onClose }) {
    const isStudents = viewType === 'students';
    const [availableItems, setAvailableItems] = useState([]);
    const [assignedItems, setAssignedItems] = useState([]);
    const [selectedIds, setSelectedIds] = useState([]);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            if (isStudents) {
                const [allRes] = await Promise.all([
                    api.get("/teacher/students")
                ]);
                const all = allRes.data;
                const assigned = all.filter(s => s.classroom_id === classroom.id);
                const available = all.filter(s => !s.classroom_id);

                setAssignedItems(assigned);
                setAvailableItems(available);
            } else {
                const levelsRes = await api.get("/teacher/class-management/levels");
                const freshLevel = levelsRes.data.find(l => l.id === classroom.level_id);
                const freshClass = freshLevel?.classrooms.find(c => c.id === classroom.id);
                if (freshClass) {
                    const coursesRes = await api.get("/teacher/courses");
                    const allCourses = coursesRes.data;
                    const currentCourseIds = freshClass.courses.map(c => c.id);
                    setAssignedItems(allCourses.filter(c => currentCourseIds.includes(c.id)));
                    setAvailableItems(allCourses.filter(c => !currentCourseIds.includes(c.id)));
                }
            }
        } catch (err) {
            console.error("Error fetching detailed data", err);
        }
    };

    const handleAssign = async () => {
        if (selectedIds.length === 0) return;
        try {
            const endpoint = isStudents
                ? `/teacher/class-management/classrooms/${classroom.id}/students`
                : `/teacher/class-management/classrooms/${classroom.id}/courses`;

            const payload = isStudents
                ? { student_ids: selectedIds }
                : { course_ids: selectedIds };

            await api.post(endpoint, payload);
            setSelectedIds([]);
            await fetchData();

        } catch (err) {
            console.error("Assign error", err);
        }
    };

    const handleUnassign = async (itemId) => {
        if (!window.confirm("Remove this item from the class?")) return;
        try {
            const endpoint = isStudents
                ? `/teacher/class-management/classrooms/${classroom.id}/students/${itemId}`
                : `/teacher/class-management/classrooms/${classroom.id}/courses/${itemId}`;

            await api.delete(endpoint);
            await fetchData();
        } catch (err) {
            console.error("Unassign error", err);
        }
    };

    const toggleSelection = (id) => {
        if (selectedIds.includes(id)) setSelectedIds(selectedIds.filter(x => x !== id));
        else setSelectedIds([...selectedIds, id]);
    };

    return (
        <div className="manage-overlay">
            <div className="manage-content">
                {/* Header */}
                <div className="manage-header">
                    <button onClick={onClose} className="back-button">
                        <ArrowLeft size={18} />
                        Back
                    </button>
                    <div className="manage-header-group">
                        <h2 className="manage-title">
                            Manage {isStudents ? 'Students' : 'Courses'}
                        </h2>
                        <p className="manage-subtitle">
                            {classroom.name} • <span className="font-bold highlight-text">{assignedItems.length} Assigned</span>
                        </p>
                    </div>
                </div>

                <div className="manage-grid">

                    {/* LEFT COLUMN: Assigned Items */}
                    <div className="manage-column">
                        <div className="manage-section-header">
                            <div className="icon-box">
                                <Check size={20} className="check-icon-green" />
                                <h3>Assigned {isStudents ? 'Students' : 'Courses'}</h3>
                            </div>
                        </div>

                        <div className="scroll-area-assigned">
                            {assignedItems.length === 0 ? (
                                <div className="empty-state-box">
                                    No {isStudents ? 'students' : 'courses'} assigned yet.
                                </div>
                            ) : (
                                assignedItems.map(item => (
                                    <div key={item.id} className="assigned-card">
                                        <div className="assigned-card-left">
                                            <div className={`user-avatar ${isStudents ? 'avatar-student' : 'avatar-course'}`}>
                                                {isStudents ? item.username[0].toUpperCase() : item.course_number}
                                            </div>
                                            <div className="user-info">
                                                <div className="user-name">{isStudents ? item.username : `Course ${item.course_number}`}</div>
                                                <div className="user-email">{isStudents ? item.email : item.description}</div>
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => handleUnassign(item.id)}
                                            className="delete-btn"
                                            title="Unassign"
                                        >
                                            <Trash2 size={18} />
                                        </button>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    {/* RIGHT COLUMN: Available Items (Add) */}
                    <div className="manage-column">
                        <div className="manage-section-header">
                            <div className="icon-box">
                                <UserPlus size={20} className="highlight-icon" />
                                <h3>Available to Add</h3>
                            </div>
                            {selectedIds.length > 0 && (
                                <button
                                    className="btn-primary btn-selected"
                                    onClick={handleAssign}
                                >
                                    Add {selectedIds.length} Selected
                                </button>
                            )}
                        </div>

                        <div className="selection-grid">
                            {availableItems.length === 0 ? (
                                <div className="empty-state-box">
                                    No available items to add.
                                </div>
                            ) : (
                                availableItems.map(item => {
                                    const isSelected = selectedIds.includes(item.id);
                                    return (
                                        <div
                                            key={item.id}
                                            onClick={() => toggleSelection(item.id)}
                                            className={`selection-card ${isSelected ? 'selected' : ''}`}
                                        >
                                            <div className="selection-check-circle">
                                                {isSelected && <Check size={16} strokeWidth={3} />}
                                            </div>
                                            <div className="selection-card-content">
                                                <div className={`selection-card-title ${isSelected ? 'selected' : ''}`}>
                                                    {isStudents ? item.username : `Course ${item.course_number}`}
                                                </div>
                                                <div className="selection-card-desc">
                                                    {isStudents ? item.email : item.description || "No description"}
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })
                            )}
                        </div>
                    </div>

                </div>
            </div>
        </div>
    );
}
