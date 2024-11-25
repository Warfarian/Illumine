import { Navigate, useLocation } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import api from "../api";
import { REFRESH_TOKEN, ACCESS_TOKEN, USER_ROLE } from "../constants";
import { useState, useEffect } from "react";

function ProtectedRoute({ children, allowedRoles }) {
    const [isLoading, setIsLoading] = useState(true);
    const [isAuthorized, setIsAuthorized] = useState(false);
    const location = useLocation();

    useEffect(() => {
        const verifyAuth = async () => {
            try {
                const authorized = await authenticateUser();
                setIsAuthorized(authorized);
            } catch (error) {
                console.error("Authentication failed:", error);
                setIsAuthorized(false);
            } finally {
                setIsLoading(false);
            }
        };

        verifyAuth();
    }, [location.pathname]);

    const authenticateUser = async () => {
        const token = localStorage.getItem('access_token');
        const storedRole = localStorage.getItem('user_role');

        if (!token || !storedRole) {
            return false;
        }

        try {
            const decoded = jwtDecode(token);
            const now = Date.now() / 1000;

            // Check token expiration
            if (decoded.exp < now) {
                await refreshToken();
            }

            return allowedRoles.includes(storedRole);
        } catch (error) {
            return false;
        }
    };

    if (isLoading) {
        return <div>Loading...</div>;
    }

    return isAuthorized ? children : <Navigate to="/login" replace />;
}

export default ProtectedRoute