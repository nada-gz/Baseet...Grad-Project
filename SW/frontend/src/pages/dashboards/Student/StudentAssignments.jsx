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
  if (diff <= 0) return "Due!";
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
  const minutes = Math.floor((diff / (1000 * 60)) % 60);
  if (days > 0) return `${days} day(s) left`;
  if (hours > 0) return `${hours} hour(s) left`;
  return `${minutes} minute(s) left`;
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
        for (let assignment of assRes.data) {
          try {
            const subRes = await api.get(
              `/students/${student.id}/assignments/${assignment.id}/submission`
            );
            assignment.submission = subRes.data;
          } catch {
            assignment.submission = null;
          }
        }
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

  const submitAssignment = async (assignmentId, selectedFiles) => {
    const formData = new FormData();
    formData.append("description", description);
    selectedFiles.forEach((file) => formData.append("files", file));

    const res = await api.post(
      `/students/${student.id}/assignments/${assignmentId}/submit`,
      formData,
      { headers: { "Content-Type": "multipart/form-data" } }
    );

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
    setUploadingFor(assignmentId);
    setFiles(selectedFiles);
    submitAssignment(assignmentId, selectedFiles);
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

                        {openLessons[lesson.id] ? (
                          lesson.assignments?.length > 0 ? (
                            <>
                              <div className="materials-list">
                                {lesson.assignments.map((assignment) => (
                                  <div key={assignment.id} className="material-item">
                                    <div className="material-info">
                                      <div className="material-icon">
                                        {assignmentIcons[assignment.assignment_type] || (
                                          <File size={18} />
                                        )}
                                      </div>
                                      <div className="material-text">
                                        <p className="material-title">{assignment.title}</p>
                                        {assignment.description && (
                                          <p className="material-description">
                                            {assignment.description}
                                          </p>
                                        )}
                                        {assignment.deadline && (
                                          <p className="material-deadline">
                                            Deadline:{" "}
                                            {new Date(assignment.deadline).toLocaleString()} (
                                            {formatRemaining(assignment.deadline)})
                                          </p>
                                        )}
                                      </div>
                                    </div>

                                    <input
                                      type="file"
                                      multiple
                                      style={{ display: "none" }}
                                      ref={(el) => (fileInputsRef.current[assignment.id] = el)}
                                      onChange={(e) => handleFileChange(assignment.id, e)}
                                    />

                                    {status === "locked" ? (
                                      <span className="material-locked">
                                        <Lock size={24} />
                                      </span>
                                    ) : (
                                      <div className="material-actions-wrapper">
                                        <a
                                          href={`http://127.0.0.1:8000${assignment.file_url}`}
                                          target="_blank"
                                          rel="noopener noreferrer"
                                          className="material-btn material-btn-outline material-btn-equal"
                                        >
                                          <Eye size={16} /> View
                                        </a>

                                        <button
                                          className="material-btn material-btn-outline material-btn-equal"
                                          onClick={() => handleUploadClick(assignment.id)}
                                        >
                                          {assignment.submission ? (
                                            <>
                                              <RefreshCcw size={16} /> Resubmit
                                            </>
                                          ) : (
                                            <>
                                              <Upload size={16} /> Upload
                                            </>
                                          )}
                                        </button>
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>

                              {/* Submitted & Feedback Section */}
                              {lesson.assignments.some((a) => a.submission) && (
                                <div className="submission-feedback-wrapper">
                                  {lesson.assignments.map(
                                    (assignment) =>
                                      assignment.submission && (
                                        <div
                                          key={assignment.id}
                                          className="submission-feedback-card"
                                        >
                                          <div className="submitted-section">
                                            <span className="submitted-label">
                                              Submitted •{" "}
                                              {assignment.submission.updated_at ||
                                                assignment.submission.submitted_at
                                                ? new Date(
                                                  assignment.submission.updated_at ||
                                                  assignment.submission.submitted_at
                                                ).toLocaleString()
                                                : "Unknown date"}
                                            </span>
                                            <div className="submitted-files">
                                              {assignment.submission.submission_files?.map(
                                                (file, i) => (
                                                  <a
                                                    key={i}
                                                    href={`http://127.0.0.1:8000${file.file_url}`}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="submitted-file-small link"
                                                  >
                                                    {file.file_name}
                                                  </a>
                                                )
                                              )}
                                            </div>
                                          </div>

                                          {assignment.submission.feedback && (
                                            <div className="feedback-box">
                                              <div className="feedback-title">Feedback</div>
                                              <div className="feedback-comment">
                                                {assignment.submission.feedback.comment}
                                              </div>
                                              {assignment.submission.feedback.rating && (
                                                <div className="feedback-rating">
                                                  {renderStars(
                                                    assignment.submission.feedback.rating
                                                  )}
                                                </div>
                                              )}
                                            </div>
                                          )}
                                        </div>
                                      )
                                  )}
                                </div>
                              )}
                            </>
                          ) : (
                            <div className="materials-empty-icon">
                              <span>No assignments uploaded yet</span>
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
