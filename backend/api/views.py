from django.contrib.auth.models import User, Group
from django.urls import reverse
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError
from .models import Student, Faculty, Subject
from .serializers import StudentSerializer, UserSerializer, SubjectSerializer,ProfileSerializer
from .permissions import IsFaculty, IsStudent, IsOwnerOrReadOnly
from .models import Profile
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import Http404
from rest_framework.decorators import api_view, permission_classes
from django.conf import settings
import os
import logging
from rest_framework.authtoken.models import Token

logger = logging.getLogger(__name__)

class RegisterSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=['student', 'faculty'], write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        role = validated_data.pop('role')  
        user = User.objects.create_user(**validated_data)  
        group, _ = Group.objects.get_or_create(name=role)  
        user.groups.add(group)  

        if role == 'student':
            Student.objects.create(user=user)  
        elif role == 'faculty':
            Faculty.objects.create(user=user)  

        return user
    

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name', 'dob', 'gender', 
                 'blood_group', 'contact_number', 'address', 'profile_picture']
        
    def validate_dob(self, value):
        """
        Validate date of birth format
        """
        if value and isinstance(value, str):
            try:
                from datetime import datetime
                datetime.strptime(value, '%Y-%m-%d')
                return value
            except ValueError:
                raise serializers.ValidationError("Invalid date format. Use YYYY-MM-DD")
        return value

    def to_representation(self, instance):
        """
        Modify the data before sending to frontend
        """
        data = super().to_representation(instance)
        
        for field in data:
            if data[field] is None:
                data[field] = ""
                
        if data.get('dob'):
            try:
                from datetime import datetime
                date_obj = datetime.strptime(data['dob'], '%Y-%m-%d')
                data['dob'] = date_obj.strftime('%Y-%m-%d')
            except:
                pass
                
        return data

class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        try:
            logger.info(f"Registration attempt with data: {request.data}")  # Debug log

            # Validate required fields
            required_fields = ['username', 'password', 'email', 'first_name', 'last_name', 'department', 'role']
            missing_fields = [field for field in required_fields if not request.data.get(field)]
            
            if missing_fields:
                return Response(
                    {
                        "detail": f"Missing required fields: {', '.join(missing_fields)}",
                        "received_data": request.data
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate role
            role = request.data['role'].lower()
            if role not in ['student', 'faculty']:
                return Response(
                    {"detail": "Invalid role. Must be either 'student' or 'faculty'"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if username exists
            if User.objects.filter(username=request.data['username']).exists():
                return Response(
                    {"detail": "Username already exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if email exists
            if User.objects.filter(email=request.data['email']).exists():
                return Response(
                    {"detail": "Email already exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create user
            user = User.objects.create_user(
                username=request.data['username'],
                email=request.data['email'],
                password=request.data['password'],
                first_name=request.data['first_name'],
                last_name=request.data['last_name']
            )

            # Get or create groups
            student_group, _ = Group.objects.get_or_create(name='student')
            faculty_group, _ = Group.objects.get_or_create(name='faculty')

            if role == 'student':
                # Create student profile
                student = Student.objects.create(
                    user=user,
                    first_name=request.data['first_name'],
                    last_name=request.data['last_name'],
                    email=request.data['email'],
                    department=request.data['department']
                )
                # Add to student group
                student_group = Group.objects.get(name='student')
                student_group.user_set.add(user)
                
                # Assign subjects based on department
                student.assign_department_subjects()

            elif role == 'faculty':
                # Create faculty profile
                Faculty.objects.create(
                    user=user,
                    first_name=request.data['first_name'],
                    last_name=request.data['last_name'],
                    email=request.data['email'],
                    department=request.data['department']
                )
                # Add to faculty group
                faculty_group = Group.objects.get(name='faculty')
                faculty_group.user_set.add(user)

            # Generate token
            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                'token': token.key,
                'user_id': user.id,
                'role': role
            })

        except Exception as e:
            print(f"Registration error: {str(e)}")  # Debug log
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        print("Login attempt received:", request.data)  # Debug log
        
        try:
            username = request.data.get('username')
            password = request.data.get('password')

            if not username or not password:
                return Response(
                    {"detail": "Both username and password are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if user exists
            try:
                user = User.objects.get(username=username)
                print(f"User found: {user.username}")
                print(f"Groups: {[g.name for g in user.groups.all()]}")
            except User.DoesNotExist:
                print(f"No user found with username: {username}")
                return Response(
                    {"detail": "No account found with this username"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Attempt to get the token pair
            response = super().post(request, *args, **kwargs)
            
            # If we get here, authentication was successful
            role = None
            if user.groups.filter(name__iexact='student').exists():
                role = 'student'
            elif user.groups.filter(name__iexact='faculty').exists():
                role = 'faculty'

            response.data['role'] = role
            print("Login successful:", response.data)
            
            return response
            
        except Exception as e:
            print(f"Login error: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )


class CreateStudentView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsFaculty]

    def perform_create(self, serializer):
        # Create user account
        user = User.objects.create_user(
            username=self.request.data.get('username'),
            email=self.request.data.get('email'),
            password=self.request.data.get('password')
        )
        
        # Add to student group
        student_group = Group.objects.get(name='student')
        user.groups.add(student_group)
        
        # Create student profile with default subjects
        student = serializer.save(user=user)
        
        # Assign default subjects
        default_subjects = Subject.objects.filter(name__in=[
            "Introduction to Computer Science",
            "Data Structures and Algorithms",
            "Database Management Systems",
            "Operating Systems",
            "Computer Networks",
            "Software Engineering"
        ])
        student.subjects.set(default_subjects)

class PromoteToFacultyView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    permission_classes = [IsFaculty]

    def update(self, request, *args, **kwargs):
        student = self.get_object()
        user = student.user
        
        # Change group from student to faculty
        student_group = Group.objects.get(name='student')
        faculty_group = Group.objects.get(name='faculty')
        user.groups.remove(student_group)
        user.groups.add(faculty_group)
        
        # Create faculty profile
        faculty = Faculty.objects.create(
            user=user,
            department="Computer Science"  # Default department
        )
        
        # Delete student profile
        student.delete()
        
        return Response({"message": "Successfully promoted to faculty"}, status=200)

class InitializeDefaultSubjectsView(APIView):
    permission_classes = [IsFaculty]

    def post(self, request):
        default_subjects = [
            {"name": "Introduction to Computer Science", "code": "CS101"},
            {"name": "Data Structures and Algorithms", "code": "CS201"},
            {"name": "Database Management Systems", "code": "CS301"},
            {"name": "Operating Systems", "code": "CS401"},
            {"name": "Computer Networks", "code": "CS501"},
            {"name": "Software Engineering", "code": "CS601"}
        ]

        created_subjects = []
        for subject_data in default_subjects:
            subject, created = Subject.objects.get_or_create(
                name=subject_data["name"],
                defaults={"code": subject_data["code"]}
            )
            created_subjects.append(subject)

        # Assign subjects to all existing students
        students = Student.objects.all()
        for student in students:
            student.subjects.add(*created_subjects)

        return Response({"message": "Default subjects initialized successfully"}, status=200)

class StudentListView(generics.ListAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsFaculty]

    def get_queryset(self):
        # Get students for the current faculty's subject
        faculty = self.request.user.faculty
        if faculty.subject:
            return Student.objects.filter(subjects=faculty.subject)
        return Student.objects.none()

class FacultyStudentAssignmentView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsFaculty]

    def update(self, request, *args, **kwargs):
        try:
            student = self.get_object()
            faculty = request.user.faculty
            
            if not faculty.subject:
                return Response(
                    {"detail": "No subject assigned to faculty"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Add the faculty's subject to student's subjects
            student.subjects.add(faculty.subject)
            
            return Response(StudentSerializer(student).data)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StudentProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
            student = Student.objects.get(user=request.user)
            
            data = {
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'email': student.email,
                'contact_number': profile.contact_number,
                'address': profile.address,
                'profile_picture': request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None,
                'gender': profile.gender,
                'dob': profile.dob,
                'blood_group': profile.blood_group,
                'roll_number': student.roll_number,
                'department': student.department
            }
            return Response(data)
        except Exception as e:
            print(f"Error getting profile: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
            student = Student.objects.get(user=request.user)

            # Handle profile picture
            if 'profile_picture' in request.FILES:
                profile.profile_picture = request.FILES['profile_picture']

            # Update profile fields
            profile.first_name = request.data.get('first_name', profile.first_name)
            profile.last_name = request.data.get('last_name', profile.last_name)
            profile.contact_number = request.data.get('contact_number', profile.contact_number)
            profile.address = request.data.get('address', profile.address)
            profile.gender = request.data.get('gender', profile.gender)
            profile.blood_group = request.data.get('blood_group', profile.blood_group)
            
            # Handle date of birth
            dob = request.data.get('dob')
            if dob:
                profile.dob = dob

            profile.save()

            # Update student fields
            student.first_name = request.data.get('first_name', student.first_name)
            student.last_name = request.data.get('last_name', student.last_name)
            student.save()

            return Response({
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'email': student.email,
                'contact_number': profile.contact_number,
                'address': profile.address,
                'profile_picture': request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None,
                'gender': profile.gender,
                'dob': profile.dob,
                'blood_group': profile.blood_group,
                'roll_number': student.roll_number,
                'department': student.department
            })
        except Exception as e:
            print(f"Error updating profile: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SubjectFacultyView(generics.RetrieveAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.student

class AssignStudentView(APIView):
    permission_classes = [IsFaculty]

    def post(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
            student.faculty = request.user.faculty
            student.save()
            return Response({'message': 'Student assigned successfully.'}, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

class StudentHomeView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsStudent]
    
    def get(self, request):
        return Response({
            "message": "Welcome to the student homepage!",
            "username": request.user.username
        })

class FacultyHomeView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsFaculty]
    
    def get(self, request):
        return Response({
            "message": "Welcome to the faculty homepage!",
            "username": request.user.username
        })
    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        try:
            profile, created = Profile.objects.get_or_create(user=request.user)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def put(self, request):
        try:
            profile, created = Profile.objects.get_or_create(user=request.user)
            serializer = ProfileSerializer(profile, data=request.data, partial=True)
            
            if serializer.is_valid():
                # Handle file upload separately with better error handling
                if 'profile_picture' in request.FILES:
                    try:
                        profile.profile_picture = request.FILES['profile_picture']
                    except Exception as e:
                        return Response({"error": "Invalid file upload"}, status=400)
                
                serializer.save()
                return Response(serializer.data, status=200)
            
            return Response(serializer.errors, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class FacultyProfileView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def get(self, request):
        try:
            faculty = Faculty.objects.get(user=request.user)
            return Response({
                'id': faculty.id,
                'first_name': faculty.first_name,
                'last_name': faculty.last_name,
                'email': faculty.email,
                'department': faculty.department
            })
        except Faculty.DoesNotExist:
            return Response(
                {"detail": "Faculty profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request):
        try:
            # Get or create faculty profile
            faculty, created = Faculty.objects.get_or_create(
                user=request.user,
                defaults={'department': 'General'}
            )
            
            # Get or create user profile
            profile, created = Profile.objects.get_or_create(
                user=request.user
            )
            
            # Update profile fields
            if 'first_name' in request.data:
                profile.first_name = request.data['first_name']
            if 'last_name' in request.data:
                profile.last_name = request.data['last_name']
            if 'contact_number' in request.data:
                profile.contact_number = request.data['contact_number']
            if 'address' in request.data:
                profile.address = request.data['address']
            
            profile.save()
            
            # Update faculty-specific fields
            if 'department' in request.data:
                faculty.department = request.data['department']
                faculty.save()
            
            return Response({
                'username': request.user.username,
                'email': request.user.email,
                'department': faculty.department,
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'contact_number': profile.contact_number,
                'address': profile.address,
            })
            
        except Exception as e:
            print(f"Error updating faculty profile: {str(e)}")  # Debug log
            return Response(
                {"detail": "Error updating faculty profile"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StudentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get students associated with the faculty
        students = Student.objects.filter(faculty=request.user.faculty)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            # Automatically assign the faculty
            serializer.save(faculty=request.user.faculty)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StudentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, faculty):
        try:
            return Student.objects.get(pk=pk, faculty=faculty)
        except Student.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        student = self.get_object(pk, request.user.faculty)
        serializer = StudentSerializer(student)
        return Response(serializer.data)

    def put(self, request, pk):
        student = self.get_object(pk, request.user.faculty)
        serializer = StudentSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        student = self.get_object(pk, request.user.faculty)
        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        print("Refresh token request received:", request.data)  # Debug log
        
        try:
            response = super().post(request, *args, **kwargs)
            print("Token refresh successful")  # Debug log
            return response
            
        except Exception as e:
            print(f"Token refresh error: {str(e)}")  # Debug log
            return Response(
                {"detail": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_users(request):
    users = User.objects.all()
    data = []
    for user in users:
        data.append({
            'username': user.username,
            'groups': [g.name for g in user.groups.all()],
            'is_active': user.is_active,
            'has_usable_password': user.has_usable_password(),
        })
    return Response(data)

@api_view(['POST'])
@permission_classes([AllowAny])
def debug_create_user(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        role = request.data.get('role', 'student')

        user = User.objects.create_user(username=username, password=password)
        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)

        return Response({
            'status': 'success',
            'username': username,
            'role': role
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=400)

class FacultyDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def get(self, request):
        try:
            faculty = request.user.faculty
            students = Student.objects.all()
            subjects = Subject.objects.filter(faculty=faculty)

            data = {
                'faculty_info': {
                    'name': f"{faculty.user.profile.first_name} {faculty.user.profile.last_name}",
                    'department': faculty.department,
                    'email': faculty.user.email,
                },
                'subjects': [{
                    'code': subject.code,
                    'name': subject.name,
                    'students_count': subject.students.count()
                } for subject in subjects],
                'students': [{
                    'id': student.id,
                    'name': f"{student.first_name} {student.last_name}",
                    'roll_number': student.roll_number,
                    'email': student.email
                } for student in students]
            }
            return Response(data)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StudentManagementView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def get(self, request):
        """Get all students"""
        try:
            students = Student.objects.all()
            data = [{
                'id': student.id,
                'username': student.user.username,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'department': student.department,
                'roll_number': student.roll_number
            } for student in students]
            return Response(data)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Create new student"""
        try:
            # Validate required fields
            required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
            missing_fields = [field for field in required_fields if not request.data.get(field)]
            
            if missing_fields:
                return Response(
                    {
                        "detail": f"Missing required fields: {', '.join(missing_fields)}",
                        "received_data": request.data
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if username already exists
            if User.objects.filter(username=request.data['username']).exists():
                return Response(
                    {"detail": "This username is already taken"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if email already exists
            if User.objects.filter(email=request.data['email']).exists():
                return Response(
                    {"detail": "A user with this email already exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create user account
            try:
                user = User.objects.create_user(
                    username=request.data['username'],
                    email=request.data['email'],
                    password=request.data['password']
                )
            except Exception as e:
                return Response(
                    {"detail": f"Error creating user: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Add to student group
            try:
                student_group = Group.objects.get(name='student')
                student_group.user_set.add(user)
            except Group.DoesNotExist:
                user.delete()
                return Response(
                    {"detail": "Student group not found. Please contact administrator."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Create student profile
            try:
                student = Student.objects.create(
                    user=user,
                    first_name=request.data['first_name'],
                    last_name=request.data['last_name'],
                    email=request.data['email'],
                    department=request.data.get('department', 'Computer Science')
                    # roll_number will be auto-generated in the save method
                )
            except Exception as e:
                user.delete()
                return Response(
                    {"detail": f"Error creating student profile: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create profile
            try:
                Profile.objects.create(
                    user=user,
                    first_name=request.data['first_name'],
                    last_name=request.data['last_name']
                )
            except Exception as e:
                student.delete()
                user.delete()
                return Response(
                    {"detail": f"Error creating user profile: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({
                'message': 'Student created successfully',
                'student_id': student.id,
                'student_data': {
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'department': student.department,
                    'roll_number': student.roll_number
                }
            })

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return Response(
                {"detail": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, student_id):
        """Update student details"""
        try:
            student = Student.objects.get(id=student_id)
            user = student.user
            profile = user.profile

            # Update user email if changed
            if 'email' in request.data and request.data['email'] != user.email:
                # Check if email is already taken
                if User.objects.filter(email=request.data['email']).exclude(id=user.id).exists():
                    return Response(
                        {"detail": "Email already exists"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                user.email = request.data['email']
                user.username = request.data['email']  # Update username to match email
                user.save()

            # Update student fields
            student.first_name = request.data.get('first_name', student.first_name)
            student.last_name = request.data.get('last_name', student.last_name)
            student.email = request.data.get('email', student.email)
            student.department = request.data.get('department', student.department)
            student.save()

            # Update profile fields
            profile.first_name = request.data.get('first_name', profile.first_name)
            profile.last_name = request.data.get('last_name', profile.last_name)
            profile.save()

            return Response({
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'department': student.department
            })
        except Student.DoesNotExist:
            return Response(
                {"detail": "Student not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error updating student: {str(e)}")  # Debug log
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SubjectListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subjects = Subject.objects.all()
        data = [{
            'code': subject.code,
            'name': subject.name,
            'description': subject.description,
            'credits': subject.credits,
            'faculty': {
                'first_name': subject.faculty.first_name,
                'last_name': subject.faculty.last_name
            } if subject.faculty else None
        } for subject in subjects]
        return Response(data)

class FacultySubjectView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def get(self, request):
        try:
            faculty = Faculty.objects.get(user=request.user)
            if not faculty.subject:
                return Response(
                    {"detail": "No subject assigned yet"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            return Response({
                'code': faculty.subject.code,
                'name': faculty.subject.name,
                'description': faculty.subject.description,
                'credits': faculty.subject.credits,
                'students': [{
                    'id': student.id,
                    'name': f"{student.first_name} {student.last_name}",
                    'roll_number': student.roll_number
                } for student in faculty.subject.students.all()]
            })
        except Faculty.DoesNotExist:
            return Response(
                {"detail": "Faculty profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StudentSubjectsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            student = Student.objects.get(user=request.user)
            subjects = student.subjects.all().select_related('assigned_faculty')  
            
            data = [{
                'code': subject.code,
                'name': subject.name,
                'description': subject.description,
                'credits': subject.credits,
                'faculty': {
                    'first_name': subject.assigned_faculty.first_name,
                    'last_name': subject.assigned_faculty.last_name,
                    'email': subject.assigned_faculty.email
                } if subject.assigned_faculty else None
            } for subject in subjects]
            
            return Response(data)
        except Student.DoesNotExist:
            return Response(
                {"detail": "Student profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )