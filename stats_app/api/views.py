"""API views for statistical data in the stats_app using Django REST Framework."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from reviews_app.models import Review
from profiles_app.models import Profile
from offers_app.models import Offer
from django.db.models import Avg


class BaseInfoView(APIView):
    """View for retrieving aggregated statistics like review counts and ratings, accessible publicly."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        """Retrieve counts of reviews, business profiles, and offers, and the average review rating."""
        try:
            review_count = Review.objects.count()
            average_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0.0
            average_rating = round(average_rating, 1)
            business_profile_count = Profile.objects.filter(type='business').count()
            offer_count = Offer.objects.count()
            data = {
                'review_count': review_count,
                'average_rating': average_rating,
                'business_profile_count': business_profile_count,
                'offer_count': offer_count
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)