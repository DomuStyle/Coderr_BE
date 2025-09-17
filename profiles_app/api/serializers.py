"""Serializers for the profiles_app to handle user and profile data in Django REST Framework."""

from django.contrib.auth.models import User
from rest_framework import serializers
from profiles_app.models import Profile

class UserSerializer(serializers.ModelSerializer):
    """Serializes User model data for profile-related API responses."""
    class Meta:
        model = User
        fields = ['username', 'email']
        extra_kwargs = {
            'username': {'read_only': True}
        }

class ProfileSerializer(serializers.ModelSerializer):
    """Serializes Profile model data, including nested user information and image uploads."""
    user = UserSerializer()
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)
    file = serializers.ImageField(allow_null=True, required=False)

    class Meta:
        model = Profile
        fields = [
            'user', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type',
            'created_at'
        ]
        read_only_fields = ['created_at']

    def to_internal_value(self, data):
        """Handle flat email input by mapping it to nested user data."""
        if 'email' in data:
            user_data = data.get('user', {})
            user_data['email'] = data.pop('email')
            data['user'] = user_data
        return super().to_internal_value(data)

    def to_representation(self, instance):
        """Flatten user fields and convert file field to an absolute URL if available."""
        # Set non-nullable fields to empty strings if None.
        representation = super().to_representation(instance)
        non_nullable_fields = ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']
        for field in non_nullable_fields:
            if representation[field] is None:
                representation[field] = ''
        if instance.file:
            request = self.context.get('request', None)
            if request is not None:
                representation['file'] = request.build_absolute_uri(instance.file.url)
            else:
                representation['file'] = instance.file.url
        else:
            representation['file'] = None
        user_data = representation.pop('user')
        representation['user'] = instance.user.id
        representation['username'] = user_data['username']
        representation['email'] = user_data['email']
        return representation

    def update(self, instance, validated_data):
        """Update profile and nested user data, handling file uploads explicitly."""
        user_data = validated_data.pop('user', {})
        if user_data:
            instance.user.email = user_data.get('email', instance.user.email)
            instance.user.save()
        file = validated_data.pop('file', None)
        if file is not None:
            instance.file = file
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class BusinessProfileSerializer(ProfileSerializer):
    """Serializes business profiles, excluding email and created_at in list views."""
    class Meta(ProfileSerializer.Meta):
        fields = [
            'user', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type'
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('email', None)
        representation.pop('created_at', None)
        return representation

class CustomerProfileSerializer(ProfileSerializer):
    """Serializes customer profiles, excluding email and created_at in list views."""
    class Meta(ProfileSerializer.Meta):
        fields = [
            'user', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type'
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('email', None)
        representation.pop('created_at', None)
        return representation