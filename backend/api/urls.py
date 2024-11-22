from django.urls import path
from . import views

urlpatterns = [
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('student/create/', views.CreateStudentView.as_view(), name='create_student'),
    path('student/profile/', views.StudentProfileView.as_view(), name='student_profile'),
    path('faculty/student/assign/', views.FacultyStudentAssignmentView.as_view(), name='assign_student'),
    path('subjects/', views.SubjectFacultyView.as_view(), name='subject_faculty')
]
