"""Test cases for profile-related API endpoints in Django REST Framework, covering happy and unhappy paths."""

from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from profiles_app.models import Profile
from datetime import datetime
import pytz


class ProfileTestsHappy(APITestCase):
    """Test cases for successful (happy path) scenarios in profile APIs."""

    def setUp(self):
        self.client = APIClient()
        # Create user and update profile with values matching expected assertions.
        self.user = User.objects.create_user(
            username='testuser',
            email='test@business.de',
            password='testpass123'
        )
        self.profile = self.user.profile
        self.profile.first_name = 'Max'
        self.profile.last_name = 'Mustermann'
        self.profile.location = 'Berlin'
        self.profile.tel = '123456789'
        self.profile.description = 'Business description'
        self.profile.working_hours = '9-17'
        self.profile.type = 'business'
        self.profile.created_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
        self.profile.save()
        
        # Create another business profile for list tests.
        self.user2 = User.objects.create_user(
            username='anotherbusiness',
            email='another@business.de',
            password='testpass456'
        )
        self.profile2 = self.user2.profile
        self.profile2.first_name = 'Anna'
        self.profile2.last_name = 'Schmidt'
        self.profile2.location = 'Munich'
        self.profile2.tel = '987654321'
        self.profile2.description = 'Freelancer'
        self.profile2.working_hours = '10-18'
        self.profile2.type = 'business'
        self.profile2.save()

        # Create a customer profile to test filtering.
        self.customer_user = User.objects.create_user(
            username='customer',
            email='customer@test.de',
            password='testpass789'
        )
        self.customer_profile = self.customer_user.profile
        self.customer_profile.first_name = 'Jane'
        self.customer_profile.last_name = 'Doe'
        self.customer_profile.location = 'Hamburg'
        self.customer_profile.tel = '555555555'
        self.customer_profile.description = ''
        self.customer_profile.working_hours = ''
        self.customer_profile.type = 'customer'
        self.customer_profile.save()

        self.client.force_authenticate(user=self.user)

    def test_get_profile_authenticated(self):
        """Test retrieving profile details as an authenticated user."""
        url = reverse('profile-detail', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
            'created_at': self.profile.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        self.assertEqual(response.data, expected_data)

    def test_patch_profile_owner(self):
        """Test updating own profile as the owner."""
        url = reverse('profile-detail', kwargs={'pk': self.user.id})
        data = {
            'first_name': 'Updated',
            'tel': '987654321',
            'description': 'Updated description'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.first_name, 'Updated')
        self.assertEqual(self.profile.tel, '987654321')
        self.assertEqual(self.profile.description, 'Updated description')

    def test_get_business_profiles_authenticated(self):
        """Test retrieving a list of business profiles as an authenticated user."""
        url = reverse('business-profiles-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Two business profiles
        # Check for expected fields without email/created_at
        for profile in response.data:
            self.assertNotIn('email', profile)
            self.assertNotIn('created_at', profile)

    def test_get_customer_profiles_authenticated(self):
        """Test retrieving a list of customer profiles as an authenticated user."""
        url = reverse('customer-profiles-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # One customer profile
        for profile in response.data:
            self.assertNotIn('email', profile)
            self.assertNotIn('created_at', profile)

    def test_get_business_profiles_empty_fields(self):
        """Test business profile list handles empty fields correctly."""
        empty_business_user = User.objects.create_user(
            username='emptybusiness',
            email='empty@business.de',
            password='pass'
        )
        empty_business_profile = empty_business_user.profile
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
        for profile in response.data:
            if profile['user'] == empty_business_user.id:
                self.assertEqual(profile['first_name'], '')
                self.assertEqual(profile['location'], '')

    def test_get_customer_profiles_empty_fields(self):
        """Test customer profile list handles empty fields correctly."""
        empty_customer_user = User.objects.create_user(
            username='emptycustomer',
            email='empty@customer.de',
            password='pass'
        )
        empty_customer_profile = empty_customer_user.profile
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

    def test_get_business_profiles_empty_list(self):
        """Test retrieving business profiles when none exist."""
        Profile.objects.filter(type='business').delete()
        url = reverse('business-profiles-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_customer_profiles_empty_list(self):
        """Test retrieving customer profiles when none exist."""
        Profile.objects.filter(type='customer').delete()
        url = reverse('customer-profiles-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_patch_customer_profile_multipart(self):
        """Test updating a customer profile with multipart/form-data."""
        # Authenticate as the customer user
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('profile-detail', kwargs={'pk': self.customer_user.id})
        data = {
            'first_name': ['UpdatedCustomer'],  # Simulate frontend sending list values
            'last_name': ['Test'],
            'email': ['newcustomer@business.de']
        }
        response = self.client.patch(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer_user.refresh_from_db()
        self.customer_profile.refresh_from_db()
        self.assertEqual(self.customer_profile.first_name, 'UpdatedCustomer')
        self.assertEqual(self.customer_profile.last_name, 'Test')
        self.assertEqual(self.customer_user.email, 'newcustomer@business.de')

    def test_patch_business_profile_multipart(self):
        """Test updating a business profile with multipart/form-data."""
        url = reverse('profile-detail', kwargs={'pk': self.user.id})
        data = {
            'first_name': ['UpdatedBusiness'],
            'last_name': ['Test'],
            'email': ['newbusiness@business.de'],
            'location': ['Munich'],
            'tel': ['987654321'],
            'description': ['Updated business description'],
            'working_hours': ['10-18']
        }
        response = self.client.patch(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.first_name, 'UpdatedBusiness')
        self.assertEqual(self.profile.last_name, 'Test')
        self.assertEqual(self.user.email, 'newbusiness@business.de')
        self.assertEqual(self.profile.location, 'Munich')
        self.assertEqual(self.profile.tel, '987654321')
        self.assertEqual(self.profile.description, 'Updated business description')
        self.assertEqual(self.profile.working_hours, '10-18')


class ProfileTestsUnhappy(APITestCase):
    """Test cases for error (unhappy path) scenarios in profile APIs."""

    def setUp(self):
        self.client = APIClient()
        # Create user and update profile for testing.
        self.user = User.objects.create_user(
            username='testuser',
            email='test@business.de',
            password='testpass123'
        )
        self.profile = self.user.profile
        self.profile.first_name = 'Max'
        self.profile.last_name = 'Mustermann'
        self.profile.location = 'Berlin'
        self.profile.tel = '123456789'
        self.profile.description = 'Business description'
        self.profile.working_hours = '9-17'
        self.profile.type = 'business'
        self.profile.created_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
        self.profile.save()
        self.client.force_authenticate(user=self.user)

    def test_get_profile_unauthenticated(self):
        """Test retrieving a profile without authentication."""
        self.client.force_authenticate(user=None)
        url = reverse('profile-detail', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_profile_not_owner(self):
        """Test updating a profile that is not owned by the user."""
        other_user = User.objects.create_user(username='other', password='pass')
        url = reverse('profile-detail', kwargs={'pk': other_user.id})
        response = self.client.patch(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_business_profiles_unauthenticated(self):
        """Test retrieving business profiles without authentication."""
        self.client.force_authenticate(user=None)
        url = reverse('business-profiles-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_customer_profiles_unauthenticated(self):
        """Test retrieving customer profiles without authentication."""
        self.client.force_authenticate(user=None)
        url = reverse('customer-profiles-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_profile_exceeds_max_length_multipart(self):
        """Test patching a profile with fields exceeding max length using multipart/form-data."""
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={'pk': self.user.id})
        data = {
            'first_name': ['A' * 51],  # Exceeds max_length=50
            'tel': ['123456789012345678901']  # Exceeds max_length=20
        }
        response = self.client.patch(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('first_name', response.data)
        self.assertIn('tel', response.data)
        self.assertEqual(response.data['first_name'], ['Ensure this field has no more than 50 characters.'])
        self.assertEqual(response.data['tel'], ['Ensure this field has no more than 20 characters.'])

    def test_patch_profile_invalid_file_multipart(self):
        """Test patching a profile with an invalid file type using multipart/form-data."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={'pk': self.user.id})
        data = {
            'first_name': ['ValidName'],
            'file': SimpleUploadedFile("test.txt", b"not an image", content_type="text/plain")  # Invalid file type
        }
        response = self.client.patch(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', response.data)
        self.assertEqual(response.data['file'], ['Upload a valid image. The file you uploaded was either not an image or a corrupted image.'])
