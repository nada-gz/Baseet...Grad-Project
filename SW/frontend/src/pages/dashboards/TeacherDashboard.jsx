import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import useAuth from "../../hooks/useAuth";
import api from "../../services/api";

export default function TeacherDashboard() {
  const { user, loading, error } = useAuth();
  const [students, setStudents] = useState([]);
  const [fetchError, setFetchError] = useState("");

  useEffect(() => {
    const loadStudents = async () => {
      setFetchError("");
      try {
        const response = await api.get("/users"); // fetch all users
        // filter only students
        setStudents(response.data.filter((u) => u.role.toLowerCase() === "student"));
      } catch (err) {
        console.error("Error loading students:", err);
        setFetchError("Failed to load students. Please try again later.");
      }
    };
    loadStudents();
  }, []);

  if (loading) return <p className="p-6">Loading...</p>;
  if (error) return <p className="p-6 text-red-600">Error loading user.</p>;

  return (
    <div className="min-h-screen bg-gray-50 p-6 lg:p-8">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between mb-6">
        <div>
          <p className="text-lg text-slate-500">Class Dashboard</p>
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-800">
            Welcome back, {user?.username || "Ms. Monaaa"}
          </h1>
        </div>
        <button className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-400 hover:bg-blue-500 text-white px-4 py-2 font-medium shadow-sm transition-colors">
          <span aria-hidden>⬆️</span>
          <span>Upload Material</span>
        </button>
      </div>

      {/* Summary grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
        {/* Card A: Class Mood */}
        <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-6 flex flex-col gap-4">
          <div className="flex items-center gap-2 text-slate-700 font-semibold">
            <span aria-hidden>👥</span>
            <span>Class Mood</span>
          </div>
          <div className="text-6xl text-center" aria-label="Class mood">😊</div>
          <p className="text-center text-slate-400 text-sm">
            Average class emotion: Content
          </p>
        </div>

        {/* Card B: Engagement */}
        <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-6 flex flex-col gap-4">
          <div className="flex items-center gap-2 text-slate-700 font-semibold">
            <span aria-hidden>📈</span>
            <span>Engagement</span>
          </div>
          <div className="text-5xl font-bold text-slate-800">78%</div>
          <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
            <div className="h-full w-[78%] bg-[#A3B18A]" />
          </div>
          <p className="text-slate-400 text-sm">Class average for this week</p>
        </div>

        {/* Card C: Quick Actions */}
        <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-6 flex flex-col gap-4">
          <div className="text-slate-800 font-semibold">Quick Actions</div>
          <div className="flex flex-col gap-3">
            <button className="flex items-center gap-3 rounded-lg bg-slate-50 hover:bg-slate-100 px-3 py-3 text-left text-slate-700 transition-colors">
              <span aria-hidden>📚</span>
              <span>Edit Curriculum</span>
            </button>
            <button className="flex items-center gap-3 rounded-lg bg-slate-50 hover:bg-slate-100 px-3 py-3 text-left text-slate-700 transition-colors">
              <span aria-hidden>📊</span>
              <span>View Analytics</span>
            </button>
          </div>
        </div>
      </div>

      {/* Existing students list */}
      <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-6">
        <h2 className="text-xl font-semibold text-slate-800 mb-4">Students</h2>

        {fetchError && <p className="text-red-600 mb-2">{fetchError}</p>}

        <ul className="space-y-2">
          {students.map((s) => (
            <li key={s.id} className="flex justify-between border-b border-slate-100 pb-2">
              <span className="text-slate-700">
                {s.username} ({s.email})
              </span>
              <Link
                className="text-blue-600 hover:underline"
                to={`/profile/${s.id}`}
              >
                View Profile
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
