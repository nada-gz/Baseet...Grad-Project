import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../../services/api";
import useAuth from "../../../hooks/useAuth";
import { BookOpen, ChevronRight } from "lucide-react";

export default function StudentCourses() {
    const { user: student } = useAuth();
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchCourses = async () => {
            if (!student?.id) return;
            try {
                const res = await api.get(`/students/${student.id}/assigned-courses`);
                const sortedCourses = res.data.sort((a, b) => {
                    const nameA = (a.title || `Course ${a.course_number}`).toLowerCase();
                    const nameB = (b.title || `Course ${b.course_number}`).toLowerCase();
                    return nameA.localeCompare(nameB);
                });
                setCourses(sortedCourses);
            } catch (err) {
                console.error("Failed to load courses:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchCourses();
    }, [student?.id]);

    if (loading) return <div className="p-8">Loading courses...</div>;

    return (
        <div className="student-courses-page">

            {courses.length === 0 ? (
                <div className="text-center p-10 bg-white rounded-lg border border-dashed border-slate-300">
                    <p className="text-slate-500">No courses available yet.</p>
                </div>
            ) : (
                <div className="student-courses-grid">
                    {courses.map((course) => (
                        <Link
                            key={course.id}
                            to={`/dashboard/student/courses/${course.id}`}
                            className="student-course-card"
                        >
                            <div className="student-course-header">
                                <h2 className="student-course-title">{course.title || `Course ${course.course_number}`}</h2>
                                <BookOpen size={28} />
                            </div>

                            <div className="student-course-body">
                                <label className="student-course-label">Description</label>
                                <div className="student-course-desc">
                                    {course.description || "No description available for this course."}
                                </div>
                            </div>

                            <div className="student-course-footer">
                                <span>View Milestones</span>
                                <ChevronRight size={20} />
                            </div>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
}
