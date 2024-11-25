import { useState, useEffect } from "react";
import api from "../api";
import Avatar from '../components/Avatar';
import '../styles/pages/dashboard.css';

function FacultyHome() {
    const [facultyProfile, setFacultyProfile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchFacultyProfile();
    }, []);

    const fetchFacultyProfile = async () => {
        try {
            setLoading(true);
            const response = await api.get("/api/faculty/profile/");
            setFacultyProfile(response.data);
        } catch (err) {
            setError("Failed to load profile");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

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
            setFacultyProfile(response.data);
        } catch (err) {
            setError("Failed to upload image");
            console.error(err);
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
        </div>
    );
}

export default FacultyHome;