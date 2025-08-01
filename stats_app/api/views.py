from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from reviews_app.models import Review
from profiles_app.models import Profile
from offers_app.models import Offer
from django.db.models import Avg

class BaseInfoView(APIView):
    permission_classes = []  # No permissions, public per docu

    def get(self, request):
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