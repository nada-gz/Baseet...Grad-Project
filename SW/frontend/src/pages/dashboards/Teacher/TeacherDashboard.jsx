import { Link } from "react-router-dom";
import useAuth from "../../../hooks/useAuth";
import { Users, BookOpen, ChartBar } from "lucide-react"; // icons

export default function TeacherDashboard() {
  const { user, loading, error } = useAuth();

  if (loading) return <p className="p-6">Loading...</p>;
  if (error) return <p className="p-6 text-red-600">Error loading user.</p>;

  return (
    <div className="p-6">

      <div className="teacher-cards-row">

        {/* Lesson Preparation Card */}
        <div className="teacher-card">
          <div className="card-icon">
            <BookOpen className="h-12 w-12 text-primary" />
          </div>
          <div className="card-title text-primary">Prepare Lessons</div>
          <div className="card-description">
            Design courses, build structured milestones, and create detailed lessons with learning materials and exercises.
          </div>
          <div className="card-buttons">
            <Link to="/dashboard/teacher/lessons-prep" className="btn btn-primary">
              Go to Lesson Preparation
            </Link>
          </div>
        </div>

        {/* Class Management Card */}
        <div className="teacher-card">
          <div className="card-icon">
            <Users className="h-12 w-12 text-primary" />
          </div>
          <div className="card-title text-primary">Manage Your Class</div>
          <div className="card-description">
            Organize learning levels, create classes, assign students, and link relevant courses to each class.
          </div>
          <div className="card-buttons">
            <Link to="/dashboard/teacher/classrooms" className="btn btn-primary">
              Go to Class Management
            </Link>
          </div>
        </div>

        {/* Student Monitoring Card */}
        <div className="teacher-card">
          <div className="card-icon">
            <ChartBar className="h-12 w-12 text-primary" />
          </div>
          <div className="card-title text-primary">Monitor Students</div>
          <div className="card-description">
            View all students in one place, track their academic progress, and monitor their real-time psychological state through biometric sensors.
          </div>
          <div className="card-buttons">
            <Link to="/dashboard/teacher/students" className="btn btn-primary">
              Go to Student Monitoring
            </Link>
          </div>
        </div>

        
        

        

        
      </div>
    </div>
  );
}
