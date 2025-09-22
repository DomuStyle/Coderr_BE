"""URL configuration for the reviews_app, defining API endpoints for review-related views."""

from django.urls import path
from .views import ReviewListView, ReviewSpecificView


# Define URL patterns for review-related API endpoints.
urlpatterns = [
    path('reviews/', ReviewListView.as_view(), name='review-list'),
    path('reviews/<int:pk>/', ReviewSpecificView.as_view(), name='review-detail'),
]