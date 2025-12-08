import { useState, useEffect } from "react";
import api from "../../services/api";
import useAuth from "../../hooks/useAuth";
import { Link } from "react-router-dom";

export default function StudentDashboard() {
  const { user, loading: authLoading, error: authError } = useAuth();

  const [milestones, setMilestones] = useState([]);
  const [selectedMilestone, setSelectedMilestone] = useState(null);
  const [loading, setLoading] = useState(true);

  // Simulating real backend milestone progress
  useEffect(() => {
    const loadMilestones = async () => {
      try {
        const response = await api.get(`/student/${user.id}/milestones`);
        setMilestones(response.data);
      } catch (error) {
        console.error("Error loading milestones:", error);
      } finally {
        setLoading(false);
      }
    };

    if (user) loadMilestones();
  }, [user]);

  if (authLoading || loading) return <div className="dashboard-loading">Loading...</div>;
  if (authError) return <div className="dashboard-error">Error loading dashboard.</div>;

  const currentLesson = milestones.find(m => m.status === "in-progress");

  return (
    <div className="student-dashboard">

      {/* LEFT: MILESTONE MENU */}
      <aside className="milestone-sidebar">
        <h2 className="sidebar-title">📘 Your Lessons</h2>

        <ul className="milestone-list">
          {milestones.map((m) => (
            <li
              key={m.id}
              className={`milestone-item ${m.status}`}
              onClick={() => m.status !== "locked" && setSelectedMilestone(m)}
            >
              <span className="milestone-name">{m.title}</span>
              {m.status === "completed" && <span className="status-icon">✔</span>}
              {m.status === "locked" && <span className="status-icon">🔒</span>}
            </li>
          ))}
        </ul>
      </aside>

      {/* RIGHT: CONTENT DISPLAY */}
      <main className="lesson-content">
        {selectedMilestone ? (
          <>
            <h1 className="lesson-title">{selectedMilestone.title}</h1>
            <p className="lesson-description">{selectedMilestone.description}</p>
            <Link to={`/lesson/${selectedMilestone.id}`} className="btn btn-primary">
              Open Lesson
            </Link>
          </>
        ) : (
          <>
            <h1 className="lesson-title">Continue Your Progress</h1>
            {currentLesson ? (
              <>
                <p className="lesson-description">{currentLesson.description}</p>

                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${currentLesson.progress}%` }}
                  ></div>
                </div>

                <Link
                  to={`/lesson/${currentLesson.id}`}
                  className="btn btn-primary continue-btn"
                >
                  Continue Lesson ➜
                </Link>
              </>
            ) : (
              <p>No lessons assigned yet.</p>
            )}
          </>
        )}
      </main>
    </div>
  );
}
