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
    min_price = serializers.DecimalField(source='annotated_min_price', max_digits=10, decimal_places=2, read_only=True) # Use annotated value
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
    

class OfferCreateSerializer(serializers.ModelSerializer):
    # nested details for creation
    details = FullOfferDetailSerializer(many=True)
    # image field
    image = serializers.ImageField(allow_null=True, required=False)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def validate_details(self, value):
        # ensure exactly 3 details are provided
        if len(value) != 3:
            raise serializers.ValidationError('Exactly 3 details are required.')
        # ensure unique offer_type
        offer_types = [detail['offer_type'] for detail in value]
        if len(set(offer_types)) != len(offer_types):
            raise serializers.ValidationError('Offer types must be unique.')
        return value

    def create(self, validated_data):
        # extract details data
        details_data = validated_data.pop('details')
        # create offer
        offer = Offer.objects.create(user=self.context['request'].user, **validated_data)
        # create details
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer
   
    
class OfferUpdateSerializer(OfferCreateSerializer):
    # allow partial updates for details
    details = FullOfferDetailSerializer(many=True, required=False, partial=True)

    class Meta(OfferCreateSerializer.Meta):
        fields = ['id', 'title', 'image', 'description', 'details']  
        extra_kwargs = {'id': {'read_only': True}}  # make id read-only

    def validate_details(self, value):
        # optional validation for partial updates, ensure offer_type if provided
        for detail in value:
            if 'offer_type' not in detail:
                raise serializers.ValidationError('offer_type is required for detail updates.')
        return value

    def update(self, instance, validated_data):
        # update offer fields
        details_data = validated_data.pop('details', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        # update details by offer_type
        for detail_data in details_data:
            offer_type = detail_data.pop('offer_type')
            detail = OfferDetail.objects.filter(offer=instance, offer_type=offer_type).first()
            if detail:
                for attr, value in detail_data.items():
                    setattr(detail, attr, value)
                detail.save()
        return instance