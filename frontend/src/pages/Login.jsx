import { Link, useNavigate, useLocation } from "react-router-dom";
import { useState } from "react";
import Form from "../components/Forms";
import '../styles/styles.css';

function Login() {
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const location = useLocation();

    const handleLoginSuccess = (data) => {
        console.log("Login success data:", data); // Debug log
        
        // Store tokens
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        localStorage.setItem('user_role', data.role);

        // Clear any previous error
        setError(null);

        // Determine redirect path based on role
        const redirectPath = data.role === 'faculty' ? '/faculty_home' : '/student_home';
        console.log("Redirecting to:", redirectPath); // Debug log
        navigate(redirectPath, { replace: true });
    };

    const handleLoginFailure = (error) => {
        console.error("Login failure:", error); // Debug log
        
        // Clear any existing tokens
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_role');

        setError(error.response?.data?.detail || "Login failed. Please try again.");
    };

    return (
        <div className="auth-container">
            <div className="form-container">
                <div>
                    <h2 className="form-header">
                        Sign in to your account
                    </h2>
                </div>
                
                <Form
                    method="login"
                    onSuccess={handleLoginSuccess}
                    onFailure={handleLoginFailure}
                />

                {error && (
                    <div className="form-error" role="alert">
                        {error}
                    </div>
                )}

                <div className="text-center">
                    <Link 
                        to="/register" 
                        className="form-link"
                    >
                        Don't have an account? Register
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default Login;