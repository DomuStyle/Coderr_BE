"""URL configuration for the profiles_app, defining API endpoints for profile-related views."""

from django.urls import path
from .views import ProfileDetailView, BusinessProfileListView, CustomerProfileListView


# Define URL patterns for profile-related API endpoints.
urlpatterns = [
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('profiles/business/', BusinessProfileListView.as_view(), name='business-profiles-list'),
    path('profiles/customer/', CustomerProfileListView.as_view(), name='customer-profiles-list'),
]