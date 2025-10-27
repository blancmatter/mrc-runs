from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile


class RegistrationForm(UserCreationForm):
    """Extended registration form with emergency contact information."""
    email = forms.EmailField(
        required=True,
        help_text="Required. Enter a valid email address.",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
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
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., John Smith'})
    )
    emergency_contact_phone = forms.CharField(
        max_length=20,
        required=True,
        help_text="Required. Phone number of your emergency contact.",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 07123 456789'})
    )
    date_of_birth = forms.DateField(
        required=False,
        help_text="Optional. Your date of birth (YYYY-MM-DD).",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to password fields
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

    def clean_email(self):
        """Validate that the email is unique."""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email address already exists.')
        return email

    def clean_username(self):
        """Validate username with a more helpful error message."""
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise ValidationError('This username is already taken. Please choose a different one.')
        return username

    def save(self, commit=True):
        """Save the user and create associated UserProfile."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
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
