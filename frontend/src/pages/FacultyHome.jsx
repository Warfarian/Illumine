import { useState, useEffect } from 'react';
import api from '../api';
import StudentFormModal from '../components/StudentFormModal';
import '../styles/components/FacultyHome.css';

function FacultyHome() {
    const [profile, setProfile] = useState(null);
    const [students, setStudents] = useState([]);
    const [selectedStudent, setSelectedStudent] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [assignedSubject, setAssignedSubject] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchProfile();
        fetchStudents();
        fetchAssignedSubject();
    }, []);

    const fetchProfile = async () => {
        try {
            const response = await api.get('/api/faculty/profile/');
            setProfile(response.data);
        } catch (err) {
            console.error('Error fetching profile:', err);
            if (err.response?.status === 401) {
                // Handle unauthorized access
                window.location.href = '/login';
            }
        }
    };

    const fetchStudents = async () => {
        try {
            const response = await api.get('/api/faculty/students/');
            setStudents(response.data);
            setError(null); // Clear any existing errors on successful fetch
        } catch (err) {
            console.error('Error fetching students:', err);
            setError('Unable to load students. Please try again later.');
        }
    };

    const fetchAssignedSubject = async () => {
        try {
            const response = await api.get('/api/faculty/subject/');
            setAssignedSubject(response.data);
        } catch (err) {
            if (err.response?.status === 404) {
                console.log('No subject assigned');
            } else {
                console.error('Error fetching assigned subject:', err);
            }
        }
    };

    const handleCreateStudent = async (_, formData) => {
        try {
            await api.post('/api/faculty/students/', formData);
            fetchStudents();
            setShowModal(false);
            alert('Student created successfully');
        } catch (err) {
            console.error('Error creating student:', err);
            alert(err.response?.data?.detail || 'Failed to create student');
        }
    };

    const handleUpdateStudent = async (studentId, formData) => {
        try {
            await api.put(`/api/faculty/students/${studentId}/`, formData);
            fetchStudents();
            setShowModal(false);
            alert('Student updated successfully');
        } catch (err) {
            console.error('Error updating student:', err);
            alert(err.response?.data?.detail || 'Failed to update student');
        }
    };

    return (
        <div className="faculty-home">
            {/* Profile Section */}
            {profile && (
                <div className="header">
                    <div className="header-content">
                        <div className="profile-info">
                            <h2>Welcome, {profile.first_name} {profile.last_name}</h2>
                            <p>Department: {profile.department}</p>
                        </div>
                        <button 
                            className="add-button"
                            onClick={() => {
                                setSelectedStudent(null);
                                setShowModal(true);
                            }}
                        >
                            Add New Student
                        </button>
                    </div>
                </div>
            )}

            {/* Assigned Subject Section */}
            <div className="section">
                <h3>Assigned Subject</h3>
                {assignedSubject ? (
                    <div className="subject-info">
                        <h4>{assignedSubject.code} - {assignedSubject.name}</h4>
                        <p>{assignedSubject.description}</p>
                        <p>Credits: {assignedSubject.credits}</p>
                        
                        {assignedSubject.students && assignedSubject.students.length > 0 && (
                            <div className="subject-students">
                                <h5>Enrolled Students</h5>
                                <ul>
                                    {assignedSubject.students.map(student => (
                                        <li key={student.id}>
                                            {student.name} ({student.roll_number})
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                ) : (
                    <p>No subject assigned yet</p>
                )}
            </div>

            {/* Students Section */}
            <div className="section">
                <h3>Students</h3>
                {error ? (
                    <div className="error-message">
                        <p>{error}</p>
                        <button 
                            className="action-button"
                            onClick={fetchStudents}
                            style={{marginTop: '10px'}}
                        >
                            Retry
                        </button>
                    </div>
                ) : (
                    <div className="table-container">
                        <table className="faculty-table">
                            <thead>
                                <tr>
                                    <th>Roll Number</th>
                                    <th>Name</th>
                                    <th>Username</th>
                                    <th>Email</th>
                                    <th>Department</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {students.map(student => (
                                    <tr key={student.id}>
                                        <td>{student.roll_number}</td>
                                        <td>{`${student.first_name} ${student.last_name}`}</td>
                                        <td>{student.username}</td>
                                        <td>{student.email}</td>
                                        <td>{student.department}</td>
                                        <td>
                                            <button 
                                                className="action-button"
                                                onClick={() => {
                                                    setSelectedStudent(student);
                                                    setShowModal(true);
                                                }}
                                            >
                                                Edit
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {showModal && (
                <StudentFormModal
                    student={selectedStudent}
                    onSubmit={selectedStudent ? handleUpdateStudent : handleCreateStudent}
                    onClose={() => {
                        setShowModal(false);
                        setSelectedStudent(null);
                    }}
                />
            )}
        </div>
    );
}

export default FacultyHome;