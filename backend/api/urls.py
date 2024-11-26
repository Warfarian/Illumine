from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .views import LoginView, RegisterView, UserProfileView, CustomTokenRefreshView, StudentProfileView, StudentManagementView, SubjectListView, FacultySubjectView, StudentSubjectsView, FacultyProfileView, faculty_subject_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Authentication endpoints
    path('api/token/', views.LoginView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterView.as_view(), name='register'),
    
    # Other endpoints
    path('api/profile/', UserProfileView.as_view(), name='profile'),
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('student/create/', views.CreateStudentView.as_view(), name='create_student'),
    path('student/profile/', views.StudentProfileView.as_view(), name='student_profile'),
    path('faculty/student/assign/', views.FacultyStudentAssignmentView.as_view(), name='assign_student'),
    path('subjects/', views.SubjectFacultyView.as_view(), name='subject_faculty'),
    path('student_home/', views.StudentHomeView.as_view(), name='student_home'),
    path('faculty_home/', views.FacultyHomeView.as_view(), name='faculty_home'),
    path('faculty/promote-student/<int:pk>/', views.PromoteToFacultyView.as_view(), name='promote_student'),
    path('subjects/initialize-default/', views.InitializeDefaultSubjectsView.as_view(), name='initialize_subjects'),
    path('api/faculty/profile/', FacultyProfileView.as_view(), name='faculty-profile'),
    path('api/debug/users/', views.debug_users, name='debug_users'),
    path('api/debug/create-user/', views.debug_create_user, name='debug_create_user'),
    path('api/student/profile/', StudentProfileView.as_view(), name='student-profile'),
    path('api/faculty/students/', StudentManagementView.as_view(), name='faculty-students'),
    path('api/faculty/students/<int:pk>/', StudentManagementView.as_view(), name='faculty-student-detail'),
    path('api/subjects/', SubjectListView.as_view(), name='subject-list'),
    path('api/faculty/subject/', FacultySubjectView.as_view(), name='faculty-subject'),
    path('api/student/subjects/', StudentSubjectsView.as_view(), name='student-subjects'),
    path('faculty/subject/', faculty_subject_view, name='faculty-subject'),
    path('api/faculty/students/<int:student_id>/', views.faculty_student_detail_view, name='faculty-student-detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
