from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from runs.models import Run
from datetime import date, time


class Command(BaseCommand):
    help = 'Creates sample data for testing'

    def handle(self, *args, **kwargs):
        # Create some test users
        users_created = 0
        for i in range(1, 6):
            username = f'user{i}'
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username,
                    email=f'user{i}@example.com',
                    password='password123'
                )
                users_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {users_created} test users'))
        
        # Create some test runs
        runs_data = [
            {
                'date': date(2025, 10, 20),
                'time': time(9, 0),
                'meeting_place': 'Main Entrance',
                'venue': 'Victoria Park',
                'length_km': 5.0,
                'max_capacity': 20
            },
            {
                'date': date(2025, 10, 22),
                'time': time(18, 30),
                'meeting_place': 'Canal Towpath',
                'venue': 'Regent\'s Canal',
                'length_km': 10.0,
                'max_capacity': 15
            },
            {
                'date': date(2025, 10, 25),
                'time': time(7, 0),
                'meeting_place': 'North Gate',
                'venue': 'Hampstead Heath',
                'length_km': 8.5,
                'max_capacity': 3
            },
        ]
        
        runs_created = 0
        for run_data in runs_data:
            if not Run.objects.filter(
                date=run_data['date'],
                venue=run_data['venue']
            ).exists():
                Run.objects.create(**run_data)
                runs_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {runs_created} test runs'))
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
