import { useState, useEffect } from "react";
import api from "../api";
import '../styles/pages/StudentHome.css';
import { logout } from "../api";

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
    const [subjects, setSubjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [editMode, setEditMode] = useState(false);
    const [formData, setFormData] = useState({});
    const [selectedImage, setSelectedImage] = useState(null);
    const [successMessage, setSuccessMessage] = useState("");

    useEffect(() => {
        let mounted = true;
        
        // Add error handling for unauthorized access
        if (!localStorage.getItem('access_token')) {
            setError('No authentication token found');
            setLoading(false);
            return;
        }

        const fetchData = async () => {
            if (!mounted) return;

            try {
                const [profileRes, subjectsRes] = await Promise.all([
                    api.get("/api/student/profile/"),
                    api.get('/api/student/subjects/')
                ]);

                if (mounted) {
                    setProfile(profileRes.data);
                    setSubjects(subjectsRes.data);
                    setFormData(profileRes.data);
                    setError(null);
                }
            } catch (err) {
                console.error("Error fetching data:", err);
                if (mounted) {
                    if (err.response?.status === 401) {
                        localStorage.clear(); 
                        window.location.href = '/login'; 
                        return;
                    }
                    setError(err.response?.data?.error || "Error loading data");
                }
            } finally {
                if (mounted) {
                    setLoading(false);
                }
            }
        };

        fetchData();

        return () => {
            mounted = false;
        };
    }, []);


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
            const formDataToSend = new FormData();
            
            // Append all non-file fields
            Object.keys(formData).forEach(key => {
                if (key !== 'profile_picture') {
                    formDataToSend.append(key, formData[key] || '');
                }
            });

            // Handle profile picture
            const fileInput = e.target.querySelector('input[type="file"]');
            if (fileInput && fileInput.files[0]) {
                formDataToSend.append('profile_picture', fileInput.files[0]);
            }

            const response = await api.put('/api/student/profile/', formDataToSend, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            console.log('Profile update response:', response.data);

            // Immediately update the profile with the new data
            setProfile(response.data);
            setFormData(response.data);
            setSelectedImage(null);
            setEditMode(false);
            setSuccessMessage("Profile updated successfully!");

            // Fetch the profile again to ensure we have the latest data
            const refreshResponse = await api.get("/api/student/profile/");
            setProfile(refreshResponse.data);
            
        } catch (err) {
            console.error('Update error:', err);
            setError(err.response?.data?.detail || 'Failed to update profile');
        } finally {
            setLoading(false);
        }
    };

    const handleImageSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            setSelectedImage(URL.createObjectURL(file));
        }
    };

    if (loading) {
        return <div className="loading">Loading...</div>;
    }

    if (error) {
        return <div className="error">{error}</div>;
    }

    return (
        <div className="container">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h1 className="heading-1">Student Dashboard</h1>
                <button 
                    onClick={() => logout()}
                    style={{
                        padding: '8px 16px',
                        backgroundColor: '#dc3545',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontWeight: '500',
                        transition: 'background-color 0.2s',
                    }}
                    onMouseOver={(e) => e.target.style.backgroundColor = '#bb2d3b'}
                    onMouseOut={(e) => e.target.style.backgroundColor = '#dc3545'}
                >
                    Logout
                </button>
            </div>
            
            {profile && (
                <div className="profile-card">
                    <div style={styles.dashboardHeader}>
                        <div style={styles.userInfo}>
                            <h2>{profile.first_name} {profile.last_name}</h2>
                            <p style={styles.infoText}>Email: {profile.email || 'Not provided'}</p>
                            <p style={styles.infoText}>Contact: {profile.contact_number || 'Not provided'}</p>
                        </div>
                        <div style={styles.profilePicture}>
                            <img
                                src={selectedImage || profile?.profile_picture || '/default-avatar.png'}
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
                        </div>
                    </div>

                    {successMessage && (
                        <div className="success-message">
                            {successMessage}
                        </div>
                    )}

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
                                className="edit-button"
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
                                        onChange={handleImageSelect}
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
            <div className="subjects-section">
                <h3>Subjects</h3>
                <div className="subjects-grid">
                    {subjects.map(subject => (
                        <div key={subject.code} className="subject-card">
                            <div className="subject-header">
                                <h4>{subject.code}</h4>
                                <span className="credits">Credits: {subject.credits}</span>
                            </div>
                            <h5>{subject.name}</h5>
                            <p className="description">{subject.description}</p>
                            {subject.faculty ? (
                                <div className="faculty-info">
                                    <p className="faculty-name">
                                        <strong>Faculty:</strong> Prof. {subject.faculty.first_name} {subject.faculty.last_name}
                                    </p>
                                    {subject.faculty.email && (
                                        <p className="faculty-email">
                                            <strong>Contact:</strong> {subject.faculty.email}
                                        </p>
                                    )}
                                </div>
                            ) : (
                                <p className="no-faculty">Faculty not assigned</p>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default StudentHome;