from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Min
from offers_app.models import Offer, OfferDetail, Profile
from .serializers import OfferListSerializer, FullOfferDetailSerializer, OfferCreateSerializer
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated


class OfferListView(ListAPIView):
    serializer_class = OfferListSerializer
    permission_classes = []

    def get_queryset(self):
        # start with all offers, ensure unique results
        queryset = Offer.objects.select_related('user').order_by('-created_at').distinct()
        # apply filters based on query parameters
        creator_id = self.request.query_params.get('creator_id')
        if creator_id:
            queryset = queryset.filter(user__id=creator_id)
        min_price = self.request.query_params.get('min_price')
        if min_price:
            try:
                # filter offers where min_price >= given value
                queryset = queryset.annotate(
                    min_price=Min('details__price')
                ).filter(min_price__gte=float(min_price))
            except ValueError:
                raise serializers.ValidationError({'min_price': 'Invalid value'})
        max_delivery_time = self.request.query_params.get('max_delivery_time')
        if max_delivery_time:
            try:
                queryset = queryset.filter(details__delivery_time_in_days__lte=int(max_delivery_time))
            except ValueError:
                raise serializers.ValidationError({'max_delivery_time': 'Invalid value'})
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))
        ordering = self.request.query_params.get('ordering')
        if ordering in ['updated_at', 'min_price']:
            queryset = queryset.annotate(
                min_price=Min('details__price')
            ).order_by(ordering)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        # require authentication for POST
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        # check if user is business
        if not Profile.objects.filter(user=request.user, type='business').exists():
            return Response({'error': 'Only business users can create offers'}, status=status.HTTP_403_FORBIDDEN)
        # create offer
        serializer = OfferCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            offer = serializer.save()
            # return serialized offer using OfferCreateSerializer to include full details
            return Response(OfferCreateSerializer(offer).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class OfferDetailView(RetrieveAPIView):
    serializer_class = FullOfferDetailSerializer
    permission_classes = [IsAuthenticated]  # Align with GET /api/offers/{id}/
    queryset = OfferDetail.objects.all()
    lookup_field = 'id'