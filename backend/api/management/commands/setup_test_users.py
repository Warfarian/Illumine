from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import transaction
from api.models import Faculty, Profile, Student, Subject

class Command(BaseCommand):
    help = 'Creates test users for development'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # Create groups if they don't exist
        faculty_group, _ = Group.objects.get_or_create(name='faculty')
        student_group, _ = Group.objects.get_or_create(name='student')

        # Create test faculty user
        faculty_user = User.objects.create_user(
            username='testfaculty',
            email='testfaculty@example.com',
            password='test1234'
        )
        faculty_user.groups.add(faculty_group)

        # Create test student user
        student_user = User.objects.create_user(
            username='teststudent',
            email='teststudent@example.com',
            password='test1234'
        )
        student_user.groups.add(student_group)

        # Create a test subject
        subject, _ = Subject.objects.get_or_create(
            name='Computer Science 101',
            faculty=faculty_user
        )

        # Add subject to student
        student_user.subjects.add(subject)

        self.stdout.write(self.style.SUCCESS('Successfully created test users'))