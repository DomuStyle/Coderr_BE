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
            status='in_progress'
            # created_at=datetime(2024, 9, 29, 10, 0, 0, tzinfo=pytz.UTC),
            # updated_at=datetime(2024, 9, 30, 12, 0, 0, tzinfo=pytz.UTC)
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

    # order patch tests

    def test_update_order_status_success(self):
        # test updating order status as business user
        self.client.force_authenticate(user=self.business_user)  # Switch to business user
        old_updated_at = self.order.updated_at  # Capture old updated_at as datetime
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        data = {'status': 'completed'}
        response = self.client.patch(url, data, format='json')
        # assert response status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # refresh order from DB to get updated values
        self.order.refresh_from_db()
        # assert response structure
        self.assertEqual(response.data['id'], self.order.id)
        self.assertEqual(response.data['customer_user'], self.customer_user.id)
        self.assertEqual(response.data['business_user'], self.business_user.id)
        self.assertEqual(response.data['title'], 'Logo Design')
        self.assertEqual(response.data['revisions'], 3)
        self.assertEqual(response.data['delivery_time_in_days'], 5)
        self.assertEqual(response.data['price'], '150.00')
        self.assertEqual(response.data['features'], ['Logo Design', 'Visitenkarten'])
        self.assertEqual(response.data['offer_type'], 'basic')
        self.assertEqual(response.data['status'], 'completed')
        self.assertEqual(response.data['created_at'], self.order.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'))
        # check updated_at has changed or is at least equal (accounts for fast tests)
        self.assertGreaterEqual(self.order.updated_at, old_updated_at)
        # string comparison for response (allow equality if no delay)
        self.assertGreaterEqual(response.data['updated_at'], response.data['created_at'])

class OrderTestsUnhappy(APITestCase):
    
    def setUp(self):
        # clear existing orders to ensure clean state
        Order.objects.all().delete()
        # set up test client
        self.client = APIClient()
        # create customer user (renamed for consistency)
        self.customer_user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='testpass123'
        )
        Profile.objects.create(user=self.customer_user, type='customer')  # default as customer
        # create business user
        self.business_user = User.objects.create_user(
            username='business',
            email='business@example.com',
            password='testpass456'
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
            status='in_progress'
        )
        self.client.force_authenticate(user=self.customer_user)   # authenticate as customer for POST tests

    def test_get_orders_unauthenticated(self):
        # test listing orders when not authenticated
        self.client.force_authenticate(user=None)
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # order create tests

    # def test_create_order_non_customer(self):
    #     # test creating order as non-customer
    #     Profile.objects.filter(user=self.user).update(type='business')
    #     url = reverse('order-list')
    #     data = {'offer_detail_id': 1}
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_non_customer(self):
        # test creating order as non-customer
        Profile.objects.filter(user=self.customer_user).update(type='business')
        url = reverse('order-list')
        data = {'offer_detail_id': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_order_non_business(self):
        # test updating status as non-business (customer)
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        data = {'status': 'completed'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Permission denied')

    def test_create_order_invalid_offer_detail(self):
        # test creating order with invalid offer_detail_id
        url = reverse('order-list')
        data = {'offer_detail_id': 999}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['offer_detail_id'][0]), 'Offer detail not found.')

    def test_create_order_unauthenticated(self):
        # test creating order when not authenticated
        self.client.force_authenticate(user=None)
        url = reverse('order-list')
        data = {'offer_detail_id': 1}  # Dummy ID, as validation won't be reached
        response = self.client.post(url, data, format='json')
        # assert response status code is 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # assert error message
        # self.assertEqual(response.data['error'], 'Authentication required')

    def test_update_order_invalid_status(self):
        # test updating with invalid status
        self.client.force_authenticate(user=self.business_user)
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        data = {'status': 'invalid'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('"invalid" is not a valid choice.', str(response.data['status']))
