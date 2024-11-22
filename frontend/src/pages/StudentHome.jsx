import { useState, useEffect } from "react";
import api from "../api";

function StudentHome() {
    const [profile, setProfile] = useState({});

    useEffect(() => {
        api
            .get("/api/profile/")
            .then((res) => setProfile(res.data))
            .catch((err) => alert(err));
    }, []);

    return (
        <div>
            <h1>Student Dashboard</h1>
            <p>Name: {profile.name}</p>
            <p>Email: {profile.email}</p>
        </div>
    );
}

export default StudentHome;
