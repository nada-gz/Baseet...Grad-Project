
import React, { useState, useEffect } from "react";
import api from "../../../services/api";
import { Trash2, User as UserIcon } from "lucide-react";
import "../../../styles/index.css"; // Reuse existing styles

export default function StudentMonitoring() {
    const [levels, setLevels] = useState([]); // Array of level objects with descriptions
    const [allStudents, setAllStudents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [view, setView] = useState("dashboard"); // "dashboard" | "detail"
    const [selectedLevel, setSelectedLevel] = useState(null);

    // ---------------- FETCH DATA ----------------
    const fetchData = async () => {
        setLoading(true);
        try {
            const [levelsRes, studentsRes, lessonsRes] = await Promise.all([
                api.get("/teacher/levels"),
                api.get("/teacher/students"),
                api.get("/teacher/lessons")
            ]);

            console.log("Levels Res:", levelsRes.data);
            console.log("Lessons Res:", lessonsRes.data);
            console.log("Students Res:", studentsRes.data);

            // 1. Get descriptions map
            const descMap = {};
            (levelsRes.data || []).forEach(l => {
                descMap[l.level_number] = l.description || "";
            });

            // 2. Extract unique levels from lessons
            const uniqueLevels = new Set([
                ...(levelsRes.data || []).map(l => l.level_number),
                ...(lessonsRes.data || []).map(l => l.level_number)
            ]);

            // 3. Build level objects
            const combinedLevels = Array.from(uniqueLevels).sort((a, b) => a - b).map(num => ({
                level_number: num,
                description: descMap[num] || ""
            }));

            setLevels(combinedLevels);
            setAllStudents(studentsRes.data || []);
        } catch (err) {
            console.error("Fetch data error:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    // Filter students for the selected level
    const getStudentsForLevel = (levelNum) => {
        return allStudents.filter(s => s.level_number === levelNum);
    };

    if (loading) return <p className="p-8">Loading...</p>;

    // --- DASHBOARD VIEW (Level Cards) ---
    if (view === "dashboard") {
        return (
            <div className="lesson-prep-container level-prep-container">
                <h1 className="text-2xl font-bold mb-6">Student Monitoring</h1>
                <p className="text-gray-600 mb-6">Select a level to view its students.</p>

                <div className="levels-grid">
                    {levels.map((level) => {
                        const studentCount = getStudentsForLevel(level.level_number).length;
                        return (
                            <div
                                key={level.level_number}
                                className="level-card-dashboard"
                                onClick={() => {
                                    setSelectedLevel(level);
                                    setView("detail");
                                }}
                            >
                                <div className="level-card-header">
                                    <h2 className="level-card-title">Level {level.level_number}</h2>
                                    {/* No delete button here, just monitoring */}
                                </div>

                                <div className="mb-2" style={{ flexGrow: 1 }}>
                                    <label className="level-card-desc-label">Description</label>
                                    <p className="text-gray-700 text-sm whitespace-pre-wrap">
                                        {level.description || "No description provided."}
                                    </p>
                                </div>

                                <div className="level-card-footer">
                                    <span>{studentCount} Students</span>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        );
    }

    // --- DETAIL VIEW (Student List) ---
    if (!selectedLevel) return null;

    const levelStudents = getStudentsForLevel(selectedLevel.level_number);

    return (
        <div className="lesson-prep-container">
            <div className="flex items-center mb-6">
                <div className="back-box">
                    <button
                        className="mr-4 back"
                        onClick={() => {
                            setView("dashboard");
                            setSelectedLevel(null);
                        }}
                    >
                        &larr; Back to Levels
                    </button>
                </div>
                <h1 className="text-2xl level-card-title">Level {selectedLevel.level_number} Students</h1>
            </div>

            <div className="student-list-container">
                {levelStudents.length === 0 ? (
                    <div className="text-center p-8 bg-white rounded shadow">
                        <p className="text-gray-500">No students assigned to this level yet.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {levelStudents.map(student => (
                            <div key={student.id} className="student-card cursor-pointer hover:shadow-lg transition">
                                <div className="card-icon">
                                    <UserIcon size={40} />
                                </div>
                                <h3 className="card-title">{student.username}</h3>
                                <p className="card-description">{student.email}</p>
                                {/* Future: Add buttons for monitoring actions */}
                                <div className="mt-4">
                                    <span className="text-xs font-semibold bg-gray-200 px-2 py-1 rounded text-gray-700">
                                        Age: {student.age || "N/A"}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
