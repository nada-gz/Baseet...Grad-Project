import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../../services/api";
import { Trash2, User as UserIcon, BookOpen, Activity } from "lucide-react";
import "../../../styles/index.css"; // Reuse existing styles

export default function StudentMonitoring() {
    const navigate = useNavigate();
    const [courses, setCourses] = useState([]); // Array of course objects with descriptions
    const [allStudents, setAllStudents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [view, setView] = useState("dashboard"); // "dashboard" | "detail"
    const [selectedCourse, setSelectedCourse] = useState(null);

    // ---------------- FETCH DATA ----------------
    const fetchData = async () => {
        setLoading(true);
        try {
            const [coursesRes, studentsRes, lessonsRes] = await Promise.all([
                api.get("/teacher/courses"),
                api.get("/teacher/students"),
                api.get("/teacher/lessons")
            ]);

            console.log("Courses Res:", coursesRes.data);
            console.log("Lessons Res:", lessonsRes.data);
            console.log("Students Res:", studentsRes.data);

            // 1. Get descriptions map
            const descMap = {};
            (coursesRes.data || []).forEach(c => {
                descMap[c.course_number] = c.description || "";
            });

            // 2. Extract unique courses from lessons
            const uniqueCourses = new Set([
                ...(coursesRes.data || []).map(c => c.course_number),
                ...(lessonsRes.data || []).map(l => l.course_number)
            ]);

            // 3. Build course objects
            const combinedCourses = Array.from(uniqueCourses).sort((a, b) => a - b).map(num => ({
                course_number: num,
                description: descMap[num] || ""
            }));

            setCourses(combinedCourses);
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

    // Filter students for the selected course
    const getStudentsForCourse = (courseNum) => {
        return allStudents.filter(s => s.course_number === courseNum);
    };

    if (loading) return <p className="p-8">Loading...</p>;

    // --- DASHBOARD VIEW (Course Cards) ---
    if (view === "dashboard") {
        return (
            <div className="lesson-prep-container level-prep-container">
                <h1 className="text-2xl font-bold mb-6">Student Monitoring</h1>
                <p className="text-gray-600 mb-6">Select a course to view its students.</p>

                <div className="levels-grid">
                    {courses.map((course) => {
                        const studentCount = getStudentsForCourse(course.course_number).length;
                        return (
                            <div
                                key={course.course_number}
                                className="level-card-dashboard"
                                onClick={() => {
                                    setSelectedCourse(course);
                                    setView("detail");
                                }}
                            >
                                <div className="level-card-header">
                                    <h2 className="level-card-title">Course {course.course_number}</h2>
                                    {/* No delete button here, just monitoring */}
                                </div>

                                <div className="mb-2" style={{ flexGrow: 1 }}>
                                    <label className="level-card-desc-label">Description</label>
                                    <p className="text-gray-700 text-sm whitespace-pre-wrap">
                                        {course.description || "No description provided."}
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
    if (!selectedCourse) return null;

    const courseStudents = getStudentsForCourse(selectedCourse.course_number);

    return (
        <div className="lesson-prep-container">
            <div className="flex items-center mb-6">
                <div className="back-box">
                    <button
                        className="mr-4 back"
                        onClick={() => {
                            setView("dashboard");
                            setSelectedCourse(null);
                        }}
                    >
                        &larr; Back to Courses
                    </button>
                </div>
                <h1 className="text-2xl level-card-title">Course {selectedCourse.course_number} Students</h1>
            </div>

            <div className="student-list-container">
                {courseStudents.length === 0 ? (
                    <div className="text-center p-8 bg-white rounded shadow">
                        <p className="text-gray-500">No students assigned to this course yet.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {courseStudents.map(student => (
                            <div key={student.id} className="student-card cursor-pointer hover:shadow-lg transition bg-white p-6 rounded-lg shadow">
                                <div className="flex justify-center mb-4 text-gray-400">
                                    <UserIcon size={40} />
                                </div>
                                <h3 className="text-xl font-bold text-center mb-1">{student.username}</h3>
                                <p className="text-sm text-gray-500 text-center mb-4">{student.email}</p>

                                <div className="flex justify-center gap-12 mt-12">
                                    <button
                                        className="btn btn-sm btn-outline flex items-center gap-2 hover:bg-blue-50 transition-colors"
                                        style={{ fontSize: '0.9rem', padding: '0.7rem 1.5rem', borderColor: '#e2e8f0' }}
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            navigate(`/dashboard/teacher/students/${student.id}/progress`);
                                        }}
                                    >
                                        <BookOpen size={18} className="text-blue-500" />
                                        <span className="font-medium text-gray-700">Academic</span>
                                    </button>
                                    <button
                                        className="btn btn-sm btn-primary flex items-center gap-2 hover:opacity-90 transition-opacity shadow-sm"
                                        style={{ fontSize: '0.9rem', padding: '0.7rem 1.5rem' }}
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            navigate(`/dashboard/teacher/students/${student.id}/live`);
                                        }}
                                    >
                                        <Activity size={18} />
                                        <span className="font-medium">Live</span>
                                    </button>
                                </div>

                                <div className="mt-4 text-center">
                                    <span className="text-xs font-semibold bg-gray-100 px-2 py-1 rounded text-gray-600">
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

