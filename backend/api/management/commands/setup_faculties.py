from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from api.models import Faculty, Subject

class Command(BaseCommand):
    help = 'Create initial faculties and assign them to subjects'

    def handle(self, *args, **kwargs):
        
        faculty_group, _ = Group.objects.get_or_create(name='faculty')

        faculty_data = [
            {
                'username': 'prof_wolverine',
                'email': 'prof.wolverine@university.com',
                'first_name': 'Logan',
                'last_name': 'Howlett',
                'subject_code': 'CS101',
                'password': 'faculty123'
            },
            {
                'username': 'prof_cyclops',
                'email': 'prof.cyclops@university.com',
                'first_name': 'Scott',
                'last_name': 'Summers',
                'subject_code': 'CS201',
                'password': 'faculty123'
            },
            {
                'username': 'prof_storm',
                'email': 'prof.storm@university.com',
                'first_name': 'Ororo',
                'last_name': 'Munroe',
                'subject_code': 'CS301',
                'password': 'faculty123'
            },
            {
                'username': 'prof_beast',
                'email': 'prof.beast@university.com',
                'first_name': 'Henry',
                'last_name': 'McCoy',
                'subject_code': 'CS302',
                'password': 'faculty123'
            },
            {
                'username': 'prof_jean',
                'email': 'prof.jean@university.com',
                'first_name': 'Jean',
                'last_name': 'Grey',
                'subject_code': 'CS401',
                'password': 'faculty123'
            },
            {
                'username': 'prof_rogue',
                'email': 'prof.rogue@university.com',
                'first_name': 'Anna Marie',
                'last_name': 'D’Ancanto',
                'subject_code': 'CS402',
                'password': 'faculty123'
            },
            {
                'username': 'prof_quicksilver',
                'email': 'prof.quicksilver@university.com',
                'first_name': 'Pietro',
                'last_name': 'Maximoff',
                'subject_code': 'CS403',
                'password': 'faculty123'
            },
            {
                'username': 'prof_jubilee',
                'email': 'prof.jubilee@university.com',
                'first_name': 'Jubilation',
                'last_name': 'Lee',
                'subject_code': 'CS404',
                'password': 'faculty123'
            },
            {
                'username': 'prof_ice_man',
                'email': 'prof.ice.man@university.com',
                'first_name': 'Bobby',
                'last_name': 'Drake',
                'subject_code': 'CS405',
                'password': 'faculty123'
            },
            {
                'username': 'prof_mystique',
                'email': 'prof.mystique@university.com',
                'first_name': 'Raven',
                'last_name': 'Darkhölme',
                'subject_code': 'CS406',
                'password': 'faculty123'
            }
        ]

        for data in faculty_data:
            try:
                user, created = User.objects.get_or_create(
                    username=data['username'],
                    defaults={
                        'email': data['email'],
                        'first_name': data['first_name'],
                        'last_name': data['last_name']
                    }
                )

                if created:
                    user.set_password(data['password'])
                    user.save()
                    faculty_group.user_set.add(user)
                    self.stdout.write(self.style.SUCCESS(f"Created user {user.username}"))

                subject = Subject.objects.get(code=data['subject_code'])

                faculty, created = Faculty.objects.get_or_create(
                    user=user,
                    defaults={
                        'first_name': data['first_name'],
                        'last_name': data['last_name'],
                        'email': data['email'],
                        'department': 'Computer Science',
                        'subject': subject
                    }
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created faculty {faculty.first_name} {faculty.last_name} "
                            f"for subject {subject.code}"
                        )
                    )
                else:
                    faculty.subject = subject
                    faculty.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Updated faculty {faculty.first_name} {faculty.last_name} "
                            f"for subject {subject.code}"
                        )
                    )

            except Subject.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"Subject {data['subject_code']} does not exist"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error creating faculty for {data['username']}: {str(e)}"
                    )
                )

        self.stdout.write(self.style.SUCCESS('Successfully set up faculties'))
