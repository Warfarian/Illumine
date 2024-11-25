import axios from "axios";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "./constants";

const api = axios.create({
    baseURL: "http://localhost:8000",
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
        console.log("Request config:", {
            url: config.url,
            method: config.method,
            headers: config.headers,
            data: config.data
        });

        // Don't add auth header for login/register endpoints
        if (config.url.includes('/token/') || config.url.includes('/register/')) {
            return config;
        }

        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        if (config.data instanceof FormData) {
            config.headers['Content-Type'] = 'multipart/form-data';
        } else {
            config.headers['Content-Type'] = 'application/json';
        }

        return config;
    },
    (error) => {
        console.error("Request interceptor error:", error);
        return Promise.reject(error);
    }
);

// Response interceptor
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // If error is 401 and we haven't tried to refresh token yet
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token');
                const response = await api.post('/api/token/refresh/', {
                    refresh: refreshToken
                });

                const { access } = response.data;
                localStorage.setItem('access_token', access);

                // Retry the original request
                originalRequest.headers.Authorization = `Bearer ${access}`;
                return api(originalRequest);
            } catch (refreshError) {
                // If refresh token fails, logout user
                localStorage.clear();
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }

        return handleApiError(error);
    }
);


export default api 