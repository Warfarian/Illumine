from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Student, Subject, Faculty, Profile

class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=["faculty", "student"], write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "password", "role"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        role = validated_data.pop("role")
        user = User.objects.create_user(**validated_data)
        
        if role == "faculty":
            group, _ = Group.objects.get_or_create(name="Faculty")
            user.groups.add(group)
        elif role == "student":
            group, _ = Group.objects.get_or_create(name="Students")
            user.groups.add(group)
        
        user.save()
        return user

class SubjectSerializer(serializers.ModelSerializer):
    faculty = serializers.StringRelatedField()

    class Meta:
        model = Subject
        fields = ['id', 'name', 'faculty']

class StudentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = [
            'id',
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
            'department',
            'gender',
            'blood_group',
            'contact_number',
            'address',
            'profile_picture'
        ]

    def create(self, validated_data):
        print("Starting create method with data:", validated_data)  # Debug print
        
        try:
            # Extract user-specific data
            username = validated_data.pop('username')
            password = validated_data.pop('password')
            email = validated_data.get('email')
            
            print(f"Creating user with username: {username}, email: {email}")  # Debug print

            # Create User instance first
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', '')
            )
            
            print(f"User created with ID: {user.id}")  # Debug print

            # Add to student group
            student_group, _ = Group.objects.get_or_create(name='student')
            user.groups.add(student_group)
            
            print("Creating student with data:", validated_data)  # Debug print
            
            # Create Student instance with the user
            student = Student.objects.create(
                user=user,
                first_name=validated_data.get('first_name'),
                last_name=validated_data.get('last_name'),
                email=validated_data.get('email'),
                department=validated_data.get('department'),
                gender=validated_data.get('gender'),
                blood_group=validated_data.get('blood_group'),
                contact_number=validated_data.get('contact_number'),
                address=validated_data.get('address')
            )
            
            print(f"Student created with ID: {student.id}")  # Debug print
            return student
            
        except Exception as e:
            print(f"Error in create method: {str(e)}")  # Debug print
            # If student creation fails, delete the user to avoid orphaned users
            if 'user' in locals():
                print(f"Deleting user due to error")  # Debug print
                user.delete()
            raise serializers.ValidationError(str(e))

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    department = serializers.CharField(source='user.faculty.department', read_only=True)
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id', 'first_name', 'last_name', 'email', 'department',
            'dob', 'gender', 'blood_group', 'contact_number', 
            'address', 'profile_picture'
        ]

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

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
        
        # Handle null values
        for field in data:
            if data[field] is None:
                data[field] = ""
                
        # Format date
        if data.get('dob'):
            try:
                from datetime import datetime
                date_obj = datetime.strptime(data['dob'], '%Y-%m-%d')
                data['dob'] = date_obj.strftime('%Y-%m-%d')
            except:
                pass
                
        return data

class StudentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()  
    
    class Meta:
        model = Student
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'department',
            'roll_number',
            'contact_number',
            'address',
            'gender',
            'blood_group',
            'dob',
            'profile_picture'
        ]        
        read_only_fields = ['roll_number']

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['profile_picture'] = self.get_profile_picture(instance)
        return data

    def get_username(self, obj):
        return obj.user.username if obj.user else ''
