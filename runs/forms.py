from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile


class RegistrationForm(UserCreationForm):
    """Extended registration form with emergency contact information.

    Uses email address as the username for simpler login.
    """
    first_name = forms.CharField(
        max_length=150,
        required=True,
        help_text="Required. Your first name.",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., John'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        help_text="Required. Your last name.",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Smith'})
    )
    email = forms.EmailField(
        required=True,
        help_text="Required. This will be your username for login.",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g., john.smith@example.com'})
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        help_text="Optional. Your phone number.",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 07123 456789'})
    )
    emergency_contact_name = forms.CharField(
        max_length=100,
        required=True,
        help_text="Required. Name of your emergency contact.",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Jane Smith'})
    )
    emergency_contact_phone = forms.CharField(
        max_length=20,
        required=True,
        help_text="Required. Phone number of your emergency contact.",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 07987 654321'})
    )
    date_of_birth = forms.DateField(
        required=False,
        help_text="Optional. Your date of birth.",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to password fields
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        # Update password help text with all validation requirements
        self.fields['password1'].help_text = (
            'Your password must contain at least 8 characters, '
            'cannot be too similar to your other personal information, '
            'cannot be a commonly used password, and cannot be entirely numeric.'
        )

    def clean_email(self):
        """Validate that the email is unique (used as username)."""
        email = self.cleaned_data.get('email')
        if email:
            # Check both email and username fields since email becomes username
            if User.objects.filter(email=email).exists():
                raise ValidationError('A user with this email address already exists.')
            if User.objects.filter(username=email).exists():
                raise ValidationError('A user with this email address already exists.')
        return email

    def save(self, commit=True):
        """Save the user and create associated UserProfile.

        Sets username to email address for simpler login.
        """
        user = super().save(commit=False)
        # Use email as username
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data.get('phone_number', ''),
                emergency_contact_name=self.cleaned_data['emergency_contact_name'],
                emergency_contact_phone=self.cleaned_data['emergency_contact_phone'],
                date_of_birth=self.cleaned_data.get('date_of_birth')
            )
        return user
