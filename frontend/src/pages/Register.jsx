import { Link } from "react-router-dom";
import Form from "../components/Forms";

function Register() {
    return (
        <div className="register-container">
            <Form route="/api/register/" method="register" /> 
            <p>
                Already have an account?{" "}
                <Link to="/login">Login here</Link>
            </p>
        </div>
    );
}

export default Register;
