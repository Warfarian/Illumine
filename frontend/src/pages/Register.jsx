import { useNavigate, Link } from "react-router-dom";
import Form from "../components/Forms";

function Register() {
    const navigate = useNavigate();

    const handleRegisterSuccess = () => {
        alert("Registration successful! Please login with your credentials.");
        navigate('/login');
    };

    const handleRegisterFailure = (error) => {
        console.error("Registration failed:", error);
    };

    return (
        <div className="form-container">
            <div className="form-content">
                <div>
                    <h2 className="form-header">
                        Create your account
                    </h2>
                    <p className="form-text">
                        Already have an account?{' '}
                        <Link 
                            to="/login" 
                            className="form-link"
                        >
                            Sign in here
                        </Link>
                    </p>
                </div>
                
                <Form
                    method="register"
                    onSuccess={handleRegisterSuccess}
                    onFailure={handleRegisterFailure}
                />
            </div>
        </div>
    );
}

export default Register;
