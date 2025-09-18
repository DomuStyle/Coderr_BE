"""Test cases for stats-related API endpoints in Django REST Framework, covering happy and unhappy paths."""

from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from profiles_app.models import Profile
from reviews_app.models import Review
from offers_app.models import Offer

class StatsTestsHappy(APITestCase):
    """Test cases for successful (happy path) scenarios in stats APIs."""

    def setUp(self):
        """Set up test data with business profiles, offers, and reviews."""
        # Clear existing data to ensure test isolation.
        Review.objects.all().delete()
        Profile.objects.all().delete()
        Offer.objects.all().delete()
        self.client = APIClient()
        # Create three business profiles.
        business_user1 = User.objects.create_user(username='business1', password='test')
        business_profile1 = Profile.objects.get(user=business_user1)
        business_profile1.type = 'business'
        business_profile1.save()
        business_user2 = User.objects.create_user(username='business2', password='test')
        business_profile2 = Profile.objects.get(user=business_user2)
        business_profile2.type = 'business'
        business_profile2.save()
        business_user3 = User.objects.create_user(username='business3', password='test')
        business_profile3 = Profile.objects.get(user=business_user3)
        business_profile3.type = 'business'
        business_profile3.save()
        # Create two offers.
        Offer.objects.create(user=business_user1, title='Offer1', description='Test')
        Offer.objects.create(user=business_user2, title='Offer2', description='Test')
        # Create two reviews with ratings 4 and 5.
        reviewer = User.objects.create_user(username='reviewer', password='test')
        reviewer_profile = Profile.objects.get(user=reviewer)
        reviewer_profile.type = 'customer'
        reviewer_profile.save()
        Review.objects.create(business_user=business_user1, reviewer=reviewer, rating=4, description='Test')
        Review.objects.create(business_user=business_user2, reviewer=reviewer, rating=5, description='Test')

    def test_get_base_info(self):
        """Test retrieving aggregated statistics via the base info endpoint."""
        url = reverse('base-info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            'review_count': 2,
            'average_rating': 4.5,
            'business_profile_count': 3,
            'offer_count': 2
        }
        self.assertEqual(response.data, expected_data)

class StatsTestsUnhappy(APITestCase):
    """Test cases for error or edge-case (unhappy path) scenarios in stats APIs."""

    def setUp(self):
        """Set up an empty test database for edge-case testing."""
        Review.objects.all().delete()
        Profile.objects.all().delete()
        Offer.objects.all().delete()
        self.client = APIClient()

    def test_get_base_info_no_data(self):
        """Test retrieving base info when no data exists."""
        url = reverse('base-info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            'review_count': 0,
            'average_rating': 0.0,
            'business_profile_count': 0,
            'offer_count': 0
        }
        self.assertEqual(response.data, expected_data)