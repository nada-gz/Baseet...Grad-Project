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
    <div className="student-materials-page kid-friendly-vibe">
      <div className="hero-banner-frame">
        <img
          src={require("../../../assets/baseet_studying_banner.png")}
          alt="Baseet Studying"
        />
        <div className="frame-text-overlay">
          <h1>💎 ! كنز المعلومات</h1>
          <p>اكتشف الكتب والفيديوهات اللي هتخليك أشطر بطل</p>
        </div>
      </div>

      {courses.length === 0 ? (
        <div className="empty-milestones">
          <p>لسه مفيش كورسات.. بسيط مستنيك!</p>
        </div>
      ) : (
        <>
          {/* Course Filter */}
          <div className="course-filter-section" style={{ marginBottom: "2rem" }}>
            <div className="flex items-center gap-4">
              <select
                className="kid-select"
                value={selectedCourse || ""}
                onChange={(e) => setSelectedCourse(Number(e.target.value) || null)}
              >
                {courses.map((course) => (
                  <option key={course.id} value={course.id}>
                    {course.title || `Course ${course.course_number}`}
                  </option>
                ))}
              </select>
              <span className="filter-label" style={{ fontWeight: 800, fontSize: "1.1rem" }}>: اختر الكورس</span>
            </div>
          </div>

          {Object.keys(milestones).length === 0 ? (
            <div className="empty-milestones mt-4">
              <p>لسه مفيش مراحل موجودة.. بسيط مستنيك!</p>
            </div>
          ) : (
            <div className="milestones-container">
              {Object.entries(milestones)
                .sort(([a], [b]) => Number(a) - Number(b))
                .map(([milestoneNumberStr, lessons]) => {
                  const milestoneNumber = Number(milestoneNumberStr);
                  return (
                    <div key={milestoneNumber} className="milestone-island">
                      <div className="milestone-header-kid">
                        <div className="milestone-badge">مرحلة {milestoneNumber}</div>
                        <h2 className="milestone-title">المرحلة {milestoneNumber}</h2>
                      </div>

                      <div className="lesson-materials-container">
                        {lessons.map((lesson) => {
                          const status = getLessonStatus(lesson);
                          const isOpen = openLessons[lesson.id];

                          return (
                            <div key={lesson.id} className={`lesson-material-block ${status}`}>
                              <div
                                className="lesson-header-pill"
                                onClick={() => toggleLesson(lesson.id)}
                              >
                                <div className="lesson-pill-info">
                                  <div className="lesson-pill-icon">
                                    {isOpen ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                                  </div>
                                  <span>درس {lesson.lesson_number}: {lesson.title}</span>
                                </div>
                                {status === "locked" && <Lock size={18} className="text-secondary-text" />}
                              </div>

                              {isOpen && (
                                <div className="materials-bubbles-row">
                                  {lesson.materials?.length > 0 ? (
                                    lesson.materials.map((material) => (
                                      <div key={material.id} className="material-bubble">
                                        <div className="material-bubble-content">
                                          <div className="material-bubble-icon">
                                            {status === "locked" ? (
                                              <Lock size={24} />
                                            ) : (
                                              materialIcons[material.material_type] || <File size={24} />
                                            )}
                                          </div>
                                          <div className="material-bubble-text">
                                            <h4>{material.title}</h4>
                                          </div>
                                        </div>

                                        <div className="material-bubble-actions">
                                          {status !== "locked" && (
                                            <a
                                              href={material.file_url ? `http://127.0.0.1:8000${material.file_url}` : "#"}
                                              target="_blank"
                                              rel="noopener noreferrer"
                                              className="btn-circle-action"
                                              title="View"
                                            >
                                              <Eye size={18} />
                                            </a>
                                          )}
                                        </div>
                                      </div>
                                    ))
                                  ) : (
                                    <div className="empty-bubble">مفيش ملفات موجودة حالياً 😅</div>
                                  )}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
            </div>
          )}
        </>
      )}
    </div>
  );
}
