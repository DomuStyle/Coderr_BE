from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from orders_app.models import Order
from profiles_app.models import Profile
from .serializers import OrderSerializer, OrderCreateSerializer
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