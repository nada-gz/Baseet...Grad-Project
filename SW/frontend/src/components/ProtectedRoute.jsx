import React from "react";
import { Navigate, Outlet } from "react-router-dom";

const ProtectedRoute = ({ allowedRoles }) => {

    const token = localStorage.getItem("token");
    let role = localStorage.getItem("role");

    // Not logged in
    if (!token) {
        return <Navigate to="/login" replace />;
    }

    // If role is missing (for users created before role feature), default to "student"
    if (!role) {
        role = "student";
        localStorage.setItem("role", role);
    }

    // Role mismatch
    if (allowedRoles && !allowedRoles.includes(role)) {
        return <Navigate to="/not-allowed" replace />;
    }

    // Allowed → render the page
    return <Outlet />;
};

export default ProtectedRoute;
