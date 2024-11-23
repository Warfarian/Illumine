from django.contrib.auth.models import User, Group
from django.urls import reverse
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Student, Faculty, Subject
from .serializers import StudentSerializer, UserSerializer, SubjectSerializer
from .permissions import IsFaculty, IsStudent, IsOwnerOrReadOnly

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
    
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()  
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
        response = super().post(request, *args, **kwargs)
        
        user = User.objects.get(username=request.data.get('username'))
        
        role = user.groups.first().name if user.groups.exists() else None
        if hasattr(user, 'student'):
            role = 'student'
        elif hasattr(user, 'faculty'):
            role = 'faculty'

        response.data['role'] = role
        
        if role == 'student':
            redirect_url = reverse('student_home')  
        elif role == 'faculty':
            redirect_url = reverse('faculty_home')  
        else:
            redirect_url = reverse('login')  
            
        response.data['redirect_url'] = request.build_absolute_uri(redirect_url)
        
        return response

class CreateStudentView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsFaculty]

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
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def get_object(self):
        return self.request.user.student

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