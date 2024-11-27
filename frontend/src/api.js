import axios from "axios";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "./constants";

const API_URL = import.meta.env.VITE_API_URL || "/choreo-apis/illumineuniversity/backend/v1";

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
});

// Custom error handling function
const handleApiError = (error) => {
    if (error.response) {
        // Server responded with error status
        switch (error.response.status) {
            case 400:
                console.error('Bad Request:', error.response.data);
                // You might want to handle specific validation errors here
                if (error.response.data.validation_errors) {
                    return Promise.reject({
                        type: 'VALIDATION_ERROR',
                        errors: error.response.data.validation_errors
                    });
                }
                break;
            case 401:
                console.error('Unauthorized');
                break;
            case 403:
                console.error('Forbidden');
                break;
            case 404:
                console.error('Not Found');
                break;
            case 500:
                console.error('Server Error');
                break;
            default:
                console.error('API Error:', error.response.status);
        }
        return Promise.reject({
            type: 'API_ERROR',
            status: error.response.status,
            data: error.response.data
        });
    } else if (error.request) {
        // Request made but no response received
        console.error('Network Error:', error.request);
        return Promise.reject({
            type: 'NETWORK_ERROR',
            error: error.request
        });
    } else {
        // Something else happened while setting up the request
        console.error('Error:', error.message);
        return Promise.reject({
            type: 'REQUEST_ERROR',
            error: error.message
        });
    }
};

// Request interceptor
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        console.log('Full error details:', {
            status: error.response?.status,
            url: error.config?.url,
            baseURL: error.config?.baseURL,
            fullURL: error.config?.baseURL + error.config?.url,
            headers: error.config?.headers,
            data: error.response?.data
        });
        const originalRequest = error.config;

        // Prevent infinite refresh loops
        if (originalRequest?.url === '/api/token/refresh/') {
            localStorage.clear();
            window.location.href = '/login';
            return Promise.reject(error);
        }

        // If error is 401 and we haven't tried refreshing token yet
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token');
                
                if (!refreshToken) {
                    throw new Error('No refresh token available');
                }

                const response = await axios.post(
                    `${API_URL}/api/token/refresh/`,
                    { refresh: refreshToken },
                    {
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    }
                );

                if (response.data.access) {
                    localStorage.setItem('access_token', response.data.access);
                    api.defaults.headers.Authorization = `Bearer ${response.data.access}`;
                    originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
                    return api(originalRequest);
                }
            } catch (refreshError) {
                console.error('Token refresh failed:', refreshError);
                localStorage.clear();
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }

        // Handle other errors
        if (error.response) {
            console.error(`API Error ${error.response.status}:`, error.response.data);
        } else if (error.request) {
            console.error('Network Error:', error.request);
        } else {
            console.error('Error:', error.message);
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