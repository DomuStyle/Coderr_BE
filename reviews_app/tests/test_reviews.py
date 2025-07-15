from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from profiles_app.models import Profile
from reviews_app.models import Review
from rest_framework import status
from datetime import datetime
import pytz
import time

class ReviewTestsHappy(APITestCase):

    def setUp(self):
        # clear existing reviews to ensure clean state
        Review.objects.all().delete()
        # set up test client
        self.client = APIClient()
        # create reviewer (customer)
        self.reviewer = User.objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='testpass123'
        )
        Profile.objects.create(user=self.reviewer, type='customer')
        # create business user 1
        self.business_user1 = User.objects.create_user(
            username='business1',
            email='business1@example.com',
            password='testpass456'
        )
        Profile.objects.create(user=self.business_user1, type='business')
        # create business user 2
        self.business_user2 = User.objects.create_user(
            username='business2',
            email='business2@example.com',
            password='testpass789'
        )
        Profile.objects.create(user=self.business_user2, type='business')
        # create review 2 first (earlier logical updated_at)
        self.review2 = Review.objects.create(
            business_user=self.business_user2,
            reviewer=self.reviewer,
            rating=5,
            description='Top Qualität und schnelle Lieferung!'
        )
        time.sleep(1)  # Delay to ensure later timestamp for review1
        # create review 1 second (later logical updated_at)
        self.review1 = Review.objects.create(
            business_user=self.business_user1,
            reviewer=self.reviewer,
            rating=4,
            description='Sehr professioneller Service.'
        )
        # authenticate as reviewer
        self.client.force_authenticate(user=self.reviewer)

    # get review tests

    def test_get_reviews_list(self):
        # test listing all reviews
        url = reverse('review-list')
        response = self.client.get(url)
        # assert response status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # assert response structure (order by -updated_at, so review1 first)
        expected_data = [
            {
                'id': self.review1.id,
                'business_user': self.business_user1.id,
                'reviewer': self.reviewer.id,
                'rating': 4,
                'description': 'Sehr professioneller Service.',
                'created_at': self.review1.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'updated_at': self.review1.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')
            },
            {
                'id': self.review2.id,
                'business_user': self.business_user2.id,
                'reviewer': self.reviewer.id,
                'rating': 5,
                'description': 'Top Qualität und schnelle Lieferung!',
                'created_at': self.review2.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'updated_at': self.review2.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
        ]
        self.assertEqual(response.data, expected_data)

    def test_get_reviews_filtered_and_ordered(self):
        # test listing reviews with filter and ordering
        url = reverse('review-list') + f'?business_user_id={self.business_user1.id}&ordering=rating'
        response = self.client.get(url)
        # assert response status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # assert response structure (filtered to business_user1, ordered by rating ascending)
        expected_data = [
            {
                'id': self.review1.id,
                'business_user': self.business_user1.id,
                'reviewer': self.reviewer.id,
                'rating': 4,
                'description': 'Sehr professioneller Service.',
                'created_at': self.review1.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'updated_at': self.review1.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
        ]
        self.assertEqual(response.data, expected_data)

    # create review tests

    def test_create_review_success(self):
        # test creating review as customer
        # Create a new business user not yet reviewed
        business_user3 = User.objects.create_user(
            username='business3',
            email='business3@example.com',
            password='testpass012'
        )
        Profile.objects.create(user=business_user3, type='business')
        url = reverse('review-list')
        data = {
            'business_user': business_user3.id,  # Use new business_user
            'rating': 5,
            'description': 'Hervorragende Erfahrung!'
        }
        response = self.client.post(url, data, format='json')
        # assert response status code is 201
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # assert response structure
        self.assertEqual(response.data['business_user'], business_user3.id)
        self.assertEqual(response.data['reviewer'], self.reviewer.id)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['description'], 'Hervorragende Erfahrung!')
        self.assertEqual(response.data['created_at'], response.data['updated_at'])


class ReviewTestsUnhappy(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=None)  # Default unauthenticated

    # get order tests

    def test_get_reviews_unauthenticated(self):
        # test listing reviews when not authenticated
        url = reverse('review-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)