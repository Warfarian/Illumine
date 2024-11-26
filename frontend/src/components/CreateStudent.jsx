import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

function CreateStudent() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        email: '',
        roll_number: '',
        department: '',
    });
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await api.post('/api/faculty/students/', formData);
            navigate('/faculty/home');
        } catch (err) {
            setError('Failed to create student');
            console.error(err);
        }
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    return (
        <div className="dashboard">
            <h1 className="heading-1">Create New Student</h1>
            
            {error && <div className="error-message">{error}</div>}
            
            <form onSubmit={handleSubmit} className="form">
                <div className="form-group">
                    <label htmlFor="first_name">First Name</label>
                    <input
                        type="text"
                        id="first_name"
                        name="first_name"
                        value={formData.first_name}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="last_name">Last Name</label>
                    <input
                        type="text"
                        id="last_name"
                        name="last_name"
                        value={formData.last_name}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="email">Email</label>
                    <input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="roll_number">Roll Number</label>
                    <input
                        type="text"
                        id="roll_number"
                        name="roll_number"
                        value={formData.roll_number}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="department">Department</label>
                    <input
                        type="text"
                        id="department"
                        name="department"
                        value={formData.department}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-buttons">
                    <button type="submit" className="save-button">
                        Create Student
                    </button>
                    <button 
                        type="button" 
                        className="cancel-button"
                        onClick={() => navigate('/faculty/home')}
                    >
                        Cancel
                    </button>
                </div>
            </form>
        </div>
    );
}

export default CreateStudent;