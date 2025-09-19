"""Serializers for the reviews_app to handle review data in Django REST Framework."""

from django.contrib.auth.models import User
from rest_framework import serializers
from reviews_app.models import Review
from profiles_app.models import Profile


class ReviewSerializer(serializers.ModelSerializer):
    """Serializes review data for API responses, formatting timestamps in ISO format."""
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'business_user', 'reviewer', 'rating',
            'description', 'created_at', 'updated_at'
        ]


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializes input data for creating new reviews, with custom validation for business users."""
    business_user = serializers.IntegerField(write_only=True)  

    class Meta:
        model = Review
        fields = ['business_user', 'rating', 'description'] 

    def validate_business_user(self, value): 
        """Validate that the business user ID corresponds to an existing business profile."""
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('Business user not found or not a business profile.')
        if not Profile.objects.filter(user=user, type='business').exists():
            raise serializers.ValidationError('Business user not found or not a business profile.')
        return value

    def validate(self, data):
        """Validate that no duplicate review exists for the same business user and reviewer."""
        business_user_id = data['business_user']  # Updated reference
        if Review.objects.filter(business_user_id=business_user_id, reviewer=self.context['request'].user).exists():
            raise serializers.ValidationError('You have already reviewed this business user.')
        return data

    def create(self, validated_data):
        """Create a review instance, assigning the business user and reviewer."""
        business_user = User.objects.get(id=validated_data.pop('business_user')) 
        validated_data['business_user'] = business_user
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)

    def validate_rating(self, value):
        """Validate that the rating is between 1 and 5."""
        if not 1 <= value <= 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value
    

class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Serializes data for updating existing reviews."""
    class Meta:
        model = Review
        fields = ['rating', 'description']

    def validate_rating(self, value):
        """Validate that the rating is between 1 and 5."""
        if not 1 <= value <= 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value