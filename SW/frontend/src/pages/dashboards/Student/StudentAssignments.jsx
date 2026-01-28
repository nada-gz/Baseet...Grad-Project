import { useEffect, useState, useRef } from "react";
import api from "../../../services/api";
import useAuth from "../../../hooks/useAuth";
import {
  FileText,
  Image,
  File,
  Lock,
  Eye,
  ChevronDown,
  ChevronRight,
  Frown,
  Upload,
  RefreshCcw,
} from "lucide-react";

const assignmentIcons = {
  pdf: <FileText size={18} />,
  docx: <FileText size={18} />,
  img: <Image size={18} />,
  zip: <File size={18} />,
};

function formatRemaining(deadline) {
  if (!deadline) return "";
  const now = new Date();
  const end = new Date(deadline);
  const diff = end - now;

  const absDiff = Math.abs(diff);
  const days = Math.floor(absDiff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((absDiff / (1000 * 60 * 60)) % 24);
  const minutes = Math.floor((absDiff / (1000 * 60)) % 60);

  if (diff <= 0) {
    if (days > 0) return `Overdue by ${days} day(s)`;
    if (hours > 0) return `Overdue by ${hours} hour(s)`;
    if (minutes > 0) return `Overdue by ${minutes} minute(s)`;
    return "Due!";
  } else {
    if (days > 0) return `${days} day(s) left`;
    if (hours > 0) return `${hours} hour(s) left`;
    return `${minutes} minute(s) left`;
  }
}

function renderStars(rating) {
  if (!rating) return null;
  const fullStars = "★".repeat(rating);
  const emptyStars = "☆".repeat(5 - rating);
  return (
    <span style={{ color: "#FBBF24", marginLeft: "6px" }}>
      {fullStars}{emptyStars} ({rating}/5)
    </span>
  );
}

export default function StudentAssignments() {
  const { user: student } = useAuth();

  const [milestones, setMilestones] = useState({});
  const [openMilestones, setOpenMilestones] = useState({});
  const [openLessons, setOpenLessons] = useState({});
  const [uploadingFor, setUploadingFor] = useState(null);
  const [files, setFiles] = useState([]);
  const [description, setDescription] = useState("");
  const fileInputsRef = useRef({});

  // Course Filtering
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(null);

  useEffect(() => {
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
        if (sortedCourses.length > 0) setSelectedCourse(sortedCourses[0].id);
      } catch (err) {
        console.error("Failed to load courses:", err);
      }
    };
    fetchCourses();
  }, [student?.id]);

  useEffect(() => {
    const loadLessonsAssignmentsAndSubmissions = async () => {
      const params = selectedCourse ? { course_id: selectedCourse } : {};
      const res = await api.get(`/students/${student.id}/lessons`, { params });

      const grouped = {};
      const initialOpenMilestones = {};
      const initialOpenLessons = {};

      for (let lesson of res.data) {
        const assRes = await api.get(
          `/students/${student.id}/lessons/${lesson.id}/assignments`
        );
        // Submissions are now included in the assignments response from the backend
        lesson.assignments = assRes.data;

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
    if (student?.id && selectedCourse) loadLessonsAssignmentsAndSubmissions();
  }, [student?.id, selectedCourse]);

  const getLessonStatus = (lesson) => {
    if (lesson.progress === 100) return "completed";
    if (lesson.status === "in-progress") return "in-progress";
    return "locked";
  };

  const [errorMessage, setErrorMessage] = useState(null);

  const submitAssignment = async (assignmentId, selectedFiles) => {
    setErrorMessage(null); // Clear previous errors
    try {
      const formData = new FormData();
      formData.append("description", description);
      selectedFiles.forEach((file) => formData.append("files", file));

      // Correct endpoint: /students/{student_id}/assignments/{assignment_id}/submit
      const res = await api.postForm(
        `/students/${student.id}/assignments/${assignmentId}/submit`,
        formData
      );

      // Update state to reflect submission without reload
      setMilestones((prev) => {
        const updated = { ...prev };
        for (const milestoneLessons of Object.values(updated)) {
          for (const lesson of milestoneLessons) {
            const assignment = lesson.assignments.find((a) => a.id === assignmentId);
            if (assignment) assignment.submission = res.data;
          }
        }
        return updated;
      });

      setUploadingFor(null);
      setFiles([]);
      setDescription("");
      alert("Submitted successfully");
    } catch (err) {
      console.error("Submission error:", err);
      const msg = err.response?.data?.detail || "Submission failed";
      setErrorMessage(typeof msg === 'string' ? msg : JSON.stringify(msg));
      setUploadingFor(null); // Stop spinner
    }
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

  const handleUploadClick = (assignmentId) => {
    if (fileInputsRef.current[assignmentId]) {
      fileInputsRef.current[assignmentId].click();
    }
  };

  const handleFileChange = (assignmentId, e) => {
    const selectedFiles = [...e.target.files];
    if (selectedFiles.length === 0) return; // Do not proceed if no files selected

    setUploadingFor(assignmentId);
    setFiles(selectedFiles);
    submitAssignment(assignmentId, selectedFiles);
  };

  return (
    <div className="student-assignments-page kid-friendly-vibe">
      <div className="hero-blob-container assignments-style" style={{ borderColor: '#E0E7FF', boxShadow: '0 12px 0 #E0E7FF' }}>
        <div className="hero-blob-bg" style={{ background: 'radial-gradient(circle, #F1F4FF 0%, #E0E7FF 100%)' }}></div>
        <div className="hero-blob-content">
          <div className="hero-blob-image-wrapper shift-right">
            <img
              src={require("../../../assets/hi_baseet.png")}
              alt="Hi Baseet"
              className="hero-blob-img"
            />
          </div>
          <div className="hero-blob-text">
            <h1 style={{ color: '#6C63FF' }}>🏆 ! تحدي الأبطال </h1>
            <p>ورينا شطارتك وحل المهمات عشان تجمع النجوم</p>
          </div>
        </div>
      </div>

      {errorMessage && (
        <div className="error-bubble-container">
          <div className="error-bubble">
            <span className="error-icon">⚠️</span>
            <p>{errorMessage}</p>
            <button className="close-error" onClick={() => setErrorMessage(null)}>×</button>
          </div>
        </div>
      )}

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
              <p>لسه مفيش مهمات موجودة.. بسيط مستنيك!</p>
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

                      <div className="lesson-assignments-container">
                        {lessons.map((lesson) => {
                          const status = getLessonStatus(lesson);
                          const isOpen = openLessons[lesson.id];

                          return (
                            <div key={lesson.id} className={`lesson-assignment-block ${status}`}>
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
                                <div className="assignments-bubbles-container">
                                  {lesson.assignments?.length > 0 ? (
                                    lesson.assignments.map((assignment) => (
                                      <div key={assignment.id} className="assignment-bubble-wrapper">
                                        <div className="assignment-bubble">
                                          <div className="assignment-bubble-main">
                                            <div className="assignment-bubble-icon">
                                              {status === "locked" ? (
                                                <Lock size={24} />
                                              ) : (
                                                assignmentIcons[assignment.assignment_type] || <File size={24} />
                                              )}
                                            </div>
                                            <div className="assignment-bubble-text">
                                              <h4>{assignment.title}</h4>
                                              {assignment.deadline && !assignment.submission && (
                                                <div className="deadline-pill">
                                                  ⏱️ {formatRemaining(assignment.deadline)}
                                                </div>
                                              )}
                                            </div>
                                          </div>

                                          <div className="assignment-bubble-actions">
                                            {status !== "locked" && (
                                              <>
                                                {/* View Files */}
                                                {(assignment.files || []).map((f) => (
                                                  <a
                                                    key={f.id}
                                                    href={`http://127.0.0.1:8000${f.file_url}`}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="btn-circle-action"
                                                    title="View"
                                                  >
                                                    <Eye size={18} />
                                                  </a>
                                                ))}

                                                {/* Upload/Resubmit */}
                                                <button
                                                  className={`btn-circle-action ${assignment.submission ? 'resubmit' : 'upload'}`}
                                                  onClick={() => handleUploadClick(assignment.id)}
                                                  title={assignment.submission ? "Resubmit" : "Upload"}
                                                >
                                                  {assignment.submission ? <RefreshCcw size={18} /> : <Upload size={18} />}
                                                </button>
                                              </>
                                            )}
                                          </div>

                                          <input
                                            type="file"
                                            multiple
                                            style={{ display: "none" }}
                                            ref={(el) => (fileInputsRef.current[assignment.id] = el)}
                                            onChange={(e) => handleFileChange(assignment.id, e)}
                                          />
                                        </div>

                                        {/* Status & Feedback */}
                                        {assignment.submission && (
                                          <div className="submission-card-kid">
                                            <div className="submission-header">
                                              <span className={`status-badge-kid ${assignment.submission.status}`}>
                                                {assignment.submission.status === 'evaluated' ? 'تم التقييم ✨' :
                                                  assignment.submission.status === 'resubmitted' ? 'تم الإرسال مرة أخرى 🚀' :
                                                    assignment.submission.status === 'submitted' ? 'تم الإرسال 👍' : 'لم يتم الإرسال'}
                                              </span>
                                              {assignment.deadline && (
                                                <span className="deadline-text">آخر موعد: {new Date(assignment.deadline).toLocaleDateString()}</span>
                                              )}
                                            </div>

                                            {assignment.submission.feedback && (
                                              <div className="baseet-feedback-speech">
                                                <div className="baseet-mini-avatar">
                                                  <img src={require("../../../assets/hii_baseet.png")} alt="Baseet" />
                                                </div>
                                                <div className="speech-bubble">
                                                  <div className="speech-content">
                                                    <p>{assignment.submission.feedback.comment}</p>
                                                    {assignment.submission.feedback.rating && (
                                                      <div className="stars-kid">
                                                        {"⭐".repeat(assignment.submission.feedback.rating)}
                                                      </div>
                                                    )}
                                                  </div>
                                                </div>
                                              </div>
                                            )}
                                          </div>
                                        )}
                                      </div>
                                    ))
                                  ) : (
                                    <div className="empty-bubble">مفيش مهمات موجودة حالياً 😅</div>
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
