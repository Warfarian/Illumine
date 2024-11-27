const handleLogin = async (credentials) => {
    try {
        const response = await api.post('/api/token/', credentials);
        // Add logging
        console.log('Login response:', response);
        
        if (response.data.access) {
            localStorage.setItem('access_token', response.data.access);
            localStorage.setItem('refresh_token', response.data.refresh);
            // ... rest of your success handling
        }
    } catch (error) {
        console.error('Login error details:', {
            status: error.response?.status,
            data: error.response?.data,
            message: error.message,
            url: error.config?.url,
            baseURL: error.config?.baseURL
        });

        // More user-friendly error handling
        let errorMessage = 'Login failed. ';
        if (error.response?.status === 503) {
            errorMessage += 'The service is temporarily unavailable. Please try again later.';
        } else if (error.response?.status === 401) {
            errorMessage += 'Invalid credentials.';
        } else {
            errorMessage += 'Please check your connection and try again.';
        }
        
        // Show error to user (assuming you have some notification system)
        alert(errorMessage);
    }
}; 