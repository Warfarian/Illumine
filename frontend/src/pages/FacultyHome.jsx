import { useState, useEffect } from "react";
import api from "../api";
import Avatar from '../components/Avatar';
import '../styles/pages/dashboard.css';
import { getFacultyProfile } from '../api';
import { Link } from "react-router-dom";

function FacultyHome() {
    const [facultyProfile, setFacultyProfile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [students, setStudents] = useState([]);

    useEffect(() => {
        const loadProfile = async () => {
            try {
                const response = await getFacultyProfile();
                setFacultyProfile(response.data);
            } catch (err) {
                console.error('Error loading faculty profile:', err);
                setError('Failed to load profile');
            }
        };

        loadProfile();
    }, []);

    const handleImageUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('profile_picture', file);

        try {
            setLoading(true);
            const response = await api.patch("/api/faculty/profile/", formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                }
            });
            fetchStudents();
        } catch (err) {
            alert(err.response?.data?.message || "Error adding student");
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="dashboard">Loading...</div>;
    if (error) return <div className="dashboard error-message">{error}</div>;

    return (
        <div className="dashboard">
            <div className="dashboard-header">
                <h1 className="heading-1">Faculty Dashboard</h1>
            </div>

            {facultyProfile && (
                <div className="profile-card">
                    <div className="profile-info">
                        <Avatar 
                            src={facultyProfile.profile_picture}
                            alt={`${facultyProfile.first_name}'s profile`}
                            onUpload={handleImageUpload}
                        />
                        <div className="profile-details">
                            <h2 className="heading-2">Profile Information</h2>
                            <div className="info-grid">
                                <div className="info-item">
                                    <span className="info-label">Name</span>
                                    <span className="info-value">
                                        {facultyProfile.first_name} {facultyProfile.last_name}
                                    </span>
                                </div>
                                <div className="info-item">
                                    <span className="info-label">Department</span>
                                    <span className="info-value">{facultyProfile.department}</span>
                                </div>
                                <div className="info-item">
                                    <span className="info-label">Email</span>
                                    <span className="info-value">{facultyProfile.email}</span>
                                </div>
                                <div className="info-item">
                                    <span className="info-label">Contact</span>
                                    <span className="info-value">{facultyProfile.contact_number}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            <div className="dashboard-actions">
                <Link to="/faculty/create-student" className="button primary">
                    Create New Student
                </Link>
            </div>

            <div className="students-section">
                <h2 className="heading-2">My Students</h2>
                <div className="students-grid">
                    {students.map((student) => (
                        <div key={student.id} className="student-card">
                            <div className="student-info">
                                <h3>{student.first_name} {student.last_name}</h3>
                                <p>Roll Number: {student.roll_number}</p>
                                <p>Email: {student.email}</p>
                            </div>
                            <div className="student-actions">
                                <Link 
                                    to={`/faculty/edit-student/${student.id}`} 
                                    className="button secondary"
                                >
                                    Edit
                                </Link>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default FacultyHome;