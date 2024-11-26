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
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            Profile.objects.get_or_create(user=user)
            
            refresh = RefreshToken.for_user(user)
            role = user.groups.first().name if user.groups.exists() else None

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'role': role
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsFaculty] 

class FacultyStudentAssignmentView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsFaculty]

    def update(self, request, *args, **kwargs):
        student = self.get_object()
        student.faculty = request.user.faculty  
        student.save()
        return Response(StudentSerializer(student).data)

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
            print(f"Attempting to get profile for user: {request.user.username}")  # Debug log
            
            # Get or create faculty profile
            faculty, created = Faculty.objects.get_or_create(
                user=request.user,
                defaults={'department': 'Computer Science'}  # Set a default department
            )
            print(f"Faculty profile {'created' if created else 'found'}")  # Debug log

            # Get or create user profile
            profile, created = Profile.objects.get_or_create(
                user=request.user,
                defaults={
                    'first_name': '',
                    'last_name': '',
                    'contact_number': '',
                    'address': ''
                }
            )
            print(f"User profile {'created' if created else 'found'}")  # Debug log
            
            data = {
                'username': request.user.username,
                'email': request.user.email,
                'department': faculty.department,
                'first_name': profile.first_name or '',
                'last_name': profile.last_name or '',
                'contact_number': profile.contact_number or '',
                'address': profile.address or '',
            }
            
            return Response(data)
            
        except Exception as e:
            print(f"Error in FacultyProfileView: {str(e)}")  # Debug log
            import traceback
            print(traceback.format_exc())  # Print full traceback
            return Response(
                {"detail": f"Error retrieving faculty profile: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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