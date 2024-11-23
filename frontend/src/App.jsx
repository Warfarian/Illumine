import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import FacultyHome from "./pages/FacultyHome";
import StudentHome from "./pages/StudentHome";
import NotFound from "./pages/NotFound";
import ProtectedRoute from "./components/ProtectedRoute";
import './styles/styles.css';

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Register />} /> 
                <Route
                    path="/faculty"
                    element={
                        <ProtectedRoute allowedRoles={["faculty"]}>
                            <FacultyHome />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/student"
                    element={
                        <ProtectedRoute allowedRoles={["student"]}>
                            <StudentHome />
                        </ProtectedRoute>
                    }
                />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="*" element={<NotFound />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
