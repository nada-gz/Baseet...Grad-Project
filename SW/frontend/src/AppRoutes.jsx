import { createBrowserRouter, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";

// Layout
import MainLayout from "./layouts/MainLayout";

// Pages - Public
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import NotAllowed from "./pages/auth/NotAllowed";

// Pages - Protected - Dashboards
import TeacherDashboard from "./pages/dashboards/TeacherDashboard";
import StudentDashboard from "./pages/dashboards/StudentDashboard";
import ParentDashboard from "./pages/dashboards/ParentDashboard";
import SupervisorDashboard from "./pages/dashboards/SupervisorDashboard";

// Pages - Protected - Profile
import StudentProfile from "./pages/profiles/StudentProfile";

import AllStudents from "./pages/dashboards/AllStudents";

const router = createBrowserRouter([
  // Public routes
  { path: "/login", element: <Login /> },
  { path: "/register", element: <Register /> },
  { path: "/not-allowed", element: <NotAllowed /> },

  // Protected routes - Teacher
  {
    element: <ProtectedRoute allowedRoles={["teacher"]} />,
    children: [
      {
        element: <MainLayout />,
        children: [{ path: "/dashboard/teacher", element: <TeacherDashboard /> }],
      },
    ],
  },

  // Protected routes - Student profile (teacher/parent/student)
  {
    element: <ProtectedRoute allowedRoles={["teacher", "parent", "student"]} />,
    children: [
      {
        element: <MainLayout />,
        children: [
          { path: "/profile/:studentId", element: <StudentProfile /> },
        ],
      },
    ],
  },

  // Protected routes - Student
  {
    element: <ProtectedRoute allowedRoles={["student"]} />,
    children: [
      {
        element: <MainLayout />,
        children: [
          { path: "/dashboard/student", element: <StudentDashboard /> },
          { path: "/profile/:studentId", element: <StudentProfile /> },
        ],
      },
    ],
  },

  // Protected routes - Parent
  {
    element: <ProtectedRoute allowedRoles={["parent"]} />,
    children: [
      {
        element: <MainLayout />,
        children: [{ path: "/dashboard/parent", element: <ParentDashboard /> }],
      },
    ],
  },

  // Protected routes - Supervisor
  {
    element: <ProtectedRoute allowedRoles={["supervisor"]} />,
    children: [
      {
        element: <MainLayout />,
        children: [{ path: "/dashboard/supervisor", element: <SupervisorDashboard /> }],
      },
    ],
  },

  // Protected routes - all students
  {
    element: <ProtectedRoute allowedRoles={["teacher", "parent", "supervisor"]} />,
    children: [
      {
        element: <MainLayout />,
        children: [{ path: "/students", element: <AllStudents /> }],
      },
    ],
  },


  // Default redirect
  { path: "/", element: <Navigate to="/login" replace /> },

  // Catch-all redirect
  { path: "*", element: <Navigate to="/login" replace /> },
]);

export default router;
