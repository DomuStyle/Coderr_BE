# standard bib imports
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class Profile(models.Model):
    # choices for user type
    USER_TYPE_CHOICES = (
        ('business', 'Business'),
        ('customer', 'Customer'),
    )

    # one-to-one relationship with the User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    # first name, defaults to empty string
    first_name = models.CharField(max_length=50, default='', blank=True)
    # last name, defaults to empty string
    last_name = models.CharField(max_length=50, default='', blank=True)
    # profile picture, stored in 'profile_pictures/' directory
    file = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    # location, defaults to empty string
    location = models.CharField(max_length=100, default='', blank=True)
    # phone number with regex validation
    tel = models.CharField(
        max_length=20,
        default='',
        blank=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="phone number must be valid.")]
    )
    # description, defaults to empty string
    description = models.TextField(default='', blank=True)
    # working hours, relevant for business users, defaults to empty string
    working_hours = models.CharField(max_length=50, default='', blank=True)
    # user type (business or customer)
    type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    # creation timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User_Profile'
        verbose_name_plural = 'User_Profiles'

    def __str__(self):
        return f"{self.user.username}'s Profile"







