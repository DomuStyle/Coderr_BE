from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.db.models import Q, Min
from offers_app.models import Offer, OfferDetail
from django.db.models.functions import Coalesce
from decimal import Decimal, InvalidOperation
from profiles_app.models import Profile
from .serializers import OfferListSerializer, FullOfferDetailSerializer, OfferCreateSerializer, OfferUpdateSerializer
from .permissions import IsOfferOwnerOrReadOnly
from rest_framework import serializers, exceptions
from rest_framework.permissions import IsAuthenticated


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 1  # default
    page_size_query_param = 'page_size'  # allow override
    max_page_size = 100


class OfferListView(ListAPIView):
    serializer_class = OfferListSerializer
    permission_classes = []
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = Offer.objects.select_related('user').order_by('-created_at').distinct()
        queryset = queryset.annotate(
            annotated_min_price=Coalesce(Min('details__price'), Decimal('0'))  # always annotate min_price for serializer
        )
        creator_id = self.request.query_params.get('creator_id')
        if creator_id:
            queryset = queryset.filter(user__id=creator_id)
        min_price = self.request.query_params.get('min_price')
        if min_price:
            try:
                min_price_val = Decimal(min_price)
                queryset = queryset.annotate(
                    annotated_min_price=Coalesce(Min('details__price'), Decimal('0'))
                ).filter(annotated_min_price__gte=min_price_val)  # Use consistent name
            except (ValueError, InvalidOperation):
                raise exceptions.ValidationError({'min_price': 'Invalid value'})
        max_delivery_time = self.request.query_params.get('max_delivery_time')
        if max_delivery_time:
            try:
                queryset = queryset.filter(details__delivery_time_in_days__lte=int(max_delivery_time))
            except ValueError:
                raise exceptions.ValidationError({'max_delivery_time': 'Invalid value'})
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))
        ordering = self.request.query_params.get('ordering')
        if ordering in ['updated_at', 'min_price']:
            queryset = queryset.annotate(
                annotated_min_price=Min('details__price')  # Use consistent name for ordering too
            ).order_by('annotated_min_price' if ordering == 'min_price' else ordering)
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
        # check if user is business; now works with correct Profile import
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


class OfferSpecificView(DestroyAPIView, UpdateAPIView, RetrieveAPIView):
    # specify serializer for specific offer
    serializer_class = OfferListSerializer
    # require authentication per endpoint doc
    permission_classes = [IsAuthenticated, IsOfferOwnerOrReadOnly]
    queryset = Offer.objects.all()
    lookup_field = 'pk'

    def get_queryset(self):
        # annotate annotated_min_price for min_price field in serializer (to match doc)
        return Offer.objects.annotate(
            annotated_min_price=Coalesce(Min('details__price'), Decimal('0'))
        )

    def get_serializer_class(self):
        # use OfferUpdateSerializer for PATCH
        if self.request.method == 'PATCH':
            return OfferUpdateSerializer
        return super().get_serializer_class()

    # def patch(self, request, *args, **kwargs):
    #     # ensure user is owner
    #     offer = self.get_object()
    #     if offer.user != request.user:
    #         return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    #     return self.partial_update(request, *args, **kwargs)
    
    # def delete(self, request, *args, **kwargs):
    #     offer = self.get_object()
    #     if offer.user != request.user:
    #         return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    #     return self.destroy(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        # permission class handles 403
        return self.partial_update(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        # permission class handles 403
        return self.destroy(request, *args, **kwargs)