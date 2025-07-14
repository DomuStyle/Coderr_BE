from django.urls import path
from .views import OfferListView, OfferDetailView, OfferSpecificView

urlpatterns = [
    path('offers/', OfferListView.as_view(), name='offer-list'),
    path('offers/<int:pk>/', OfferSpecificView.as_view(), name='offer-detail'),
    path('offerdetails/<int:id>/', OfferDetailView.as_view(), name='offerdetail-detail'),
]