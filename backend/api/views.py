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
        print("Login attempt for username:", request.data.get('username'))
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            user = User.objects.get(username=request.data.get('username'))
            print(f"Login successful for {user.username}")
            print(f"User groups: {[g.name for g in user.groups.all()]}")
            
            # Add role to response
            role = 'faculty' if user.groups.filter(name='faculty').exists() else 'student'
            response.data['role'] = role
            
        return response

class CreateStudentView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsFaculty]

    def perform_create(self, serializer):
        # Create user account
        user = User.objects.create_user(
            username=self.request.data.get('username'),
            first_name=self.request.data.get('first_name'),
            last_name=self.request.data.get('last_name'),
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
            student = Student.objects.get(user=request.user)
            serializer = StudentSerializer(student, context={'request': request})
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response(
                {"detail": "Student not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request):
        try:
            student = Student.objects.get(user=request.user)
            
            # Handle file upload
            if 'profile_picture' in request.FILES:
                student.profile_picture = request.FILES['profile_picture']

            # Update other fields
            for field in ['contact_number', 'address', 'gender', 'blood_group', 'dob']:
                if field in request.data:
                    setattr(student, field, request.data[field] or '')

            student.save()

            # Return fresh data using serializer
            serializer = StudentSerializer(student, context={'request': request})
            return Response(serializer.data)

        except Student.DoesNotExist:
            return Response(
                {"detail": "Student not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error updating student: {str(e)}")
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
    def get(self, request):
        # Add print statement for debugging
        print("User:", request.user)
        print("User groups:", request.user.groups.all())
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
        try:
            # Get the faculty member
            faculty = Faculty.objects.get(user=request.user)
            print(f"Faculty: {faculty.first_name} {faculty.last_name}")  # Debug log
            print(f"Faculty Department: {faculty.department}")  # Debug log
            print(f"Faculty Subject: {faculty.subject}")  # Debug log

            # Get students who match both department and subject
            students = Student.objects.filter(
                department=faculty.department,
                subjects=faculty.subject
            ).distinct()
            
            print(f"Found {students.count()} students")  # Debug log
            
            serializer = StudentSerializer(students, many=True)
            return Response(serializer.data)
            
        except Faculty.DoesNotExist:
            return Response(
                {"detail": "Faculty profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error fetching students: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        try:
            print("Creating student with data:", request.data)

            # First create the user
            user = User.objects.create_user(
                username=request.data['username'],
                password=request.data['password'],
                email=request.data['email'],
                first_name=request.data['first_name'],
                last_name=request.data['last_name']
            )

            # Add user to student group
            student_group, _ = Group.objects.get_or_create(name='student')
            user.groups.add(student_group)

            # Create the student with only the fields that exist in your model
            student = Student.objects.create(
                user=user,
                first_name=request.data['first_name'],
                last_name=request.data['last_name'],
                email=request.data['email'],
                department=request.data['department']
            )

            # Return the created student data
            return Response({
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'department': student.department
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error creating student: {str(e)}")
            # If there was an error and user was created, delete it
            if 'user' in locals():
                user.delete()
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, pk):
        try:
            print("Updating student with data:", request.data)  # Debug print
            student = Student.objects.get(pk=pk)
            
            # Update student fields
            student.first_name = request.data.get('first_name', student.first_name)
            student.last_name = request.data.get('last_name', student.last_name)
            student.email = request.data.get('email', student.email)
            student.department = request.data.get('department', student.department)
            student.save()
            
            # Update associated user
            if student.user:
                student.user.first_name = student.first_name
                student.user.last_name = student.last_name
                student.user.email = student.email
                student.user.save()

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
            print(f"Error updating student: {str(e)}")  # Debug print
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
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Remove IsFaculty temporarily for testing
def faculty_subject_view(request):
    # Debug prints
    print("1. Authenticated User:", request.user.username)
    print("2. User Groups:", [g.name for g in request.user.groups.all()])
    print("3. Is User Authenticated?", request.user.is_authenticated)
    
    try:
        faculty = Faculty.objects.get(user=request.user)
        print("4. Found Faculty:", faculty)
        
        if not hasattr(faculty, 'subject'):
            print("5. No subject attribute found")
            return Response(
                {"detail": "No subject assigned yet"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        if not faculty.subject:
            print("6. Subject is None")
            return Response(
                {"detail": "No subject assigned yet"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        print("7. Faculty Subject:", faculty.subject)
        
        return Response({
            'code': faculty.subject.code if faculty.subject else None,
            'name': faculty.subject.name if faculty.subject else None,
            'description': faculty.subject.description if faculty.subject else None,
            'credits': faculty.subject.credits if faculty.subject else None
        })
        
    except Faculty.DoesNotExist as e:
        print("Error: Faculty does not exist -", str(e))
        return Response(
            {"detail": "Faculty profile not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print("Unexpected error:", str(e))
        return Response(
            {"detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def faculty_students_view(request):
    print("User:", request.user.username)
    print("Groups:", [g.name for g in request.user.groups.all()])
    
    try:
        faculty = Faculty.objects.get(user=request.user)
        students = Student.objects.all()  # Or filter based on your requirements
        
        data = [{
            'id': student.id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'email': student.email,
            'roll_number': student.roll_number,
            'department': student.department
        } for student in students]
        
        return Response(data)
        
    except Faculty.DoesNotExist:
        return Response(
            {"detail": "Faculty profile not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print("Error:", str(e))
        return Response(
            {"detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def faculty_student_detail_view(request, student_id):
    print(f"User: {request.user}, Method: {request.method}")  # Debug log
    
    try:
        # Verify faculty
        faculty = Faculty.objects.get(user=request.user)
        student = Student.objects.get(id=student_id)

        if request.method == 'GET':
            data = {
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'department': student.department,
                'roll_number': student.roll_number
            }
            return Response(data)

        elif request.method == 'PUT':
            # Update student details
            if 'first_name' in request.data:
                student.first_name = request.data['first_name']
            if 'last_name' in request.data:
                student.last_name = request.data['last_name']
            if 'email' in request.data:
                student.email = request.data['email']
            if 'department' in request.data:
                student.department = request.data['department']
            
            student.save()
            
            # Update user profile if it exists
            if hasattr(student.user, 'profile'):
                profile = student.user.profile
                if 'first_name' in request.data:
                    profile.first_name = request.data['first_name']
                if 'last_name' in request.data:
                    profile.last_name = request.data['last_name']
                profile.save()

            return Response({
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'department': student.department,
                'roll_number': student.roll_number
            })

    except Faculty.DoesNotExist:
        return Response(
            {"detail": "Faculty profile not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Student.DoesNotExist:
        return Response(
            {"detail": "Student not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"Error: {str(e)}")  # Debug log
        return Response(
            {"detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class PromoteToFacultyView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def post(self, request, student_id):
        try:
            print(f"Starting promotion for student ID: {student_id}")  # Debug log
            
            # Get the student
            student = Student.objects.get(pk=student_id)
            user = student.user
            print(f"Found student: {student.first_name} {student.last_name}")  # Debug log

            # Create faculty instance
            faculty = Faculty.objects.create(
                user=user,
                first_name=student.first_name,
                last_name=student.last_name,
                email=student.email,
                department=student.department
            )
            print(f"Created faculty record with ID: {faculty.id}")  # Debug log

            # Add to faculty group
            faculty_group = Group.objects.get_or_create(name='faculty')[0]
            user.groups.add(faculty_group)
            print("Added to faculty group")  # Debug log

            # Remove student group
            student_group = Group.objects.get(name='student')
            user.groups.remove(student_group)
            print("Removed from student group")  # Debug log

            # Remove all subject enrollments
            student.subjects.clear()
            print("Cleared subject enrollments")  # Debug log
            
            # Delete the student record
            student.delete()
            print("Deleted student record")  # Debug log

            return Response({
                'message': 'Successfully promoted to faculty',
                'faculty_id': faculty.id
            })

        except Student.DoesNotExist:
            print(f"Student {student_id} not found")  # Debug log
            return Response(
                {'detail': 'Student not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error promoting student to faculty: {str(e)}")  # Debug log
            return Response(
                {'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )