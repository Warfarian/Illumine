import axios from "axios";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "./constants";

const API_URL = "http://localhost:8000";

console.log('Using API URL:', API_URL);

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    },
    timeout: 30000,
    withCredentials: true,
});

// Add request interceptor for debugging
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        console.error('Request error:', error);
        return Promise.reject(error);
    }
);

// Add response interceptor with retry logic
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (!originalRequest || originalRequest._retry) {
            return Promise.reject(error);
        }

        // Only retry once
        originalRequest._retry = true;

        if (error.code === 'ERR_NETWORK' || error.response?.status === 503) {
            console.log('Network error, retrying...');
            return api(originalRequest);
        }

        return Promise.reject(error);
    }
);

// Faculty profile endpoints
export const getFacultyProfile = () => {
    return api.get('/api/faculty/profile/');
};

export const updateFacultyProfile = (data) => {
    return api.put('/api/faculty/profile/', data);
};

// Update profile endpoint
export const updateProfile = async (profileData) => {
    try {
        const response = await api.put('/api/student/profile/', profileData);
        return response.data;
    } catch (error) {
        console.error('Profile update error:', error);
        throw error;
    }
};

export const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    window.location.href = '/login';
};

export default api;