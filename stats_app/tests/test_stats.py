from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from profiles_app.models import Profile
from reviews_app.models import Review
from offers_app.models import Offer

class StatsTestsHappy(APITestCase):
    def setUp(self):
        # debug print to verify test DB starts empty (remove after verification)
        print(f"Users before setup: {User.objects.count()}")
        # clear existing data to ensure clean state
        Review.objects.all().delete()
        Profile.objects.all().delete()
        Offer.objects.all().delete()
        # set up test client (no auth needed)
        self.client = APIClient()
        # create data for stats
        # Business profiles (3)
        business_user1 = User.objects.create_user(username='business1', password='test')
        # get existing profile (auto-created by signal) and set type to business
        business_profile1 = Profile.objects.get(user=business_user1)
        business_profile1.type = 'business'
        business_profile1.save()
        business_user2 = User.objects.create_user(username='business2', password='test')
        # get existing profile and set type to business
        business_profile2 = Profile.objects.get(user=business_user2)
        business_profile2.type = 'business'
        business_profile2.save()
        business_user3 = User.objects.create_user(username='business3', password='test')
        # get existing profile and set type to business
        business_profile3 = Profile.objects.get(user=business_user3)
        business_profile3.type = 'business'
        business_profile3.save()
        # Offers (2)
        Offer.objects.create(user=business_user1, title='Offer1', description='Test')
        Offer.objects.create(user=business_user2, title='Offer2', description='Test')
        # Reviews (2, ratings 4 and 5, avg 4.5)
        reviewer = User.objects.create_user(username='reviewer', password='test')
        # get existing profile and set type to customer
        reviewer_profile = Profile.objects.get(user=reviewer)
        reviewer_profile.type = 'customer'
        reviewer_profile.save()
        Review.objects.create(business_user=business_user1, reviewer=reviewer, rating=4, description='Test')
        Review.objects.create(business_user=business_user2, reviewer=reviewer, rating=5, description='Test')

    # get stats tests

    def test_get_base_info(self):
        # test retrieving base info
        url = reverse('base-info')
        response = self.client.get(url)
        # assert response status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # assert response structure
        expected_data = {
            'review_count': 2,
            'average_rating': 4.5,
            'business_profile_count': 3,
            'offer_count': 2
        }
        self.assertEqual(response.data, expected_data)


class StatsTestsUnhappy(APITestCase):

    # get stats tests

    def test_get_base_info_no_data(self):
        # test base info with no data
        Review.objects.all().delete()
        Profile.objects.all().delete()
        Offer.objects.all().delete()
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