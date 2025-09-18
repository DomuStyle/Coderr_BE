"""Serializers for the user_auth_app to handle user registration and authentication in Django REST Framework."""

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers

class RegistrationSerializer(serializers.ModelSerializer):
    """Serializes data for creating new user accounts with profile type."""
    email = serializers.EmailField(required=True)
    repeated_password = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True, allow_blank=False)
    type = serializers.ChoiceField(choices=['customer', 'business'], write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True}
        }

    def validate(self, data):
        """Ensure passwords match during registration."""
        password = data.get('password')
        repeated_password = data.get('repeated_password')
        if password != repeated_password:
            raise serializers.ValidationError({'repeated_password': 'Passwords must match'})
        return data

    def validate_email(self, value):
        """Ensure the email is unique and normalized to lowercase."""
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email address is already taken')
        return value

    def validate_username(self, value):
        """Ensure the username is unique."""
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('This username is already taken')
        return value

    def create(self, validated_data):
        """Create a new user, using a default type if not provided."""
        validated_data.pop('repeated_password')
        user_type = validated_data.pop('type', 'customer')
        validated_data['email'] = validated_data['email'].lower()
        user = User.objects.create_user(**validated_data)
        return user

class CustomAuthTokenSerializer(serializers.Serializer):
    """Serializes credentials for user authentication."""
    username = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        """Validate user credentials and authenticate the user."""
        username = attrs.get('username')
        password = attrs.get('password')
        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            if not user:
                raise serializers.ValidationError(
                    {'non_field_errors': 'Invalid username or password.'},
                    code='authentication'
                )
        else:
            raise serializers.ValidationError(
                {'non_field_errors': 'Both username and password are required.'},
                code='required'
            )
        attrs['user'] = user
        return attrs