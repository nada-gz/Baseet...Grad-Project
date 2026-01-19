import { useEffect, useState } from "react";
import api from "../../../services/api";
import useAuth from "../../../hooks/useAuth";
import {
  FileText,
  Image,
  Video,
  Presentation,
  File,
  Lock,
  Eye,
  Download,
  Music,
  ChevronDown,
  ChevronRight,
  Frown,
} from "lucide-react";

/**
 * Supported material types:
 * word | pdf | ppt | img | video | audio
 */
const materialIcons = {
  word: <FileText size={18} />,
  pdf: <FileText size={18} />,
  ppt: <Presentation size={18} />,
  img: <Image size={18} />,
  video: <Video size={18} />,
  audio: <Music size={18} />,
};

export default function StudentMaterials() {
  const { user: student } = useAuth();

  const [milestones, setMilestones] = useState({});
  const [openMilestones, setOpenMilestones] = useState({});
  const [openLessons, setOpenLessons] = useState({});
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(null);

  useEffect(() => {
    // 1. Fetch Courses
    const fetchCourses = async () => {
      if (!student?.id) return;
      try {
        const res = await api.get(`/students/${student.id}/assigned-courses`);
        const sortedCourses = res.data.sort((a, b) => {
          const titleA = (a.title || `Course ${a.course_number}`).toLowerCase();
          const titleB = (b.title || `Course ${b.course_number}`).toLowerCase();
          return titleA.localeCompare(titleB);
        });
        setCourses(sortedCourses);
        // Default to first course if available
        if (sortedCourses.length > 0) setSelectedCourse(sortedCourses[0].id);
      } catch (err) {
        console.error("Failed to load courses:", err);
      }
    };
    fetchCourses();
  }, [student?.id]);

  useEffect(() => {
    const loadLessonsAndMaterials = async () => {
      // Fetch lessons filtered by selected course
      const params = selectedCourse ? { course_id: selectedCourse } : {};
      const res = await api.get(`/students/${student.id}/lessons`, { params });

      const grouped = {};
      const initialOpenMilestones = {};
      const initialOpenLessons = {};

      for (let lesson of res.data) {
        // fetch materials for each lesson
        const matRes = await api.get(
          `/students/${student.id}/lessons/${lesson.id}/materials`
        );
        lesson.materials = matRes.data;

        if (!grouped[lesson.milestone_number]) grouped[lesson.milestone_number] = [];
        grouped[lesson.milestone_number].push(lesson);

        // Expand by default
        initialOpenMilestones[lesson.milestone_number] = true;
        initialOpenLessons[lesson.id] = true;
      }

      setMilestones(grouped);
      setOpenMilestones(initialOpenMilestones);
      setOpenLessons(initialOpenLessons);
    };

    if (student?.id && selectedCourse) loadLessonsAndMaterials();
  }, [student?.id, selectedCourse]);

  const getLessonStatus = (lesson) => {
    if (lesson.progress === 100) return "completed";
    if (lesson.status === "in-progress") return "in-progress";
    return "locked";
  };

  const toggleMilestone = (milestoneNumber) => {
    setOpenMilestones((prev) => ({
      ...prev,
      [milestoneNumber]: !prev[milestoneNumber],
    }));
  };

  const toggleLesson = (lessonId) => {
    setOpenLessons((prev) => ({
      ...prev,
      [lessonId]: !prev[lessonId],
    }));
  };

  return (
    <div className="materials-page">
      {courses.length === 0 ? (
        <div className="text-center p-10 bg-white rounded-lg border border-dashed border-slate-300">
          <p className="text-slate-500">No courses assigned yet.</p>
        </div>
      ) : (
        <>
          {/* Course Filter */}
          <div className="course-filter-section" style={{ marginBottom: "1rem" }}>
            <div className="flex items-center gap-3">
              <p className="filter-text">Filter by Course:</p>
              <select
                className="p-2 border border-slate-300 rounded-lg text-sm bg-white"
                value={selectedCourse || ""}
                onChange={(e) => setSelectedCourse(Number(e.target.value) || null)}
              >
                {courses.map((course) => (
                  <option key={course.id} value={course.id}>
                    {course.title || `Course ${course.course_number}`}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {Object.keys(milestones).length === 0 ? (
            <div className="text-center p-10 bg-white rounded-lg border border-dashed border-slate-300 mt-4">
              <p className="text-slate-500 italic">No milestones assigned yet for this course.</p>
            </div>
          ) : (
            Object.entries(milestones).map(([milestoneNumber, lessons]) => (
              <div key={milestoneNumber} className="milestone-card">
                {/* Milestone Header */}
                <div
                  className="milestone-header"
                  onClick={() => toggleMilestone(milestoneNumber)}
                >
                  {openMilestones[milestoneNumber] ? (
                    <ChevronDown size={18} color="var(--highlight)" />
                  ) : (
                    <ChevronRight size={18} color="var(--highlight)" />
                  )}
                  <h2>Milestone {milestoneNumber}</h2>
                </div>

                {/* Lessons */}
                {openMilestones[milestoneNumber] &&
                  lessons.map((lesson) => {
                    const status = getLessonStatus(lesson);

                    return (
                      <div key={lesson.id} className="lesson-block">
                        <div
                          className="lesson-header"
                          onClick={() => toggleLesson(lesson.id)}
                        >
                          {openLessons[lesson.id] ? (
                            <ChevronDown size={16} />
                          ) : (
                            <ChevronRight size={16} />
                          )}
                          <span>
                            Lesson {lesson.lesson_number}: {lesson.title}
                          </span>
                        </div>

                        {/* Materials */}
                        {openLessons[lesson.id] ? (
                          lesson.materials?.length > 0 ? (
                            <div className="materials-list">
                              {lesson.materials.map((material) => (
                                <div key={material.id} className="material-item">
                                  {status === "locked" ? (
                                    <>
                                      <div className="material-info">
                                        <div className="material-icon">
                                          {materialIcons[material.material_type] || (
                                            <File size={18} />
                                          )}
                                        </div>
                                        <div className="material-text">
                                          <p className="material-title">{material.title}</p>
                                          {material.description && (
                                            <p className="material-description">
                                              {material.description}
                                            </p>
                                          )}
                                        </div>
                                      </div>
                                      <span className="material-locked">
                                        <Lock size={24} />
                                      </span>
                                    </>
                                  ) : (
                                    <div className="material-item-content flex items-center justify-between w-full">
                                      <a
                                        href={material.file_url ? `http://127.0.0.1:8000${material.file_url}` : "#"}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="material-info clickable-material flex-grow"
                                        style={{ textDecoration: "none", color: "inherit", display: "flex", alignItems: "center" }}
                                      >
                                        <div className="material-icon">
                                          {materialIcons[material.material_type] || (
                                            <File size={18} />
                                          )}
                                        </div>
                                        <div className="material-text">
                                          <p className="material-title">{material.title}</p>
                                          {material.description && (
                                            <p className="material-description">
                                              {material.description}
                                            </p>
                                          )}
                                        </div>
                                      </a>
                                      <a
                                        href={material.file_url ? `http://127.0.0.1:8000${material.file_url}` : "#"}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="material-btn material-btn-outline material-btn-equal ml-4"
                                      >
                                        <Eye size={16} /> View
                                      </a>
                                    </div>
                                  )}
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div className="materials-empty-icon">
                              <span>No materials uploaded yet</span>
                              <Frown size={24} className="sad-icon" />
                            </div>
                          )
                        ) : null}
                      </div>
                    );
                  })}
              </div>
            ))
          )}
        </>
      )}
    </div>
  );
}
