import axios from "axios";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "./constants";

// Create axios instance with base configuration
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
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
        const token = localStorage.getItem(ACCESS_TOKEN);
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        console.error('Request Interceptor Error:', error);
        return Promise.reject(error);
    }
);

// Response interceptor
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Handle 401 and token refresh
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refresh = localStorage.getItem(REFRESH_TOKEN);
                if (!refresh) {
                    throw new Error('No refresh token available');
                }

                const response = await api.post("/api/token/refresh/", { refresh });
                const { access } = response.data;

                if (!access) {
                    throw new Error('No access token received');
                }

                localStorage.setItem(ACCESS_TOKEN, access);
                originalRequest.headers.Authorization = `Bearer ${access}`;

                return api(originalRequest);
            } catch (refreshError) {
                console.error('Token refresh failed:', refreshError);
                localStorage.clear();
                window.location.href = "/login";
                return Promise.reject(refreshError);
            }
        }

        return handleApiError(error);
    }
);


export default api 