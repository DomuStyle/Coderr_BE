# standard bib imports
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

# third party imports
from rest_framework import serializers

# local imports
from user_auth_app.models import UserProfile


class RegistrationSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=True)
    repeated_password = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True, allow_blank=False)
    type = serializers.ChoiceField(choices=['customer', 'business'])
    
    class Meta:
        model = User # specifies that this serializer is based on the User model
        fields = ['id', 'username', 'email', 'password', 'repeated_password', 'type'] # defines the fields to be included
        extra_kwargs = {
            'password': {
                'write_only': True # ensures the password is not included in response data
            }
        }

    def create(self, validated_data):
        # extract password from validated data and remove it
        pw = validated_data.pop('password')
        # extract repeated password and remove it
        repeated_pw = validated_data.pop('repeated_password')
        # extract user type and remove it
        user_type = validated_data.pop('type')
        # extract username, apply title case, and remove it
        username = validated_data.pop('username').title()

        # check if passwords match
        if pw != repeated_pw:
            # raise validation error if passwords don't match
            raise serializers.ValidationError({'error': "Passwords don't match"})
        
        # check if email is already registered
        if User.objects.filter(email=validated_data['email']).exists():
            # raise validation error if email exists
            raise serializers.ValidationError({'error': "This email address is already taken"})
        
        # check if username is already taken
        if User.objects.filter(username=username).exists():
            # raise validation error if username exists
            raise serializers.ValidationError({'error': "This username is already taken"})
        
        # split username into parts for first and last name
        name_parts = username.strip().split(maxsplit=1)
        # set first name to first part
        first_name = name_parts[0]
        # set last name to second part if it exists, else empty string
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        # create new user instance with provided email, username, and names
        account = User(
            email=validated_data['email'],
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        
        # hash the password for security
        account.set_password(pw)
        # save the user to the database
        account.save()
        
        # return the newly created user instance
        return account
    

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