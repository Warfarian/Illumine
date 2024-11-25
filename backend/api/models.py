from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models

class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, default="General Department")

    def __str__(self):
        return self.user.username

class Subject(models.Model):
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=10, unique=True, null=False, blank=False, default='')
    
    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        # Auto-generate code if not provided
        if not self.code:
            # Find the next available code
            last_subject = Subject.objects.order_by('-id').first()
            if last_subject:
                last_code_num = int(last_subject.code[2:]) if last_subject.code else 0
                self.code = f'CS{last_code_num + 1:03d}'
            else:
                self.code = 'CS001'
        
        super().save(*args, **kwargs)
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile = models.OneToOneField('Profile', on_delete=models.CASCADE, null=True, blank=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True)
    contact_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
