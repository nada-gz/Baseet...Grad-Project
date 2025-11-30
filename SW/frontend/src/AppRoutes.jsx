import { createBrowserRouter, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";

// Layout
import MainLayout from "./layouts/MainLayout";

// Pages - Public
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import NotAllowed from "./pages/general/NotAllowed";

// Pages - Protected - Dashboards
import TeacherDashboard from "./pages/dashboard/TeacherDashboard";
import StudentDashboard from "./pages/dashboard/StudentDashboard";
import ParentDashboard from "./pages/dashboard/ParentDashboard";
import SupervisorDashboard from "./pages/dashboard/SupervisorDashboard";

// Pages - Protected - Profile
import StudentProfile from "./pages/profile/StudentProfile";

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
        children: [
          { path: "/dashboard/teacher", element: <TeacherDashboard /> },
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
        children: [
          { path: "/dashboard/parent", element: <ParentDashboard /> },
          { path: "/profile/:studentId", element: <StudentProfile /> },
        ],
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

  // Default redirect
  { path: "/", element: <Navigate to="/login" replace /> },

  // Catch-all redirect
  { path: "*", element: <Navigate to="/login" replace /> },
]);

export default router;
