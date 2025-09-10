from django.contrib.auth.models import User
from rest_framework import serializers
from reviews_app.models import Review
from profiles_app.models import Profile

class ReviewSerializer(serializers.ModelSerializer):
    # format timestamps
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'business_user', 'reviewer', 'rating',
            'description', 'created_at', 'updated_at'
        ]


class ReviewCreateSerializer(serializers.ModelSerializer):
    business_user_id = serializers.IntegerField(write_only=True)  # changed to IntegerField for custom validation

    class Meta:
        model = Review
        fields = ['business_user_id', 'rating', 'description']

    def validate_business_user_id(self, value):
        # fetch and validate business user
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('Business user not found or not a business profile.')
        if not Profile.objects.filter(user=user, type='business').exists():
            raise serializers.ValidationError('Business user not found or not a business profile.')
        return value

    def validate(self, data):
        # check for duplicate review
        business_user_id = data['business_user_id']
        if Review.objects.filter(business_user_id=business_user_id, reviewer=self.context['request'].user).exists():
            raise serializers.ValidationError('You have already reviewed this business user.')
        return data

    def create(self, validated_data):
        # get business user from validated id
        business_user = User.objects.get(id=validated_data.pop('business_user_id'))
        validated_data['business_user'] = business_user
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value
   
    
class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'description']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value