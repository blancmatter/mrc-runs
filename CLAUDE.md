# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MRC Runs Management System is a Django-based web application for managing running events. Users can view and sign up for runs with capacity management, while administrators manage runs and track attendance. The application includes responsive mobile support with PWA capabilities.

## Development Commands

### Initial Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or .venv/bin/Activate.ps1  # PowerShell

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Create sample data for testing
python manage.py create_sample_data
```

### Running the Application
```bash
# Start development server
python manage.py runserver

# Access points:
# - User interface: http://127.0.0.1:8000/
# - Admin interface: http://127.0.0.1:8000/admin/
```

### Testing
```bash
# Run all tests for the runs app
python manage.py test runs

# Run tests with verbose output
python manage.py test runs --verbosity=2

# Run specific test class or method
python manage.py test runs.tests.RunModelTest
python manage.py test runs.tests.RunModelTest.test_is_full
```

### Database Management
```bash
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Access Django shell for data exploration
python manage.py shell
```

## Architecture

### Django Project Structure
- **mrc_runs/**: Main project configuration directory
  - `settings.py`: Project settings (Django 4.2, SQLite database)
  - `urls.py`: Root URL configuration including admin, runs app, and auth URLs

- **runs/**: Main application containing all run management logic
  - Core Django app handling run events, sign-ups, and attendance tracking

### Core Models (runs/models.py)

**Run Model**: Represents a running event
- Fields: `date`, `time`, `meeting_place`, `venue`, `length_km`, `max_capacity`
- Key methods:
  - `get_signups_count()`: Returns count of signed-up users
  - `is_full()`: Checks if capacity is reached
  - `available_spots()`: Calculates remaining capacity
- Default ordering: `['date', 'time']`

**SignUp Model**: Tracks user registrations and attendance
- Fields: `user` (FK to User), `run` (FK to Run), `signed_up_at`, `attended`
- Constraint: `unique_together = ['user', 'run']` prevents duplicate sign-ups
- Validation: `clean()` method prevents sign-ups when run is full
- Overrides `save()` to enforce validation

### Views Architecture (runs/views.py)

**run_list**: Public view listing all runs
- Shows all runs with capacity information
- For authenticated users, includes list of their sign-ups
- Passes `runs` and `user_signups` to template

**run_signup**: Login-required view for sign-ups
- Validates user not already signed up
- Validates run not full
- Creates SignUp record with proper error handling
- Uses Django messages framework for feedback

**run_cancel**: Login-required view for cancellations
- Finds and deletes user's SignUp record
- Handles non-existent sign-ups gracefully
- Uses Django messages framework for feedback

### URL Structure (runs/urls.py)
- `/`: Run list view
- `/signup/<run_id>/`: Sign up for a run
- `/cancel/<run_id>/`: Cancel sign-up
- `/accounts/`: Django auth URLs (login, logout, etc.)
- `/admin/`: Django admin interface

### Admin Interface (runs/admin.py)

**RunAdmin**: Enhanced admin for Run model
- List display: venue, date, time, length, capacity, sign-up count, full status
- Filters: date, venue
- Search: venue, meeting_place
- Inline editing: SignUpInline for managing participants within run detail

**SignUpAdmin**: Admin for SignUp model
- List display: user, run, sign-up time, attendance status
- Filters: attended status, run date
- Search: username, email, venue

### Template System

**Responsive Templates**: The app uses Bootstrap 5 for responsive design
- `base.html`: Main responsive base template with mobile-first approach
- `run_list.html`: Responsive run listing (desktop table view, mobile card view)
- `*_original.html`: Original desktop-only templates preserved for reference
- `*_responsive.html`: Development versions of responsive templates

Templates use Django's template inheritance and include mobile optimizations:
- Touch-friendly button sizes (44px minimum)
- Adaptive layouts based on screen size
- Bootstrap 5 grid system

### PWA Implementation

**Static Files** (runs/static/):
- `manifest.json`: Web app manifest for installable mobile experience
- `sw.js`: Service worker for offline capabilities and caching
- `icons/`: App icons for different platforms/sizes

### Management Commands

**create_sample_data**: Custom command for testing
- Creates 5 test users (user1-user5, password: password123)
- Creates 3 sample runs at different venues
- Usage: `python manage.py create_sample_data`

## Key Development Patterns

### Capacity Management
The application enforces capacity limits at multiple levels:
1. Model validation in `SignUp.clean()` method
2. View-level checks before creating sign-ups
3. Admin interface displays capacity status

Race conditions are partially mitigated by validation in the model's save method, but for production use with high concurrency, consider using database-level constraints or transactions.

### User Authentication Flow
- Django's built-in auth system via `django.contrib.auth`
- Login required for sign-up/cancel actions using `@login_required` decorator
- Auth URLs mounted at `/accounts/` (includes login, logout, password reset)
- Templates check `request.user.is_authenticated` for conditional rendering

### Message Framework Usage
All user actions provide feedback through Django's messages framework:
- Success messages: Sign-up/cancel confirmations
- Warning messages: Already signed up, not signed up
- Error messages: Full capacity, validation errors

### Testing Coverage
The test suite (runs/tests.py) covers:
- Model creation and validation
- Capacity enforcement
- View functionality (sign-up, cancel)
- Full run behavior
- Edge cases and error conditions

## Database Schema Notes

- Using SQLite for development (`db.sqlite3`)
- File is git-ignored
- For production, configure PostgreSQL or MySQL in settings.py
- All models use Django's default `BigAutoField` for primary keys

## Mobile & PWA Considerations

The application is designed mobile-first:
- Responsive templates serve both desktop and mobile
- PWA features allow installation on mobile devices
- Service worker provides offline functionality
- Manifest enables "Add to Home Screen" on mobile browsers

When testing mobile features:
- Use Chrome DevTools device emulation
- Test on actual devices via network IP address
- Verify PWA installation flow works

## Production Deployment Notes

Before deploying to production:
1. Change `SECRET_KEY` in settings.py
2. Set `DEBUG = False`
3. Configure `ALLOWED_HOSTS`
4. Set up proper database (PostgreSQL recommended)
5. Configure static files collection: `python manage.py collectstatic`
6. Use proper WSGI server (Gunicorn, uWSGI)
7. Set up proper authentication backends if needed
