from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from profiles_app.models import Profile
from .serializers import ProfileSerializer, BusinessProfileSerializer, CustomerProfileSerializer


class ProfileDetailView(APIView):
    # require authentication
    permission_classes = [IsAuthenticated]
    # support JSON and multipart for PATCH with file uploads
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get(self, request, pk):
        try:
            # fetch profile by user ID
            profile = Profile.objects.get(user__id=pk)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk):
        # ensure user can only edit their own profile
        if request.user.id != pk:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        try:
            # fetch and update profile
            profile = Profile.objects.get(user__id=pk)
            serializer = ProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)


class BusinessProfileListView(ListAPIView):
    # require authentication
    permission_classes = [IsAuthenticated]
    serializer_class = BusinessProfileSerializer
    queryset = Profile.objects.filter(type='business').select_related('user')
    pagination_class = None


class CustomerProfileListView(ListAPIView):
    # require authentication
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerProfileSerializer
    queryset = Profile.objects.filter(type='customer').select_related('user')
    pagination_class = None