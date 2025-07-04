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
    # define username field for authentication input
    username = serializers.CharField(required=True, allow_blank=False)
    
    # define password field, write-only with hidden input for security
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,  # preserve whitespace in password
        write_only=True  # ensure password is not included in response
    )

    def validate(self, attrs):
        # extract username from validated attributes
        username = attrs.get('username')
        # extract password from validated attributes
        password = attrs.get('password')

        # check if both username and password are provided
        if username and password:
            # authenticate user with provided username and password
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            # check if authentication failed
            if not user:
                # raise validation error for invalid credentials
                raise serializers.ValidationError(
                    {'non_field_errors': 'Invalid username or password.'},
                    code='authentication'
                )
        else:
            # raise validation error if either field is missing
            raise serializers.ValidationError(
                {'non_field_errors': 'Both username and password are required.'},
                code='required'
            )

        # store authenticated user in attributes for view access
        attrs['user'] = user
        # return validated attributes
        return attrs