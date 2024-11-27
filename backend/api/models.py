from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

class Subject(models.Model):
    SUBJECT_CHOICES = [
        ('CS101', 'Introduction to Programming'),
        ('CS201', 'Data Structures and Algorithms'),
        ('CS301', 'Database Management Systems'),
        ('CS302', 'Operating Systems'),
        ('CS401', 'Computer Networks'),
        ('CS402', 'Software Engineering'),
        ('CS403', 'Artificial Intelligence'),
        ('CS404', 'Web Development'),
        ('CS405', 'Cybersecurity'),
        ('CS406', 'Machine Learning')
    ]

    code = models.CharField(max_length=10, choices=SUBJECT_CHOICES, unique=True, default='CS101')
    name = models.CharField(max_length=100)
    faculty = models.OneToOneField('Faculty', on_delete=models.SET_NULL, null=True, related_name='subject_taught')
    description = models.TextField(blank=True)
    credits = models.IntegerField(default=3)

    def __str__(self):
        faculty = self.assigned_faculty
        if faculty:
            return f"{self.code} - {self.name} (Prof. {faculty.last_name})"
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['code']

class Student(models.Model):
    DEPARTMENT_CHOICES = [
        ('Computer Science', 'Computer Science'),
        ('Information Technology', 'Information Technology'),
        ('Software Engineering', 'Software Engineering'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, default='Computer Science')
    roll_number = models.CharField(max_length=20, unique=True)
    subjects = models.ManyToManyField('Subject', related_name='students')
    
    # Add these new fields
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    dob = models.DateField(null=True, blank=True)

    def profile_picture_path(instance, filename):
        # Get file extension
        ext = filename.split('.')[-1]
        # Create filename using username from related User model
        filename = f"{instance.user.username}.{ext}"
        return f'profile_pictures/{filename}'

    profile_picture = models.ImageField(
        upload_to=profile_picture_path,
        null=True,
        blank=True
    )

    def assign_department_subjects(self):
        """Assign subjects based on department"""
        department_subjects = {
            'Computer Science': ['CS101', 'CS201', 'CS301', 'CS302'],
            'Information Technology': ['CS101', 'CS404', 'CS405', 'CS406'],
            'Software Engineering': ['CS101', 'CS402', 'CS403', 'CS404']
        }

        # Clear existing subjects
        self.subjects.clear()

        # Assign new subjects based on department
        subject_codes = department_subjects.get(self.department, [])
        subjects = Subject.objects.filter(code__in=subject_codes)
        self.subjects.add(*subjects)

    def save(self, *args, **kwargs):
        if not self.roll_number:
            year = str(datetime.datetime.now().year)[-2:]
            count = Student.objects.filter(roll_number__startswith=year).count() + 1
            dept_code = self.department[:2].upper()
            self.roll_number = f"{year}{dept_code}{str(count).zfill(3)}"
        
        is_new = self._state.adding  # Check if this is a new student
        super().save(*args, **kwargs)
        
        if is_new or 'department' in kwargs.get('update_fields', []):
            self.assign_department_subjects()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.roll_number})"

    class Meta:
        ordering = ['roll_number']

class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100, default='Computer Science')
    subject = models.OneToOneField(
        'Subject', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_faculty'
    )

    class Meta:
        verbose_name_plural = "Faculty"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

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
