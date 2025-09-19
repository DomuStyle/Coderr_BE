"""Test cases for review-related API endpoints in Django REST Framework, covering happy and unhappy paths."""
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from profiles_app.models import Profile
from reviews_app.models import Review
from datetime import datetime
import pytz
import time


class ReviewTestsHappy(APITestCase):
    """Test cases for successful (happy path) scenarios in review APIs."""

    def setUp(self):
        """Set up test environment with users and profiles."""
        Review.objects.all().delete()
        self.client = APIClient()
        self.reviewer = User.objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='testpass123'
        )
        self.reviewer_profile = Profile.objects.get(user=self.reviewer)
        self.reviewer_profile.type = 'customer'
        self.reviewer_profile.save()
        self.business_user1 = User.objects.create_user(
            username='business1',
            email='business1@example.com',
            password='testpass456'
        )
        self.business_user1_profile = Profile.objects.get(user=self.business_user1)
        self.business_user1_profile.type = 'business'
        self.business_user1_profile.save()
        self.business_user2 = User.objects.create_user(
            username='business2',
            email='business2@example.com',
            password='testpass789'
        )
        self.business_user2_profile = Profile.objects.get(user=self.business_user2)
        self.business_user2_profile.type = 'business'
        self.business_user2_profile.save()
        self.client.force_authenticate(user=self.reviewer)

    def test_get_reviews_list(self):
        """Test retrieving all reviews in descending order by updated_at."""
        review2 = Review.objects.create(
            business_user=self.business_user2,
            reviewer=self.reviewer,
            rating=5,
            description='Top Qualität und schnelle Lieferung!'
        )
        time.sleep(1)  # Ensure distinct timestamps for ordering
        review1 = Review.objects.create(
            business_user=self.business_user1,
            reviewer=self.reviewer,
            rating=4,
            description='Sehr professioneller Service.'
        )
        url = reverse('review-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = [
            {
                'id': review1.id,
                'business_user': self.business_user1.id,
                'reviewer': self.reviewer.id,
                'rating': 4,
                'description': 'Sehr professioneller Service.',
                'created_at': review1.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'updated_at': review1.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')
            },
            {
                'id': review2.id,
                'business_user': self.business_user2.id,
                'reviewer': self.reviewer.id,
                'rating': 5,
                'description': 'Top Qualität und schnelle Lieferung!',
                'created_at': review2.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'updated_at': review2.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
        ]
        self.assertEqual(response.data, expected_data)

    def test_get_reviews_filtered_and_ordered(self):
        """Test retrieving reviews filtered by business user and ordered by rating."""
        review2 = Review.objects.create(
            business_user=self.business_user2,
            reviewer=self.reviewer,
            rating=5,
            description='Top Qualität und schnelle Lieferung!'
        )
        time.sleep(1)  # Ensure distinct timestamps for ordering
        review1 = Review.objects.create(
            business_user=self.business_user1,
            reviewer=self.reviewer,
            rating=4,
            description='Sehr professioneller Service.'
        )
        url = reverse('review-list') + f'?business_user_id={self.business_user1.id}&ordering=rating'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = [
            {
                'id': review1.id,
                'business_user': self.business_user1.id,
                'reviewer': self.reviewer.id,
                'rating': 4,
                'description': 'Sehr professioneller Service.',
                'created_at': review1.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'updated_at': review1.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
        ]
        self.assertEqual(response.data, expected_data)

    def test_create_review_success(self):
        """Test creating a review as an authenticated customer."""
        url = reverse('review-list')
        data = {
            'business_user': self.business_user1.id,
            'rating': 5,
            'description': 'Excellent service!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['business_user'], self.business_user1.id)
        self.assertEqual(response.data['reviewer'], self.reviewer.id)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['description'], 'Excellent service!')

    def test_update_review_success(self):
        """Test updating a review as the review owner."""
        review = Review.objects.create(
            business_user=self.business_user1,
            reviewer=self.reviewer,
            rating=4,
            description='Original description'
        )
        url = reverse('review-detail', kwargs={'pk': review.id})
        data = {'rating': 5, 'description': 'Updated description'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['description'], 'Updated description')

    def test_delete_review_success(self):
        """Test deleting a review as the review owner."""
        review = Review.objects.create(
            business_user=self.business_user1,
            reviewer=self.reviewer,
            rating=4,
            description='Test review'
        )
        url = reverse('review-detail', kwargs={'pk': review.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=review.id).exists())


class ReviewTestsUnhappy(APITestCase):
    """Test cases for error (unhappy path) scenarios in review APIs."""

    def setUp(self):
        """Set up test environment with users and profiles."""
        Review.objects.all().delete()
        self.client = APIClient()
        self.reviewer = User.objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='testpass123'
        )
        self.reviewer_profile = Profile.objects.get(user=self.reviewer)
        self.reviewer_profile.type = 'customer'
        self.reviewer_profile.save()
        self.business_user = User.objects.create_user(
            username='business',
            email='business@example.com',
            password='testpass456'
        )
        self.business_profile = Profile.objects.get(user=self.business_user)
        self.business_profile.type = 'business'
        self.business_profile.save()
        self.non_owner = User.objects.create_user(
            username='nonowner',
            email='nonowner@example.com',
            password='testpass789'
        )
        self.non_owner_profile = Profile.objects.get(user=self.non_owner)
        self.non_owner_profile.type = 'customer'
        self.non_owner_profile.save()
        self.client.force_authenticate(user=self.reviewer)

    def test_get_reviews_unauthenticated(self):
        """Test retrieving reviews without authentication."""
        self.client.force_authenticate(user=None)
        url = reverse('review-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review_invalid_rating(self):
        """Test creating a review with an invalid rating value."""
        url = reverse('review-list')
        data = {'business_user': self.business_user.id, 'rating': 0, 'description': 'Test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Rating must be between 1 and 5.', str(response.data))

    def test_create_review_invalid_business_user(self):
        """Test creating a review with an invalid business user ID."""
        url = reverse('review-list')
        data = {'business_user': 999, 'rating': 5, 'description': 'Test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Business user not found or not a business profile.', str(response.data))

    def test_create_review_unauthenticated(self):
        """Test creating a review without authentication."""
        self.client.force_authenticate(user=None)
        url = reverse('review-list')
        data = {'business_user': 1, 'rating': 5, 'description': 'Test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review_non_customer(self):
        """Test creating a review as a non-customer user."""
        Profile.objects.filter(user=self.reviewer).update(type='business')
        url = reverse('review-list')
        data = {'business_user': self.business_user.id, 'rating': 5, 'description': 'Test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_review_duplicate(self):
        """Test creating a duplicate review for the same business user."""
        Review.objects.create(
            business_user=self.business_user,
            reviewer=self.reviewer,
            rating=4,
            description='Test'
        )
        url = reverse('review-list')
        data = {
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'Duplicate'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('You have already reviewed this business user.', str(response.data))

    def test_update_review_unauthenticated(self):
        """Test updating a review without authentication."""
        review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.reviewer,
            rating=4,
            description='Test'
        )
        self.client.force_authenticate(user=None)
        url = reverse('review-detail', kwargs={'pk': review.id})
        data = {'rating': 5}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_review_not_owner(self):
        """Test updating a review as a non-owner user."""
        review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.reviewer,
            rating=4,
            description='Test'
        )
        self.client.force_authenticate(user=self.non_owner)
        url = reverse('review-detail', kwargs={'pk': review.id})
        data = {'rating': 5}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('You are not the owner of this review.', str(response.data))

    def test_update_review_invalid_rating(self):
        """Test updating a review with an invalid rating value."""
        review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.reviewer,
            rating=4,
            description='Test'
        )
        url = reverse('review-detail', kwargs={'pk': review.id})
        data = {'rating': 0}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Rating must be between 1 and 5.', str(response.data))

    def test_update_review_not_found(self):
        """Test updating a non-existent review."""
        url = reverse('review-detail', kwargs={'pk': 999})
        data = {'rating': 5}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_review_unauthenticated(self):
        """Test deleting a review without authentication."""
        review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.reviewer,
            rating=4,
            description='Test'
        )
        self.client.force_authenticate(user=None)
        url = reverse('review-detail', kwargs={'pk': review.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_review_not_owner(self):
        """Test deleting a review as a non-owner user."""
        review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.reviewer,
            rating=4,
            description='Test'
        )
        self.client.force_authenticate(user=self.non_owner)
        url = reverse('review-detail', kwargs={'pk': review.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('You are not the owner of this review.', str(response.data))

    def test_delete_review_not_found(self):
        """Test deleting a non-existent review."""
        url = reverse('review-detail', kwargs={'pk': 999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)