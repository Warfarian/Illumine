from django.core.management.base import BaseCommand
from api.models import Subject

class Command(BaseCommand):
    help = 'Create initial subjects'

    def handle(self, *args, **kwargs):
        subjects_data = [
            {
                'code': 'CS101',
                'name': 'Introduction to Programming',
                'description': 'Fundamental concepts of programming using Python',
                'credits': 3
            },
            {
                'code': 'CS201',
                'name': 'Data Structures',
                'description': 'Implementation and analysis of fundamental data structures',
                'credits': 4
            },
            {
                'code': 'CS301',
                'name': 'Database Systems',
                'description': 'Design and implementation of database systems',
                'credits': 3
            },
            {
                'code': 'CS302',
                'name': 'Advanced Algorithms',
                'description': 'Advanced algorithmic techniques and problem-solving strategies',
                'credits': 4
            },
            {
                'code': 'CS401',
                'name': 'Artificial Intelligence',
                'description': 'Fundamentals of AI and machine learning',
                'credits': 4
            },
            {
                'code': 'CS402',
                'name': 'Web Development',
                'description': 'Modern web development technologies and practices',
                'credits': 3
            },
            {
                'code': 'CS403',
                'name': 'Computer Networks',
                'description': 'Principles and practices of computer networking',
                'credits': 3
            },
            {
                'code': 'CS404',
                'name': 'Software Engineering',
                'description': 'Software development methodologies and project management',
                'credits': 4
            },
            {
                'code': 'CS405',
                'name': 'Cybersecurity',
                'description': 'Security principles and practices in computing',
                'credits': 3
            },
            {
                'code': 'CS406',
                'name': 'Cloud Computing',
                'description': 'Cloud architectures and distributed systems',
                'credits': 3
            }
        ]

        for data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'description': data['description'],
                    'credits': data['credits']
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created subject {subject.code} - {subject.name}")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"Subject {subject.code} already exists")
                )

        self.stdout.write(self.style.SUCCESS('Successfully created all subjects'))