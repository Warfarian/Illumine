from django.contrib.auth.models import User, Group
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Student, Faculty, Subject
from .serializers import StudentSerializer, UserSerializer, SubjectSerializer
from .permissions import IsFaculty, IsStudent, IsOwnerOrReadOnly
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']  

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


# Register View
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Login View (using JWT)
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

# Faculty Views

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

# Student Views

class StudentProfileView(generics.RetrieveUpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        return self.request.user.student

class SubjectFacultyView(generics.RetrieveAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.student 
