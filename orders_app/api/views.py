from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from orders_app.models import Order
from profiles_app.models import Profile
from .serializers import OrderSerializer, OrderCreateSerializer, OrderUpdateSerializer
from django.db.models import Q


class OrderListView(ListAPIView):
    # require authentication
    permission_classes = [IsAuthenticated]
    # serializer for list
    serializer_class = OrderSerializer
    # disable pagination to match endpoint spec (simple list)
    pagination_class = None
    
    def get_queryset(self):
        # filter orders for authenticated user as customer or business
        user = self.request.user
        queryset = Order.objects.filter(Q(customer_user=user) | Q(business_user=user)).select_related('customer_user', 'business_user')
        return queryset.order_by('-created_at')

    def post(self, request):
        # require authentication for POST
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        # check if user is customer
        if not Profile.objects.filter(user=request.user, type='customer').exists():
            return Response({'error': 'Only customers can create orders'}, status=status.HTTP_403_FORBIDDEN)
        # create order
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class OrderSpecificView(UpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return OrderUpdateSerializer
        return super().get_serializer_class()

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        if order.business_user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # Return full order using OrderSerializer
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)