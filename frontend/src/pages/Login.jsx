import { Link, useNavigate, useLocation } from "react-router-dom";
import { useState } from "react";
import Form from "../components/Forms";
import { ACCESS_TOKEN, REFRESH_TOKEN, USER_ROLE } from "../constants";

function Login() {
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const location = useLocation();

    const handleLoginSuccess = (data) => {
        const { access, refresh, role } = data;
        
        localStorage.setItem(ACCESS_TOKEN, access);
        localStorage.setItem(REFRESH_TOKEN, refresh);
        localStorage.setItem(USER_ROLE, role);

        const from = location.state?.from?.pathname || `/${role}-home`;
        navigate(from, { replace: true });
    };

    const handleLoginFailure = (error) => {
        setError(error.message || "Login failed");
    };

    return (
        <div className="login-container">
            <Form
                route="/api/token/"
                method="POST"
                onSuccess={handleLoginSuccess}
                onFailure={handleLoginFailure}
            />
            {error && <p className="error-message">{error}</p>}
            <p className="register-link">
                New here? <Link to="/register">Register</Link>
            </p>
        </div>
    );
}

export default Login;
