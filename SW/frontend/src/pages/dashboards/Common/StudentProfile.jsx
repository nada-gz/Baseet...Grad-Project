import { useParams } from "react-router-dom";
import useAuth from "../../../hooks/useAuth";

export default function StudentProfile() {
  const { studentId } = useParams();
  const { user } = useAuth();

  return (
    <div>
      <h1>Student Profile</h1>
      <p>Viewing student ID: {studentId}</p>
      <p>Logged in as: {user?.email}</p>
    </div>
  );
}
