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
                'date': date(2025, 11, 19),
                'time': time(6, 30),
                'meeting_place': 'Liverpool Central Station',
                'venue': 'Ship & Mitre',
                'length_km': 5.0,
                'max_capacity': 60
            },
            {
                'date': date(2025, 10, 26),
                'time': time(18, 30),
                'meeting_place': 'Sefton Park Cafe',
                'venue': 'Black Cat Rose Lane',
                'length_km': 5.0,
                'max_capacity': 3
            },
            {
                'date': date(2025, 11, 22),
                'time': time(13, 0),
                'meeting_place': 'Black Lodge',
                'venue': 'Monthly Run - Black Lodge',
                'length_km': 5.0,
                'max_capacity': 80
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
