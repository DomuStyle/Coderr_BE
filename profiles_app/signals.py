"""Signal handlers for the profiles_app to automatically create profiles for new users."""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a Profile instance with default values when a new User is created."""
    if created:
        Profile.objects.create(user=instance)