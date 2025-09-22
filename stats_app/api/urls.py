"""URL configuration for the stats_app, defining API endpoints for statistical data views."""

from django.urls import path
from .views import BaseInfoView


# Define URL patterns for statistical data API endpoints.
urlpatterns = [
    path('base-info/', BaseInfoView.as_view(), name='base-info'),
]