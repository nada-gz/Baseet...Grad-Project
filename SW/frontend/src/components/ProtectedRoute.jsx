import React from "react";
import { Navigate, Outlet } from "react-router-dom";

const ProtectedRoute = ({ allowedRoles }) => {
  const token = localStorage.getItem("token");

  // Parse user safely
  let user;
  try {
    user = JSON.parse(localStorage.getItem("user"));
  } catch {
    user = null;
  }

  let role = user?.role || localStorage.getItem("role") || "student";

  // Not logged in or user missing
  if (!token || !user) {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    return <Navigate to="/login" replace />;
  }

  // Role mismatch
  if (allowedRoles && !allowedRoles.includes(role)) {
    return <Navigate to="/not-allowed" replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
