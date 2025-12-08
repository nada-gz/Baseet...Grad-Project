import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import useAuth from "../../hooks/useAuth";
import api from "../../services/api";

const Surface = ({ children, className = "" }) => (
  <div className={`td-surface ${className}`}>{children}</div>
);

const moodFromEngagement = (value = 0) => {
  if (value >= 70) return { emoji: "🙂", label: "Content" };
  if (value >= 40) return { emoji: "😐", label: "Neutral" };
  return { emoji: "😟", label: "Low" };
};

export default function TeacherDashboard() {
  const { user, loading, error } = useAuth();
  const [students, setStudents] = useState([]);
  const [fetchError, setFetchError] = useState("");
  const [selectedStudent, setSelectedStudent] = useState(null);

  const [materials] = useState([
    { id: 1, title: "Week 3 - Reading Pack", addedAt: new Date() },
    { id: 2, title: "Math Practice Set", addedAt: new Date(Date.now() - 24 * 60 * 60 * 1000) },
    { id: 3, title: "Science Lab Safety", addedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000) },
  ]);

  useEffect(() => {
    const loadStudents = async () => {
      setFetchError("");
      try {
        const response = await api.get("/users");
        setStudents(response.data.filter((u) => u.role.toLowerCase() === "student"));
      } catch (err) {
        console.error("Error loading students:", err);
        setFetchError("Failed to load students. Please try again later.");
      }
    };
    loadStudents();
  }, []);

  const averageEngagement = useMemo(() => 78, []);
  const mood = moodFromEngagement(averageEngagement);

  const attentionStudents = useMemo(() => {
    if (!students.length) {
      return [
        {
          id: "demo-1",
          name: "Jana",
          issue: "Low participation in class",
          engagement: 42,
          notes: "Encourage during group activities",
          history: ["Missed 2 assignments", "Quiet in discussions"],
        },
        {
          id: "demo-2",
          name: "Joudy",
          issue: "Struggles with math concepts",
          engagement: 35,
          notes: "Schedule a 1:1 session",
          history: ["Requested extra help", "Low quiz scores"],
        },
      ];
    }
    return students.slice(0, 2).map((s) => ({
      id: s.id,
      name: s.username,
      issue: "Flagged for low engagement",
      engagement: 45,
      notes: "Review recent assignments",
      history: ["Low engagement trend", "Needs follow-up"],
    }));
  }, [students]);

  const isNewMaterial = (date) => {
    const diffDays = (Date.now() - date.getTime()) / (1000 * 60 * 60 * 24);
    return diffDays <= 2;
  };

  if (loading) return <p className="p-6">Loading...</p>;
  if (error) return <p className="p-6 text-red-600">Error loading user.</p>;

  return (
    <div className="td-page">
      <div className="td-header">
        <div className="td-header-text">
          <p className="td-subtitle">Class Dashboard</p>
          <h1 className="td-title">Welcome back, {user?.username || "Ms. Monaaa"}</h1>
        </div>
        <button aria-label="Upload material" className="td-btn-primary td-btn-upload">
          <span aria-hidden>⬆️</span>
          <span>Upload Material</span>
        </button>
      </div>

      <div className="td-grid-summary">
        <Surface className="td-card td-card-column">
          <div className="td-card-header">
            <span aria-hidden>👥</span>
            <span>Class Mood</span>
          </div>
          <div key={mood.emoji} className="td-mood-emoji" aria-label={`Class mood ${mood.label}`}>
            {mood.emoji}
          </div>
          <p className="td-card-footer">Average class emotion: {mood.label}</p>
        </Surface>

        <Surface className="td-card td-card-column">
          <div className="td-card-header">
            <span aria-hidden>📈</span>
            <span>Engagement</span>
          </div>
          <div className="td-metric">{averageEngagement}%</div>
          <div className="td-progress" title={`Engagement: ${averageEngagement}%`}>
            <div className="td-progress-fill" style={{ width: `${Math.min(averageEngagement, 100)}%` }} />
          </div>
          <p className="td-card-footer">Class average for this week</p>
        </Surface>

        <Surface className="td-card td-card-column">
          <div className="td-card-title">Quick Actions</div>
          <div className="td-quick-actions">
            {[
              { icon: "📚", label: "Edit Curriculum", hint: "Update lessons" },
              { icon: "📊", label: "View Analytics", hint: "Check trends" },
            ].map((action) => (
              <button
                key={action.label}
                aria-label={action.label}
                title={action.hint}
                className="td-quick-action-btn"
              >
                <span aria-hidden>{action.icon}</span>
                <span>{action.label}</span>
              </button>
            ))}
          </div>
        </Surface>
      </div>

      <div className="td-grid-split">
        <Surface className="td-card td-card-column">
          <div className="td-card-row">
            <h3 className="td-section-title">Needs Attention</h3>
            <span className="td-muted">{attentionStudents.length} students</span>
          </div>
          <div className="td-attention-grid">
            {attentionStudents.map((s) => (
              <button
                key={s.id}
                aria-label={`View ${s.name} profile`}
                onClick={() => setSelectedStudent(s)}
                className="td-attention-card"
              >
                <div className="td-card-row">
                  <p className="td-card-strong">{s.name}</p>
                  <span className="td-pill">{s.engagement}% engagement</span>
                </div>
                <p className="td-muted mt-1">{s.issue}</p>
                <div className="td-card-row mt-3">
                  <span className="td-muted">View issue history</span>
                  <span className="td-link-plain">View Profile →</span>
                </div>
              </button>
            ))}
          </div>
        </Surface>

        <Surface className="td-card td-card-column">
          <div className="td-card-row">
            <h3 className="td-section-title">Recent Materials</h3>
            <span className="td-muted">{materials.length} items</span>
          </div>
          <div className="td-materials-list">
            {materials.map((m) => (
              <div key={m.id} className="td-material-row">
                <div className="td-material-text">
                  <div className="td-card-row td-material-title">
                    <p className="td-card-strong">{m.title}</p>
                    {isNewMaterial(m.addedAt) && <span className="td-badge">New</span>}
                  </div>
                  <span className="td-muted-small">Added {m.addedAt.toLocaleDateString()}</span>
                </div>
                <button aria-label={`Download ${m.title}`} className="td-btn-secondary">
                  <span aria-hidden>⬇️</span>
                  <span>Download</span>
                </button>
              </div>
            ))}
          </div>
        </Surface>
      </div>

      <Surface className="td-card">
        <h2 className="td-section-title">Students</h2>
        {fetchError && <p className="td-error">{fetchError}</p>}
        <ul className="td-list">
          {students.map((s) => (
            <li key={s.id} className="td-list-row">
              <span className="td-card-strong">
                {s.username} ({s.email})
              </span>
              <Link className="td-link" to={`/profile/${s.id}`}>
                View Profile
              </Link>
            </li>
          ))}
        </ul>
      </Surface>

      {selectedStudent && (
        <div className="td-modal-backdrop" role="dialog" aria-modal="true">
          <div className="td-modal">
            <button
              aria-label="Close"
              onClick={() => setSelectedStudent(null)}
              className="td-modal-close"
            >
              ✕
            </button>
            <h3 className="td-modal-title">{selectedStudent.name}</h3>
            <p className="td-muted">{selectedStudent.issue}</p>
            <div className="td-modal-body">
              <div>
                <p className="td-card-strong">Engagement trend</p>
                <div className="td-progress td-progress-muted">
                  <div
                    className="td-progress-fill td-progress-warning"
                    style={{ width: `${selectedStudent.engagement}%` }}
                  />
                </div>
              </div>
              <div>
                <p className="td-card-strong">Issue history</p>
                <ul className="td-list-bullets">
                  {selectedStudent.history?.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="td-card-strong">Notes</p>
                <p className="td-muted">{selectedStudent.notes}</p>
              </div>
            </div>
            <div className="td-modal-actions">
              <button
                aria-label="Close modal"
                onClick={() => setSelectedStudent(null)}
                className="td-btn-ghost"
              >
                Close
              </button>
              <Link
                to={`/profile/${selectedStudent.id}`}
                className="td-btn-primary"
              >
                Go to Profile
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
