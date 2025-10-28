# MRC Runs Management System

A Django-based web application for managing running events, allowing users to view and sign up for runs while preventing over-capacity bookings. Administrators can manage runs and track attendance.

## Features

### User Features
- **Self-Registration**: Create your own account with email, name, and emergency contact information
- **Flexible Login**: Log in with either email address or username
- **View Available Runs**: Browse all scheduled runs with details including date, time, venue, meeting place, and distance
- **User Authentication**: Secure login/logout functionality with email-based authentication
- **User Profiles**: Extended profiles with emergency contact details for safety during runs
- **Sign Up for Runs**: Register for runs with a single click
- **Cancel Sign-Ups**: Remove yourself from runs you can no longer attend
- **Capacity Management**: Automatic prevention of sign-ups when runs are full
- **Visual Feedback**: Clear indicators for available spots and full runs
- **Real-time Updates**: See current capacity and your sign-up status

### Admin Features
- **Run Management**: Create, edit, and delete runs via Django admin interface
- **Attendance Tracking**: Mark which users attended each run
- **Inline Editing**: View and manage all sign-ups within the run detail page
- **Capacity Monitoring**: See sign-up counts and full/available status at a glance
- **Filtering & Search**: Filter runs by date, venue, and other criteria
- **User Management**: Full access to Django's user management system
- **User Profile Access**: View and manage user profiles including emergency contact information

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

Skip steps 2 and 3 if you wish to use your native python install for the requirements

1. **Clone the repository**:
   ```bash
   git clone https://github.com/blancmatter/mrc-runs.git
   cd mrc-runs
   ```
2. **Install venv (if not already installed)**:
   ```bash
   pip install venv
   ```

2. **Create & Activate Virtual Environment**:
   ```bash
   python -m venv venv
   (linux) source venv/bin/activate
   (powershell) .venv/bin/Activate.ps1
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Create a superuser** (for admin access):
   ```bash
   python manage.py createsuperuser
   ```

5. **Create sample data** (optional):
   ```bash
   python manage.py create_sample_data
   ```

6. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

7. **Access the application**:
   - User interface: http://127.0.0.1:8000/
   - Admin interface: http://127.0.0.1:8000/admin/

## Usage

### For Users

1. **Register**: Click "Register" in the header to create a new account
   - Provide your first name, last name, and email address (used for login)
   - Set a secure password
   - Add emergency contact information (required for safety)
   - Optionally add phone number and date of birth
2. **Login**: Click "Login" in the header and use your email address (or username) and password
3. **Browse Runs**: Visit the homepage to see all available runs
4. **Sign Up**: Click the "Sign Up" button next to any run with available spots
5. **Cancel**: Click "Cancel" to remove yourself from a run
6. **View Status**: See which runs you're signed up for (indicated by the "Cancel" button)

### For Administrators

1. **Access Admin Panel**: Navigate to `/admin/` and login with superuser credentials
2. **Manage Runs**:
   - Click "Runs" > "Add run" to create a new run
   - Click on a run to edit its details
   - View the list of signed-up users inline
3. **Take Attendance**:
   - Open any run in the admin panel
   - Check the "Attended" checkbox for users who showed up
   - Click "Save" to record attendance
4. **Monitor Capacity**: The admin list view shows sign-up counts and full status

## Project Structure

```
mrc-runs/
├── manage.py                      # Django management script
├── requirements.txt               # Python dependencies
├── mrc_runs/                     # Project settings
│   ├── settings.py               # Main settings file (includes custom auth backend)
│   ├── urls.py                   # URL routing
│   └── wsgi.py                   # WSGI configuration
└── runs/                          # Main application
    ├── models.py                 # Data models (Run, SignUp, UserProfile)
    ├── views.py                  # View functions
    ├── forms.py                  # Form definitions (RegistrationForm)
    ├── backends.py               # Custom authentication backend
    ├── admin.py                  # Admin configuration
    ├── urls.py                   # App URL routing
    ├── tests.py                  # Test suite (35 tests)
    ├── templates/                # HTML templates
    │   ├── runs/
    │   │   ├── base.html        # Base template
    │   │   └── run_list.html    # Run listing page
    │   └── registration/
    │       ├── login.html       # Login page
    │       └── register.html    # Registration page
    └── management/
        └── commands/
            └── create_sample_data.py  # Sample data generator
```

## Models

### Run
Represents a running event with the following fields:
- `date`: Date of the run
- `time`: Start time
- `meeting_place`: Where participants should gather
- `venue`: Location of the run
- `length_km`: Distance in kilometers
- `max_capacity`: Maximum number of participants

Methods:
- `is_full()`: Check if the run has reached capacity
- `get_signups_count()`: Get the number of sign-ups
- `available_spots()`: Calculate remaining capacity

### SignUp
Represents a user's registration for a run:
- `user`: Foreign key to Django User model
- `run`: Foreign key to Run model
- `signed_up_at`: Timestamp of sign-up
- `attended`: Boolean indicating attendance

Constraints:
- Unique together: (user, run) - prevents duplicate sign-ups
- Validation: Prevents sign-ups when run is full

### UserProfile
Extended user profile with additional information:
- `user`: One-to-one relationship with Django User model
- `phone_number`: Optional phone number
- `emergency_contact_name`: Required emergency contact name
- `emergency_contact_phone`: Required emergency contact phone number
- `date_of_birth`: Optional date of birth
- `created_at`: Timestamp when profile was created
- `updated_at`: Timestamp of last profile update

Features:
- Automatically created during user registration
- Accessible via `user.profile` relationship
- Managed through admin interface with inline editing

## Authentication

### Custom Authentication Backend
The application uses a custom authentication backend (`EmailOrUsernameBackend`) that provides flexible login options:

**Features:**
- Users can log in with either their email address OR username
- New users: Email becomes their username automatically during registration
- Legacy users: Can use their original username or their email address
- Backward compatible: No data migration required

**How it works:**
1. User enters email or username in the login form
2. Backend checks for matching username OR email in the database
3. Password is verified against the matched user account
4. Session is created upon successful authentication

**Security:**
- Protection against timing attacks
- Proper password hashing using Django's built-in system
- Handles edge cases like duplicate emails gracefully

## Testing

Run the test suite:
```bash
python manage.py test runs
```

The test suite includes:
- Model creation and validation tests (Run, SignUp, UserProfile)
- Capacity enforcement tests
- View functionality tests
- Sign-up and cancellation tests
- Full run behavior tests
- User registration and form validation tests
- Authentication backend tests (email/username login)
- Emergency contact validation tests

All 35 tests pass successfully.

## Security Notes

- The `SECRET_KEY` in `settings.py` should be changed for production use
- `DEBUG` should be set to `False` in production
- Add proper `ALLOWED_HOSTS` configuration for deployment
- The database (db.sqlite3) is excluded from version control

## Future Enhancements

Potential features for future development:
- Email notifications for sign-ups and reminders
- Running history and personal statistics tracking
- Run statistics and analytics dashboard
- Social features (comments, ratings, run photos)
- Waitlist system for full runs
- Past run archiving with filtering
- Social authentication (Google, Apple Sign-in)
- Mobile-responsive design improvements
- API endpoints for mobile apps
- HTMX integration for dynamic interactions

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please visit the GitHub repository:
https://github.com/blancmatter/mrc-runs
