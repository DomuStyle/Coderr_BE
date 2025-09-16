"""Test cases for offer-related API endpoints in Django REST Framework, covering happy and unhappy paths."""

from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from profiles_app.models import Profile
from offers_app.models import Offer, OfferDetail
from datetime import datetime
import pytz

class OfferTestsHappy(APITestCase):
    """Test cases for successful (happy path) scenarios in offer APIs."""

    def setUp(self):
        # Clear existing offers to ensure test isolation.
        Offer.objects.all().delete()
        OfferDetail.objects.all().delete()
        self.client = APIClient()
        # Create business user with values matching expected assertions.
        self.user = User.objects.create_user(
            username='jdoe',
            email='jdoe@business.de',
            password='testpass123'
        )
        self.profile = self.user.profile
        self.profile.type = 'business'
        self.profile.first_name = 'John'
        self.profile.last_name = 'Doe'
        self.profile.save()
        # Create an offer with data matching test assertions.
        self.offer = Offer.objects.create(
            user=self.user,
            title='Website Design',
            description='Professionelles Website-Design...',
            created_at=datetime(2024, 9, 25, 10, 0, 0, tzinfo=pytz.UTC),
            updated_at=datetime(2024, 9, 28, 12, 0, 0, tzinfo=pytz.UTC)
        )
        # Create details with values matching expected assertions.
        self.detail_basic = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic',
            revisions=2,
            delivery_time_in_days=7,
            price=100.00,
            features=['Basic Design'],
            offer_type='basic'
        )
        self.detail_standard = OfferDetail.objects.create(
            offer=self.offer,
            title='Standard',
            revisions=5,
            delivery_time_in_days=10,
            price=200.00,
            features=['Standard Design'],
            offer_type='standard'
        )
        self.detail_premium = OfferDetail.objects.create(
            offer=self.offer,
            title='Premium',
            revisions=10,
            delivery_time_in_days=14,
            price=500.00,
            features=['Premium Design'],
            offer_type='premium'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_offer_detail(self):
        """Test retrieving a single offer detail via the API."""
        detail = OfferDetail.objects.get(title='Basic', offer=self.offer)
        url = reverse('offerdetail-detail', kwargs={'id': detail.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            'id': detail.id,
            'title': 'Basic',
            'revisions': 2,
            'delivery_time_in_days': 7,
            'price': '100.00',
            'features': ['Basic Design'],
            'offer_type': 'basic'
        }
        self.assertEqual(response.data, expected_data)

    def test_get_offers_paginated(self):
        """Test retrieving a paginated list of offers."""
        url = reverse('offer-list')
        response = self.client.get(url)
        details = OfferDetail.objects.filter(offer=self.offer).order_by('id')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [
                {
                    'id': self.offer.id,
                    'user': self.user.id,
                    'title': 'Website Design',
                    'image': None,
                    'description': 'Professionelles Website-Design...',
                    'created_at': self.offer.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'updated_at': self.offer.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'details': [
                        {'id': details[0].id, 'url': f'http://testserver{reverse("offerdetail-detail", kwargs={"id": details[0].id})}'},
                        {'id': details[1].id, 'url': f'http://testserver{reverse("offerdetail-detail", kwargs={"id": details[1].id})}'},
                        {'id': details[2].id, 'url': f'http://testserver{reverse("offerdetail-detail", kwargs={"id": details[2].id})}'}
                    ],
                    'min_price': '100.00',
                    'min_delivery_time': 7,
                    'user_details': {
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'username': 'jdoe'
                    }
                }
            ]
        }
        self.assertEqual(response.data, expected_data)

    def test_get_offers_filter_creator(self):
        """Test filtering offers by creator ID."""
        url = reverse('offer-list') + f'?creator_id={self.user.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['user'], self.user.id)

    def test_get_offers_filter_min_price(self):
        """Test filtering offers by minimum price."""
        url = reverse('offer-list') + '?min_price=150'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)

    def test_get_offers_search(self):
        """Test searching offers by title."""
        url = reverse('offer-list') + '?search=Website'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Website Design')

    def test_create_offer_success(self):
        """Test creating an offer as a business user with exactly three details."""
        url = reverse('offer-list')
        data = {
            'title': 'Grafikdesign-Paket',
            'image': None,
            'description': 'Ein umfassendes Grafikdesign-Paket für Unternehmen.',
            'details': [
                {
                    'title': 'Basic Design',
                    'revisions': 2,
                    'delivery_time_in_days': 5,
                    'price': '100.00',
                    'features': ['Logo Design', 'Visitenkarte'],
                    'offer_type': 'basic'
                },
                {
                    'title': 'Standard Design',
                    'revisions': 5,
                    'delivery_time_in_days': 7,
                    'price': '200.00',
                    'features': ['Logo Design', 'Visitenkarte', 'Briefpapier'],
                    'offer_type': 'standard'
                },
                {
                    'title': 'Premium Design',
                    'revisions': 10,
                    'delivery_time_in_days': 10,
                    'price': '500.00',
                    'features': ['Logo Design', 'Visitenkarte', 'Briefpapier', 'Flyer'],
                    'offer_type': 'premium'
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Grafikdesign-Paket')
        self.assertEqual(len(response.data['details']), 3)
        self.assertEqual(response.data['details'][0]['offer_type'], 'basic')
        self.assertEqual(response.data['details'][1]['offer_type'], 'standard')
        self.assertEqual(response.data['details'][2]['offer_type'], 'premium')

    def test_update_offer_success(self):
        """Test updating an offer by its owner."""
        url = reverse('offer-detail', kwargs={'pk': self.offer.id})
        data = {
            'title': 'Updated Website Design',
            'details': [
                {
                    'title': 'Updated Basic',
                    'revisions': 3,
                    'delivery_time_in_days': 6,
                    'price': '120.00',
                    'features': ['Updated Basic Design'],
                    'offer_type': 'basic'
                }
            ]
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Website Design')
        self.assertEqual(response.data['details'][0]['title'], 'Updated Basic')
        self.assertEqual(response.data['details'][0]['revisions'], 3)
        self.assertEqual(response.data['details'][0]['delivery_time_in_days'], 6)
        self.assertEqual(response.data['details'][0]['price'], '120.00')
        self.assertEqual(response.data['details'][0]['features'], ['Updated Basic Design'])
        self.assertEqual(response.data['description'], 'Professionelles Website-Design...')
        self.assertEqual(response.data['details'][1]['title'], 'Standard')

    def test_delete_offer_success(self):
        """Test deleting an offer by its owner."""
        url = reverse('offer-detail', kwargs={'pk': self.offer.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(id=self.offer.id).exists())

class OfferTestsUnhappy(APITestCase):
    """Test cases for error (unhappy path) scenarios in offer APIs."""

    def setUp(self):
        # Clear existing offers to ensure test isolation.
        Offer.objects.all().delete()
        OfferDetail.objects.all().delete()
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='jdoe',
            email='jdoe@business.de',
            password='testpass123'
        )
        self.profile = self.user.profile
        self.profile.type = 'business'
        self.profile.save()
        # Create an offer with data for unhappy tests.
        self.offer = Offer.objects.create(
            user=self.user,
            title='Website Design',
            description='Professionelles Website-Design...',
            created_at=datetime(2024, 9, 25, 10, 0, 0, tzinfo=pytz.UTC),
            updated_at=datetime(2024, 9, 28, 12, 0, 0, tzinfo=pytz.UTC)
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title='Basic',
            revisions=2,
            delivery_time_in_days=7,
            price=100.00,
            features=['Basic Design'],
            offer_type='basic'
        )
        # Create another user for non-owner tests.
        self.user2 = User.objects.create_user(
            username='jane',
            email='jane@business.de',
            password='testpass456'
        )
        self.profile2 = self.user2.profile
        self.profile2.type = 'business'
        self.profile2.save()
        self.client.force_authenticate(user=self.user)

    def test_get_offers_invalid_params(self):
        """Test handling invalid query parameters in offer list."""
        url = reverse('offer-list') + '?min_price=invalid'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'min_price': 'Invalid value'})

    def test_create_offer_non_business(self):
        """Test creating an offer as a non-business user."""
        Profile.objects.filter(user=self.user).update(type='customer')
        url = reverse('offer-list')
        data = {
            'title': 'Grafikdesign-Paket',
            'description': 'Ein umfassendes Grafikdesign-Paket für Unternehmen.',
            'details': [
                {
                    'title': 'Basic Design',
                    'revisions': 2,
                    'delivery_time_in_days': 5,
                    'price': '100.00',
                    'features': ['Logo Design', 'Visitenkarte'],
                    'offer_type': 'basic'
                },
                {
                    'title': 'Standard Design',
                    'revisions': 5,
                    'delivery_time_in_days': 7,
                    'price': '200.00',
                    'features': ['Logo Design', 'Visitenkarte', 'Briefpapier'],
                    'offer_type': 'standard'
                },
                {
                    'title': 'Premium Design',
                    'revisions': 10,
                    'delivery_time_in_days': 10,
                    'price': '500.00',
                    'features': ['Logo Design', 'Visitenkarte', 'Briefpapier', 'Flyer'],
                    'offer_type': 'premium'
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Only business users can create offers')

    def test_create_offer_insufficient_details(self):
        """Test creating an offer with fewer than three details."""
        url = reverse('offer-list')
        data = {
            'title': 'Grafikdesign-Paket',
            'description': 'Ein umfassendes Grafikdesign-Paket für Unternehmen.',
            'details': [
                {
                    'title': 'Basic Design',
                    'revisions': 2,
                    'delivery_time_in_days': 5,
                    'price': '100.00',
                    'features': ['Logo Design', 'Visitenkarte'],
                    'offer_type': 'basic'
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Exactly 3 details are required.', str(response.data['details']))

    def test_create_offer_unauthenticated(self):
        """Test creating an offer without authentication."""
        self.client.force_authenticate(user=None)
        url = reverse('offer-list')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_offer_non_owner(self):
        """Test updating an offer as a non-owner."""
        business_user = User.objects.create_user(username='business', password='pass', email='business@example.com')
        business_profile = Profile.objects.get(user=business_user)
        business_profile.type = 'business'
        business_profile.save()
        non_owner = User.objects.create_user(username='nonowner', password='pass', email='nonowner@example.com')
        non_owner_profile = Profile.objects.get(user=non_owner)
        non_owner_profile.type = 'customer'
        non_owner_profile.save()
        offer = Offer.objects.create(user=business_user, title='Test Offer', description='Test Desc')
        url = reverse('offer-detail', kwargs={'pk': offer.id})
        data = {'title': 'Updated Title'}
        self.client.force_authenticate(user=non_owner)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], 'Permission denied')

    def test_update_offer_not_found(self):
        """Test updating a non-existent offer."""
        url = reverse('offer-detail', kwargs={'pk': 999})
        data = {'title': 'Updated'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)