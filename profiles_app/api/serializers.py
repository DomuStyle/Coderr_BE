from rest_framework import serializers
from profiles_app.models import Profile
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']  # Include writable/readable User fields; username read-only below
        extra_kwargs = {
            'username': {'read_only': True}  # Prevent changing username
        }


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nest UserSerializer; writable for email updates
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)
    file = serializers.ImageField(allow_null=True, required=False)  # Added: Support file uploads, allow null/empty

    class Meta:
        model = Profile
        fields = [
            'user', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type',
            'created_at'
        ]  # Removed 'username' and 'email'—now under nested 'user'
        read_only_fields = ['created_at']

    def to_internal_value(self, data):
        # Handle flat input for email by mapping to nested 'user'
        if 'email' in data:
            # Create or update the nested 'user' dict
            user_data = data.get('user', {})
            user_data['email'] = data.pop('email')  # Move email to nested
            data['user'] = user_data
        return super().to_internal_value(data)  # Proceed with standard validation

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        non_nullable_fields = ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']
        for field in non_nullable_fields:
            if representation[field] is None:
                representation[field] = ''
        # Fixed: Return full URL for file if exists, else null
        if instance.file:
            # Use request from context to build absolute URL (if request available, else relative)
            request = self.context.get('request', None)
            if request is not None:
                representation['file'] = request.build_absolute_uri(instance.file.url)
            else:
                representation['file'] = instance.file.url  # Relative URL if no request context
        else:
            representation['file'] = None
        # Flatten nested user fields for response (to match docs structure)
        user_data = representation.pop('user')
        representation['user'] = instance.user.id  # Add user ID as top-level
        representation['username'] = user_data['username']
        representation['email'] = user_data['email']
        return representation

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})  # Handle nested user data
        if user_data:
            instance.user.email = user_data.get('email', instance.user.email)
            instance.user.save()
        # Handle file explicitly (multipart sends it as File object or empty)
        file = validated_data.pop('file', None)
        if file is not None:
            instance.file = file
        # Update remaining Profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class BusinessProfileSerializer(ProfileSerializer):
    class Meta(ProfileSerializer.Meta):
        fields = [
            'user', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type'
        ]  # Adjusted—no 'username'/'email'; to_representation handles flattening if needed

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # For list views, exclude email/created_at as per original intent
        representation.pop('email', None)
        representation.pop('created_at', None)
        return representation


class CustomerProfileSerializer(ProfileSerializer):
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

