import { useState, useEffect } from "react";
import api from "../api";

function FacultyHome() {
    const [students, setStudents] = useState([]);

    useEffect(() => {
        fetchStudents();
    }, []);

    const fetchStudents = () => {
        api
            .get("/api/students/")
            .then((res) => setStudents(res.data))
            .catch((err) => alert(err));
    };

    return (
        <div>
            <h1>Faculty Dashboard</h1>
            <ul>
                {students.map((student) => (
                    <li key={student.id}>{student.name}</li>
                ))}
            </ul>
        </div>
    );
}

export default FacultyHome;
