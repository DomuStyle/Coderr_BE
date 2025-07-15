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

    # update review tests

    def test_update_review_success(self):
        # test updating review as reviewer
        url = reverse('review-detail', kwargs={'pk': self.review1.id})
        data = {
            'rating': 5,
            'description': 'Noch besser als erwartet!'
        }
        old_updated_at = self.review1.updated_at  # Capture old updated_at as datetime
        response = self.client.patch(url, data, format='json')
        # assert response status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # refresh review from DB to get updated values
        self.review1.refresh_from_db()
        # assert response structure
        self.assertEqual(response.data['id'], self.review1.id)
        self.assertEqual(response.data['business_user'], self.business_user1.id)
        self.assertEqual(response.data['reviewer'], self.reviewer.id)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['description'], 'Noch besser als erwartet!')
        self.assertEqual(response.data['created_at'], self.review1.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'))
        # check updated_at has changed or is at least equal
        self.assertGreaterEqual(self.review1.updated_at, old_updated_at)
        self.assertGreaterEqual(response.data['updated_at'], response.data['created_at'])
    

class ReviewTestsUnhappy(APITestCase):

    def setUp(self):
        self.client = APIClient()
        # create reviewer for duplicate test
        self.user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='testpass'
        )
        Profile.objects.create(user=self.user, type='customer')
        # create business user for duplicate test
        self.business_user1 = User.objects.create_user(
            username='test_business',
            email='test_business@example.com',
            password='testpass'
        )
        Profile.objects.create(user=self.business_user1, type='business')
        # self.client.force_authenticate(user=None)  # Default unauthenticated

        # create reviewer
        self.reviewer = User.objects.create_user(
            username='reviewer',
            password='testpass'
        )
        Profile.objects.create(user=self.reviewer, type='customer')
        # create non-owner user
        self.non_owner = User.objects.create_user(
            username='non_owner',
            password='testpass'
        )
        Profile.objects.create(user=self.non_owner, type='customer')
        # create business user
        self.business_user = User.objects.create_user(
            username='business',
            password='testpass'
        )
        Profile.objects.create(user=self.business_user, type='business')
        # create review for testing
        self.review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.reviewer,
            rating=4,
            description='Test'
        )
        self.client.force_authenticate(user=None)  # Default unauthenticated

    # get review tests

    def test_get_reviews_unauthenticated(self):
        # test listing reviews when not authenticated
        url = reverse('review-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # create review tests

    def test_create_review_unauthenticated(self):
        # test creating review unauthenticated
        self.client.force_authenticate(user=None)
        url = reverse('review-list')
        data = {'business_user': 1, 'rating': 5, 'description': 'Test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review_non_customer(self):
        # test creating as non-customer
        Profile.objects.filter(user=self.user).update(type='business')
        self.client.force_authenticate(user=self.user)
        url = reverse('review-list')
        data = {'business_user': self.business_user1.id, 'rating': 5, 'description': 'Test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  

    def test_create_review_duplicate(self):
        # test creating duplicate review
        self.client.force_authenticate(user=self.user)  # Authenticate as customer
        Review.objects.create(
            business_user=self.business_user1,
            reviewer=self.user,
            rating=4,
            description='Test'
        )
        url = reverse('review-list')
        data = {
            'business_user': self.business_user1.id,
            'rating': 5,
            'description': 'Duplicate'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('You have already reviewed this business user.', str(response.data))

    # update review tests

    def test_update_review_unauthenticated(self):
        # test updating review unauthenticated
        self.client.force_authenticate(user=None)
        url = reverse('review-detail', kwargs={'pk': self.review.id})
        data = {'rating': 5}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_review_not_owner(self):
        # test updating as non-owner
        self.client.force_authenticate(user=self.non_owner)
        url = reverse('review-detail', kwargs={'pk': self.review.id})
        data = {'rating': 5}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('You are not the owner of this review.', str(response.data))

    def test_update_review_invalid_rating(self):
        # test updating with invalid rating
        self.client.force_authenticate(user=self.reviewer)
        url = reverse('review-detail', kwargs={'pk': self.review.id})
        data = {'rating': 0}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Rating must be between 1 and 5.', str(response.data))

    def test_update_review_not_found(self):
        # test updating non-existent review
        self.client.force_authenticate(user=self.reviewer)
        url = reverse('review-detail', kwargs={'pk': 999})
        data = {'rating': 5}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)