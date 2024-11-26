import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import '../styles/components/forms.css';

function Form({ method, onSuccess, onFailure }) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [email, setEmail] = useState("");
    const [role, setRole] = useState("student");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const isRegister = method === "register";

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            const endpoint = isRegister ? '/api/register/' : '/api/token/';
            const payload = {
                username: username.trim(),
                password: password.trim(),
                ...(isRegister && { 
                    email: email.trim(), 
                    role: role.trim() 
                })
            };

            console.log("Making request to:", endpoint);
            console.log("With payload:", payload);

            const response = await api.post(endpoint, payload);
            console.log("Server response:", response.data);

            if (response.data) {
                if (isRegister) {
                    alert("Registration successful! Please login with your credentials.");
                    navigate('/login');
                } else {
                    if (!response.data.access || !response.data.refresh) {
                        throw new Error("Invalid response format from server");
                    }

                    localStorage.setItem('access_token', response.data.access);
                    localStorage.setItem('refresh_token', response.data.refresh);
                    localStorage.setItem('user_role', response.data.role?.toLowerCase() || '');

                    if (onSuccess) {
                        onSuccess(response.data);
                    }
                }
            }
        } catch (err) {
            console.error("Request failed:", {
                status: err.response?.status,
                data: err.response?.data,
                message: err.message
            });
            
            const errorMessage = err.response?.data?.detail || 
                               err.message || 
                               "An error occurred during authentication";
            setError(errorMessage);
            
            if (onFailure) {
                onFailure(err);
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="form-content">
            <div className="form-group">
                <label className="form-label">Username</label>
                <input
                    type="text"
                    required
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="form-input"
                    placeholder="Username"
                />
            </div>

            {isRegister && (
                <div className="form-group">
                    <label className="form-label">Email</label>
                    <input
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="form-input"
                        placeholder="Email"
                    />
                </div>
            )}

            <div className="form-group">
                <label className="form-label">Password</label>
                <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="form-input"
                    placeholder="Password"
                />
            </div>

            {isRegister && (
                <div className="form-group">
                    <label className="form-label">Role</label>
                    <select
                        value={role}
                        onChange={(e) => setRole(e.target.value)}
                        className="form-select"
                    >
                        <option value="student">Student</option>
                        <option value="faculty">Faculty</option>
                    </select>
                </div>
            )}

            {error && (
                <div className="form-error">
                    {error}
                </div>
            )}

            <button
                type="submit"
                disabled={loading}
                className="form-button"
            >
                {loading ? "Processing..." : (isRegister ? "Register" : "Sign in")}
            </button>
        </form>
    );
}

export default Form;