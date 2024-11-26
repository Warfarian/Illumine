import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import api from "../api";
import { REFRESH_TOKEN, ACCESS_TOKEN, USER_ROLE } from "../constants";
import { useState, useEffect } from "react";

function ProtectedRoute({ children, allowedRoles }) {
    const navigate = useNavigate();
    const location = useLocation();
    const userRole = localStorage.getItem('user_role')?.toLowerCase();
    const token = localStorage.getItem('access_token');

    useEffect(() => {
        console.log("Protected Route Check:", {  // Add debug logging
            userRole,
            allowedRoles,
            hasToken: !!token
        });

        if (!token) {
            navigate('/login', { replace: true, state: { from: location } });
            return;
        }

        if (!userRole || !allowedRoles.includes(userRole)) {
            console.log("Unauthorized access attempt");  // Add debug logging
            navigate('/login', { replace: true });
        }
    }, [navigate, location, userRole, allowedRoles, token]);

    return token && userRole && allowedRoles.includes(userRole) ? children : null;
}

export default ProtectedRoute