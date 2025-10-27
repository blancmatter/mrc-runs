from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from datetime import date, time
from .models import Run, SignUp, UserProfile
from .forms import RegistrationForm


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


class UserProfileModelTest(TestCase):
    """Test cases for UserProfile model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            phone_number='07123456789',
            emergency_contact_name='John Doe',
            emergency_contact_phone='07987654321',
            date_of_birth=date(1990, 1, 1)
        )

    def test_profile_creation(self):
        """Test that a user profile can be created."""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.emergency_contact_name, 'John Doe')
        self.assertEqual(self.profile.emergency_contact_phone, '07987654321')

    def test_profile_str_representation(self):
        """Test the string representation of a profile."""
        expected = f"{self.user.username}'s Profile"
        self.assertEqual(str(self.profile), expected)

    def test_profile_relationship(self):
        """Test the one-to-one relationship with User."""
        self.assertEqual(self.user.profile, self.profile)


class RegistrationFormTest(TestCase):
    """Test cases for RegistrationForm."""

    def test_valid_registration_form(self):
        """Test registration form with valid data."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'emergency_contact_name': 'Jane Doe',
            'emergency_contact_phone': '07123456789',
            'phone_number': '07987654321',
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_registration_form_missing_required_fields(self):
        """Test registration form with missing required fields."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            # Missing emergency contact fields
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('emergency_contact_name', form.errors)
        self.assertIn('emergency_contact_phone', form.errors)

    def test_registration_form_password_mismatch(self):
        """Test registration form with mismatched passwords."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'DifferentPass456!',
            'emergency_contact_name': 'Jane Doe',
            'emergency_contact_phone': '07123456789',
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_registration_form_duplicate_username(self):
        """Test registration form with existing username."""
        User.objects.create_user(username='existinguser', password='pass')
        form_data = {
            'username': 'existinguser',
            'email': 'new@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'emergency_contact_name': 'Jane Doe',
            'emergency_contact_phone': '07123456789',
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_registration_form_duplicate_email(self):
        """Test registration form with existing email."""
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='pass'
        )
        form_data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'emergency_contact_name': 'Jane Doe',
            'emergency_contact_phone': '07123456789',
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class RegistrationViewTest(TestCase):
    """Test cases for registration view."""

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')

    def test_registration_page_loads(self):
        """Test that the registration page loads successfully."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
        self.assertIsInstance(response.context['form'], RegistrationForm)

    def test_successful_registration(self):
        """Test successful user registration."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'emergency_contact_name': 'Jane Doe',
            'emergency_contact_phone': '07123456789',
            'phone_number': '07987654321',
        }
        response = self.client.post(self.register_url, data=form_data)

        # Check redirect after successful registration
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('run_list'))

        # Check user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')

        # Check UserProfile was created
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.emergency_contact_name, 'Jane Doe')
        self.assertEqual(user.profile.emergency_contact_phone, '07123456789')
        self.assertEqual(user.profile.phone_number, '07987654321')

    def test_registration_with_optional_fields_empty(self):
        """Test registration with optional fields left empty."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'emergency_contact_name': 'Jane Doe',
            'emergency_contact_phone': '07123456789',
            # phone_number and date_of_birth are optional
        }
        response = self.client.post(self.register_url, data=form_data)

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='newuser')
        self.assertEqual(user.profile.phone_number, '')
        self.assertIsNone(user.profile.date_of_birth)

    def test_registration_auto_login(self):
        """Test that user is automatically logged in after registration."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'emergency_contact_name': 'Jane Doe',
            'emergency_contact_phone': '07123456789',
        }
        response = self.client.post(self.register_url, data=form_data, follow=True)

        # Check user is authenticated
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.context['user'].username, 'newuser')

    def test_registration_with_invalid_data(self):
        """Test registration with invalid data."""
        form_data = {
            'username': 'newuser',
            'email': 'invalid-email',  # Invalid email
            'password1': 'ComplexPass123!',
            'password2': 'DifferentPass!',  # Mismatched password
            'emergency_contact_name': 'Jane Doe',
            'emergency_contact_phone': '07123456789',
        }
        response = self.client.post(self.register_url, data=form_data)

        # Should not redirect, stays on registration page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

        # User should not be created
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_authenticated_user_redirect(self):
        """Test that authenticated users are redirected from registration page."""
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('run_list'))
