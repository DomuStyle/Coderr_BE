from rest_framework.generics import ListAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from orders_app.models import Order
from profiles_app.models import Profile
from .serializers import OrderSerializer, OrderCreateSerializer, OrderUpdateSerializer
from django.db.models import Q
from django.contrib.auth.models import User


class OrderListView(ListAPIView):
    # require authentication
    permission_classes = [IsAuthenticated]
    # serializer for list
    serializer_class = OrderSerializer
    # disable pagination (simple list)
    pagination_class = None
    
    def get_queryset(self):
        # filter orders for authenticated user as customer or business
        user = self.request.user
        queryset = Order.objects.filter(Q(customer_user=user) | Q(business_user=user)).select_related('customer_user', 'business_user')
        return queryset.order_by('-created_at')

    # def post(self, request):
    #     # check if user is customer
    #     if not Profile.objects.filter(user=request.user, type='customer').exists():
    #         return Response({'error': 'Only customers can create orders'}, status=status.HTTP_403_FORBIDDEN)
    #     # create order
    #     serializer = OrderCreateSerializer(data=request.data, context={'request': request})
    #     if serializer.is_valid():
    #         order = serializer.save()
    #         return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        # check if the authenticated user is a customer; if not, return a 403 error to match permissions in the doc
        if not Profile.objects.filter(user=request.user, type='customer').exists():
            return Response({'error': 'Only customers can create orders'}, status=status.HTTP_403_FORBIDDEN)
        # instantiate the OrderCreateSerializer with the request data and context (including the request for user access)
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        # validate the serializer; if valid, proceed to save
        if serializer.is_valid():
            # save the serializer to create the order object
            order = serializer.save()
            # serialize the new order using OrderSerializer to get the response data structure matching the doc
            data = OrderSerializer(order).data
            # add the input offer_detail_id to the data dict; this clarifies the linked detail without changing the model
            data['offer_detail_id'] = serializer.validated_data['offer_detail_id']
            # return the enhanced data with 201 status, ensuring the response includes the expected order details plus the input id
            return Response(data, status=status.HTTP_201_CREATED)
        # if invalid, return errors with 400 status as per the doc
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderSpecificView(DestroyAPIView, UpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    # queryset = Order.objects.all()
    queryset = Order.objects.select_related('customer_user', 'business_user')
    lookup_field = 'pk'

    def get_permissions(self):
        # Use IsAdminUser for DELETE
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        return super().get_permissions()

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
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

    # def delete(self, request, *args, **kwargs):
    #     # No additional checks needed, IsAdminUser handles permission
    #     return self.destroy(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        self.perform_destroy(order)
        return Response({'detail': 'Order deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    

class OrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        if not User.objects.filter(id=business_user_id).exists():
            return Response({'error': 'Business user not found'}, status=status.HTTP_404_NOT_FOUND)
        count = Order.objects.filter(business_user_id=business_user_id, status='in_progress').count()
        return Response({'order_count': count}, status=status.HTTP_200_OK)
    

class CompletedOrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        if not User.objects.filter(id=business_user_id).exists():
            return Response({'error': 'Business user not found'}, status=status.HTTP_404_NOT_FOUND)
        count = Order.objects.filter(business_user_id=business_user_id, status='completed').count()
        return Response({'completed_order_count': count}, status=status.HTTP_200_OK)