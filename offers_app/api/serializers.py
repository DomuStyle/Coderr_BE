from rest_framework import serializers
from offers_app.models import Offer, OfferDetail
from profiles_app.models import Profile

class OfferDetailSerializer(serializers.ModelSerializer):
    # url field for detail endpoint
    url = serializers.HyperlinkedIdentityField(
        view_name='offerdetail-detail',
        lookup_field='id'
    )

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']


class FullOfferDetailSerializer(serializers.ModelSerializer):
    # serialize all fields for offer detail
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']


class OfferListSerializer(serializers.ModelSerializer):
    # nested user details
    user_details = serializers.SerializerMethodField()
    # nested offer details
    details = OfferDetailSerializer(many=True, read_only=True)
    # format timestamps without microseconds
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)
    # image field
    image = serializers.ImageField(allow_null=True, required=False)
    # ensure decimal precision for min_price
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    # min_delivery_time as integer
    min_delivery_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details', 'min_price',
            'min_delivery_time', 'user_details'
        ]

    def get_user_details(self, obj):
        # return user profile details
        profile = Profile.objects.get(user=obj.user)
        return {
            'first_name': profile.first_name or '',
            'last_name': profile.last_name or '',
            'username': obj.user.username
        }