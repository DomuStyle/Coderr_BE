from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from profiles_app.models import Profile
from .serializers import ProfileSerializer, BusinessProfileSerializer


class ProfileDetailView(APIView):
    # require authentication
    permission_classes = [IsAuthenticated]

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
        

# class BusinessProfileListView(APIView):
#     # require authentication
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         # fetch all business profiles
#         profiles = Profile.objects.filter(type='business')
#         serializer = ProfileSerializer(profiles, many=True)
#         # exclude email and created_at from response
#         data = [
#             {key: item[key] for key in item if key not in ['email', 'created_at']}
#             for item in serializer.data
#         ]
#         return Response(data, status=status.HTTP_200_OK)

class BusinessProfileListView(ListAPIView):
    # require authentication
    permission_classes = [IsAuthenticated]
    serializer_class = BusinessProfileSerializer
    queryset = Profile.objects.filter(type='business')