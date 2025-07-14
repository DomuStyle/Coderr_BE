from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from profiles_app.models import Profile
from offers_app.models import Offer, OfferDetail
from rest_framework import status
from datetime import datetime
import pytz


class OfferTestsHappy(APITestCase):

    def setUp(self):
        # clear existing offers to ensure clean state
        Offer.objects.all().delete()
        OfferDetail.objects.all().delete()
        # set up test client
        self.client = APIClient()
        # create business user
        self.user = User.objects.create_user(
            username='jdoe',
            email='jdoe@business.de',
            password='testpass123'
        )
        Profile.objects.create(user=self.user, type='business', first_name='John', last_name='Doe')
        # create another user
        self.user2 = User.objects.create_user(
            username='jane',
            email='jane@business.de',
            password='testpass456'
        )
        Profile.objects.create(user=self.user2, type='business')
        # create offer
        self.offer = Offer.objects.create(
            user=self.user,
            title='Website Design',
            description='Professionelles Website-Design...',
            created_at=datetime(2024, 9, 25, 10, 0, 0, tzinfo=pytz.UTC),
            updated_at=datetime(2024, 9, 28, 12, 0, 0, tzinfo=pytz.UTC)
        )
        # create offer details
        OfferDetail.objects.create(
            offer=self.offer,
            title='Basic',
            revisions=2,
            delivery_time_in_days=7,
            price=100.00,
            features=['Basic Design'],
            offer_type='basic'
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title='Standard',
            revisions=5,
            delivery_time_in_days=10,
            price=200.00,
            features=['Standard Design'],
            offer_type='standard'
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title='Premium',
            revisions=10,
            delivery_time_in_days=14,
            price=500.00,
            features=['Premium Design'],
            offer_type='premium'
        )
        # authenticate client
        self.client.force_authenticate(user=self.user)

    def test_get_offer_detail(self):
        # test retrieving a single offer detail
        detail = OfferDetail.objects.get(title='Basic', offer=self.offer)
        url = reverse('offerdetail-detail', kwargs={'id': detail.id})  # Changed 'pk' to 'id'
        response = self.client.get(url)
        # assert response status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # assert response data
        expected_data = {
            'id': detail.id,
            'title': 'Basic',
            'revisions': 2,
            'delivery_time_in_days': 7,
            'price': '100.00',  # Decimal fields serialize as strings
            'features': ['Basic Design'],
            'offer_type': 'basic'
        }
        self.assertEqual(response.data, expected_data)

    def test_get_offers_paginated(self):
        # test retrieving paginated list of offers
        url = reverse('offer-list')
        response = self.client.get(url)
        # get actual detail IDs
        details = OfferDetail.objects.filter(offer=self.offer).order_by('id')
        # assert response status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # assert response structure
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
                    'min_price': '100.00',  # DecimalField serializes as string
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
        # test filtering by creator_id
        url = reverse('offer-list') + f'?creator_id={self.user.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['user'], self.user.id)

    def test_get_offers_filter_min_price(self):
        # test filtering by min_price
        url = reverse('offer-list') + '?min_price=150'
        response = self.client.get(url)
        # debug: print all offers
        # print(Offer.objects.all().values('id', 'title', 'user__username'))
        # print(response.data)
        # assert response status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # assert no offers with min_price >= 150
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)

    def test_get_offers_search(self):
        # test searching by title
        url = reverse('offer-list') + '?search=Website'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Website Design')


class OfferTestsUnappy(APITestCase):

    def setUp(self):
        # clear existing offers to ensure clean state
        Offer.objects.all().delete()
        OfferDetail.objects.all().delete()
        # set up test client and user
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='jdoe',
            email='jdoe@business.de',
            password='testpass123'
        )
        Profile.objects.create(user=self.user, type='business')
        self.offer = Offer.objects.create(
            user=self.user,
            title='Website Design',
            description='Professionelles Website-Design...',
            created_at=datetime(2024, 9, 25, 10, 0, 0, tzinfo=pytz.UTC),
            updated_at=datetime(2024, 9, 28, 12, 0, 0, tzinfo=pytz.UTC)
        )
        # create offer details
        OfferDetail.objects.create(
            offer=self.offer,
            title='Basic',
            revisions=2,
            delivery_time_in_days=7,
            price=100.00,
            features=['Basic Design'],
            offer_type='basic'
        )
        # authenticate client (optional, as endpoint doesn't require auth)
        self.client.force_authenticate(user=self.user)

    def test_get_offers_invalid_params(self):
        # test invalid query parameters
        url = reverse('offer-list') + '?min_price=invalid'
        response = self.client.get(url)
        # assert response status code is 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # assert error message
        self.assertEqual(response.data, {'min_price': 'Invalid value'})