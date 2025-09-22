"""API views for managing reviews in Django REST Framework, including listing, creation, updates, and deletion."""

from django.db.models import Q
from rest_framework.generics import ListAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from reviews_app.models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer, ReviewUpdateSerializer
from profiles_app.models import Profile


class ReviewListView(ListAPIView):
    """View for listing and creating reviews, with no pagination for simple lists."""
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer
    pagination_class = None

    def get_queryset(self):
        """Filter and order reviews based on query parameters."""
        queryset = Review.objects.select_related('business_user', 'reviewer')
        business_user_id = self.request.query_params.get('business_user_id')
        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)
        reviewer_id = self.request.query_params.get('reviewer_id')
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)
        ordering = self.request.query_params.get('ordering')
        if ordering in ['updated_at', 'rating']:
            queryset = queryset.order_by(ordering)
        return queryset.order_by('-updated_at')

    def post(self, request):
        """Create a new review, restricted to customer users."""
        # Restrict review creation to customer users.
        if not Profile.objects.filter(user=request.user, type='customer').exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = ReviewCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            review = serializer.save()
            return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewSpecificView(DestroyAPIView, UpdateAPIView):
    """View for updating or deleting a specific review."""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    queryset = Review.objects.all()
    lookup_field = 'pk'

    def get_serializer_class(self):
        """Use update serializer for PATCH requests."""
        if self.request.method == 'PATCH':
            return ReviewUpdateSerializer
        return super().get_serializer_class()

    def patch(self, request, *args, **kwargs):
        """Perform partial update, restricted to the review's owner."""
        review = self.get_object()
        if review.reviewer != request.user:
            return Response({'error': 'You are not the owner of this review.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ReviewSerializer(review).data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """Delete the review, restricted to the review's owner."""
        review = self.get_object()
        if review.reviewer != request.user:
            return Response({'error': 'You are not the owner of this review.'}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(review)
        return Response(status=status.HTTP_204_NO_CONTENT)