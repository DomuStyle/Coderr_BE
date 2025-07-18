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
        # clear existing offers to ensure clean state (optional, but good for isolation)
        Offer.objects.all().delete()
        OfferDetail.objects.all().delete()
        # set up test client
        self.client = APIClient()
        # create business user with expected username/first_name/last_name
        self.user = User.objects.create_user(
            username='jdoe',  # Matches expected in user_details assertions
            email='jdoe@business.de',
            password='testpass123'
        )
        self.profile = self.user.profile  # Fetch auto-created Profile
        self.profile.type = 'business'
        self.profile.first_name = 'John'
        self.profile.last_name = 'Doe'
        self.profile.save()  # Save updates
        
        # Create an offer with data matching test assertions
        self.offer = Offer.objects.create(
            user=self.user,
            title='Website Design',
            description='Professionelles Website-Design...',
            created_at=datetime(2024, 9, 25, 10, 0, 0, tzinfo=pytz.UTC),
            updated_at=datetime(2024, 9, 28, 12, 0, 0, tzinfo=pytz.UTC)
        )
        # Create 3 details with values to match assertions (revisions=2 for basic, delivery=7 for basic/min=7, features=['Basic Design'], etc.)
        self.detail_basic = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic',
            revisions=2,  # Matches expected
            delivery_time_in_days=7,  # Matches min_delivery_time=7
            price=100.00,
            features=['Basic Design'],  # Matches expected
            offer_type='basic'
        )
        self.detail_standard = OfferDetail.objects.create(
            offer=self.offer,
            title='Standard',
            revisions=5,
            delivery_time_in_days=10,
            price=200.00,
            features=['Standard Design'],  # Matches expected
            offer_type='standard'
        )
        self.detail_premium = OfferDetail.objects.create(
            offer=self.offer,
            title='Premium',
            revisions=10,
            delivery_time_in_days=14,
            price=500.00,
            features=['Premium Design'],  # Matches expected
            offer_type='premium'
        )

        # authenticate the client
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

    # create offer tests

    def test_create_offer_success(self):
        # test creating an offer as business user with 3 details
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
        # assert response status code is 201
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # assert response structure
        self.assertEqual(response.data['title'], 'Grafikdesign-Paket')
        self.assertEqual(len(response.data['details']), 3)
        self.assertEqual(response.data['details'][0]['offer_type'], 'basic')
        self.assertEqual(response.data['details'][1]['offer_type'], 'standard')
        self.assertEqual(response.data['details'][2]['offer_type'], 'premium')

    # patch offer tests

    def test_update_offer_success(self):
    # test updating an offer by owner
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
        # assert response status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # assert updated fields
        self.assertEqual(response.data['title'], 'Updated Website Design')
        self.assertEqual(response.data['details'][0]['title'], 'Updated Basic')
        self.assertEqual(response.data['details'][0]['revisions'], 3)
        self.assertEqual(response.data['details'][0]['delivery_time_in_days'], 6)
        self.assertEqual(response.data['details'][0]['price'], '120.00')
        self.assertEqual(response.data['details'][0]['features'], ['Updated Basic Design'])
        # assert unchanged fields
        self.assertEqual(response.data['description'], 'Professionelles Website-Design...')
        self.assertEqual(response.data['details'][1]['title'], 'Standard')

    # delete offer tests

    def test_delete_offer_success(self):
        url = reverse('offer-detail', kwargs={'pk': self.offer.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(id=self.offer.id).exists())


class OfferTestsUnappy(APITestCase):

    def setUp(self):
        # clear existing offers to ensure clean state
        Offer.objects.all().delete()
        OfferDetail.objects.all().delete()
        # set up test client and user
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='jdoe',  # Matches any expected in unhappy tests
            email='jdoe@business.de',
            password='testpass123'
        )
        self.profile = self.user.profile  # Fetch auto-created
        self.profile.type = 'business'
        self.profile.save()

        # Create an offer with data for unhappy tests
        self.offer = Offer.objects.create(
            user=self.user,
            title='Website Design',
            description='Professionelles Website-Design...',
            created_at=datetime(2024, 9, 25, 10, 0, 0, tzinfo=pytz.UTC),
            updated_at=datetime(2024, 9, 28, 12, 0, 0, tzinfo=pytz.UTC)
        )
        # Create at least one detail (from commented setUp)
        OfferDetail.objects.create(
            offer=self.offer,
            title='Basic',
            revisions=2,
            delivery_time_in_days=7,
            price=100.00,
            features=['Basic Design'],
            offer_type='basic'
        )

        # create another user for non-owner tests
        self.user2 = User.objects.create_user(
            username='jane',
            email='jane@business.de',
            password='testpass456'
        )
        self.profile2 = self.user2.profile
        self.profile2.type = 'business'
        self.profile2.save()

        # authenticate client (optional, as endpoint doesn't require auth, but for consistency)
        self.client.force_authenticate(user=self.user)

    def test_get_offers_invalid_params(self):
        # test invalid query parameters
        url = reverse('offer-list') + '?min_price=invalid'
        response = self.client.get(url)
        # assert response status code is 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # assert error message
        self.assertEqual(response.data, {'min_price': 'Invalid value'})

    # create offer tests

    def test_create_offer_non_business(self):
        # test creating offer as non-business user
        Profile.objects.filter(user=self.user).update(type='customer')  # change to non-business
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
        # assert response status code is 403
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # assert error message
        self.assertEqual(response.data['error'], 'Only business users can create offers')

    def test_create_offer_insufficient_details(self):
        # test creating offer with fewer than 3 details
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
        # assert response status code is 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # assert error message
        self.assertIn('Exactly 3 details are required.', str(response.data['details']))

    def test_create_offer_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse('offer-list')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # patch offer tests

    def test_update_offer_non_owner(self):
        # test updating offer as non-owner
        other_offer = Offer.objects.create(
            user=self.user2,
            title='Other Offer',
            description='Other...',
            created_at=datetime(2024, 9, 25, 10, 0, 0, tzinfo=pytz.UTC),
            updated_at=datetime(2024, 9, 28, 12, 0, 0, tzinfo=pytz.UTC)
        )
        url = reverse('offer-detail', kwargs={'pk': other_offer.id})
        data = {'title': 'Updated'}
        response = self.client.patch(url, data, format='json')
        # assert response status code is 403
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Permission denied')

    def test_update_offer_not_found(self):
        # test updating non-existent offer
        url = reverse('offer-detail', kwargs={'pk': 999})
        data = {'title': 'Updated'}
        response = self.client.patch(url, data, format='json')
        # assert response status code is 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)