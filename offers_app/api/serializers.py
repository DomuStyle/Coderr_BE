"""Serializers for the offers_app to handle Offer and OfferDetail data in Django REST Framework."""

from rest_framework import serializers
from offers_app.models import Offer, OfferDetail
from profiles_app.models import Profile


class OfferDetailSerializer(serializers.ModelSerializer):
    """Serializes basic OfferDetail fields for read-only access."""
    url = serializers.HyperlinkedIdentityField(
        view_name='offerdetail-detail',
        lookup_field='id'
    )

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']


class FullOfferDetailSerializer(serializers.ModelSerializer):
    """Serializes all OfferDetail fields, including price with decimal precision."""
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']


class OfferListSerializer(serializers.ModelSerializer):
    """Serializes Offer data with nested details and user profile information."""
    user_details = serializers.SerializerMethodField()
    details = OfferDetailSerializer(many=True, read_only=True)
    # Format timestamps in ISO format without microseconds.
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)
    image = serializers.ImageField(allow_null=True, required=False)
    min_price = serializers.DecimalField(source='annotated_min_price', max_digits=10, decimal_places=2, read_only=True)  # Uses annotated value from the model.
    min_delivery_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details', 'min_price',
            'min_delivery_time', 'user_details'
        ]

    def get_user_details(self, obj):
        """Retrieve user profile details for the offer's owner."""
        profile = Profile.objects.get(user=obj.user)
        return {
            'first_name': profile.first_name or '',
            'last_name': profile.last_name or '',
            'username': obj.user.username
        }


class OfferCreateSerializer(serializers.ModelSerializer):
    """Serializes data for creating new offers with nested details."""
    details = FullOfferDetailSerializer(many=True)
    image = serializers.ImageField(allow_null=True, required=False)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def validate_details(self, value):
        # Validate that exactly three details are provided to enforce consistent offer structures.
        if len(value) != 3:
            raise serializers.ValidationError('Exactly 3 details are required.')
        # Ensure offer types are unique across details.
        offer_types = [detail['offer_type'] for detail in value]
        if len(set(offer_types)) != len(offer_types):
            raise serializers.ValidationError('Offer types must be unique.')
        return value

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(user=self.context['request'].user, **validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer


class OfferUpdateSerializer(OfferCreateSerializer):
    """Serializes data for updating existing offers with optional nested details."""
    details = FullOfferDetailSerializer(many=True, required=False, partial=True)

    class Meta(OfferCreateSerializer.Meta):
        fields = ['id', 'title', 'image', 'description', 'details']
        extra_kwargs = {'id': {'read_only': True}}

    def validate_details(self, value):
        # Validate that offer_type is provided for each detail during updates.
        for detail in value:
            if 'offer_type' not in detail:
                raise serializers.ValidationError('offer_type is required for detail updates.')
        return value

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        for detail_data in details_data:
            offer_type = detail_data.pop('offer_type')
            detail = OfferDetail.objects.filter(offer=instance, offer_type=offer_type).first()
            if detail:
                for attr, value in detail_data.items():
                    setattr(detail, attr, value)
                detail.save()
        return instance