import { Navigate } from "react-router-dom";
import {jwtDecode} from "jwt-decode";
import api from "../api";
import { REFRESH_TOKEN, ACCESS_TOKEN, USER_ROLE } from "../constants";
import { useState, useEffect } from "react";

function ProtectedRoute({ children, allowedRoles }) {
    const [isAuthorized, setIsAuthorized] = useState(null);

    useEffect(() => {
        authenticateUser().catch((err) => {
            console.error("Authentication error:", err);
            setIsAuthorized(false);
        });
    }, []);

    const refreshToken = async () => {
        const refresh = localStorage.getItem(REFRESH_TOKEN);
        if (!refresh) {
            throw new Error("No refresh token available.");
        }

        try {
            const res = await api.post("/api/token/refresh/", { refresh });
            localStorage.setItem(ACCESS_TOKEN, res.data.access);
            return res.data.access;
        } catch (error) {
            console.error("Refresh token failed:", error);
            throw error;
        }
    };

    const authenticateUser = async () => {
        const token = localStorage.getItem(ACCESS_TOKEN);
        if (!token) {
            setIsAuthorized(false); 
            return;
        }

        let decoded;
        try {
            decoded = jwtDecode(token);
        } catch (error) {
            console.error("Failed to decode token:", error);
            setIsAuthorized(false);
            return;
        }

        const now = Date.now() / 1000; 
        const { exp: tokenExpiration, role: userRole } = decoded;


        localStorage.setItem(USER_ROLE, userRole);

        if (tokenExpiration < now) {
            try {
                const newToken = await refreshToken();
                const { role: refreshedRole } = jwtDecode(newToken);
                if (allowedRoles.includes(refreshedRole)) {
                    setIsAuthorized(true);
                } else {
                    setIsAuthorized(false);
                }
            } catch (error) {
                setIsAuthorized(false); 
            }
        } else if (!allowedRoles.includes(userRole)) {
            setIsAuthorized(false); 
        } else {
            setIsAuthorized(true); 
        }
    };

    if (isAuthorized === null) {
        return <div>Loading...</div>;
    }

    return isAuthorized ? children : <Navigate to="/login" />;
}

export default ProtectedRoute;
