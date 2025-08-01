from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from profiles_app.models import Profile
from rest_framework import status
from datetime import datetime
import pytz


class ProfileTestsHappy(APITestCase):

    def setUp(self):
        # set up test client and user
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@business.de',
            password='testpass123'
        )
        self.profile = self.user.profile  # Fetch auto-created Profile
        self.profile.first_name = 'Max'
        self.profile.last_name = 'Mustermann'
        self.profile.location = 'Berlin'
        self.profile.tel = '123456789'
        self.profile.description = 'Business description'
        self.profile.working_hours = '9-17'
        self.profile.type = 'business'
        self.profile.created_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
        self.profile.save()  # Save updates
        
        # create another business profile
        self.user2 = User.objects.create_user(
            username='anotherbusiness',
            email='another@business.de',
            password='testpass456'
        )
        self.profile2 = self.user2.profile  # Fetch auto-created
        self.profile2.first_name = 'Anna'
        self.profile2.last_name = 'Schmidt'
        self.profile2.location = 'Munich'
        self.profile2.tel = '987654321'
        self.profile2.description = 'Freelancer'
        self.profile2.working_hours = '10-18'
        self.profile2.type = 'business'
        self.profile2.save()

        # create a customer profile to ensure filtering
        self.customer_user = User.objects.create_user(
            username='customer',
            email='customer@test.de',
            password='testpass789'
        )
        self.customer_profile = self.customer_user.profile  # Fetch auto-created
        self.customer_profile.first_name = 'Jane'
        self.customer_profile.last_name = 'Doe'
        self.customer_profile.location = 'Hamburg'
        self.customer_profile.tel = '555555555'
        self.customer_profile.description = ''
        self.customer_profile.working_hours = ''
        self.customer_profile.type = 'customer'
        self.customer_profile.save()

        # authenticate the client
        self.client.force_authenticate(user=self.user)

    def test_get_profile_authenticated(self):
        # test retrieving profile details for authenticated user
        url = reverse('profile-detail', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        
        # assert response status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # assert response data matches expected profile
        expected_data = {
            'user': self.user.id,
            'username': 'testuser',
            'first_name': 'Max',
            'last_name': 'Mustermann',
            'file': None,
            'location': 'Berlin',
            'tel': '123456789',
            'description': 'Business description',
            'working_hours': '9-17',
            'type': 'business',
            'email': 'test@business.de',
            'created_at': self.profile.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')  # Match serializer format
        }
        self.assertEqual(response.data, expected_data)

    def test_patch_profile_owner(self):
        # test updating own profile
        url = reverse('profile-detail', kwargs={'pk': self.user.id})
        data = {
            'first_name': 'Updated',
            'tel': '987654321',
            'description': 'Updated description',
            'working_hours': '10-18'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['tel'], '987654321')

    def test_get_profile_empty_fields(self):
        # test profile with empty fields
        empty_user = User.objects.create_user(username='emptyuser', password='pass')
        empty_profile = empty_user.profile  # Fetch auto-created
        empty_profile.first_name = ''
        empty_profile.last_name = ''
        empty_profile.location = ''
        empty_profile.tel = ''
        empty_profile.description = ''
        empty_profile.working_hours = ''
        empty_profile.type = 'customer'
        empty_profile.save()
        url = reverse('profile-detail', kwargs={'pk': empty_profile.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], '')
        self.assertEqual(response.data['location'], '')

    def test_get_business_profiles_authenticated(self):
        # test retrieving list of business profiles for authenticated user
        url = reverse('business-profiles-list')
        response = self.client.get(url)
        
        # assert response status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # assert response contains only business profiles
        expected_data = [
            {
                'user': self.user.id,
                'username': 'testuser',
                'first_name': 'Max',
                'last_name': 'Mustermann',
                'file': None,
                'location': 'Berlin',
                'tel': '123456789',
                'description': 'Business description',
                'working_hours': '9-17',
                'type': 'business'
            },
            {
                'user': self.user2.id,
                'username': 'anotherbusiness',
                'first_name': 'Anna',
                'last_name': 'Schmidt',
                'file': None,
                'location': 'Munich',
                'tel': '987654321',
                'description': 'Freelancer',
                'working_hours': '10-18',
                'type': 'business'
            }
        ]
        self.assertEqual(response.data, expected_data)
        # assert no customer profiles are included
        self.assertEqual(len(response.data), 2)

    def test_get_business_profiles_empty_fields(self):
        # test business profile with empty fields
        empty_business_user = User.objects.create_user(
            username='emptybusiness',
            email='empty@business.de',
            password='pass'
        )
        empty_business_profile = empty_business_user.profile  # Fetch auto-created
        empty_business_profile.first_name = ''
        empty_business_profile.last_name = ''
        empty_business_profile.location = ''
        empty_business_profile.tel = ''
        empty_business_profile.description = ''
        empty_business_profile.working_hours = ''
        empty_business_profile.type = 'business'
        empty_business_profile.save()
        url = reverse('business-profiles-list')
        response = self.client.get(url)
        # assert empty fields return ''
        for profile in response.data:
            if profile['user'] == empty_business_user.id:
                self.assertEqual(profile['first_name'], '')
                self.assertEqual(profile['location'], '')
                self.assertEqual(profile['description'], '')

    def test_get_business_profiles_empty_list(self):
        # test when no business profiles exist
        Profile.objects.filter(type='business').delete()  # remove business profiles
        url = reverse('business-profiles-list')
        response = self.client.get(url)
        
        # assert response status code is 200 and empty list
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_customer_profiles_authenticated(self):
        # test retrieving list of customer profiles
        url = reverse('customer-profiles-list')
        response = self.client.get(url)
        
        # assert response status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # assert response contains only customer profiles
        expected_data = [
            {
                'user': self.customer_user.id,
                'username': 'customer',
                'first_name': 'Jane',
                'last_name': 'Doe',
                'file': None,
                'location': 'Hamburg',
                'tel': '555555555',
                'description': '',
                'working_hours': '',
                'type': 'customer'
            }
        ]
        self.assertEqual(response.data, expected_data)
        self.assertEqual(len(response.data), 1)

    def test_get_customer_profiles_empty_fields(self):
        # test customer profile with empty fields
        empty_customer_user = User.objects.create_user(
            username='emptycustomer',
            email='empty@customer.de',
            password='pass'
        )
        empty_customer_profile = empty_customer_user.profile  # Fetch auto-created
        empty_customer_profile.first_name = ''
        empty_customer_profile.last_name = ''
        empty_customer_profile.location = ''
        empty_customer_profile.tel = ''
        empty_customer_profile.description = ''
        empty_customer_profile.working_hours = ''
        empty_customer_profile.type = 'customer'
        empty_customer_profile.save()
        url = reverse('customer-profiles-list')
        response = self.client.get(url)
        for profile in response.data:
            if profile['user'] == empty_customer_user.id:
                self.assertEqual(profile['first_name'], '')
                self.assertEqual(profile['location'], '')

    def test_get_customer_profiles_empty_list(self):
        # test when no customer profiles exist
        Profile.objects.filter(type='customer').delete()
        url = reverse('customer-profiles-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

class ProfileTestsUnhappy(APITestCase):

    def setUp(self):
        # set up test client and user
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@business.de',
            password='testpass123'
        )
        self.profile = self.user.profile  # Fetch auto-created
        self.profile.first_name = 'Max'
        self.profile.last_name = 'Mustermann'
        self.profile.location = 'Berlin'
        self.profile.tel = '123456789'
        self.profile.description = 'Business description'
        self.profile.working_hours = '9-17'
        self.profile.type = 'business'
        self.profile.created_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
        self.profile.save()
        # authenticate the client
        self.client.force_authenticate(user=self.user)

    def test_get_profile_unauthenticated(self):
        # test retrieving profile when not authenticated
        self.client.force_authenticate(user=None)  # remove authentication
        url = reverse('profile-detail', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        
        # assert response status code is 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_profile_not_owner(self):
        # test updating someone else's profile
        other_user = User.objects.create_user(username='other', password='pass')
        url = reverse('profile-detail', kwargs={'pk': other_user.id})
        response = self.client.patch(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_business_profiles_unauthenticated(self):
        # test retrieving business profiles when not authenticated
        self.client.force_authenticate(user=None)  # remove authentication
        url = reverse('business-profiles-list')
        response = self.client.get(url)
        
        # assert response status code is 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_customer_profiles_unauthenticated(self):
        # test retrieving customer profiles when not authenticated
        self.client.force_authenticate(user=None)
        url = reverse('customer-profiles-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)