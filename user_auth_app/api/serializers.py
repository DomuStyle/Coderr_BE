# standard bib imports
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

# third party imports
from rest_framework import serializers

# local imports
# from user_auth_app.models import UserProfile


class RegistrationSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=True)
    repeated_password = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True, allow_blank=False)
    type = serializers.ChoiceField(choices=['customer', 'business'], write_only=True)
    
    class Meta:
        model = User # specifies that this serializer is based on the User model
        fields = ['id', 'username', 'email', 'password', 'repeated_password', 'type'] # defines the fields to be included
        extra_kwargs = {
            'password': {
                'write_only': True # ensures the password is not included in response data
            },
            'id': {
                'read_only': True
            }
        }

    def validate(self, data):
        # extract password and repeated_password for validation
        password = data.get('password')
        repeated_password = data.get('repeated_password')
        # check if passwords match
        if password != repeated_password:
            # raise validation error if passwords don't match
            raise serializers.ValidationError({'repeated_password': "Passwords must match"})
        # return validated data
        return data
    
    def validate_email(self, value):
        # normalize email to lowercase to ensure consistency
        value = value.lower()
        # check if email is already registered
        if User.objects.filter(email=value).exists():
            # raise validation error if email exists
            raise serializers.ValidationError("This email address is already taken")
        # return validated email
        return value
    
    def validate_username(self, value):
        # check if username is already taken
        if User.objects.filter(username__iexact=value).exists():
            # raise validation error if username exists
            raise serializers.ValidationError("This username is already taken")
        # return normalized username
        return value

    def create(self, validated_data):
        # extract and remove type from validated data
        user_type = validated_data.pop('type')
        # remove repeated_password as it's not needed for user creation
        validated_data.pop('repeated_password')
        # normalize email to lowercase
        validated_data['email'] = validated_data['email'].lower()
        # create user with validated data
        user = User.objects.create_user(**validated_data)
        
        # return the created user
        return user
    

class CustomAuthTokenSerializer(serializers.Serializer):
    # defines an email field to be used for authentication
    email = serializers.EmailField()
    
    # defines a password field with styling to hide input characters
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False  # ensures that spaces in the password are not automatically removed
    )

    def validate(self, attrs):
        # retrieves email and password from the validated attributes
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            try:
                # tries to find a user with the given email address
                user_obj = User.objects.get(email=email)
            except User.DoesNotExist:
                # raises a validation error if no user with the provided email exists
                raise serializers.ValidationError("Invalid email or password.")

            # attempts to authenticate the user using the retrieved username and password
            user = authenticate(username=user_obj.username, password=password)

            if not user:
                # raises a validation error if authentication fails
                raise serializers.ValidationError("Invalid email or password.")
        else:
            # raises a validation error if either email or password is missing
            raise serializers.ValidationError("Both email and password are required.")

        # adds the authenticated user to the attributes and returns them
        attrs['user'] = user
        return attrs