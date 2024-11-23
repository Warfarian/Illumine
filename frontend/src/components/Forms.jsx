import { useState } from "react";
import { useNavigate } from "react-router-dom"; 
import api from "../api";

function Form({ route, method, onSuccess, onFailure }) {
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [role, setRole] = useState("student");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate(); 
    const isRegister = method === "register"; 

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const data = { username, email, password };
            if (isRegister) data.role = role;

            const res = await api.post(route, data);

            if (onSuccess) {
                onSuccess(res.data);

                if (isRegister) {
                    navigate("/login"); 
                }
            }
        } catch (error) {
            if (onFailure) {
                onFailure("Invalid credentials. Please try again.");
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="form-container">
            <h1>{isRegister ? "Register" : "Login"}</h1>
            <input
                type="text"
                className="form-input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter username"
                required
            />
            {isRegister && (
                <input
                    type="email"
                    className="form-input"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter email"
                    required
                />
            )}
            <input
                type="password"
                className="form-input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                required
            />
            {isRegister && (
                <select
                    className="form-input"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                >
                    <option value="student">Student</option>
                    <option value="faculty">Faculty</option>
                </select>
            )}
            {loading && <div className="loading-spinner">Loading...</div>}
            <button type="submit" className="form-button">
                {isRegister ? "Register" : "Login"}
            </button>
        </form>
    );
}

export default Form;
