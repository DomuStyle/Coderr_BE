"""API views for managing offers and offer details in Django REST Framework."""

from django.db.models import Q, Min
from offers_app.models import Offer, OfferDetail
from django.db.models.functions import Coalesce
from decimal import Decimal, InvalidOperation
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import exceptions
from profiles_app.models import Profile
from .serializers import OfferListSerializer, FullOfferDetailSerializer, OfferCreateSerializer, OfferUpdateSerializer
from .permissions import IsOfferOwnerOrReadOnly, IsOfferDetailOwnerOrReadOnly


class CustomPageNumberPagination(PageNumberPagination):
    """Custom pagination class with configurable page size."""
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 100


class OfferListView(ListAPIView):
    """View for listing offers with filtering, searching, and pagination."""
    serializer_class = OfferListSerializer
    permission_classes = []
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        # Annotate min_price consistently for use in filtering and ordering.
        queryset = Offer.objects.select_related('user').order_by('-created_at').distinct()
        queryset = queryset.annotate(
            annotated_min_price=Coalesce(Min('details__price'), Decimal('0'))
        )
        creator_id = self.request.query_params.get('creator_id')
        if creator_id:
            queryset = queryset.filter(user__id=creator_id)
        min_price = self.request.query_params.get('min_price')
        if min_price:
            try:
                min_price_val = Decimal(min_price)
                queryset = queryset.filter(annotated_min_price__gte=min_price_val)
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
            queryset = queryset.order_by('annotated_min_price' if ordering == 'min_price' else ordering)
        return queryset

    def list(self, request, *args, **kwargs):
        """List offers with pagination if applicable."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        """Create a new offer, restricted to authenticated business users."""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        if not Profile.objects.filter(user=request.user, type='business').exists():
            return Response({'error': 'Only business users can create offers'}, status=status.HTTP_403_FORBIDDEN)
        serializer = OfferCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            offer = serializer.save()
            return Response(OfferCreateSerializer(offer).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OfferDetailView(RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating, or deleting a specific offer detail."""
    serializer_class = FullOfferDetailSerializer
    permission_classes = [IsAuthenticated, IsOfferDetailOwnerOrReadOnly]
    queryset = OfferDetail.objects.all()
    lookup_field = 'id'


class OfferSpecificView(DestroyAPIView, UpdateAPIView, RetrieveAPIView):
    """View for retrieving, updating, or deleting a specific offer."""
    serializer_class = OfferListSerializer
    permission_classes = [IsAuthenticated, IsOfferOwnerOrReadOnly]
    queryset = Offer.objects.all()
    lookup_field = 'pk'

    def get_queryset(self):
        """Annotate min_price for consistency in serialization."""
        return Offer.objects.annotate(
            annotated_min_price=Coalesce(Min('details__price'), Decimal('0'))
        )

    def get_serializer_class(self):
        """Use update serializer for PATCH requests."""
        if self.request.method == 'PATCH':
            return OfferUpdateSerializer
        return super().get_serializer_class()

    def patch(self, request, *args, **kwargs):
        """Perform partial update, with permissions handling ownership."""
        return self.partial_update(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        """Delete the offer, with permissions handling ownership."""
        return self.destroy(request, *args, **kwargs)