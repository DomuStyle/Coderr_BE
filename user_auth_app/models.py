"""Django model for extending user data in the user_auth_app."""

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """Extends the Django User model with additional profile information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        """Return the username for string representation."""
        return self.user.username