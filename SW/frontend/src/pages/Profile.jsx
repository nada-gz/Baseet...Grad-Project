import { useParams } from "react-router-dom";

export default function Profile() {
  const { studentId } = useParams();

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-4">Profile</h1>
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-gray-700">
          Student ID: <span className="font-semibold">{studentId}</span>
        </p>
        <p className="text-sm text-gray-500 mt-2">
          TODO: Implement profile content for student {studentId}
        </p>
      </div>
    </div>
  );
}

