import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import useAuth from "../../hooks/useAuth";
import api from "../../services/api";

// Reusable surface
const Surface = ({ children, className = "" }) => (
  <div className={`bg-white rounded-xl border border-slate-100 shadow-sm ${className}`}>
    {children}
  </div>
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
    <div className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between mb-6">
        <div>
          <p className="text-sm sm:text-base text-slate-500">Class Dashboard</p>
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-800">
            Welcome back, {user?.username || "Ms. Monaaa"}
          </h1>
        </div>
        <button
          aria-label="Upload material"
          className="inline-flex w-full sm:w-auto items-center justify-center gap-2 rounded-lg bg-sky-500 hover:bg-sky-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-400 text-white px-4 py-2 font-medium shadow-sm transition-all"
        >
          <span aria-hidden>⬆️</span>
          <span>Upload Material</span>
        </button>
      </div>

      {/* Summary grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
        {/* Class Mood */}
        <Surface className="p-6 flex flex-col gap-4">
          <div className="flex items-center gap-2 text-slate-700 font-semibold">
            <span aria-hidden>👥</span>
            <span>Class Mood</span>
          </div>
          <div
            key={mood.emoji}
            className="text-6xl text-center animate-bounce"
            aria-label={`Class mood ${mood.label}`}
          >
            {mood.emoji}
          </div>
          <p className="text-center text-slate-400 text-sm">
            Average class emotion: {mood.label}
          </p>
        </Surface>

        {/* Engagement */}
        <Surface className="p-6 flex flex-col gap-4">
          <div className="flex items-center gap-2 text-slate-700 font-semibold">
            <span aria-hidden>📈</span>
            <span>Engagement</span>
          </div>
          <div className="text-5xl font-bold text-slate-800">
            {averageEngagement}%
          </div>
          <div
            className="h-2 w-full rounded-full bg-slate-100 overflow-hidden"
            title={`Engagement: ${averageEngagement}%`}
          >
            <div
              className="h-full rounded-full bg-gradient-to-r from-emerald-400 via-lime-300 to-amber-300 transition-all"
              style={{ width: `${Math.min(averageEngagement, 100)}%` }}
            />
          </div>
          <p className="text-slate-400 text-sm">Class average for this week</p>
        </Surface>

        {/* Quick Actions */}
        <Surface className="p-6 flex flex-col gap-4">
          <div className="text-slate-800 font-semibold">Quick Actions</div>
          <div className="flex flex-col gap-3">
            {[
              { icon: "📚", label: "Edit Curriculum", hint: "Update lessons" },
              { icon: "📊", label: "View Analytics", hint: "Check trends" },
            ].map((action) => (
              <button
                key={action.label}
                aria-label={action.label}
                title={action.hint}
                className="flex items-center gap-3 rounded-lg bg-slate-50 hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-400 px-3 py-3 text-left text-slate-700 transition-all transform hover:-translate-y-[1px] hover:shadow-sm"
              >
                <span aria-hidden>{action.icon}</span>
                <span>{action.label}</span>
              </button>
            ))}
          </div>
        </Surface>
      </div>

      {/* Needs Attention & Materials */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-8">
        <Surface className="p-6 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-800">Needs Attention</h3>
            <span className="text-sm text-slate-400">{attentionStudents.length} students</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {attentionStudents.map((s) => (
              <button
                key={s.id}
                aria-label={`View ${s.name} profile`}
                onClick={() => setSelectedStudent(s)}
                className="text-left rounded-xl border border-slate-100 bg-white p-4 shadow-[0_1px_3px_rgba(0,0,0,0.04)] transition-all hover:-translate-y-[2px] hover:shadow-md focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-400"
              >
                <div className="flex items-center justify-between">
                  <p className="font-semibold text-slate-800">{s.name}</p>
                  <span className="text-xs px-2 py-1 rounded-full bg-amber-100 text-amber-700">
                    {s.engagement}% engagement
                  </span>
                </div>
                <p className="text-sm text-slate-500 mt-1">{s.issue}</p>
                <div className="mt-3 flex items-center justify-between">
                  <span className="text-sm text-slate-500">View issue history</span>
                  <span className="text-sky-600 text-sm font-medium">View Profile →</span>
                </div>
              </button>
            ))}
          </div>
        </Surface>

        <Surface className="p-6 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-800">Recent Materials</h3>
            <span className="text-sm text-slate-400">{materials.length} items</span>
          </div>
          <div className="space-y-3">
            {materials.map((m) => (
              <div
                key={m.id}
                className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50 px-3 py-3"
              >
                <div className="flex flex-col">
                  <div className="flex items-center gap-2">
                    <p className="font-medium text-slate-800">{m.title}</p>
                    {isNewMaterial(m.addedAt) && (
                      <span className="text-[11px] px-2 py-1 rounded-full bg-emerald-100 text-emerald-700">New</span>
                    )}
                  </div>
                  <span className="text-xs text-slate-500">
                    Added {m.addedAt.toLocaleDateString()}
                  </span>
                </div>
                <button
                  aria-label={`Download ${m.title}`}
                  className="inline-flex items-center gap-1 rounded-md bg-sky-500 hover:bg-sky-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-400 text-white px-3 py-1.5 text-sm font-medium transition-all"
                >
                  <span aria-hidden>⬇️</span>
                  <span>Download</span>
                </button>
              </div>
            ))}
          </div>
        </Surface>
      </div>

      {/* Students list */}
      <Surface className="p-6">
        <h2 className="text-xl font-semibold text-slate-800 mb-4">Students</h2>

        {fetchError && <p className="text-red-600 mb-2">{fetchError}</p>}

        <ul className="space-y-2">
          {students.map((s) => (
            <li
              key={s.id}
              className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-slate-100 pb-2 gap-2"
            >
              <span className="text-slate-700">
                {s.username} ({s.email})
              </span>
              <Link
                className="text-sky-600 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-400"
                to={`/profile/${s.id}`}
              >
                View Profile
              </Link>
            </li>
          ))}
        </ul>
      </Surface>

      {/* Modal */}
      {selectedStudent && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
          role="dialog"
          aria-modal="true"
        >
          <div className="w-full max-w-lg rounded-xl bg-white shadow-2xl p-6 relative">
            <button
              aria-label="Close"
              onClick={() => setSelectedStudent(null)}
              className="absolute right-3 top-3 text-slate-500 hover:text-slate-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-400"
            >
              ✕
            </button>
            <h3 className="text-xl font-semibold text-slate-800 mb-2">
              {selectedStudent.name}
            </h3>
            <p className="text-slate-600 mb-4">{selectedStudent.issue}</p>
            <div className="space-y-3">
              <div>
                <p className="text-sm font-medium text-slate-700">Engagement trend</p>
                <div className="h-2 w-full rounded-full bg-slate-100 mt-2">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-amber-300 to-red-300"
                    style={{ width: `${selectedStudent.engagement}%` }}
                  />
                </div>
              </div>
              <div>
                <p className="text-sm font-medium text-slate-700">Issue history</p>
                <ul className="list-disc list-inside text-sm text-slate-600">
                  {selectedStudent.history?.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="text-sm font-medium text-slate-700">Notes</p>
                <p className="text-sm text-slate-600">{selectedStudent.notes}</p>
              </div>
            </div>
            <div className="mt-6 flex flex-col sm:flex-row justify-end gap-3">
              <button
                aria-label="Close modal"
                onClick={() => setSelectedStudent(null)}
                className="rounded-lg px-4 py-2 text-slate-700 hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-400"
              >
                Close
              </button>
              <Link
                to={`/profile/${selectedStudent.id}`}
                className="rounded-lg bg-sky-500 hover:bg-sky-600 text-white px-4 py-2 font-medium focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-400 text-center"
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
