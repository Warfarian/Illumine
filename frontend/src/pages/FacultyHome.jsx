import { useState, useEffect } from 'react';
import api from '../api';
import StudentFormModal from '../components/StudentFormModal';
import '../styles/components/FacultyHome.css';
import axios from 'axios';

function FacultyHome() {
    const [profile, setProfile] = useState(null);
    const [students, setStudents] = useState([]);
    const [selectedStudent, setSelectedStudent] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [assignedSubject, setAssignedSubject] = useState(null);
    const [error, setError] = useState(null);
    const [facultyDepartment, setFacultyDepartment] = useState('');
    const [enrolledStudents, setEnrolledStudents] = useState([]);

    useEffect(() => {
        fetchProfile();
        fetchStudents();
        fetchAssignedSubject();
        getFacultyProfile();
    }, []);

    const getFacultyProfile = async () => {
        try {
            const response = await api.get('/api/faculty/profile/');
            setFacultyDepartment(response.data.department);
        } catch (error) {
            console.error('Error fetching faculty profile:', error);
        }
    };

    const fetchProfile = async () => {
        try {
            const token = localStorage.getItem('access_token');
            console.log('Token used:', token);
            
            const response = await axios.get('http://localhost:8000/api/faculty/profile/', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            setProfile(response.data);
        } catch (error) {
            console.error('Error fetching profile:', error.response?.data);
            if (error.response?.status === 401) {
                window.location.href = '/login';
            }
        }
    };

    const fetchStudents = async () => {
        try {
            const response = await api.get('/api/faculty/students/', {
                params: {
                    department: facultyDepartment
                }
            });
            setStudents(response.data);
        } catch (error) {
            console.error('Error fetching students:', error);
        }
    };

    useEffect(() => {
        if (facultyDepartment) {
            fetchStudents();
        }
    }, [facultyDepartment]);

    const fetchAssignedSubject = async () => {
        try {
            const token = localStorage.getItem('access_token');
            const response = await axios.get('http://localhost:8000/api/faculty/subject/', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            setAssignedSubject(response.data);
        } catch (error) {
            console.error('Error fetching assigned subject:', error.response?.data);
        }
    };

    const fetchEnrolledStudents = async () => {
        try {
            const response = await api.get('/api/faculty/students/', {
                params: {
                    department: facultyDepartment
                }
            });
            setEnrolledStudents(response.data);
        } catch (error) {
            console.error('Error fetching enrolled students:', error);
        }
    };

    const handleCreateStudent = async (formData) => {
        try {
            console.log('Creating student with data:', formData); // Debug log
            
            const response = await api.post('/api/faculty/students/', {
                username: formData.username,
                password: formData.password,
                first_name: formData.first_name,
                last_name: formData.last_name,
                email: formData.email,
                department: formData.department,
                gender: formData.gender || '',
                blood_group: formData.blood_group || '',
                contact_number: formData.contact_number || '',
                address: formData.address || ''
            }); 

            if (response.data) {
                await fetchStudents();
                setShowModal(false);
                alert('Student created successfully');
            }
        } catch (error) {
            console.error('Error creating student:', error);
            console.error('Error response:', error.response?.data);
            const errorMessage = error.response?.data?.detail || 
                               error.message ||
                               'Failed to create student';
            alert(errorMessage);
        }
    };

    const handleUpdateStudent = async (studentId, formData) => {
        try {
            console.log('Updating student:', studentId, 'with data:', formData);
            
            const response = await api.put(`/api/faculty/students/${studentId}/`, {
                first_name: formData.first_name,
                last_name: formData.last_name,
                email: formData.email,
                department: formData.department
            });

            if (response.data) {
                await fetchStudents();
                await fetchEnrolledStudents();
                setShowModal(false);
                alert('Student updated successfully');
            }
        } catch (error) {
            console.error('Error updating student:', error);
            console.error('Error response:', error.response?.data);
            alert('Failed to update student');
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
                    onSubmit={selectedStudent ? 
                        (formData) => handleUpdateStudent(selectedStudent.id, formData) : 
                        handleCreateStudent}
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