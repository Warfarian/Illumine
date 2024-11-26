import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import FacultyHome from "./pages/FacultyHome";
import StudentHome from "./pages/StudentHome";

import ProtectedRoute from "./components/ProtectedRoute";

import './styles/styles.css';

function App() {
    return (
        <BrowserRouter>
            <Routes>
            <Route
                path="/student_home"
                element={
                    <ProtectedRoute allowedRoles={["student"]}>
                        <StudentHome />
                    </ProtectedRoute>
                }   
            />
            <Route
                path="/faculty_home"
                element={
                    <ProtectedRoute allowedRoles={["faculty"]}>
                        <FacultyHome />
                    </ProtectedRoute>
                }
            />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="*" element={<div>Page Not Found</div>} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
