# # standard bib imports
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    USER_TYPE_CHOICES = (
        ('business', 'Business'),
        ('customer', 'Customer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50, default='')
    last_name = models.CharField(max_length=50, default='')
    location = models.CharField(max_length=100, default='')
    tel = models.CharField(max_length=20, default='')
    description = models.TextField(default='')
    working_hours = models.CharField(max_length=50, default='')
    type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    file = models.ImageField(upload_to='', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"







