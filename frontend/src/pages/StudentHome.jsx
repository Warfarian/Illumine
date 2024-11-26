import { useState, useEffect } from "react";
import { updateProfile } from "../api";
import Avatar from '../components/Avatar';
import api from "../api";

const styles = {
    dashboardHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '20px',
        backgroundColor: '#f5f5f5',
        borderRadius: '8px',
        marginBottom: '20px'
    },
    userInfo: {
        flex: 1
    },
    profilePicture: {
        marginLeft: '20px'
    },
    infoText: {
        margin: '5px 0',
        color: '#666'
    }
};

function StudentHome() {
    const [profile, setProfile] = useState(null);
    const [editMode, setEditMode] = useState(false);
    const [formData, setFormData] = useState({});
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState("");
    const [selectedImage, setSelectedImage] = useState(null);

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
        setLoading(true);
        setError(null);

        try {
            const formData = new FormData();
            formData.append('first_name', e.target.first_name.value);
            formData.append('last_name', e.target.last_name.value);
            formData.append('contact_number', e.target.contact_number.value);
            formData.append('address', e.target.address.value);
            formData.append('gender', e.target.gender.value);
            formData.append('blood_group', e.target.blood_group.value);
            formData.append('dob', e.target.dob.value);

            if (e.target.profile_picture.files[0]) {
                formData.append('profile_picture', e.target.profile_picture.files[0]);
            }

            const response = await api.put('/api/student/profile/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            setProfile(response.data);
            alert('Profile updated successfully!');
            
            if (response.data.profile_picture) {
                const timestamp = new Date().getTime();
                setProfile({
                    ...response.data,
                    profile_picture: `${response.data.profile_picture}?t=${timestamp}`
                });
            }
        } catch (err) {
            console.error('Update error details:', err);
            setError('Failed to update profile');
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
                    <div style={styles.dashboardHeader}>
                        <div style={styles.userInfo}>
                            <h2>{profile.first_name} {profile.last_name}</h2>
                            <p style={styles.infoText}>Email: {profile.email || 'Not provided'}</p>
                            <p style={styles.infoText}>Contact: {profile.contact_number || 'Not provided'}</p>
                        </div>
                        <div style={styles.profilePicture}>
                            {profile.profile_picture && (
                                <img
                                    src={selectedImage || profile.profile_picture}
                                    alt="Profile"
                                    style={{
                                        width: '150px',
                                        height: '150px',
                                        objectFit: 'cover',
                                        borderRadius: '50%',
                                        border: '3px solid #fff',
                                        boxShadow: '0 0 10px rgba(0,0,0,0.1)'
                                    }}
                                />
                            )}
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
                        <form onSubmit={handleFormSubmit} encType="multipart/form-data" className="form-container">
                            <h2 className="form-title">Edit Profile</h2>
                            <div className="form-fields">
                                <div className="form-group">
                                    <label className="form-label">Profile Picture</label>
                                    <input
                                        type="file"
                                        name="profile_picture"
                                        onChange={(e) => {
                                            if (e.target.files[0]) {
                                                setSelectedImage(URL.createObjectURL(e.target.files[0]));
                                            }
                                        }}
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
                                        {loading ? "Updating..." : "Update Profile"}
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
            {error && <div className="error">{error}</div>}
        </div>
    );
}

export default StudentHome;