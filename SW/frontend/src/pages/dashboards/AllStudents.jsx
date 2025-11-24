import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getUsers } from "../../services/api";

export default function AllStudents() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadStudents = async () => {
      const data = await getUsers();
      setStudents(data.filter((u) => u.role.toLowerCase() === "student"));
      setLoading(false);
    };
    loadStudents();
  }, []);

  if (loading) return <p className="p-6">Loading...</p>;

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">All Students</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {students.map((student) => (
          <Link
            key={student.id}
            to={`/profile/${student.id}`}
            className="block bg-white shadow-md p-4 rounded-lg hover:bg-gray-100 transition"
          >
            <h2 className="text-lg font-semibold">{student.username}</h2>
            <p className="text-gray-600">{student.email}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
