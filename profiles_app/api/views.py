"""API views for managing profiles in Django REST Framework, including detail retrieval, updates, and lists by type."""

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from profiles_app.models import Profile
from .serializers import ProfileSerializer, BusinessProfileSerializer, CustomerProfileSerializer


class ProfileDetailView(APIView):
    """View for retrieving and updating a specific profile."""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, pk):
        """Retrieve a profile by user ID."""
        try:
            profile = Profile.objects.get(user__id=pk)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk):
        """Update a profile, restricted to the owner."""
        # Ensure only the profile owner can perform updates.
        if request.user.id != pk:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        try:
            profile = Profile.objects.get(user__id=pk)
            serializer = ProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)


class BusinessProfileListView(ListAPIView):
    """View for listing business profiles."""
    permission_classes = [IsAuthenticated]
    serializer_class = BusinessProfileSerializer
    queryset = Profile.objects.filter(type='business').select_related('user')
    pagination_class = None


class CustomerProfileListView(ListAPIView):
    """View for listing customer profiles."""
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerProfileSerializer
    queryset = Profile.objects.filter(type='customer').select_related('user')
    pagination_class = None