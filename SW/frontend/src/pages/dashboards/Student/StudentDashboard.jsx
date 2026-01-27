import { useState, useEffect } from "react";
import api from "../../../services/api";
import useAuth from "../../../hooks/useAuth";
import { Link } from "react-router-dom";
import { PlayCircle, BookOpen, FileText, Edit3, Eye } from "lucide-react";

export default function StudentDashboard() {
  const { user: student, loading: authLoading, error: authError } = useAuth();

  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentAssignments, setCurrentAssignments] = useState([]);
  const [assignmentStatus, setAssignmentStatus] = useState("loading"); // 'none', 'not-submitted', 'submitted', 'evaluated'
  const [selectionModal, setSelectionModal] = useState(null); // { id: ... }

  useEffect(() => {
    const loadData = async () => {
      if (!student?.id) return;
      try {
        const coursesRes = await api.get(`/students/${student.id}/assigned-courses`);
        if (coursesRes.data.length === 0) {
          setLoading(false);
          return;
        }

        // Try to find a lesson across all courses if needed, 
        // but let's at least try the first few courses if the first one is empty
        let foundLessons = [];
        let activeCourseId = null;

        for (const course of coursesRes.data) {
          const res = await api.get(`/students/${student.id}/lessons`, {
            params: { course_id: course.id }
          });
          if (res.data.length > 0) {
            foundLessons = res.data;
            activeCourseId = course.id;
            // If one of these is in-progress, we are done
            if (res.data.some(l => l.status === 'in-progress')) {
              break;
            }
          }
        }

        setLessons(foundLessons);
      } catch (err) {
        console.error("Failed to load dashboard data:", err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [student?.id]);

  // ✅ find current in-progress lesson or default to first
  const currentLesson = lessons.find((l) => l.status === "in-progress") || lessons[0];

  useEffect(() => {
    if (!currentLesson) return;

    const fetchAssignmentsAndStatus = async () => {
      try {
        const res = await api.get(
          `/students/${student.id}/lessons/${currentLesson.id}/assignments`
        );
        setCurrentAssignments(res.data);

        if (res.data.length > 0) {
          // Check submission for the first assignment
          // Assuming one assignment per lesson for simplicity as per UI
          try {
            const subRes = await api.get(
              `/students/${student.id}/assignments/${res.data[0].id}/submission`
            );
            if (subRes.data) {
              setAssignmentStatus(
                subRes.data.feedback ? "evaluated" : "submitted"
              );
            }
          } catch (err) {
            if (err.response && err.response.status === 404) {
              setAssignmentStatus("not-submitted");
            } else {
              console.error("Error checking submission:", err);
            }
          }
        } else {
          setAssignmentStatus("none");
        }
      } catch (err) {
        console.error("Failed to load assignments for dashboard:", err);
      }
    };

    fetchAssignmentsAndStatus();
  }, [currentLesson, student?.id]);

  if (authLoading || loading) {
    return <div className="dashboard-loading">Loading...</div>;
  }

  if (authError) {
    return <div className="dashboard-error">Error loading dashboard.</div>;
  }


  return (
    <div className="student-dashboard kid-friendly-vibe">
      <main className="lesson-content">
        <div className="hero-blob-container" style={{ marginBottom: '40px' }}>
          <div className="hero-blob-bg dashboard-image-blob"></div>
          <div className="hero-blob-content">
            <div className="hero-blob-text">
              <h1>أهلاً بك يا بطل</h1>
              <p>مستعد لمغامرة جديدة مع بسيط؟</p>
            </div>
          </div>
        </div>

        <img
          src={require("../../../assets/bubbles_baseet.png")}
          alt="Baseet decoration"
          className="lesson-deco"
        />

        {
          currentLesson ? (
            <>
              {/* ================= CONTINUE CARD ================= */}
              <div className="continue-card">
                <div className="continue-icon">
                  <PlayCircle size={56} />
                </div>

                <div className="continue-info">
                  <span className="continue-label">
                    Continue your progress
                  </span>

                  <h1 className="continue-title">
                    <span className="lesson-number">
                      {currentLesson.number}{" "}
                    </span>
                    {currentLesson.title}
                  </h1>

                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${currentLesson.progress}%` }}
                    />
                  </div>

                  <button
                    onClick={() => setSelectionModal({ id: currentLesson.id })}
                    className="btn btn-primary continue-btn"
                  >
                    Continue
                  </button>
                </div>
              </div>

              {/* ================= 3 ACTION CARDS ================= */}
              <div className="student-cards-row">
                {/* Lesson Material */}
                <div className="student-card">
                  <div className="card-icon">
                    <BookOpen size={36} />
                  </div>
                  <h2 className="card-title">Lesson Materials</h2>

                  {currentLesson.materials && currentLesson.materials.length > 0 ? (
                    <div className="dashboard-items-list">
                      {currentLesson.materials.slice(0, 3).map((mat) => (
                        <div key={mat.id} className="dashboard-item">
                          <div className="flex items-center overflow-hidden">
                            <FileText size={16} className="file-show text-slate-400 shrink-0" />
                            <span className="truncate text-sm text-slate-700" title={mat.title}>
                              {mat.title}
                            </span>
                          </div>
                          <a
                            href={`http://127.0.0.1:8000${mat.file_url}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn-icon-small"
                            title="View Material"
                          >
                            <Eye size={16} />
                          </a>
                        </div>
                      ))}
                      {currentLesson.materials.length > 3 && (
                        <Link to="/dashboard/student/materials" className="text-xs text-indigo-500 text-center block mt-1">
                          + {currentLesson.materials.length - 3} more
                        </Link>
                      )}
                    </div>
                  ) : (
                    <p className="text-sm text-slate-400 mb-4">No materials available</p>
                  )}

                  <div className="card-buttons mt-auto">
                    <Link
                      to="/dashboard/student/materials"
                      className="btn btn-secondary w-full text-center"
                    >
                      View All
                    </Link>
                  </div>
                </div>

                {/* Assignment */}
                <div className="student-card">
                  <div className="card-icon">
                    <FileText size={36} />
                  </div>
                  <h2 className="card-title">Assignment</h2>

                  {currentAssignments.length > 0 ? (
                    <div className="dashboard-items-list">
                      {currentAssignments.map((ass) => (
                        <div key={ass.id} className="dashboard-item-col">
                          <div className="dashboard-item" style={{ border: 'none', background: 'transparent', padding: '0', marginBottom: '4px' }}>
                            <div className="flex items-center gap-2 overflow-hidden flex-1">
                              <FileText size={16} className="file-show text-slate-400 shrink-0" />
                              <span className="truncate text-sm text-slate-700" title={ass.title}>
                                {ass.title}
                              </span>
                            </div>
                            <a
                              href={`http://127.0.0.1:8000${ass.file_url}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="btn-icon-small ml-2 shrink-0"
                              title="View Assignment File"
                            >
                              <Eye size={16} />
                            </a>
                          </div>

                          <div className="flex justify-between items-center pl-1">
                            {/* Status Badge */}
                            {assignmentStatus === "not-submitted" && (
                              <p className="ass-status text-[10px] font-bold px-1.5 py-0.5 rounded bg-red-100 text-red-600">Not Submitted</p>
                            )}
                            {assignmentStatus === "submitted" && (
                              <p className="ass-status text-[10px] font-bold px-1.5 py-0.5 rounded bg-yellow-100 text-yellow-600">Submitted</p>
                            )}
                            {assignmentStatus === "evaluated" && (
                              <p className="ass-status text-[10px] font-bold px-1.5 py-0.5 rounded bg-green-100 text-green-600">Evaluated</p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-slate-400 mb-4">No assignments</p>
                  )}

                  <div className="card-buttons mt-auto pt-4">
                    <Link
                      to="/dashboard/student/assignments"
                      className={`btn btn-secondary w-full text-center ${currentAssignments.length === 0 ? "opacity-50 pointer-events-none" : ""}`}
                    >
                      View All
                    </Link>
                  </div>

                </div>

                {/* Quiz */}
                <div className="student-card">
                  <div className="card-icon">
                    <Edit3 size={36} />
                  </div>
                  <h2 className="card-title">Quiz</h2>
                  <p className="card-description">3 attempts allowed</p>
                  <div className="card-buttons mt-auto">
                    <button className="btn btn-primary w-full">Start Quiz</button>
                  </div>
                </div>
              </div>

              <div className="dashboard-studying-footer">
                <img
                  src={require("../../../assets/baseet_studying_banner.png")}
                  alt="Baseet Studying"
                  className="studying-banner-img"
                />
                <div className="studying-text">
                  <h3> 📚 ! مغامرة المذاكرة بدأت</h3>
                  <p> ! كل درس بتخلصه بيقربك خطوة من النجاح</p>
                </div>
              </div>
            </>
          ) : (
            <p>No lessons assigned yet.</p>
          )
        }

        {selectionModal && (
          <div className="modal-overlay">
            <div className="modal-card lesson-selection-modal">
              <div className="baseet-selection-header">
                <img
                  src={require("../../../assets/hi_baseet.png")}
                  alt="Baseet waving"
                  className="baseet-selection-img"
                />
                <h3>✨ ! بسيط مستني يكلمك</h3>
                <p>تحب تذاكر الدرس ده بـ الشات، ولا الصوت، ولا الفيديو؟</p>
              </div>

              <div className="selection-actions">
                <button
                  className="selection-btn video-mode"
                  onClick={() => {
                    window.location.href = `/dashboard/student/lesson/${selectionModal.id}/video`;
                    setSelectionModal(null);
                  }}
                >
                  <div className="mode-icon">🎬</div>
                  <span>فيديو</span>
                </button>
                <button
                  className="selection-btn chat-mode"
                  onClick={() => {
                    window.location.href = `/dashboard/student/lesson/${selectionModal.id}`;
                    setSelectionModal(null);
                  }}
                >
                  <div className="mode-icon">💬</div>
                  <span>شات</span>
                </button>

                <button
                  className="selection-btn voice-mode"
                  onClick={() => {
                    window.location.href = `/dashboard/student/lesson/${selectionModal.id}/voice`;
                    setSelectionModal(null);
                  }}
                >
                  <div className="mode-icon">🎙️</div>
                  <span>صوت</span>
                </button>
              </div>

              <button
                className="btn btn-outline close-selection"
                onClick={() => setSelectionModal(null)}
              >
                إلغاء
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
