"""API views for user registration and authentication in the user_auth_app using Django REST Framework."""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from .serializers import RegistrationSerializer, CustomAuthTokenSerializer
from profiles_app.models import Profile


class RegistrationView(APIView):
    """View for registering new users and creating their profiles."""
    permission_classes = [AllowAny]

    def post(self, request):
        """Create a new user account and profile, returning an authentication token."""
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user_type = serializer.validated_data['type']
            user = serializer.save()
            profile = user.profile
            profile.type = user_type
            profile.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomLoginView(ObtainAuthToken):
    """View for authenticating users and issuing tokens."""
    permission_classes = [AllowAny]
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        """Authenticate a user and return an authentication token."""
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=False):
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id
            }
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)