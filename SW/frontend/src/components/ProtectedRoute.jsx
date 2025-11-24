import React from "react";
import { Navigate, Outlet } from "react-router-dom";

const ProtectedRoute = ({ allowedRoles }) => {

    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");

    // Not logged in
    if (!token) {
        return <Navigate to="/login" replace />;
    }

    // If role is required but missing, default to "student" for backward compatibility
    // This handles accounts created before the role feature was added
    const userRole = role || "student";
    
    // If no role was stored, save the default
    if (!role) {
        localStorage.setItem("role", userRole);
    }

    // Role mismatch
    if (allowedRoles && !allowedRoles.includes(userRole)) {
        return <Navigate to="/not-allowed" replace />;
    }

    // Allowed → render the page
    return <Outlet />;
};

export default ProtectedRoute;
