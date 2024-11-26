import { useState } from 'react';
import '../styles/components/StudentFormModal.css';

function StudentFormModal({ student, onSubmit, onClose }) {
    const [formData, setFormData] = useState({
        username: student?.username || '',
        email: student?.email || '',
        password: '',  // Only required for new students
        first_name: student?.first_name || '',
        last_name: student?.last_name || '',
        department: student?.department || 'Computer Science'
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        // Validate required fields
        const requiredFields = ['username', 'email', 'first_name', 'last_name'];
        if (!student) {
            requiredFields.push('password');
        }

        const missingFields = requiredFields.filter(field => !formData[field]);
        if (missingFields.length > 0) {
            alert(`Please fill in all required fields: ${missingFields.join(', ')}`);
            return;
        }

        try {
            await onSubmit(student?.id, formData);
        } catch (error) {
            console.error('Form submission error:', error);
            const errorMessage = error.response?.data?.detail || 'An error occurred';
            alert(errorMessage);
        }
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <h3>{student ? 'Edit Student' : 'Add New Student'}</h3>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Username: <span className="required">*</span></label>
                        <input
                            type="text"
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    {!student && (
                        <div className="form-group">
                            <label>Password: <span className="required">*</span></label>
                            <input
                                type="password"
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                required={!student}
                                minLength={6}
                            />
                        </div>
                    )}

                    <div className="form-group">
                        <label>First Name: <span className="required">*</span></label>
                        <input
                            type="text"
                            name="first_name"
                            value={formData.first_name}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Last Name: <span className="required">*</span></label>
                        <input
                            type="text"
                            name="last_name"
                            value={formData.last_name}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Email: <span className="required">*</span></label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Department: <span className="required">*</span></label>
                        <select
                            name="department"
                            value={formData.department}
                            onChange={handleChange}
                            required
                        >
                            <option value="Computer Science">Computer Science</option>
                            <option value="Information Technology">Information Technology</option>
                            <option value="Software Engineering">Software Engineering</option>
                        </select>
                    </div>

                    <div className="button-group">
                        <button type="submit" className="submit-button">
                            {student ? 'Update' : 'Create'}
                        </button>
                        <button 
                            type="button" 
                            onClick={onClose}
                            className="cancel-button"
                        >
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default StudentFormModal;