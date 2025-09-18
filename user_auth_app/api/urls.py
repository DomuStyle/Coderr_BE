"""URL configuration for the user_auth_app, defining API endpoints for user authentication views."""

from django.urls import path
from .views import RegistrationView, CustomLoginView

# Define URL patterns for user authentication API endpoints.
urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', CustomLoginView.as_view(), name='login')
]