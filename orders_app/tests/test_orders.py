from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from profiles_app.models import Profile
from orders_app.models import Order
from offers_app.models import OfferDetail, Offer
from rest_framework import status
from datetime import datetime
import pytz


class OrderTestsHappy(APITestCase):
    def setUp(self):
        # clear existing orders to ensure clean state
        Order.objects.all().delete()
        # set up test client
        self.client = APIClient()
        # create customer user
        self.customer_user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='testpass123'
        )
        Profile.objects.create(user=self.customer_user, type='customer')
        # create business user
        self.business_user = User.objects.create_user(
            username='business',
            email='business@example.com',
            password='testpass456'
        )
        # create offer for offer_detail
        self.offer = Offer.objects.create(
            user=self.business_user,
            title='Logo Design',
            description='Professional Logo Design...'
        )
        Profile.objects.create(user=self.business_user, type='business')
        # create order
        self.order = Order.objects.create(
            customer_user=self.customer_user,
            business_user=self.business_user,
            title='Logo Design',
            revisions=3,
            delivery_time_in_days=5,
            price=150.00,
            features=['Logo Design', 'Visitenkarten'],
            offer_type='basic',
            status='in_progress',
            created_at=datetime(2024, 9, 29, 10, 0, 0, tzinfo=pytz.UTC),
            updated_at=datetime(2024, 9, 30, 12, 0, 0, tzinfo=pytz.UTC)
        )
        # authenticate as customer
        self.client.force_authenticate(user=self.customer_user)

    def test_get_orders_as_customer(self):
        # test listing orders as customer
        url = reverse('order-list')
        response = self.client.get(url)
        # assert response status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # assert response structure
        expected_data = [
            {
                'id': self.order.id,
                'customer_user': self.customer_user.id,
                'business_user': self.business_user.id,
                'title': 'Logo Design',
                'revisions': 3,
                'delivery_time_in_days': 5,
                'price': '150.00',
                'features': ['Logo Design', 'Visitenkarten'],
                'offer_type': 'basic',
                'status': 'in_progress',
                'created_at': self.order.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'updated_at': self.order.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
        ]
        self.assertEqual(response.data, expected_data)

    def test_get_orders_as_business(self):
        # test listing orders as business user
        self.client.force_authenticate(user=self.business_user)
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['business_user'], self.business_user.id)

    # order create tests

    def test_create_order_success(self):
        # test creating order as customer from offer_detail_id
        offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic',
            revisions=3,
            delivery_time_in_days=5,
            price=150.00,
            features=['Logo Design', 'Visitenkarten'],
            offer_type='basic'
        )
        url = reverse('order-list')
        data = {'offer_detail_id': offer_detail.id}
        response = self.client.post(url, data, format='json')
        # assert response status code is 201
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # assert response structure
        self.assertEqual(response.data['customer_user'], self.customer_user.id)
        self.assertEqual(response.data['business_user'], self.business_user.id)
        self.assertEqual(response.data['title'], 'Logo Design')
        self.assertEqual(response.data['status'], 'in_progress')


class OrderTestsUnhappy(APITestCase):
    
    def test_get_orders_unauthenticated(self):
        # test listing orders when not authenticated
        self.client.force_authenticate(user=None)
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # order create tests