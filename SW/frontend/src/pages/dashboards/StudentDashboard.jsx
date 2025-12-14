import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { getStudentDashboard } from "../../api/student";
import { Link } from "react-router-dom";
import { PlayCircle, BookOpen, FileText, Edit3 } from "lucide-react";

export default function StudentDashboard() {
  const { user, studentId, loading: authLoading } = useAuth();

  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load dashboard data on mount
  useEffect(() => {
    const loadDashboard = async () => {
      if (!studentId) {
        setLoading(false);
        setError("Student ID not found. Please log in again.");
        return;
      }

      setLoading(true);
      setError(null);
      
      try {
        const data = await getStudentDashboard(studentId);
        setDashboardData(data);
      } catch (err) {
        console.error("Error loading dashboard:", err);
        setError("Failed to load dashboard data. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    if (studentId) {
      loadDashboard();
    } else if (!authLoading) {
      // If auth is done loading but no studentId, show error
      setLoading(false);
      setError("Student ID not found. Please log in again.");
    }
  }, [studentId, authLoading]);

  if (authLoading || loading) {
    return <div className="dashboard-loading">Loading...</div>;
  }

  if (error) {
    return <div className="dashboard-error">{error}</div>;
  }

  if (!dashboardData) {
    return <div className="dashboard-error">No dashboard data available.</div>;
  }

  const { lessons = [], materials = [], assignments = [], quizzes = [] } = dashboardData;
  const currentLesson = lessons.find(l => l.status === "in-progress");

  return (
    <div className="student-dashboard">
      <main className="lesson-content">
        <img
          src={require("../../assets/cute_purple_baseet.png")}
          alt="Baseet decoration"
          className="lesson-deco"
        />

        {currentLesson ? (
          <>
            {/* Main Continue Card */}
            <div className="continue-card">
              <div className="continue-icon">
                <PlayCircle size={56} />
              </div>
              <div className="continue-info">
                <span className="continue-label">Continue your progress</span>
                <h1 className="continue-title">
                  <span className="lesson-number">{currentLesson.number}.</span>
                  {currentLesson.title}
                </h1>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${currentLesson.progress}%` }}
                  />
                </div>
                <Link
                  to={`/lesson/${currentLesson.id}`}
                  className="btn btn-primary continue-btn"
                >
                  Continue
                </Link>
              </div>
            </div>

            {/* 3 Cards Row */}
            <div className="student-cards-row">
              {/* Lesson Material Card */}
              <div className="student-card">
                <div className="card-icon">
                  <BookOpen size={36} />
                </div>
                <h2 className="card-title">Lesson Material</h2>
                <div className="card-buttons">
                  <button className="btn btn-secondary">View</button>
                  <button className="btn btn-primary">Download</button>
                </div>
              </div>

              {/* Assignment Card */}
              <div className="student-card">
                <div className="card-icon">
                  <FileText size={36} />
                </div>
                <h2 className="card-title">Assignment</h2>
                <div className="card-buttons">
                  <button className="btn btn-secondary">View</button>
                  <button className="btn btn-primary">Upload</button>
                </div>
              </div>

              {/* Quiz Card */}
              <div className="student-card">
                <div className="card-icon">
                  <Edit3 size={36} />
                </div>
                <h2 className="card-title">Quiz</h2>
                <p className="card-description">3 attempts allowed</p>
                <button className="btn btn-primary">Start Quiz</button>
              </div>
            </div>
          </>
        ) : (
          <div className="no-lessons">
            <h1 className="lesson-title">Welcome, {user?.username}!</h1>
            <p className="lesson-description">
              {lessons.length === 0 
                ? "No lessons assigned yet. Please check back later."
                : "Select a lesson to continue your learning journey."}
            </p>
            {lessons.length > 0 && (
              <div className="lessons-list">
                <h2>Available Lessons</h2>
                <ul>
                  {lessons.map((lesson) => (
                    <li key={lesson.id}>
                      <Link to={`/lesson/${lesson.id}`}>
                        {lesson.number}. {lesson.title} ({lesson.status})
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
