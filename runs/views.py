from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Run, SignUp
from .forms import RegistrationForm


def run_list(request):
    """View to list all runs."""
    runs = Run.objects.all()
    user_signups = []
    
    if request.user.is_authenticated:
        user_signups = SignUp.objects.filter(user=request.user).values_list('run_id', flat=True)
    
    return render(request, 'runs/run_list.html', {
        'runs': runs,
        'user_signups': list(user_signups),
    })


@login_required
def run_signup(request, run_id):
    """View to sign up for a run."""
    run = get_object_or_404(Run, pk=run_id)
    
    # Check if user is already signed up
    if SignUp.objects.filter(user=request.user, run=run).exists():
        messages.warning(request, 'You are already signed up for this run.')
        return redirect('run_list')
    
    # Check if run is full
    if run.is_full():
        messages.error(request, 'This run is full. No more sign-ups allowed.')
        return redirect('run_list')
    
    try:
        SignUp.objects.create(user=request.user, run=run)
        messages.success(request, f'Successfully signed up for {run.venue} on {run.date}!')
    except ValidationError as e:
        messages.error(request, str(e))
    
    return redirect('run_list')


@login_required
def run_cancel(request, run_id):
    """View to cancel a sign-up for a run."""
    run = get_object_or_404(Run, pk=run_id)

    try:
        signup = SignUp.objects.get(user=request.user, run=run)
        signup.delete()
        messages.success(request, f'Successfully cancelled your sign-up for {run.venue} on {run.date}.')
    except SignUp.DoesNotExist:
        messages.warning(request, 'You were not signed up for this run.')

    return redirect('run_list')


def register(request):
    """View for user registration."""
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return redirect('run_list')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Specify backend for auto-login when multiple backends are configured
            login(request, user, backend='runs.backends.EmailOrUsernameBackend')
            messages.success(request, f'Welcome, {user.username}! Your account has been created successfully.')
            return redirect('run_list')
    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})
