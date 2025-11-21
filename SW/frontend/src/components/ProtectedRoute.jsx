import React from "react";
import { Navigate, Outlet } from "react-router-dom";

const ProtectedRoute = ({ allowedRoles }) => {

    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");

    // Not logged in
    if (!token) {
        return <Navigate to="/login" replace />;
    }

    // Role mismatch
    if (allowedRoles && !allowedRoles.includes(role)) {
        return <Navigate to="/not-allowed" replace />;
    }

    // Allowed → render the page
    return <Outlet />;
};

export default ProtectedRoute;
