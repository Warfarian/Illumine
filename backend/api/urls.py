from.views import RegisterView
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('student/create/', views.CreateStudentView.as_view(), name='create_student'),
    path('student/profile/', views.StudentProfileView.as_view(), name='student_profile'),
    path('faculty/student/assign/', views.FacultyStudentAssignmentView.as_view(), name='assign_student'),
    path('subjects/', views.SubjectFacultyView.as_view(), name='subject_faculty'),
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', views.LoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('student/home/', views.StudentHomeView.as_view(), name='student_home'),
    path('faculty/home/', views.FacultyHomeView.as_view(), name='faculty_home'),
]
