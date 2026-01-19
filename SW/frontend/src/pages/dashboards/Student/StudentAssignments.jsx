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
    <div className="materials-page">
      {errorMessage && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{errorMessage}</span>
          <span className="absolute top-0 bottom-0 right-0 px-4 py-3" onClick={() => setErrorMessage(null)}>
            <svg
              className="fill-current text-red-500"
              role="button"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              style={{ width: '24px', height: '24px' }}
            >
              <title>Close</title>
              <path d="M14.348 14.849a1.2 1.2 0 0 1-1.697 0L10 11.819l-2.651 3.029a1.2 1.2 0 1 1-1.697-1.697l2.758-3.15-2.759-3.152a1.2 1.2 0 1 1 1.697-1.697L10 8.183l2.651-3.031a1.2 1.2 0 1 1 1.697 1.697l-2.758 3.152 2.758 3.15a1.2 1.2 0 0 1 0 1.698z" />
            </svg>
          </span>
        </div>
      )}
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
                                    {status === "locked" ? (
                                      <div className="material-info">
                                        <div className="material-icon">
                                          {assignmentIcons[assignment.assignment_type] || (
                                            <File size={18} />
                                          )}
                                        </div>
                                        <div className="material-text">
                                          <div className="flex items-center gap-2">
                                            <p className="material-title">{assignment.title}</p>
                                            {assignment.deadline && (
                                              <div className="material-deadline text-red-500 text-[10px] font-bold bg-red-50 px-1 py-0.5 rounded border border-red-200 shrink-0">
                                                <span className="ml-1 bg-red-500 text-white px-1 rounded">
                                                  {formatRemaining(assignment.deadline)}
                                                </span>
                                              </div>
                                            )}
                                          </div>
                                          {assignment.description && (
                                            <p className="material-description">
                                              {assignment.description}
                                            </p>
                                          )}
                                        </div>
                                        <span className="material-locked">
                                          <Lock size={24} />
                                        </span>
                                      </div>
                                    ) : (
                                      <>
                                        <div className="assignment-item-content w-full flex justify-between items-start">
                                          <div className="material-info mb-2 flex-grow">
                                            <div className="material-icon">
                                              {assignmentIcons[assignment.assignment_type] || (
                                                <File size={18} />
                                              )}
                                            </div>
                                            <div className="material-text">
                                              <div className="flex items-center gap-2">
                                                <p className="material-title">{assignment.title}</p>
                                                {assignment.deadline && (
                                                  <div className="material-deadline text-red-500 text-[10px] font-bold bg-red-50 px-1 py-0.5 rounded border border-red-200 shrink-0">
                                                    {!assignment.submission && (
                                                      <span className="ml-1 bg-red-500 text-white px-1 rounded">
                                                        {formatRemaining(assignment.deadline)}
                                                      </span>
                                                    )}
                                                  </div>
                                                )}
                                              </div>
                                              {assignment.description && (
                                                <p className="material-description">
                                                  {assignment.description}
                                                </p>
                                              )}
                                            </div>
                                          </div>

                                          <div className="assignment-actions flex items-center gap-4 ml-4">


                                            {/* View Buttons for Files */}
                                            {assignment.files && assignment.files.map((f) => (
                                              <a
                                                key={f.id}
                                                href={`http://127.0.0.1:8000${f.file_url}`}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="material-btn material-btn-outline material-btn-equal"
                                              >
                                                <Eye size={16} /> View
                                              </a>
                                            ))}

                                            {/* Legacy File URL View Button */}
                                            {!assignment.files?.length && assignment.file_url && (
                                              <a
                                                href={`http://127.0.0.1:8000${assignment.file_url}`}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="vieww material-btn material-btn-outline material-btn-equal"
                                              >
                                                <Eye size={16} /> View
                                              </a>
                                            )}

                                            {/* Upload Button */}
                                            <div className="uppload material-actions-wrapper">
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
                                          </div>
                                        </div>

                                        <input
                                          type="file"
                                          multiple
                                          style={{ display: "none" }}
                                          ref={(el) => (fileInputsRef.current[assignment.id] = el)}
                                          onChange={(e) => handleFileChange(assignment.id, e)}
                                        />
                                      </>
                                    )}
                                  </div>
                                ))}
                              </div>

                              {/* Submitted & Feedback Section */}
                              <div className="submission-feedback-wrapper">
                                {lesson.assignments.map((assignment) => (
                                  <div
                                    key={assignment.id}
                                    className="submission-feedback-card"
                                  >
                                    <div className="card-assignment-item-bottom">
                                      <div className="item-assignment-status">
                                        <div className="flex items-center">
                                          <span className={`status-badge ${assignment.submission?.status === 'evaluated' ? 'badge-evaluated' :
                                            assignment.submission?.status === 'resubmitted' ? 'badge-resubmitted' :
                                              assignment.submission?.status === 'submitted' ? 'badge-submitted' : 'badge-not-submitted'
                                            }`}>
                                            {assignment.submission?.status || "not submitted yet"}
                                          </span>
                                        </div>
                                        {assignment.deadline && (
                                          <span className="material-deadline deadline text-red-500 text-[10px] font-bold bg-red-50 px-2 py-0.5 rounded border border-red-200 ml-2">
                                            Deadline: {new Date(assignment.deadline).toLocaleString()}
                                          </span>
                                        )}
                                        {(assignment.submission?.status === 'submitted' || assignment.submission?.status === 'resubmitted' || assignment.submission?.status === 'evaluated') && assignment.submission?.timing && (
                                          <span className="text-secondary-text text-sm ml-2 italic">
                                            ({assignment.submission.updated_at ? 'Resubmitted at' : 'Submitted at'}: {new Date(assignment.submission.timing).toLocaleString()})
                                          </span>
                                        )}
                                      </div>
                                      <div className="item-assignment-actions"></div>
                                      {assignment.submission && (
                                        <div className="submission-details">
                                          {assignment.submission.description && (
                                            <p className="submission-desc">
                                              {assignment.submission.description}
                                            </p>
                                          )}
                                          {assignment.submission.files && assignment.submission.files.length > 0 && (
                                            <div className="submission-files-list mt-2">
                                              {assignment.submission.files.map((file, idx) => (
                                                <div key={idx} className="flex items-center gap-2 mb-1">
                                                  <a
                                                    href={`http://127.0.0.1:8000${file.file_url}`}
                                                    target="_blank"
                                                    rel="noreferrer"
                                                    className="text-sm text-secondary-text hover:text-highlight transition-colors flex items-center gap-1"
                                                  >
                                                    📄 <span className="underline decoration-slate-300 underline-offset-4">{file.file_name}</span>
                                                  </a>
                                                </div>
                                              ))}
                                            </div>
                                          )}
                                        </div>
                                      )}
                                    </div>

                                    {assignment.submission?.feedback && (
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
                                ))}
                              </div>
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
              </div >
            ))
          )}
        </>
      )}
    </div >
  );
}
