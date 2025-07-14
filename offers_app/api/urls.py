from django.urls import path
from .views import OfferListView, OfferDetailView

urlpatterns = [
    path('offers/', OfferListView.as_view(), name='offer-list'),
    path('offerdetails/<int:id>/', OfferDetailView.as_view(), name='offerdetail-detail'),
]