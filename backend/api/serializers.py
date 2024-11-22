from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Student, Subject, Faculty

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
            user.groups.add(Group.objects.get(name="Faculty"))
        elif role == "student":
            user.groups.add(Group.objects.get(name="Students"))
        
        user.save()
        return user

class SubjectSerializer(serializers.ModelSerializer):
    faculty = serializers.StringRelatedField()

    class Meta:
        model = Subject
        fields = ['id', 'name', 'faculty']

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    profile_picture = serializers.ImageField(required=False)
    subjects = SubjectSerializer(many=True, read_only=True)
    
    class Meta:
        model = Student
        fields = ['id', 'user', 'profile_picture', 'first_name', 'last_name', 'dob', 'gender', 'blood_group', 'contact_number', 'address', 'faculty', 'subjects']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            instance.user.username = user_data.get('username', instance.user.username)
            instance.user.password = user_data.get('password', instance.user.password)
            instance.user.save()
        return super().update(instance, validated_data)
