from rest_framework import serializers
from profiles_app.models import Profile
from django.contrib.auth.models import User

class ProfileSerializer(serializers.ModelSerializer):
    # include read-only fields from User model
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type',
            'email', 'created_at'
        ]

    def to_representation(self, instance):
        # ensure non-null fields return empty string if null
        representation = super().to_representation(instance)
        non_nullable_fields = ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']
        for field in non_nullable_fields:
            if representation[field] is None:
                representation[field] = ''
        # handle file field to return filename or null
        representation['file'] = instance.file.name if instance.file else None
        return representation

