import { createBrowserRouter, Navigate, Outlet } from "react-router-dom";

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

// Protected Route Component
const ProtectedRoute = () => {
  // TODO: Replace with actual authentication check
  // For now, this is a placeholder that checks for token in localStorage
  // You should implement proper authentication logic here (e.g., JWT validation, session check)
  const token = localStorage.getItem("token");
  const isAuthenticated = !!token; // Convert to boolean
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <Outlet />;
};

// Route configuration
const router = createBrowserRouter([
  // Public routes
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/register",
    element: <Register />,
  },
  {
    path: "/not-allowed",
    element: <NotAllowed />,
  },  
  
  // Protected routes with layout
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <MainLayout />,
        children: [
          {
            path: "/dashboard/teacher",
            element: <TeacherDashboard />,
          },
          {
            path: "/dashboard/student",
            element: <StudentDashboard />,
          },
          {
            path: "/dashboard/parent",
            element: <ParentDashboard />,
          },
          {
            path: "/dashboard/supervisor",
            element: <SupervisorDashboard />,
          },
          {
            path: "/profile/:studentId",
            element: <StudentProfile />,
          },
        ],
      },
    ],
  },
  
  // Default redirect
  {
    path: "/",
    element: <Navigate to="/login" replace />,
  },
  
  // Catch all - redirect to login
  {
    path: "*",
    element: <Navigate to="/login" replace />,
  },
]);

export default router;

