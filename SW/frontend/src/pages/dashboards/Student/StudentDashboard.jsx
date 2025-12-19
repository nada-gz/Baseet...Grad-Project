import { useState, useEffect } from "react";
import api from "../../../services/api";
import useAuth from "../../../hooks/useAuth";
import { Link } from "react-router-dom";
import { PlayCircle, BookOpen, FileText, Edit3 } from "lucide-react";

export default function StudentDashboard() {
  const { user: student, loading: authLoading, error: authError } = useAuth();

  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadLessons = async () => {
      try {
        const response = await api.get(`/students/${student.id}/lessons`);
        console.log("Lessons from API:", response.data);
        setLessons(response.data);
      } catch (error) {
        console.error("Error loading lessons:", error);
      } finally {
        setLoading(false);
      }
    };

    if (student) loadLessons();
  }, [student]);

  if (authLoading || loading) {
    return <div className="dashboard-loading">Loading...</div>;
  }

  if (authError) {
    return <div className="dashboard-error">Error loading dashboard.</div>;
  }

  // ✅ find current in-progress lesson
  const currentLesson = lessons.find(
    (lesson) => lesson.status === "in-progress"
  );

  return (
    <div className="student-dashboard">
      <main className="lesson-content">
        <img
          src={require("../../../assets/cute_purple_baseet.png")}
          alt="Baseet decoration"
          className="lesson-deco"
        />

        {currentLesson ? (
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

                <Link
                  to={`/dashboard/student/lesson/${currentLesson.id}`}
                  className="btn btn-primary continue-btn"
                >
                  Continue
                </Link>
              </div>
            </div>

            {/* ================= 3 ACTION CARDS ================= */}
            <div className="student-cards-row">
              {/* Lesson Material */}
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

              {/* Assignment */}
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

              {/* Quiz */}
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
          <p>No lessons assigned yet.</p>
        )}
      </main>
    </div>
  );
}
