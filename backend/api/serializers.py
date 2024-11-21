from django.contrib.auth.models import User
from rest_framework import serializers


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
