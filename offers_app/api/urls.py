"""URL configuration for the offers_app, defining API endpoints for offer-related views."""

from django.urls import path
from .views import OfferListView, OfferDetailView, OfferSpecificView

# Define URL patterns for offer-related API endpoints.
urlpatterns = [
    path('offers/', OfferListView.as_view(), name='offer-list'),
    path('offers/<int:pk>/', OfferSpecificView.as_view(), name='offer-detail'),
    path('offerdetails/<int:id>/', OfferDetailView.as_view(), name='offerdetail-detail'),
]