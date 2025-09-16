"""Test cases for order-related API endpoints in Django REST Framework, covering happy and unhappy paths."""

from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from offers_app.models import OfferDetail, Offer
from orders_app.models import Order
from profiles_app.models import Profile
from datetime import datetime
import pytz

class OrderTestsHappy(APITestCase):
    """Test cases for successful (happy path) scenarios in order APIs."""

    def setUp(self):
        # Clear existing orders to ensure test isolation.
        Order.objects.all().delete()
        self.client = APIClient()
        # Create customer user and set profile type.
        self.customer_user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='testpass123'
        )
        self.customer_profile = Profile.objects.get(user=self.customer_user)
        self.customer_profile.type = 'customer'
        self.customer_profile.save()
        # Create business user and set profile type.
        self.business_user = User.objects.create_user(
            username='business',
            email='business@example.com',
            password='testpass456'
        )
        self.business_profile = Profile.objects.get(user=self.business_user)
        self.business_profile.type = 'business'
        self.business_profile.save()
        # Create offer for testing order creation.
        self.offer = Offer.objects.create(
            user=self.business_user,
            title='Logo Design',
            description='Professional Logo Design...'
        )
        # Create order with values matching expected assertions.
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
        self.client.force_authenticate(user=self.customer_user)

    def test_get_orders_as_customer(self):
        """Test listing orders as a customer user."""
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
        """Test listing orders as a business user."""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['business_user'], self.business_user.id)

    def test_create_order_success(self):
        """Test creating an order as a customer using a valid offer detail ID."""
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer_user'], self.customer_user.id)
        self.assertEqual(response.data['business_user'], self.business_user.id)
        self.assertEqual(response.data['title'], 'Logo Design')
        self.assertEqual(response.data['status'], 'in_progress')

    def test_update_order_status_success(self):
        """Test updating an order's status as the business user."""
        self.client.force_authenticate(user=self.business_user)  # Switch to business user for update.
        old_updated_at = self.order.updated_at
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        data = {'status': 'completed'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'completed')
        self.assertGreater(self.order.updated_at, old_updated_at)

    def test_delete_order_success(self):
        """Test deleting an order as a staff user."""
        self.business_user.is_staff = True
        self.business_user.save()
        self.client.force_authenticate(user=self.business_user)
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())

    def test_order_count_success(self):
        """Test retrieving the count of in-progress orders for a business user."""
        url = reverse('order-count', kwargs={'business_user_id': self.business_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_count'], 1)

    def test_completed_order_count_success(self):
        """Test retrieving the count of completed orders for a business user."""
        self.order.status = 'completed'
        self.order.save()
        url = reverse('completed-order-count', kwargs={'business_user_id': self.business_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed_order_count'], 1)

class OrderTestsUnhappy(APITestCase):
    """Test cases for error (unhappy path) scenarios in order APIs."""

    def setUp(self):
        # Clear existing orders to ensure test isolation.
        Order.objects.all().delete()
        self.client = APIClient()
        # Create customer user and set profile type.
        self.customer_user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='testpass123'
        )
        self.customer_profile = Profile.objects.get(user=self.customer_user)
        self.customer_profile.type = 'customer'
        self.customer_profile.save()
        # Create business user and set profile type.
        self.business_user = User.objects.create_user(
            username='business',
            email='business@example.com',
            password='testpass456'
        )
        self.business_profile = Profile.objects.get(user=self.business_user)
        self.business_profile.type = 'business'
        self.business_profile.save()
        # Create offer for testing.
        self.offer = Offer.objects.create(
            user=self.business_user,
            title='Logo Design',
            description='Professional Logo Design...'
        )
        # Create order for testing unhappy paths.
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
        self.client.force_authenticate(user=self.customer_user)

    def test_get_orders_unauthenticated(self):
        """Test listing orders without authentication."""
        self.client.force_authenticate(user=None)
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_non_customer(self):
        """Test creating an order as a non-customer user."""
        Profile.objects.filter(user=self.customer_user).update(type='business')
        url = reverse('order-list')
        data = {'offer_detail_id': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_invalid_offer_detail(self):
        """Test creating an order with an invalid offer detail ID."""
        url = reverse('order-list')
        data = {'offer_detail_id': 999}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['offer_detail_id'][0]), 'Offer detail not found.')

    def test_create_order_unauthenticated(self):
        """Test creating an order without authentication."""
        self.client.force_authenticate(user=None)
        url = reverse('order-list')
        data = {'offer_detail_id': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_order_non_business(self):
        """Test updating an order's status as a non-business user."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        data = {'status': 'completed'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Permission denied')

    def test_update_order_invalid_status(self):
        """Test updating an order with an invalid status value."""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        data = {'status': 'invalid'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('"invalid" is not a valid choice.', str(response.data['status']))

    def test_update_order_unauthenticated(self):
        """Test updating an order without authentication."""
        self.client.force_authenticate(user=None)
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        data = {'status': 'completed'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_order_not_found(self):
        """Test updating a non-existent order."""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('order-detail', kwargs={'pk': 999})
        data = {'status': 'completed'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order_non_staff(self):
        """Test deleting an order as a non-staff user."""
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_unauthenticated(self):
        """Test deleting an order without authentication."""
        self.client.force_authenticate(user=None)
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_order_not_found(self):
        """Test deleting a non-existent order."""
        self.client.force_authenticate(user=self.business_user)
        self.business_user.is_staff = True
        self.business_user.save()
        url = reverse('order-detail', kwargs={'pk': 999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_completed_order_count_unauthenticated(self):
        """Test retrieving completed order count without authentication."""
        self.client.force_authenticate(user=None)
        url = reverse('completed-order-count', kwargs={'business_user_id': self.business_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_completed_order_count_not_found(self):
        """Test retrieving completed order count for a non-existent business user."""
        url = reverse('completed-order-count', kwargs={'business_user_id': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)