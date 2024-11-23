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
                await authenticateUser();
                setIsAuthorized(true);
            } catch (error) {
                console.error("Authentication failed:", error);
                setIsAuthorized(false);
            } finally {
                setIsLoading(false);
            }
        };

        verifyAuth();
    }, [location.pathname]);

    const refreshToken = async () => {
        const refresh = localStorage.getItem(REFRESH_TOKEN);
        if (!refresh) throw new Error("No refresh token");

        const response = await api.post("/api/token/refresh/", { refresh });
        const { access, role } = response.data;
        localStorage.setItem(ACCESS_TOKEN, access);
        localStorage.setItem(USER_ROLE, role);
        return { access, role };
    };

    const authenticateUser = async () => {
        const token = localStorage.getItem(ACCESS_TOKEN);
        const storedRole = localStorage.getItem(USER_ROLE);

        if (!token || !storedRole) {
            throw new Error("No token or role");
        }

        try {
            const decoded = jwtDecode(token);
            const now = Date.now() / 1000;

            if (decoded.exp < now) {
                const { role: newRole } = await refreshToken();
                return allowedRoles.includes(newRole);
            }

            return allowedRoles.includes(storedRole);
        } catch (error) {
            throw new Error("Invalid token");
        }
    };

    if (isLoading) {
        return <div>Loading...</div>;
    }

    return isAuthorized ? children : <Navigate to="/login" state={{ from: location }} replace />;
}

export default ProtectedRoute;
