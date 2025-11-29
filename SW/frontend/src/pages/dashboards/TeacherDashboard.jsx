import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import useAuth from "../../hooks/useAuth";
import { getUsers } from "../../services/api";

export default function TeacherDashboard() {
  const { user, loading, error } = useAuth();
  const [students, setStudents] = useState([]);

  useEffect(() => {
    const loadStudents = async () => {
      const data = await getUsers();
      // filter only students
      setStudents(data.filter((u) => u.role.toLowerCase() === "student"));
    };
    loadStudents();
  }, []);

  if (loading) return <p className="p-6">Loading...</p>;
  if (error) return <p className="p-6 text-red-600">Error loading user.</p>;

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-4">Teacher Dashboard</h1>

      <div className="bg-white rounded-lg shadow-md p-6 mb-4">
        <h2 className="text-xl font-semibold mb-2">
          Welcome, {user?.username}
        </h2>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Students</h2>

        <ul className="space-y-2">
          {students.map((s) => (
            <li key={s.id} className="flex justify-between border-b pb-2">
              <span>{s.username} ({s.email})</span>
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
