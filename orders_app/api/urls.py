from django.urls import path
from .views import OrderListView, OrderSpecificView


urlpatterns = [
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderSpecificView.as_view(), name='order-detail'), 
]