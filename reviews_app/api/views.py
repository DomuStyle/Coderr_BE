from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from reviews_app.models import Review
from rest_framework.response import Response
from rest_framework import status
from .serializers import ReviewSerializer, ReviewCreateSerializer
from django.db.models import Q
from profiles_app.models import Profile


class ReviewListView(ListAPIView):
    # require authentication
    permission_classes = [IsAuthenticated]
    # serializer for list
    serializer_class = ReviewSerializer
    # disable pagination to match spec (simple list)
    pagination_class = None

    def get_queryset(self):
        queryset = Review.objects.select_related('business_user', 'reviewer')  # Add this for optimization
        # apply filters
        business_user_id = self.request.query_params.get('business_user_id')
        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)
        reviewer_id = self.request.query_params.get('reviewer_id')
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)
        # apply ordering
        ordering = self.request.query_params.get('ordering')
        if ordering in ['updated_at', 'rating']:
            queryset = queryset.order_by(ordering)
        return queryset.order_by('-updated_at')  # default order
    
    def post(self, request):
        # check if user is customer
        if not Profile.objects.filter(user=request.user, type='customer').exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
        # create review
        serializer = ReviewCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            review = serializer.save()
            return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)