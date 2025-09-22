"""Serializers for the stats_app to handle statistical data in Django REST Framework."""

from rest_framework import serializers


class BaseInfoSerializer(serializers.Serializer):
    """Serializer for base information including review count, average rating, and other counts."""
    review_count = serializers.IntegerField()
    average_rating = serializers.FloatField()
    business_profile_count = serializers.IntegerField()
    offer_count = serializers.IntegerField()