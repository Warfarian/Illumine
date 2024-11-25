import { useState, useEffect } from "react";
import api from "../api";
import Avatar from '../components/Avatar';

function StudentHome() {
    const [profile, setProfile] = useState({});
    const [editMode, setEditMode] = useState(false);
    const [formData, setFormData] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState("");

    useEffect(() => {
        fetchProfile();
    }, []);

    const fetchProfile = async () => {
        try {
            setLoading(true);
            setError(null);
            
            console.log('Fetching profile...');
            const token = localStorage.getItem('access_token');
            console.log('Token exists:', !!token);
            
            const res = await api.get("/api/profile/");
            console.log('Profile response:', res.data);
            
            setProfile(res.data);
            setFormData({
                first_name: res.data.first_name || '',
                last_name: res.data.last_name || '',
                dob: res.data.dob || '',
                gender: res.data.gender || '',
                blood_group: res.data.blood_group || '',
                contact_number: res.data.contact_number || '',
                address: res.data.address || '',
                profile_picture: res.data.profile_picture || null
            });
        } catch (err) {
            console.error("Error fetching profile:", err);
            setError(err.response?.data?.error || "Error loading profile data");
        } finally {
            setLoading(false);
        }
    };

    const handleEditToggle = () => {
        setEditMode(!editMode);
        if (!editMode) {
            setFormData(profile); // Reset form data when entering edit mode
        }
        setError(null);
        setSuccessMessage("");
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value || ""
        }));
    };

    const handleFormSubmit = async (e) => {
        e.preventDefault();
        try {
            setLoading(true);
            setError(null);
            setSuccessMessage("");
    
            const formDataToSend = new FormData();
            
            // Append all form fields
            Object.keys(formData).forEach(key => {
                if (formData[key] !== null && formData[key] !== undefined) {
                    // Special handling for profile picture
                    if (key === 'profile_picture') {
                        if (formData[key] instanceof File) {
                            formDataToSend.append(key, formData[key]);
                        }
                    } else {
                        formDataToSend.append(key, formData[key]);
                    }
                }
            });
    
            const res = await api.put("/api/profile/", formDataToSend);
            
            setProfile(res.data);
            setEditMode(false);
            setSuccessMessage("Profile updated successfully!");
            window.alert("Profile updated successfully!");
        } catch (err) {
            console.error("Update error details:", err);
            const errorMessage = err.response?.data?.error || 
                                 err.response?.data?.message || 
                                 "Error updating profile. Please try again.";
            setError(errorMessage);
            window.alert(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="loading">Loading...</div>;
    }

    return (
        <div className="container">
            <h1 className="heading-1">Student Dashboard</h1>
            
            {profile && (
                <div className="profile-card">
                    <div className="profile-info">
                        <div className="avatar-container">
                            <Avatar 
                                src={profile.profile_picture}
                                alt={`${profile.first_name || 'Student'}'s profile`}
                            />
                        </div>
                        <div className="profile-details">
                            <h2 className="heading-2">Student Profile</h2>
                            <div className="info-grid">
                                <p><strong>Name:</strong> {profile.first_name} {profile.last_name}</p>
                                <p><strong>Email:</strong> {profile.email}</p>
                                <p><strong>Contact:</strong> {profile.contact_number}</p>
                            </div>
                        </div>
                    </div>
                    {!editMode ? (
                        <div className="info-section">
                            <p><strong>First Name:</strong> {profile.first_name || "Not provided"}</p>
                            <p><strong>Last Name:</strong> {profile.last_name || "Not provided"}</p>
                            <p><strong>Date of Birth:</strong> {profile.dob || "Not provided"}</p>
                            <p><strong>Gender:</strong> {profile.gender || "Not provided"}</p>
                            <p><strong>Blood Group:</strong> {profile.blood_group || "Not provided"}</p>
                            <p><strong>Contact Number:</strong> {profile.contact_number || "Not provided"}</p>
                            <p><strong>Address:</strong> {profile.address || "Not provided"}</p>
                            <button 
                                onClick={handleEditToggle}
                                className="btn btn-primary"
                            >
                                Edit Details
                            </button>
                        </div>
                    ) : (
                        <form onSubmit={handleFormSubmit} className="form-container">
                            <h2 className="form-title">Edit Profile</h2>
                            <div className="form-fields">
                                <div className="form-group">
                                    <label className="form-label">Profile Picture</label>
                                    <input
                                        type="file"
                                        name="profile_picture"
                                        onChange={(e) => setFormData(prev => ({
                                            ...prev,
                                            profile_picture: e.target.files[0]
                                        }))}
                                        className="form-input"
                                        accept="image/*"
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">First Name</label>
                                    <input
                                        type="text"
                                        name="first_name"
                                        value={formData.first_name || ""}
                                        onChange={handleInputChange}
                                        className="form-input"
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Last Name</label>
                                    <input
                                        type="text"
                                        name="last_name"
                                        value={formData.last_name || ""}
                                        onChange={handleInputChange}
                                        className="form-input"
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Date of Birth</label>
                                    <input
                                        type="date"
                                        name="dob"
                                        value={formData.dob || ""}
                                        onChange={handleInputChange}
                                        className="form-input"
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Gender</label>
                                    <select
                                        name="gender"
                                        value={formData.gender || ""}
                                        onChange={handleInputChange}
                                        className="form-select"
                                    >
                                        <option value="">Select Gender</option>
                                        <option value="male">Male</option>
                                        <option value="female">Female</option>
                                        <option value="other">Other</option>
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Blood Group</label>
                                    <input
                                        type="text"
                                        name="blood_group"
                                        value={formData.blood_group || ""}
                                        onChange={handleInputChange}
                                        className="form-input"
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Contact Number</label>
                                    <input
                                        type="text"
                                        name="contact_number"
                                        value={formData.contact_number || ""}
                                        onChange={handleInputChange}
                                        className="form-input"
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Address</label>
                                    <textarea
                                        name="address"
                                        value={formData.address || ""}
                                        onChange={handleInputChange}
                                        className="form-input"
                                        rows="3"
                                    ></textarea>
                                </div>
                                <div className="form-buttons">
                                    <button 
                                        type="submit" 
                                        className="form-button"
                                        disabled={loading}
                                    >
                                        {loading ? "Saving..." : "Save"}
                                    </button>
                                    <button 
                                        type="button" 
                                        onClick={handleEditToggle}
                                        className="form-button"
                                        disabled={loading}
                                    >
                                        Cancel
                                    </button>
                                </div>
                            </div>
                        </form>
                    )}
                </div>
            )}
        </div>
    );
}

export default StudentHome;