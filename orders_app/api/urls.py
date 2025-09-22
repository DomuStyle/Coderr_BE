"""URL configuration for the orders_app, defining API endpoints for order-related views."""

from django.urls import path
from .views import OrderListView, OrderSpecificView, OrderCountView, CompletedOrderCountView


# Define URL patterns for order-related API endpoints.
urlpatterns = [
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderSpecificView.as_view(), name='order-detail'),
    path('order-count/<int:business_user_id>/', OrderCountView.as_view(), name='order-count'),
    path('completed-order-count/<int:business_user_id>/', CompletedOrderCountView.as_view(), name='completed-order-count'),
]