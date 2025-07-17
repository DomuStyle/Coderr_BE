# standard bib imports
from rest_framework import status

# third party imports
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

# local imports
from .serializers import RegistrationSerializer, CustomAuthTokenSerializer
from profiles_app.models import Profile

class RegistrationView(APIView):

    permission_classes = [AllowAny] # gives permission to use this view at any time

    def post(self, request):
        
        serializer = RegistrationSerializer(data=request.data)
        data = {}

        if serializer.is_valid():
            user_type = serializer.validated_data.pop('type')  # pop type for Profile
            user = serializer.save()
            # create Profile with type (fixes "Profile not found" by auto-creating on registration)
            Profile.objects.create(user=user, type=user_type)
            token, created = Token.objects.get_or_create(user=user) # get or create is used to make sure to get a token if it alrdy exists
            data = {
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id
            }

        # return success response with 201 status
            return Response(data, status=status.HTTP_201_CREATED)
        # return error response with 400 status if data is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CustomLoginView(ObtainAuthToken):
    # allows access to all users without requiring authentication
    permission_classes = [AllowAny]
    
    # sets the serializer class to handle user authentication
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        # initializes serializer with incoming request data and request context
        serializer = self.serializer_class(data=request.data, context={'request': request})

        if serializer.is_valid(raise_exception=False):
            # retrieves authenticated user from validated data
            user = serializer.validated_data['user']
            
            # creates or retrieves an authentication token for the user
            token, created = Token.objects.get_or_create(user=user)
            
            # constructs response data with user details and token key
            data = {
                'token': token.key,
                'username': user.username,
                'email': user.email,
                "user_id": user.id
            }
            # return success response with 200 status
            return Response(data, status=status.HTTP_200_OK)
        # return error response with 400 status for invalid data
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)