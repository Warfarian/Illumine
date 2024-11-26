from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Subject(models.Model):
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey('Faculty', on_delete=models.CASCADE, related_name='subjects')
    
    def __str__(self):
        return f"{self.name} - {self.faculty.user.username}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    roll_number = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100, default="Computer Science")
    subjects = models.ManyToManyField(Subject, blank=True, related_name='students')
    faculty = models.ForeignKey('Faculty', on_delete=models.SET_NULL, null=True, related_name='students')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.roll_number})"

    class Meta:
        ordering = ['roll_number']

class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, default="Computer Science")

    def __str__(self):
        return f"{self.user.username} - {self.department}"

    class Meta:
        verbose_name_plural = "Faculty"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True
    )
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True)
    contact_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
