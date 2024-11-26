from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import transaction
from api.models import Student, Subject

class Command(BaseCommand):
    help = 'Creates test users for development'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # Create the 'student' group if it doesn't exist
        student_group, _ = Group.objects.get_or_create(name='student')

        # Student users
        student_users = [
            {
                'username': 'jon.snow',
                'email': 'jon.snow@nightwatch.edu',
                'password': 'test1234',
                'first_name': 'Jon',
                'last_name': 'Snow',
                'department': 'Computer Science'
            },
            {
                'username': 'loki.laufeyson', 
                'email': 'loki.laufeyson@asgard.edu',
                'password': 'test1234',
                'first_name': 'Loki',
                'last_name': 'Laufeyson',
                'department': 'Information Technology'
            },
            {
                'username': 'sherlock.holmes',
                'email': 'sherlock.holmes@bakerst.edu', 
                'password': 'test1234',
                'first_name': 'Sherlock',
                'last_name': 'Holmes',
                'department': 'Software Engineering'
            },
            {
                'username': 'tyrion.lannister',
                'email': 'tyrion.lannister@casterly.edu',
                'password': 'test1234', 
                'first_name': 'Tyrion',
                'last_name': 'Lannister',
                'department': 'Computer Science'
            },
            {
                'username': 'walter.white',
                'email': 'walter.white@breakingbad.edu',
                'password': 'test1234',
                'first_name': 'Walter',
                'last_name': 'White', 
                'department': 'Information Technology'
            },
            {
                'username': 'arya.stark',
                'email': 'arya.stark@winterfell.edu',
                'password': 'test1234',
                'first_name': 'Arya',
                'last_name': 'Stark',
                'department': 'Software Engineering'
            },
            {
                'username' : 'gandalf.grey',
                'email' : 'gandalf.grey@middleearth.edu',
                'password' : 'test1234',
                'first_name': 'Gandalf',
                'last_name': 'Grey',
                'department': 'Software Engineering'
            },
            {
                'username' : 'frodo.baggins',
                'email' : 'frodo.baggins@shire.edu',
                'password' : 'test1234',
                'first_name': 'Frodo',
                'last_name': 'Baggins',
                'department': 'Software Engineering'
            },
            {
                'username' : 'obi.wan',
                'email' : 'obi.wan@jedi.edu',
                'password' : 'test1234',
                'first_name': 'Obi-Wan',
                'last_name': 'Kenobi',
                'department': 'Software Engineering'
            }
        ]

        for student_data in student_users:
        
            user = User.objects.create_user(
                username=student_data['username'],
                email=student_data['email'],
                password=student_data['password']
            )
            
            # Add to student group
            user.groups.add(student_group)

            # Create student profile
            student = Student.objects.create(
                user=user,
                first_name=student_data['first_name'],
                last_name=student_data['last_name'],
                email=student_data['email'],
                department=student_data['department']
            )

            self.stdout.write(self.style.SUCCESS(f"Student '{student_data['username']}' created successfully."))

        self.stdout.write(self.style.SUCCESS('Successfully created all student users.'))