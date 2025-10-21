from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from datetime import date, time
from .models import Run, SignUp


class RunModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.run = Run.objects.create(
            date=date(2025, 12, 25),
            time=time(10, 0),
            meeting_place='Test Meeting Place',
            venue='Test Venue',
            length_km=5.0,
            max_capacity=3
        )
    
    def test_run_creation(self):
        """Test that a run can be created."""
        self.assertEqual(self.run.venue, 'Test Venue')
        self.assertEqual(self.run.max_capacity, 3)
        self.assertEqual(self.run.length_km, 5.0)
    
    def test_run_str_representation(self):
        """Test the string representation of a run."""
        expected = f"Test Venue - 2025-12-25 at 10:00:00 (5.0km)"
        self.assertEqual(str(self.run), expected)
    
    def test_get_signups_count(self):
        """Test getting the count of sign-ups."""
        self.assertEqual(self.run.get_signups_count(), 0)
        SignUp.objects.create(user=self.user, run=self.run)
        self.assertEqual(self.run.get_signups_count(), 1)
    
    def test_is_full(self):
        """Test checking if a run is full."""
        self.assertFalse(self.run.is_full())
        
        # Create users and sign them up
        for i in range(3):
            user = User.objects.create_user(username=f'user{i}', password='pass')
            SignUp.objects.create(user=user, run=self.run)
        
        self.assertTrue(self.run.is_full())
    
    def test_available_spots(self):
        """Test calculating available spots."""
        self.assertEqual(self.run.available_spots(), 3)
        
        SignUp.objects.create(user=self.user, run=self.run)
        self.assertEqual(self.run.available_spots(), 2)


class SignUpModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        self.run = Run.objects.create(
            date=date(2025, 12, 25),
            time=time(10, 0),
            meeting_place='Test Meeting Place',
            venue='Test Venue',
            length_km=5.0,
            max_capacity=2
        )
    
    def test_signup_creation(self):
        """Test that a sign-up can be created."""
        signup = SignUp.objects.create(user=self.user1, run=self.run)
        self.assertEqual(signup.user, self.user1)
        self.assertEqual(signup.run, self.run)
        self.assertFalse(signup.attended)
    
    def test_signup_unique_constraint(self):
        """Test that a user cannot sign up twice for the same run."""
        SignUp.objects.create(user=self.user1, run=self.run)
        
        # Try to create duplicate sign-up
        with self.assertRaises(Exception):  # IntegrityError
            SignUp.objects.create(user=self.user1, run=self.run)
    
    def test_signup_validation_when_full(self):
        """Test that sign-up is prevented when run is full."""
        SignUp.objects.create(user=self.user1, run=self.run)
        SignUp.objects.create(user=self.user2, run=self.run)
        
        # Try to sign up when full
        user3 = User.objects.create_user(username='user3', password='pass')
        with self.assertRaises(ValidationError):
            SignUp.objects.create(user=user3, run=self.run)
    
    def test_attendance_tracking(self):
        """Test attendance can be tracked."""
        signup = SignUp.objects.create(user=self.user1, run=self.run)
        self.assertFalse(signup.attended)
        
        signup.attended = True
        signup.save()
        
        signup.refresh_from_db()
        self.assertTrue(signup.attended)


class RunViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.run = Run.objects.create(
            date=date(2025, 12, 25),
            time=time(10, 0),
            meeting_place='Test Meeting Place',
            venue='Test Venue',
            length_km=5.0,
            max_capacity=2
        )
    
    def test_run_list_view(self):
        """Test the run list view."""
        response = self.client.get(reverse('run_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Venue')
    
    def test_signup_requires_login(self):
        """Test that sign-up requires authentication."""
        response = self.client.get(reverse('run_signup', args=[self.run.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_signup_successful(self):
        """Test successful sign-up."""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('run_signup', args=[self.run.id]))
        
        self.assertEqual(response.status_code, 302)  # Redirect after sign-up
        self.assertTrue(SignUp.objects.filter(user=self.user, run=self.run).exists())
    
    def test_signup_prevented_when_full(self):
        """Test that sign-up is prevented when run is full."""
        # Fill the run
        user2 = User.objects.create_user(username='user2', password='pass')
        user3 = User.objects.create_user(username='user3', password='pass')
        SignUp.objects.create(user=user2, run=self.run)
        SignUp.objects.create(user=user3, run=self.run)
        
        # Try to sign up when full
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('run_signup', args=[self.run.id]))
        
        self.assertEqual(response.status_code, 302)
        self.assertFalse(SignUp.objects.filter(user=self.user, run=self.run).exists())
    
    def test_cancel_signup(self):
        """Test cancelling a sign-up."""
        SignUp.objects.create(user=self.user, run=self.run)
        
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('run_cancel', args=[self.run.id]))
        
        self.assertEqual(response.status_code, 302)
        self.assertFalse(SignUp.objects.filter(user=self.user, run=self.run).exists())
