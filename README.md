# Illumine - College Management System

This is a comprehensive web-based solution for managing college operations. Built with React, DRF, Django and PostgreSQL, it streamlines academic and administrative tasks for faculty and students. The system is deployed on Choreo for enhanced performance and accessibility.

**Video Demo:** [Link](https://youtu.be/2k784pHXk7c)

**Live Demo:** 

Web App: [Link](https://16e4a1c6-50f9-4104-b012-b45d80d7eeba.e1-eu-north-azure.choreoapps.dev/login)
Backend: [Link](https://7d0d6746-b26a-430f-891e-45622b282d4a-dev.e1-eu-north-azure.choreoapis.dev/illumineuniversity/backend/v1.0)

### 🎯 Features

Faculty Portal

Authentication: Secure login using JWT.

Student Management:

- Create, view, and update student profiles.
- Assign students to courses.


Dashboard: View all enrolled students and their details.

Student Portal

Personal Profile Management:

Update profile details, including name, contact information, and profile picture.

Faculty Portal

Update student details, assign students to courses, view all students and their details. 

View enrolled subjects and assigned faculty.



### 🛠️ Tech Stack

Frontend: React.js
Backend: Django REST Framework
Database: PostgreSQL
Deployment: Choreo
Authentication: JWT for secure user sessions



### 🏗️ System Architecture

Frontend (React) ←→ API Gateway(Django Rest Framework) ←→ Backend (Django) ←→ Database (PostgreSQL using Choreo)


### 🚀 Getting Started

### Prerequisites

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- PostgreSQL
- Git

**Local Development Setup**

1. Clone the repository:

```bash
git clone git@github.com:Warfarian/Illumine.git
```     

2. Navigate to the project directory:

```bash
cd illumine
```
3. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
4. Set up environment variables

```bash
touch .env
```

5. Run migrations:

```bash
python manage.py migrate
```

6. Start the Django development server:

```bash
python manage.py runserver
```

7. Frontend setup:

- Navigate to the frontend directory:   

```bash
cd frontend
```

- Install dependencies:

```bash
npm install
```

- Start the React development server:

```bash
npm start
``` 
###  🔐 Environment Variables
Backend (.env)

```bash
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/dbname (replace with your database URL)
ALLOWED_HOSTS=localhost,127.0.0.1 (replace with your frontend URL)
CORS_ORIGINS=http://localhost:3000 (replace with your frontend URL)   
```
Frontend (vite.env)

```bash
VITE_API_URL=http://localhost:8000 (replace with your backend URL)
```

###  📚 API Documentation

Authentication Endpoints

- ```POST /api/auth/login/``` - User login
- ```POST /api/auth/logout/``` - User logout

Faculty Endpoints

- ```POST /api/faculty/students/``` - Create student
- ```GET /api/faculty/students/``` - List all students
- ```PUT /api/faculty/students/{id}/``` - Update student details
- ```POST /api/faculty/assign-student/``` - Assign student to courses   

Student Endpoints

- ```GET /api/students/profile/``` - View student profile
- ```PUT /api/students/profile/``` - Update student profile
- ```GET /api/students/subjects/``` - View enrolled subjects

###  🔒 Security Features
- JWT Authentication
- Password Hashing
- CORS Protection
- Input Validation
- File Upload Validation

###  🌐 Deployment
The application is deployed on Choreo with the following components:

- Frontend Service (React)
- Backend Service (Django)
- Database (PostgreSQL)

Refer to the choreo.yaml file for detailed configurations.

###  📁 Project Structure

```bash
Illumine/
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   ├── styles/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── api.js
│   ├── App.css
│   ├── index.css
│   ├── index.jsx
│   ├── public/
│   ├── index.html
│   └── package.json
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   └── backend/
│       ├── settings.py
│       └── urls.py
└── README.md
```


### 📘 System Diagrams

**1. Entity Relationship Diagram**

![Entity Relationship Diagram](./diagrams/ERD.png)
The Entity Relationship Diagram (ERD) represents the data model of the College Management System, illustrating key entities (tables) and their relationships.

Key Entities:

- students: Contains student details such as username, roll number, first name, last name, email, date of birth, gender, blood group, contact number, and address.
- Enrollments: Tracks course enrollment information, including student_id, course_id, and enrollment_date.
- Courses: Includes course details like id, title, description, and credits.
- Faculty: Stores faculty member details, such as username, id, name, email, and department.


**2. System Architecture Flowchart**

![System Architecture Flowchart](./diagrams/system2.png)

The System Architecture Flowchart showcases the overall design of the College Management System, dividing it into three primary layers:

- Frontend Service: Manages the user interface and client-side interactions, built using React.js.
- Backend Service: Handles business logic, API endpoints, and communication with the database, powered by Django REST Framework.
- Database Service: Maintains data storage and retrieval using PostgreSQL.


**3. Technology Stack Overview**

![Technology Stack Overview](./diagrams/system1.png)

The Technology Stack Overview provides a high-level visualization of the tools and frameworks used in the project, emphasizing the microservices-based architecture.
Key Components:

- Frontend: Built with React.js, ensuring a dynamic and interactive user experience.
- Backend: Developed with Django REST Framework, providing a scalable and secure API layer.
- Database: Powered by PostgreSQL, ensuring reliable and efficient data management.


### 🌐 Links

- [Choreo](https://choreo.dev/)
- [Django](https://www.djangoproject.com/)
- [React](https://react.dev/)
- [PostgreSQL](https://www.postgresql.org/)
