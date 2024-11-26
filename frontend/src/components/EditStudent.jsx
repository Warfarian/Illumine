import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const EditStudent = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        email: '',
        roll_number: '',
        department: ''
    });
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchStudent = async () => {
            try {
                const response = await axios.get(`/api/students/${id}/`);
                setFormData(response.data);
            } catch (err) {
                setError('Failed to fetch student details');
                console.error('Error:', err);
            }
        };
        fetchStudent();
    }, [id]);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await axios.put(`/api/students/${id}/`, formData);
            navigate('/faculty_home');
        } catch (err) {
            setError(err.response?.data?.message || 'Failed to update student');
            console.error('Error:', err);
        }
    };

    return (
        <div className="container mt-5">
            <h2>Edit Student</h2>
            {error && <div className="alert alert-danger">{error}</div>}
            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label className="form-label">First Name:</label>
                    <input
                        type="text"
                        name="first_name"
                        className="form-control"
                        value={formData.first_name}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="mb-3">
                    <label className="form-label">Last Name:</label>
                    <input
                        type="text"
                        name="last_name"
                        className="form-control"
                        value={formData.last_name}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="mb-3">
                    <label className="form-label">Email:</label>
                    <input
                        type="email"
                        name="email"
                        className="form-control"
                        value={formData.email}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="mb-3">
                    <label className="form-label">Roll Number:</label>
                    <input
                        type="text"
                        name="roll_number"
                        className="form-control"
                        value={formData.roll_number}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="mb-3">
                    <label className="form-label">Department:</label>
                    <input
                        type="text"
                        name="department"
                        className="form-control"
                        value={formData.department}
                        onChange={handleChange}
                        required
                    />
                </div>
                <button type="submit" className="btn btn-primary">Update Student</button>
                <button 
                    type="button" 
                    className="btn btn-secondary ms-2"
                    onClick={() => navigate('/faculty_home')}
                >
                    Cancel
                </button>
            </form>
        </div>
    );
};

export default EditStudent;
