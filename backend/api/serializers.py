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
    user = UserSerializer(read_only=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    subjects = SubjectSerializer(many=True, read_only=True)
    
    class Meta:
        model = Student
        fields = ['id', 'user', 'profile_picture', 'first_name', 'last_name', 
                 'dob', 'gender', 'blood_group', 'contact_number', 'address', 
                 'faculty', 'subjects']

    def update(self, instance, validated_data):
        profile_picture = validated_data.pop('profile_picture', None)
        if profile_picture:
            # Delete old profile picture if it exists
            if instance.profile_picture:
                instance.profile_picture.delete(save=False)
            instance.profile_picture = profile_picture
            
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance

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
    class Meta:
        model = Student
        fields = [
            'id', 
            'first_name', 
            'last_name', 
            'email', 
            'department', 
            'roll_number',
            'subjects'
        ]
        read_only_fields = ['roll_number']  # This will be auto-generated

    def validate_email(self, value):
        if Student.objects.filter(email=value).exists():
            raise serializers.ValidationError("A student with this email already exists.")
        return value

    def validate_roll_number(self, value):
        if Student.objects.filter(roll_number=value).exists():
            raise serializers.ValidationError("A student with this roll number already exists.")
        return value