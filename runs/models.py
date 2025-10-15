from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Run(models.Model):
    """Model representing a running event."""
    date = models.DateField()
    time = models.TimeField()
    meeting_place = models.CharField(max_length=200)
    venue = models.CharField(max_length=200)
    length_km = models.DecimalField(max_digits=5, decimal_places=2, help_text="Length in kilometers")
    max_capacity = models.PositiveIntegerField(help_text="Maximum number of participants")
    
    class Meta:
        ordering = ['date', 'time']
    
    def __str__(self):
        return f"{self.venue} - {self.date} at {self.time} ({self.length_km}km)"
    
    def get_signups_count(self):
        """Return the number of users signed up for this run."""
        return self.signup_set.count()
    
    def is_full(self):
        """Check if the run has reached maximum capacity."""
        return self.get_signups_count() >= self.max_capacity
    
    def available_spots(self):
        """Return the number of available spots."""
        return max(0, self.max_capacity - self.get_signups_count())


class SignUp(models.Model):
    """Model representing a user's sign-up to a run with attendance tracking."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    signed_up_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False, help_text="Mark if the user attended the run")
    
    class Meta:
        unique_together = ['user', 'run']
        ordering = ['signed_up_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.run}"
    
    def clean(self):
        """Validate that the run is not full before allowing sign-up."""
        if self.pk is None:  # Only check on creation
            if self.run.is_full():
                raise ValidationError('This run is full. No more sign-ups allowed.')
    
    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.clean()
        super().save(*args, **kwargs)
