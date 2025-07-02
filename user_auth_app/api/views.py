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

class RegistrationView(APIView):
    permission_classes = [AllowAny] # gives permission to use this view at any time

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        data = {}

        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account) # get or create is used to make sure to get a token if it alrdy exists
            data = {
            'token': token.key,
            'fullname': saved_account.username,
            'email': saved_account.email,
            'user_id': saved_account.id
            }

        else:
            data=serializer.errors

        return Response(data)
    

class CustomLoginView(ObtainAuthToken):
    # allows access to all users without requiring authentication
    permission_classes = [AllowAny]
    
    # sets the serializer class to handle user authentication
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        # initializes serializer with incoming request data and request context
        serializer = self.serializer_class(data=request.data, context={'request': request})
        data = {}

        if serializer.is_valid():
            # retrieves authenticated user from validated data
            user = serializer.validated_data['user']
            
            # creates or retrieves an authentication token for the user
            token, created = Token.objects.get_or_create(user=user)
            
            # constructs response data with user details and token key
            data = {
                'token': token.key,
                'fullname': user.username,
                'email': user.email,
                "user_id": user.id
            }
            return Response(data, status=status.HTTP_200_OK)  # explicitly set 200 for successful login
        else:
            data = serializer.errors
            # returns response containing user authentication data
            return Response(data, status=status.HTTP_400_BAD_REQUEST)  # return 400 for validation errors