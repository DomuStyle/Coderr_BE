"""Serializers for the orders_app to handle order data in Django REST Framework."""

from rest_framework import serializers
from orders_app.models import Order
from offers_app.models import OfferDetail


class OrderSerializer(serializers.ModelSerializer):
    """Serializes order data for API responses, formatting timestamps in ISO format and prices as strings."""
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'features', 'offer_type',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'customer_user', 'business_user', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.Serializer):
    """Serializes input data for creating new orders based on an offer detail."""
    offer_detail_id = serializers.IntegerField(required=True)

    def validate_offer_detail_id(self, value):
        """Validate that the provided offer detail ID exists and has a title."""
        try:
            offer_detail = OfferDetail.objects.get(id=value)
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError('Offer detail not found.')
        if not offer_detail.title:
            raise serializers.ValidationError('Offer detail must have a title.')
        return value
    
    def create(self, validated_data):
        """Create an order using the specified offer detail's attributes."""
        offer_detail = OfferDetail.objects.get(id=validated_data['offer_detail_id'])
        order = Order.objects.create(
            customer_user=self.context['request'].user,
            business_user=offer_detail.offer.user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type
        )
        return order


class OrderUpdateSerializer(serializers.ModelSerializer):
    """Serializes data for updating an order's status."""
    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        """Validate that the provided status is a valid choice."""
        if value not in [choice[0] for choice in Order.STATUS_CHOICES]:
            raise serializers.ValidationError('Invalid status.')
        return value