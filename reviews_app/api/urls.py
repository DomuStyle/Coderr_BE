from django.urls import path
from .views import ReviewListView, ReviewSpecificView

urlpatterns = [
    path('reviews/', ReviewListView.as_view(), name='review-list'),
    path('reviews/<int:pk>/', ReviewSpecificView.as_view(), name='review-detail'),
]