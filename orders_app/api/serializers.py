from rest_framework import serializers
from orders_app.models import Order
from offers_app.models import OfferDetail

class OrderSerializer(serializers.ModelSerializer):
    # format timestamps
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)
    # price as string
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
    # input field
    offer_detail_id = serializers.IntegerField(required=True)

    def validate_offer_detail_id(self, value):
        # validate offer detail exists
        if not OfferDetail.objects.filter(id=value).exists():
            raise serializers.ValidationError('Offer detail not found.')
        return value

    def create(self, validated_data):
        # get offer detail
        offer_detail = OfferDetail.objects.get(id=validated_data['offer_detail_id'])
        # create order
        order = Order.objects.create(
            customer_user=self.context['request'].user,
            business_user=offer_detail.offer.user,
            # title=offer_detail.title,
            title=offer_detail.offer.title,  # fixed to use offer.title instead of offer_detail.title
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type
        )
        return order
    

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        # validate status value
        if value not in [choice[0] for choice in Order.STATUS_CHOICES]:
            raise serializers.ValidationError('Invalid status.')
        return value