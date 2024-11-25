from django.contrib.auth.models import User, Group
from django.urls import reverse
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Student, Faculty, Subject
from .serializers import StudentSerializer, UserSerializer, SubjectSerializer,ProfileSerializer
from .permissions import IsFaculty, IsStudent, IsOwnerOrReadOnly
from .models import Profile
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.parsers import MultiPartParser, FormParser

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
        try:
            response = super().post(request, *args, **kwargs)
            
            # Get the user
            user = User.objects.get(username=request.data.get('username'))
            
            # Determine role
            role = None
            if user.groups.filter(name='student').exists():
                role = 'student'
            elif user.groups.filter(name='faculty').exists():
                role = 'faculty'

            # Add role to response data
            response.data['role'] = role
            
            # Add redirect URL based on role
            response.data['redirect_url'] = '/student_home/' if role == 'student' else '/faculty_home/'
            
            return response
            
        except Exception as e:
            return Response(
                {"detail": "Invalid credentials"},
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

class StudentProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsStudent]
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        return self.request.user.student
    
    def perform_update(self, serializer):
        serializer.save()  

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

class FacultyProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsFaculty]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user.profile

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_update(self, serializer):
        serializer.save()

    def get(self, request, *args, **kwargs):
        try:
            profile = self.get_object()
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )