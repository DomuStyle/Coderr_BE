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
        self.profile = Profile.objects.create(
            user=self.user,
            first_name='Max',
            last_name='Mustermann',
            location='Berlin',
            tel='123456789',
            description='Business description',
            working_hours='9-17',
            type='business',
            created_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
        )
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
        empty_profile = Profile.objects.create(
            user=User.objects.create_user(username='emptyuser', password='pass'),
            first_name='',
            last_name='',
            location='',
            tel='',
            description='',
            working_hours='',
            type='customer'
        )
        url = reverse('profile-detail', kwargs={'pk': empty_profile.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], '')
        self.assertEqual(response.data['location'], '')

class ProfileTestsUnappy(APITestCase):
    
    def setUp(self):
        # set up test client and user
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@business.de',
            password='testpass123'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            first_name='Max',
            last_name='Mustermann',
            location='Berlin',
            tel='123456789',
            description='Business description',
            working_hours='9-17',
            type='business',
            created_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
        )
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