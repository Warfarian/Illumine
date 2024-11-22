from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, default="General Department")

    def __str__(self):
        return self.user.username

class Subject(models.Model):
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField(default=timezone.now)  
    gender = models.CharField(max_length=10, blank=True, null=True)
    blood_group = models.CharField(max_length=5, default="Not provided")
    contact_number = models.CharField(max_length=15, default="Not provided")
    address = models.TextField(default="308 Negra Arroyo Lane")
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)  
    subjects = models.ManyToManyField(Subject, related_name='students')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
