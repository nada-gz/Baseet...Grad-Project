import { createBrowserRouter, Navigate, Outlet } from "react-router-dom";

// Layout
import MainLayout from "./layouts/MainLayout";

// Pages - Public
import Login from "./pages/Login";
import Register from "./pages/Register";

// Pages - Protected
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";

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
  
  // Protected routes with layout
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <MainLayout />,
        children: [
          {
            path: "/dashboard/:role",
            element: <Dashboard />,
          },
          {
            path: "/profile/:studentId",
            element: <Profile />,
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

